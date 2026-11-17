"""
Mutation suite for USLmodel's verify.py (see harness/mutation.py).

Each mutant plants one realistic bug in executable_model and names the checks
that must go red. `python verify.py --mutants` proves every check still bites.
"""

from __future__ import annotations

import dataclasses
import random

from harness.mutation import Mutant, drop_every_nth, patch_result

CONSERVATION = "Tier-1: work conservation (ledger balance)"
NO_OVERLOAD = "Tier-1: no congestion loss without saturation"
NONNEG = "Tier-1: non-negative ledger, success_rate in [0,1]"
LINEAR = "Tier-2: linear regime at low load (throughput tracks arrival)"
DEGRADATION = "Tier-2 (metamorphic): turning degradation off raises the peak"
DECLINE = "Tier-2: USL decline - throughput peaks then falls (not a plateau)"


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


def _half_rate_arrivals(m):
    def arrival_process(env, server):
        rid = 0
        rate = server.cfg.arrival_rate / 2.0       # bug: rate halved (e.g. per-2s unit slip)
        while True:
            yield env.timeout(random.expovariate(rate))
            env.process(server.handle_request(rid))
            rid += 1
    m.arrival_process = arrival_process


def _dead_degradation(m):
    m.Server.degradation_multiplier = lambda self, n_active: 1.0


def _hardcoded_thread_cap(m):
    original = m.Server.__init__

    def init(self, env, cfg):
        # bug: a leftover hard-coded cap of 16 threads overrides cfg.max_threads;
        # admission control then hides the USL collapse behind a plateau
        original(self, env, dataclasses.replace(cfg, max_threads=16))
    m.Server.__init__ = init


MUTANTS = [
    Mutant("lose-requests", "every 10th request vanishes without an outcome",
           (CONSERVATION,), _lose_requests),
    Mutant("ok-marked-timeout", "finished requests also recorded as SLA timeouts",
           (NO_OVERLOAD,), _ok_marked_timeout),
    Mutant("double-count-ok", "each completion counted twice",
           (NONNEG,), _double_count),
    Mutant("half-rate-arrivals", "arrival generator runs at half the configured rate",
           (CONSERVATION, LINEAR), _half_rate_arrivals),
    Mutant("dead-degradation", "USL multiplier never applied (always 1.0)",
           (DEGRADATION,), _dead_degradation),
    Mutant("hardcoded-thread-cap", "hard-coded max_threads=16 overrides the configured cap",
           (DECLINE,), _hardcoded_thread_cap),
]
