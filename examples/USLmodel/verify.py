"""
verify.py — executable form of the "Verification & Validation criteria" section
of this example's MODEL.md. Run it standalone:

    cd examples/USLmodel
    python verify.py

Tier-1: universal conservation laws at a healthy baseline.
Tier-2: law-shape — the USL signature over an arrival-rate sweep (rise -> knee ->
        decline). Per MODEL.md "Validation": three regimes must appear; a system
        that merely plateaus (no decline) means the degradation mechanism is dead.
"""

from __future__ import annotations

import sys
import pathlib

# Let Python find the top-level `harness` package (repo root). Examples are
# independent of each other but share the one harness — by design.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from harness import RunSummary, CheckRunner          # noqa: E402
from harness.invariants import (                      # noqa: E402
    assert_work_conservation,
    assert_no_overload_loss,
    assert_nonnegative,
)
from server_sim import run, Config                   # noqa: E402


def adapt(cfg: Config) -> RunSummary:
    """Translate this model's native dict into the canonical ledger."""
    r = run(cfg)
    completed = r["completed_ok"]
    rejected = r["dropped_buffer"]      # 503 on thread cap — admission, by design
    overload = r["dropped_timeout"]     # SLA miss — congestion loss
    return RunSummary(
        offered=cfg.arrival_rate * cfg.sim_time,   # independent of the model's self-report
        completed=completed,
        rejected=rejected,
        dropped_overload=overload,
        in_flight=r["total_arrivals"] - completed - rejected - overload,
        generated=0.0,
        arrival_rate=cfg.arrival_rate,
        throughput=r["throughput_rps"],
        success_rate=r["success_rate"],
        sim_time=cfg.sim_time,
        saturated=False,                           # arrival_rate=4 is well below saturation
        label="USLmodel default",
    )


runner = CheckRunner("USLmodel")

# Run the model once at the healthy baseline; all Tier-1 checks share the result.
BASELINE = adapt(Config())


@runner.register("Tier-1: work conservation (ledger balance)")
def _conservation() -> None:
    assert_work_conservation(BASELINE)


@runner.register("Tier-1: no congestion loss without saturation")
def _no_overload() -> None:
    assert_no_overload_loss(BASELINE)


@runner.register("Tier-1: non-negative ledger, success_rate in [0,1]")
def _nonneg() -> None:
    assert_nonnegative(BASELINE)


# --- Tier-2: USL law-shape (model-specific; expectation comes from MODEL.md) ---
# Sweep config mirrors sweep.py (sla_seconds=10, max_threads=500) so the timeout-
# driven decline regime is observable. Fixed seed -> deterministic curve.
SWEEP_RATES = [1, 4, 8, 20]


def sweep_throughput(rates: list[float], **overrides) -> dict[float, float]:
    out: dict[float, float] = {}
    for rate in rates:
        r = run(Config(arrival_rate=rate, sim_time=300.0,
                       sla_seconds=10.0, max_threads=500, **overrides))
        out[rate] = r["throughput_rps"]
    return out


CURVE = sweep_throughput(SWEEP_RATES)                              # degradation ON (default)
PEAK_ON = max(CURVE.values())
PEAK_OFF = max(sweep_throughput(SWEEP_RATES, alpha=0.0, beta=0.0).values())  # degradation OFF

# Minimum effect size we insist the mechanism has, beyond simulation noise.
# This is a noise/meaningfulness margin (model-independent), NOT a coefficient-
# tuned threshold like "0.7 * ceiling".
MIN_EFFECT = 0.1


@runner.register("Tier-2: linear regime at low load (throughput tracks arrival)")
def _linear() -> None:
    lo = min(SWEEP_RATES)
    ratio = CURVE[lo] / lo
    assert 0.85 <= ratio <= 1.15, (
        f"low-load throughput does not track arrival: rate={lo}, thr={CURVE[lo]:.2f}, "
        f"ratio={ratio:.2f} (expected ~1.0)"
    )


@runner.register("Tier-2 (metamorphic): turning degradation off raises the peak")
def _degradation_bites() -> None:
    # Metamorphic relation, not a magic-number threshold. A rise->fall curve alone
    # does NOT prove USL: SLA-timeout collapse mimics it even with degradation off
    # (verified empirically). Instead, toggle the mechanism: degradation can only
    # reduce throughput (multiplier >= 1), so disabling it must RAISE the peak. If
    # degradation is dead, toggling changes nothing and the peaks coincide.
    # The "sign" (off >= on) comes from MODEL.md, qualitatively; no tuned constants.
    assert PEAK_ON < PEAK_OFF * (1.0 - MIN_EFFECT), (
        f"disabling degradation did not raise the peak: on={PEAK_ON:.2f}, off={PEAK_OFF:.2f} "
        f"- degradation mechanism appears dead"
    )


@runner.register("Tier-2: USL decline - throughput peaks then falls (not a plateau)")
def _decline() -> None:
    peak = max(CURVE.values())
    peak_rate = max(CURVE, key=CURVE.get)
    hi_rate = max(SWEEP_RATES)
    hi_thr = CURVE[hi_rate]
    # rose: throughput climbed above the low-load point
    assert peak > CURVE[min(SWEEP_RATES)] * 1.5, (
        f"throughput never rose to a knee: peak {peak:.2f} at rate {peak_rate}"
    )
    # knee before the end: the peak is not at the highest rate
    assert peak_rate < hi_rate, (
        f"throughput still rising at max rate (no knee): peak at {peak_rate}"
    )
    # fell: a real declining region (USL), not an M/M/c plateau
    assert hi_thr < 0.7 * peak, (
        f"no decline regime: thr at rate {hi_rate} = {hi_thr:.2f}, "
        f"peak = {peak:.2f} (USL must fall, not plateau)"
    )


if __name__ == "__main__":
    sys.exit(runner.run())
