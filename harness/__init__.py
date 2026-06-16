"""twotakt verification harness — shared, model-independent QA machinery.

Contents:
- run_summary.RunSummary : the canonical ledger every model translates into.
- runner.CheckRunner     : runs all checks for one example, reports a summary.
- invariants.*           : Tier-1 universal conservation laws (skeleton for now).
"""

from .run_summary import RunSummary
from .runner import CheckRunner, CheckResult
from . import invariants

__all__ = ["RunSummary", "CheckRunner", "CheckResult", "invariants"]
