"""
Mutation suite for PowerSearch / queries verify.py (see harness/mutation.py).

Each mutant plants one realistic bug in executable_model and names the checks
that must go red. `python verify.py --mutants` proves every check still bites.
"""

from __future__ import annotations

from harness.mutation import Mutant, drop_every_nth, patch_result

CONSERVATION = "Tier-1: work conservation (ledger balance)"
NO_OVERLOAD = "Tier-1: no congestion loss without saturation"
NONNEG = "Tier-1: non-negative ledger, success_rate in [0,1]"
BASELINE_SLA = "Tier-2: baseline latency well under SLA (healthy verification)"
SURVIVORSHIP = "Tier-2: survivorship bias appears under overload (eff p95 > raw p95)"


def _lose_requests(m):
    drop_every_nth(m.QueryServer, "handle_request", 10)


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


def _latency_in_ms(m):
    def edit(cfg, r):
        for key in ("latency_p50", "latency_p95", "latency_p99",
                    "eff_latency_p50", "eff_latency_p95", "eff_latency_p99"):
            if r[key] is not None:
                r[key] *= 1000.0       # bug: latency reported in ms, SLA kept in s
    patch_result(m, edit)


def _eff_ignores_timeouts(m):
    def edit(cfg, r):
        for p in ("p50", "p95", "p99"):
            r[f"eff_latency_{p}"] = r[f"latency_{p}"]   # bug: timeouts left out of eff latency
    patch_result(m, edit)


MUTANTS = [
    Mutant("lose-requests", "every 10th query vanishes without an outcome",
           (CONSERVATION,), _lose_requests),
    Mutant("ok-marked-timeout", "answered queries also recorded as SLA timeouts",
           (NO_OVERLOAD,), _ok_marked_timeout),
    Mutant("double-count-ok", "each answered query counted twice",
           (NONNEG,), _double_count),
    Mutant("latency-in-ms", "latency reported in milliseconds against an SLA in seconds",
           (BASELINE_SLA,), _latency_in_ms),
    Mutant("eff-ignores-timeouts", "effective latency computed from successes only",
           (SURVIVORSHIP,), _eff_ignores_timeouts),
]
