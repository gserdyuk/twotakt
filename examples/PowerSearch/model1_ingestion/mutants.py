"""
Mutation suite for PowerSearch / ingestion verify.py (see harness/mutation.py).

Each mutant plants one realistic bug in executable_model and names the checks
that must go red. `python verify.py --mutants` proves every check still bites.
"""

from __future__ import annotations

from harness.mutation import Mutant, drop_every_nth, patch_result

CONSERVATION = "Tier-1: work conservation (ledger balance)"
NO_OVERLOAD = "Tier-1: no congestion loss without saturation"
NONNEG = "Tier-1: non-negative ledger, success_rate in [0,1]"
WORKERS = "Tier-2 (metamorphic): undersizing the worker pool binds (stage 1)"
ES_POOL = "Tier-2 (metamorphic): undersizing the ES pool binds (stage 2)"


def _lose_requests(m):
    drop_every_nth(m.IngestionServer, "handle_request", 10)


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


def _resize(attr: str):
    def apply(m):
        original = m.IngestionServer.__init__

        def init(self, env, cfg):
            original(self, env, cfg)
            # bug: the pool is built from a constant; its Config field is never read
            setattr(self, attr, m.simpy.Resource(env, capacity=100000))
        m.IngestionServer.__init__ = init
    return apply


MUTANTS = [
    Mutant("lose-requests", "every 10th event vanishes without an outcome",
           (CONSERVATION,), _lose_requests),
    Mutant("ok-marked-timeout", "indexed events also recorded as SLA timeouts",
           (NO_OVERLOAD,), _ok_marked_timeout),
    Mutant("double-count-ok", "each indexed event counted twice",
           (NONNEG,), _double_count),
    Mutant("workers-ignored", "worker pool sized from a constant; num_workers never read",
           (WORKERS,), _resize("workers")),
    Mutant("es-pool-ignored", "ES pool sized from a constant; es_pool_size never read",
           (ES_POOL,), _resize("es_pool")),
]
