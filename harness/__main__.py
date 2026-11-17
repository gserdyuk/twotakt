"""
Repo-wide runner:

    python -m harness verify-all              # every example: verify.py + mutation suite
    python -m harness verify-all --no-mutants # checks only (fast)
    python -m harness verify-all examples/FaxRx examples/USLmodel   # a subset

An example is any folder under examples/ that contains a verify.py. Each verify.py
runs exactly as a user runs it (`python verify.py`, cwd = its folder). Exit code 0
only if every example is green and, unless --no-mutants, every mutation suite
passes (see harness/mutation.py). This is the command CI runs.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from .mutation import REPO_ROOT, mutation_report, print_report


def discover(args: list[str]) -> list[Path]:
    if args:
        return [Path(a).resolve() for a in args]
    return sorted(p.parent for p in (REPO_ROOT / "examples").rglob("verify.py"))


def run_checks(example: Path) -> tuple[bool, str]:
    env = dict(os.environ, PYTHONIOENCODING="ascii:backslashreplace", PYTHONPATH=str(REPO_ROOT))
    proc = subprocess.run([sys.executable, "verify.py"], cwd=str(example),
                          capture_output=True, text=True, env=env)
    tail = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    summary = tail[-1].strip(" -") if tail else "(no output)"
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
    return proc.returncode == 0, summary


def verify_all(argv: list[str]) -> int:
    mutants = "--no-mutants" not in argv
    examples = discover([a for a in argv if not a.startswith("--")])
    if not examples:
        print("no examples with verify.py found")
        return 1
    rows = []
    for ex in examples:
        name = str(ex.relative_to(REPO_ROOT)) if ex.is_relative_to(REPO_ROOT) else str(ex)
        t0 = time.time()
        ok, summary = run_checks(ex)
        mut = "skipped"
        if mutants:
            rep = mutation_report(ex)
            print_report(rep)
            mut = "ok" if rep.ok else "FAILED"
            ok = ok and rep.ok
        rows.append((name, summary, mut, ok, time.time() - t0))

    print("\n=== verify-all ===")
    for name, summary, mut, ok, dt in rows:
        print(f"  {'[OK]  ' if ok else '[FAIL]'} {name:40s} checks: {summary:16s} "
              f"mutants: {mut:8s} {dt:5.1f}s")
    bad = sum(1 for r in rows if not r[3])
    print(f"  ---- {len(rows) - bad}/{len(rows)} examples green ----")
    return 0 if bad == 0 else 1


def main(argv: list[str]) -> int:
    if argv and argv[0] == "verify-all":
        return verify_all(argv[1:])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
