"""
Persistent negative tests: the mutation suite.

The V&V rule "negative-test every check" used to be a one-off act: break the model
by hand, see the check go red, record it in the dev-log. After the next edit of the
model or of verify.py nobody knew whether the check still bites. This module makes
that rule executable and repeatable.

Each example keeps a `mutants.py` next to its `verify.py`:

    from harness.mutation import Mutant

    MUTANTS = [
        Mutant(
            name="dead-degradation",
            bug="USL multiplier never applied (always 1.0)",
            kills=("Tier-2 (metamorphic): turning degradation off raises the peak",),
            apply=lambda m: setattr(m.Server, "degradation_multiplier",
                                    lambda self, n: 1.0),
        ),
    ]

A mutant is a deliberately planted, *realistic* bug: `apply(model)` receives the
imported `executable_model` module and patches it in place (a class method, a
module function, the result dict). The checks are NOT touched: verify.py is then
imported fresh on top of the broken model, in its own subprocess, and every check
listed in `kills` must go red.

The suite passes only when
  1. the unmutated model is green (otherwise there is nothing to compare against);
  2. every mutant kills every check it claims to kill (a claim that no longer holds
     means the check stopped biting - the failure this module exists to catch);
  3. every check is claimed by at least one mutant (an unguarded check has never
     been shown to be able to fail);
  4. no mutant crashes the model (a crash is not a behavioural bug; it proves
     nothing about the checks).

A check that *structurally cannot* fail (e.g. a ledger whose in_flight is derived
as the residual of the same offered count, so the balance is an identity) may be
listed in `WAIVED = {"<check name>": "<why it cannot fail>"}` in mutants.py. A
waiver is reported on every run - it is a known gap in the trust floor, not a
pass - and becomes an error the moment some mutant does kill that check.

Usage:
    python verify.py --mutants                     # one example
    python -m harness verify-all                   # every example, checks + mutants

Design notes:
- One subprocess per mutant: patches never leak between mutants, and verify.py's
  module-level runs (baselines, sweeps) are recomputed on the broken model.
- Models seed their RNG from Config, so a mutant run is deterministic.
- A mutant may also turn checks red that it does not claim; that is reported for
  information but is not an error (bugs rarely stay in one lane).
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
_MARK = "@@MUTATION-RESULT@@"


@dataclass(frozen=True)
class Mutant:
    name: str                                # short id, unique within the example
    bug: str                                 # the real-world bug this stands for
    kills: Tuple[str, ...]                   # check names that MUST go red
    apply: Callable[[ModuleType], None]      # patches the executable_model module


# ---------------------------------------------------------------------------
# Small helpers for writing mutants
# ---------------------------------------------------------------------------

def patch_result(model: ModuleType, edit: Callable[[object, dict], None]) -> None:
    """Wrap model.run so that `edit(cfg, result)` mutates every result dict.

    Use for bookkeeping/metric bugs (a counter that double-counts, an outcome
    that is mislabelled). verify.py does `from executable_model import run`
    after the patch, so it receives the wrapper.
    """
    original = model.run

    def run(cfg):
        r = original(cfg)
        edit(cfg, r)
        return r

    model.run = run


def drop_every_nth(cls: type, method: str, n: int) -> None:
    """Make every n-th call of generator method `cls.method` vanish without trace.

    Stands for "work silently lost": the request is never recorded, completed,
    rejected or timed out.
    """
    original = getattr(cls, method)
    counter = {"i": 0}

    def wrapper(self, *args, **kwargs):
        counter["i"] += 1
        if counter["i"] % n == 0:
            return
            yield  # pragma: no cover - makes this a generator
        yield from original(self, *args, **kwargs)

    setattr(cls, method, wrapper)


# ---------------------------------------------------------------------------
# Child process: apply one mutant (or none), import verify.py, run the checks
# ---------------------------------------------------------------------------

def _load(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _child(example: Path, mutant_name: Optional[str]) -> None:
    os.chdir(example)
    sys.path.insert(0, str(example))
    sys.path.insert(0, str(REPO_ROOT))
    out: dict = {}
    try:
        model = importlib.import_module("executable_model")
        if mutant_name:
            mutants = _load(example / "mutants.py", "mutants")
            matches = [m for m in mutants.MUTANTS if m.name == mutant_name]
            if not matches:
                raise LookupError(f"no mutant named {mutant_name!r}")
            matches[0].apply(model)
        verify = _load(example / "verify.py", "verify")
        results = verify.runner.collect()
        out["checks"] = [{"name": r.name, "passed": r.passed, "message": r.message}
                         for r in results]
    except Exception as e:  # the model (or verify.py import) crashed under the mutant
        out["crash"] = f"{type(e).__name__}: {e}"
    print(_MARK + json.dumps(out, ensure_ascii=True))


def _spawn(example: Path, mutant_name: Optional[str]) -> dict:
    cmd = [sys.executable, "-m", "harness.mutation", "_child", str(example)]
    if mutant_name:
        cmd.append(mutant_name)
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT), PYTHONIOENCODING="ascii:backslashreplace")
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(example))
    for line in reversed(proc.stdout.splitlines()):
        if line.startswith(_MARK):
            return json.loads(line[len(_MARK):])
    tail = (proc.stderr or proc.stdout).strip().splitlines()[-3:]
    return {"crash": f"child exited {proc.returncode}: " + " | ".join(tail)}


# ---------------------------------------------------------------------------
# Parent: run the suite for one example
# ---------------------------------------------------------------------------

@dataclass
class MutationReport:
    example: str
    ok: bool = True
    problems: List[str] = field(default_factory=list)
    lines: List[str] = field(default_factory=list)
    waived: List[str] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.ok = False
        self.problems.append(msg)


def _ascii(s: str) -> str:
    return s.encode("ascii", "backslashreplace").decode("ascii")


def mutation_report(example: Path, jobs: Optional[int] = None) -> MutationReport:
    example = example.resolve()
    rep = MutationReport(example=str(example.relative_to(REPO_ROOT)) if
                         example.is_relative_to(REPO_ROOT) else str(example))
    mfile = example / "mutants.py"
    if not mfile.exists():
        rep.fail("no mutants.py: no check has been shown to be able to fail")
        return rep

    # Mutant definitions are read in-process only for their names and claims;
    # apply() always runs in a fresh child.
    sys.path.insert(0, str(REPO_ROOT))
    mod = _load(mfile, f"_mutants_{abs(hash(str(example)))}")
    defs: Sequence[Mutant] = mod.MUTANTS
    names = [m.name for m in defs]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        rep.fail(f"duplicate mutant names: {sorted(dupes)}")

    jobs = jobs or min(8, os.cpu_count() or 2)
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        base_f = pool.submit(_spawn, example, None)
        futs: Dict[str, object] = {m.name: pool.submit(_spawn, example, m.name) for m in defs}
        base = base_f.result()
        runs = {name: f.result() for name, f in futs.items()}

    if "crash" in base:
        rep.fail(f"unmutated model crashed: {base['crash']}")
        return rep
    checks = [c["name"] for c in base["checks"]]
    red_base = [c["name"] for c in base["checks"] if not c["passed"]]
    if red_base:
        rep.fail(f"unmutated model is not green ({len(red_base)} red): fix verify first")
        return rep

    waived: Dict[str, str] = dict(getattr(mod, "WAIVED", {}))
    for c in waived:
        if c not in checks:
            rep.fail(f"waiver for unknown check {c!r}")
    guarded: Dict[str, List[str]] = {c: [] for c in checks}
    for m in defs:
        res = runs[m.name]
        unknown = [k for k in m.kills if k not in guarded]
        if unknown:
            rep.fail(f"mutant {m.name}: claims unknown check(s) {unknown}")
        if "crash" in res:
            rep.fail(f"mutant {m.name}: crashed the model ({res['crash']}) - "
                     f"a crash is not a behavioural bug")
            rep.lines.append(f"  [CRASH] {m.name}")
            continue
        red = {c["name"] for c in res["checks"] if not c["passed"]}
        missed = [k for k in m.kills if k in guarded and k not in red]
        extra = sorted(red - set(m.kills))
        for k in m.kills:
            if k in red:
                guarded[k].append(m.name)
        if missed:
            rep.fail(f"mutant {m.name} SURVIVED check(s): {missed}")
            mark = "[SURVIVED]"
        elif not m.kills:
            rep.fail(f"mutant {m.name}: claims no checks")
            mark = "[EMPTY]"
        else:
            mark = "[KILLED]  "
        rep.lines.append(f"  {mark} {m.name}: {m.bug}")
        if extra:
            rep.lines.append(f"             (also red: {len(extra)} unclaimed check(s))")

    for c, killers in guarded.items():
        if c in waived:
            if killers:
                rep.fail(f"stale waiver: {c!r} is waived but mutant(s) {killers} kill it")
            else:
                rep.waived.append(c)
                rep.lines.append(f"  [WAIVED]   {c}\n             reason: {waived[c]}")
        elif not killers:
            rep.fail(f"unguarded check (no mutant turns it red): {c!r}")
    return rep


def print_report(rep: MutationReport) -> None:
    print(f"\n=== mutants: {rep.example} ===")
    for line in rep.lines:
        print(_ascii(line))
    for p in rep.problems:
        print(_ascii(f"  [FAIL] {p}"))
    if not rep.ok:
        status = "FAILED"
    elif rep.waived:
        status = f"all mutants killed; {len(rep.waived)} check(s) WAIVED as unable to fail"
    else:
        status = "all checks guarded, all mutants killed"
    print(f"  ---- {status} ----")


def run_mutants(example: Path) -> int:
    rep = mutation_report(example)
    print_report(rep)
    return 0 if rep.ok else 1


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "_child":
        _child(Path(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else None)
    elif len(sys.argv) == 2:
        sys.exit(run_mutants(Path(sys.argv[1])))
    else:
        print("usage: python -m harness.mutation <example_dir>")
        sys.exit(2)
