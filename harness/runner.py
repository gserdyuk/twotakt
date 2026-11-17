"""
The mechanism: run ALL registered checks for one example, catching failures so
one broken check does not hide the rest, then print a summary and return an exit
code (0 = all green, 1 = something failed).

Used by each example's verify.py. This operates at the level of a single example;
the repo-wide runner is `python -m harness verify-all` (harness/__main__.py).

A plain `assert` aborts on the first failure; this lets us see every result.
"""

from __future__ import annotations

import pathlib
import sys
from dataclasses import dataclass
from typing import Callable, List


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str = ""


class CheckRunner:
    def __init__(self, title: str):
        self.title = title
        self._checks: List[tuple[str, Callable[[], None]]] = []

    def register(self, name: str):
        """Decorator: register a check function (it asserts; raising = fail)."""
        def deco(fn: Callable[[], None]) -> Callable[[], None]:
            self._checks.append((name, fn))
            return fn
        return deco

    @property
    def names(self) -> List[str]:
        return [name for name, _ in self._checks]

    def run(self) -> int:
        """Run every check, print the summary, return the exit code.

        `python verify.py --mutants` instead runs the example's mutation suite
        (harness/mutation.py): every check must go red on the mutants that
        claim to kill it, so a check that no longer bites is caught on every run.
        """
        if "--mutants" in sys.argv[1:]:
            from .mutation import run_mutants
            main_file = getattr(sys.modules.get("__main__"), "__file__", None)
            if not main_file:
                print("--mutants needs to be run as `python verify.py --mutants`")
                return 2
            return run_mutants(pathlib.Path(main_file).resolve().parent)
        results = self.collect()
        self._print(results)
        return 0 if all(r.passed for r in results) else 1

    def collect(self) -> List[CheckResult]:
        """Run every check without printing (used by the mutation runner)."""
        results: List[CheckResult] = []
        for name, fn in self._checks:
            try:
                fn()
                results.append(CheckResult(name, True))
            except AssertionError as e:
                results.append(CheckResult(name, False, str(e) or "assertion failed"))
            except Exception as e:  # a check that errors out is a failure, not a crash
                results.append(CheckResult(name, False, f"ERROR {type(e).__name__}: {e}"))
        return results

    def _print(self, results: List[CheckResult]) -> None:
        print(f"\n=== verify: {self.title} ===")
        for r in results:
            mark = "[OK]  " if r.passed else "[FAIL]"
            line = f"  {mark} {r.name}"
            if not r.passed and r.message:
                line += f"\n      {r.message}"
            print(line)
        passed = sum(1 for r in results if r.passed)
        print(f"  ---- {passed}/{len(results)} green ----")
