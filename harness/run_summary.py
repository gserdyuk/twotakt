"""
The contract: a canonical, balanced ledger every model translates its own
metrics into, so the shared Tier-1 invariants (harness/invariants.py) can be
written once and applied to any model regardless of its native field names.

Design note — balanced ledger with a generation term.
The accounting identity we want to be able to assert is the continuity equation:

    offered + generated == completed + rejected + dropped_overload + in_flight

`generated` defaults to 0: our current examples have no internal source, but a
future "generating" system (keep-alive / heartbeat / retry storm) just fills in
this term and the universal law keeps holding without new logic.

Design note — two kinds of loss (added when FaxRx, an Erlang-B blocking system,
was onboarded). "Dropped" is not one thing:
- `rejected` — admission / blocking loss, BY DESIGN: a 503 on a full thread cap,
  an Erlang-B busy signal when all SIP channels are taken. Present even at low
  load; it is the system working as intended, not a fault.
- `dropped_overload` — congestion loss: an SLA timeout under load, a queue that
  overflowed because the system fell behind. This is the failure mode.
The universal "no loss below saturation" law must forbid only `dropped_overload`;
rejection is allowed. Lumping them (as the first cut did) makes the law fail on a
healthy blocking system.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RunSummary:
    # --- ledger (counts over the whole run) ---
    offered: float           # external arrivals (independent of the model's self-report where possible)
    completed: int           # finished successfully
    rejected: int = 0        # admission / blocking loss — by design (503, Erlang-B busy)
    dropped_overload: int = 0  # congestion loss — timeout / SLA miss under load
    in_flight: int = 0       # still in system at sim end
    generated: float = 0.0   # internally generated work (keep-alive etc.); 0 for now

    # --- rates / quality ---
    arrival_rate: float = 0.0
    throughput: float = 0.0
    success_rate: float = 0.0

    # --- context ---
    sim_time: float = 0.0
    saturated: bool = False  # operating-point flag: is this point above saturation (congestion regime)?
    label: str = ""          # for multi-class models (e.g. FaxRx plain / ocr)

    @property
    def dropped(self) -> int:
        """Total loss = admission rejection + congestion loss."""
        return self.rejected + self.dropped_overload
