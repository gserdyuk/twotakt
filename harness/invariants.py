"""
Tier-1 invariants: universal conservation laws, human-authored, written ONCE and
applied to any model via the RunSummary contract. They must stay independent of
any model's code generator — that independence is the whole point.

Each law carries its validity region (e.g. "below saturation"). An invariant that
does not hold at the given operating point is either out of its region (caller's
mistake) or a real bug in the model.

Universality note: these were refined when FaxRx (Erlang-B blocking) was onboarded.
"No loss below saturation" had a hidden assumption — a queueing (wait) discipline.
A blocking system rejects by design even at low load, so the law forbids only
*congestion* loss (`dropped_overload`); *admission* loss (`rejected`) is allowed.
"""

from __future__ import annotations

from .run_summary import RunSummary


def assert_work_conservation(s: RunSummary, tol: float = 0.05) -> None:
    """Ledger balance — nothing is silently created or lost (ALWAYS holds).

        offered + generated == completed + rejected + dropped_overload + in_flight

    Every unit offered/generated ends up somewhere: completed, rejected at
    admission, lost to congestion, or still in flight. While `in_flight` is
    derived as a residual by the adapter, this effectively checks that the arrival
    process produced ~ the expected count (offered = arrival_rate * sim_time,
    computed independently of the model). Catches lost / miscounted work.
    """
    inflow = s.offered + s.generated
    accounted = s.completed + s.rejected + s.dropped_overload + s.in_flight
    bound = tol * inflow if inflow else tol
    assert abs(inflow - accounted) <= bound, (
        f"ledger imbalance: in={inflow:.1f} (offered {s.offered:.1f} + generated {s.generated:.1f}) "
        f"!= accounted {accounted:.1f} (completed {s.completed} + rejected {s.rejected} + "
        f"overload {s.dropped_overload} + in_flight {s.in_flight}); tol={bound:.1f}"
    )


def assert_no_overload_loss(s: RunSummary, tol: float = 0.01) -> None:
    """Below saturation, congestion loss is negligible.

    Forbids *congestion* loss (`dropped_overload`: SLA timeouts, queue overflow)
    when the system is not in the congestion regime. Admission loss (`rejected`:
    503, Erlang-B busy) is allowed — it is by design, present even at low load.
    A small tolerance (not strict 0) absorbs the rare timeout in a healthy run.
    """
    if not s.saturated:
        bound = tol * s.offered if s.offered else 0
        assert s.dropped_overload <= bound, (
            f"congestion loss without saturation: dropped_overload {s.dropped_overload} "
            f"> tol {bound:.1f} at an unsaturated operating point"
        )


def assert_nonnegative(s: RunSummary) -> None:
    """No negative counts / rates; success_rate is a probability in [0, 1]."""
    for name in ("offered", "generated", "completed", "rejected", "dropped_overload",
                 "in_flight", "arrival_rate", "throughput", "sim_time"):
        v = getattr(s, name)
        assert v is not None and v >= 0, f"{name} is negative or None: {v!r}"
    assert s.success_rate is not None and 0.0 <= s.success_rate <= 1.0, (
        f"success_rate out of [0,1]: {s.success_rate!r}"
    )
