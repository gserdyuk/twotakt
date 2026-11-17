"""
mutants.py - the persistent negative tests for this example's verify.py.

Run:   python verify.py --mutants        (or: python -m harness verify-all)

Each Mutant plants ONE realistic bug into executable_model and names the checks
that must go red. The suite fails if a mutant survives, a check is claimed by no
mutant (unguarded), or a mutant crashes the model (a crash proves nothing).

Rules of thumb:
  - Name the bug as it would appear in a code review ("pool sized from a constant",
    "latency reported in ms"), not as the check it targets.
  - Prefer behavioural bugs (patch a Server method / __init__ / arrival_process)
    for Tier-2; bookkeeping bugs (patch_result) are fine for Tier-1 ledgers.
  - Every check must be claimed by at least one mutant. A check that structurally
    cannot fail goes into WAIVED with the reason - it is reported on every run.
"""

from __future__ import annotations

import dataclasses

from harness.mutation import Mutant, drop_every_nth, patch_result

# Copy check names verbatim from verify.py (a typo is reported as "unknown check").
CONSERVATION = "Tier-1: work conservation (ledger balance)"
NO_OVERLOAD = "Tier-1: no congestion loss without saturation"
NONNEG = "Tier-1: non-negative ledger, success_rate in [0,1]"
MECHANISM = "Tier-2 (metamorphic): <your mechanism toggle check>"


def _lose_requests(m):
    drop_every_nth(m.Server, "handle_request", 10)


def _ok_marked_timeout(m):
    def edit(cfg, r):
        moved = r["completed_ok"] // 10
        r["completed_ok"] -= moved
        r["dropped_timeout"] += moved
    patch_result(m, edit)


def _double_count(m):
    def edit(cfg, r):
        r["completed_ok"] *= 2
        r["success_rate"] = r["completed_ok"] / r["total_arrivals"]
    patch_result(m, edit)


def _pool_ignored(m):
    original = m.Server.__init__

    def init(self, env, cfg):
        original(self, env, cfg)
        self.pool = m.simpy.Resource(env, capacity=100000)   # Config field never read
    m.Server.__init__ = init


def _config_override(**fields):
    """A Config field silently replaced (hard-coded value, wrong field read)."""
    def apply(m):
        original = m.Server.__init__

        def init(self, env, cfg):
            original(self, env, dataclasses.replace(cfg, **fields))
        m.Server.__init__ = init
    return apply


MUTANTS = [
    Mutant("lose-requests", "every 10th request vanishes without an outcome",
           (CONSERVATION,), _lose_requests),
    Mutant("ok-marked-timeout", "finished requests also recorded as SLA timeouts",
           (NO_OVERLOAD,), _ok_marked_timeout),
    Mutant("double-count-ok", "each completion counted twice",
           (NONNEG,), _double_count),
    Mutant("pool-ignored", "pool sized from a constant; its Config field never read",
           (MECHANISM,), _pool_ignored),
]

WAIVED: dict[str, str] = {}
