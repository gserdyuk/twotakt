"""
verify.py — executable form of the "Verification & Validation criteria" section
of this example's MODEL.md. Run standalone:

    cd examples/USLDBmodel
    python verify.py

USLDBmodel = USLmodel + a DB connection pool (simpy.Resource(capacity=db_pool_size),
M/M/c). So:
- Tier-1 conservation transfers unchanged (same run() dict shape as USLmodel).
- Tier-2 keeps the USL shape/degradation checks (CPU is still USL) AND adds a
  pool-exhaustion metamorphic relation — the "interaction bottleneck".

NOTE (duplication): the USL shape checks (linear / degradation-MR / decline) and the
sweep helper are near-identical to examples/USLmodel/verify.py. Kept self-contained so
each example runs standalone (examples are independent). USLmodel + USLDBmodel are the
only two USL models, so extracting a shared harness/shapes.py is a reasonable next step
if a third consumer appears — flagged, not done.
"""

from __future__ import annotations

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from harness import RunSummary, CheckRunner          # noqa: E402
from harness.invariants import (                      # noqa: E402
    assert_work_conservation,
    assert_no_overload_loss,
    assert_nonnegative,
)
from server_sim import run, Config                   # noqa: E402


def adapt(cfg: Config) -> RunSummary:
    """Translate the native dict into the canonical ledger (same keys as USLmodel)."""
    r = run(cfg)
    completed = r["completed_ok"]
    rejected = r["dropped_buffer"]      # 503 on thread cap — admission, by design
    overload = r["dropped_timeout"]     # SLA miss — congestion loss
    return RunSummary(
        offered=cfg.arrival_rate * cfg.sim_time,
        completed=completed,
        rejected=rejected,
        dropped_overload=overload,
        in_flight=r["total_arrivals"] - completed - rejected - overload,
        generated=0.0,
        arrival_rate=cfg.arrival_rate,
        throughput=r["throughput_rps"],
        success_rate=r["success_rate"],
        sim_time=cfg.sim_time,
        saturated=False,                              # arrival_rate=4, pool=8: below saturation
        label=f"USLDBmodel default (pool={Config().db_pool_size})",
    )


runner = CheckRunner("USLDBmodel")

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


# --- Tier-2 (model-specific) ------------------------------------------------
# Sweep mirrors sweep.py (sla_seconds=10, max_threads=500). Fixed seed -> deterministic.
SWEEP_RATES = [1, 4, 8, 20]
OVERLOAD_RATE = 8          # past the CPU knee: where the DB pool actually binds
MIN_EFFECT = 0.1          # noise/meaningfulness margin (model-independent), not a tuned threshold


def sweep_throughput(rates: list[float], **overrides) -> dict[float, float]:
    out: dict[float, float] = {}
    for rate in rates:
        r = run(Config(arrival_rate=rate, sim_time=300.0,
                       sla_seconds=10.0, max_threads=500, **overrides))
        out[rate] = r["throughput_rps"]
    return out


def throughput_at(rate: float, **overrides) -> float:
    return run(Config(arrival_rate=rate, sim_time=300.0,
                      sla_seconds=10.0, max_threads=500, **overrides))["throughput_rps"]


CURVE = sweep_throughput(SWEEP_RATES)                              # degradation ON, default pool
PEAK_ON = max(CURVE.values())
PEAK_OFF = max(sweep_throughput(SWEEP_RATES, alpha=0.0, beta=0.0).values())


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
    assert PEAK_ON < PEAK_OFF * (1.0 - MIN_EFFECT), (
        f"disabling degradation did not raise the peak: on={PEAK_ON:.2f}, off={PEAK_OFF:.2f} "
        f"- degradation mechanism appears dead"
    )


@runner.register("Tier-2: USL decline - throughput peaks then falls (not a plateau)")
def _decline() -> None:
    peak = max(CURVE.values())
    peak_rate = max(CURVE, key=CURVE.get)
    hi_rate = max(SWEEP_RATES)
    assert peak > CURVE[min(SWEEP_RATES)] * 1.5, (
        f"throughput never rose to a knee: peak {peak:.2f} at rate {peak_rate}"
    )
    assert peak_rate < hi_rate, (
        f"throughput still rising at max rate (no knee): peak at {peak_rate}"
    )
    assert CURVE[hi_rate] < 0.7 * peak, (
        f"no decline regime: thr at rate {hi_rate} = {CURVE[hi_rate]:.2f}, peak = {peak:.2f}"
    )


@runner.register("Tier-2 (metamorphic): shrinking the DB pool binds under overload")
def _pool_bites() -> None:
    # The interaction bottleneck. The pool does NOT change the PEAK (CPU/USL bound at
    # the knee, where even pool=1 keeps up) — it binds in OVERLOAD. So toggle the pool
    # at the overload point, not the peak: a smaller pool must yield lower throughput
    # there. If the pool is not exercised, the two coincide -> caught. (MODEL.md
    # validation #2: pool exhaustion; "if curves identical for all pool sizes, the pool
    # resource is not being exercised".)
    thr_small = throughput_at(OVERLOAD_RATE, db_pool_size=1)
    thr_default = throughput_at(OVERLOAD_RATE, db_pool_size=Config().db_pool_size)
    assert thr_small < thr_default * (1.0 - MIN_EFFECT), (
        f"DB pool not exercised: at rate {OVERLOAD_RATE}, pool=1 throughput {thr_small:.2f} "
        f"is not below pool={Config().db_pool_size} throughput {thr_default:.2f}"
    )


if __name__ == "__main__":
    sys.exit(runner.run())
