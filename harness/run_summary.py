"""
The contract: a canonical, balanced ledger every model translates its own
metrics into, so the shared Tier-1 invariants (harness/invariants.py) can be
written once and applied to any model regardless of its native field names.

Design note — balanced ledger with a generation term.
The accounting identity we want to be able to assert is the continuity equation:

    offered + generated == completed + dropped + in_flight        (work balance)

`generated` defaults to 0: our current examples have no internal source, but a
future "generating" system (keep-alive / heartbeat / retry storm) just fills in
this term and the universal law keeps holding without new logic.

This is a skeleton. Fields will grow as the Tier-1 invariants need them.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RunSummary:
    # --- ledger (counts over the whole run) ---
    offered: float          # external arrivals admitted (independent of the model's self-report where possible)
    completed: int          # finished successfully
    dropped: int            # rejected / timed out
    in_flight: int = 0      # still in system at sim end
    generated: float = 0.0  # internally generated work (keep-alive etc.); 0 for now

    # --- rates / quality ---
    arrival_rate: float = 0.0
    throughput: float = 0.0
    success_rate: float = 0.0

    # --- context ---
    sim_time: float = 0.0
    saturated: bool = False  # operating-point flag: is this point above saturation?
    label: str = ""          # for multi-class models (e.g. FaxRx plain / ocr)
