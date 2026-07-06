"""
verify.py — TEMPLATE. The executable form of Phase 7 V&V for one example.

Copy into an example folder and fill the TODOs. Run standalone:

    cd examples/<name>
    python verify.py        # per-check pass/fail summary; exit 0 only if all green

Green is the gate: the executable model is trustworthy enough to run sweeps on
(Phase 8). See harness/README.md for what green does and does NOT mean.

Requires the shared validation harness package `harness/` on the path (the fixed,
human-authored trust floor — do NOT edit invariants.py per project). In twotakt it
lives at the repo root; the sys.path line below points there. In a fresh project,
copy `harness/` alongside your examples and adjust the path.

METHOD (keep it small — see the proportionality razor in harness/README.md):
  1. Adapt the model's own run() output into the canonical RunSummary ledger.
  2. Tier-1: universal conservation invariants from harness (reused, not rewritten).
  3. Tier-2: per-model checks written from THIS model's MODEL.md — curve shape, and
     metamorphic toggles (disable a mechanism -> the metric must move the right way),
     each taken at the operating point where the mechanism binds.
  4. NEGATIVE-TEST every check: confirm it goes red on a deliberately broken model.
     A check that stays green on a broken model is worthless.
"""

from __future__ import annotations

import sys
import pathlib

# Point at the repo root so `import harness` resolves. Adjust parents[N] to the depth
# of this file below the root (examples/<name>/verify.py -> parents[2]).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from harness import RunSummary, CheckRunner          # noqa: E402
from harness.invariants import (                      # noqa: E402
    assert_work_conservation,
    assert_no_overload_loss,
    assert_nonnegative,
)
from executable_model import run, Config                   # noqa: E402


def adapt(cfg: Config, r: dict, saturated: bool = False) -> RunSummary:
    """Translate this model's native dict into the canonical ledger.

    Map each drop to the right kind: `rejected` = admission/blocking (by design, e.g.
    503 on a cap, an Erlang-B busy); `dropped_overload` = congestion (SLA timeout,
    queue overflow). Multi-class / multi-stage models return several RunSummary.
    """
    completed = r["completed_ok"]              # TODO: your success count
    rejected = r["dropped_buffer"]             # TODO: admission loss (by design), or 0
    overload = r["dropped_timeout"]            # TODO: congestion loss
    return RunSummary(
        offered=cfg.arrival_rate * cfg.sim_time,   # prefer a source independent of the model
        completed=completed,
        rejected=rejected,
        dropped_overload=overload,
        in_flight=r["total_arrivals"] - completed - rejected - overload,
        arrival_rate=cfg.arrival_rate,
        throughput=r["throughput_rps"],        # TODO: your throughput key
        success_rate=r["success_rate"],
        sim_time=cfg.sim_time,
        saturated=saturated,
        label="<example> default",
    )


# Deliberately-healthy baseline: light load AND every stage generously provisioned
# (a long service time saturates a small pool at ANY load — provision all stages).
BASE_CFG = Config()                             # TODO: a genuinely healthy config
BASELINE = adapt(BASE_CFG, run(BASE_CFG), saturated=False)

runner = CheckRunner("<example>")


# --- Tier-1: universal conservation (reused from harness) --------------------
@runner.register("Tier-1: work conservation (ledger balance)")
def _conservation() -> None:
    assert_work_conservation(BASELINE)


@runner.register("Tier-1: no congestion loss without saturation")
def _no_overload() -> None:
    assert_no_overload_loss(BASELINE)


@runner.register("Tier-1: non-negative ledger, success_rate in [0,1]")
def _nonneg() -> None:
    assert_nonnegative(BASELINE)


# --- Tier-2: per-model (from MODEL.md) --------------------------------------
# Example metamorphic toggle: disabling a mechanism must move the metric the right way.
# No magic-number thresholds — only the DIRECTION, taken from MODEL.md, at the binding point.
#
# @runner.register("Tier-2 (metamorphic): turning <mechanism> off raises <metric>")
# def _mechanism_bites() -> None:
#     on = peak_metric(Config())
#     off = peak_metric(Config(<mechanism>_off))
#     assert on < off * (1.0 - 0.1), f"<mechanism> appears dead: on={on} off={off}"


if __name__ == "__main__":
    sys.exit(runner.run())
