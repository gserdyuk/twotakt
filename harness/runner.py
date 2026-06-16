"""
The mechanism: run ALL registered checks for one example, catching failures so
one broken check does not hide the rest, then print a summary and return an exit
code (0 = all green, 1 = something failed).

Used by each example's verify.py — there is no repo-wide runner yet (examples are
independent; "run them all" scaffolding comes later). This operates at the level
of a single example.

A plain `assert` aborts on the first failure; this lets us see every result.
"""

from __future__ import annotations

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

    def run(self) -> int:
        results: List[CheckResult] = []
        for name, fn in self._checks:
            try:
                fn()
                results.append(CheckResult(name, True))
            except AssertionError as e:
                results.append(CheckResult(name, False, str(e) or "assertion failed"))
            except Exception as e:  # a check that errors out is a failure, not a crash
                results.append(CheckResult(name, False, f"ERROR {type(e).__name__}: {e}"))

        self._print(results)
        return 0 if all(r.passed for r in results) else 1

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
