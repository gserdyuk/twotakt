"""
Tier-1 invariants: universal conservation laws, human-authored, written ONCE and
applied to any model via the RunSummary contract. They must stay independent of
any model's code generator — that independence is the whole point.

Each law carries its validity region (e.g. "below saturation"). An invariant that
does not hold at the given operating point is either out of its region (caller's
mistake) or a real bug in the model.
"""

from __future__ import annotations

from .run_summary import RunSummary


def assert_work_conservation(s: RunSummary, tol: float = 0.05) -> None:
    """Work is conserved — nothing is silently created or lost.

    Two parts:
    1. Ledger balance (ALWAYS holds): every unit offered/generated ended up
       somewhere — completed, dropped, or still in flight.
           offered + generated == completed + dropped + in_flight
       NOTE: while `in_flight` is derived as a residual by the adapter, this part
       effectively checks that the arrival process produced ~ the expected count
       (offered = arrival_rate * sim_time, computed independently of the model).
       Detecting *internal* loss needs the model to report in_flight independently
       — a contract refinement deferred to later.
    2. Throughput continuity (BELOW SATURATION only): if the system is not
       saturated, what comes out equals what came in — almost everything completes.
           completed ~= offered
       Above saturation `completed < offered` is correct, not a bug, so this part
       is skipped.
    """
    inflow = s.offered + s.generated
    accounted = s.completed + s.dropped + s.in_flight
    bound = tol * inflow if inflow else tol
    assert abs(inflow - accounted) <= bound, (
        f"ledger imbalance: in={inflow:.1f} (offered {s.offered:.1f} + generated {s.generated:.1f}) "
        f"!= accounted {accounted:.1f} (completed {s.completed} + dropped {s.dropped} + in_flight {s.in_flight}); "
        f"tol={bound:.1f}"
    )

    if not s.saturated:
        assert abs(s.completed - s.offered) <= tol * s.offered, (
            f"throughput continuity broken below saturation: completed {s.completed} "
            f"!= offered {s.offered:.1f} (tol {tol * s.offered:.1f})"
        )


def assert_no_drops_without_congestion(s: RunSummary) -> None:
    """No drops when the system is not saturated."""
    if not s.saturated:
        assert s.dropped == 0, (
            f"drops without congestion: dropped {s.dropped} at an unsaturated operating point"
        )


def assert_nonnegative(s: RunSummary) -> None:
    """No negative counts / rates; success_rate is a probability in [0, 1]."""
    for name in ("offered", "generated", "completed", "dropped", "in_flight",
                 "arrival_rate", "throughput", "sim_time"):
        v = getattr(s, name)
        assert v is not None and v >= 0, f"{name} is negative or None: {v!r}"
    assert s.success_rate is not None and 0.0 <= s.success_rate <= 1.0, (
        f"success_rate out of [0,1]: {s.success_rate!r}"
    )
