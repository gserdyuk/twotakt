"""
verify.py — executable form of the "What success looks like" (V&V) section of this
submodel's MODEL.md. Run standalone:

    cd examples/PowerSearch/model2_queries
    python verify.py

PowerSearch queries = a cascade of two M/M/c queues (search workers -> ES query pool)
under square-wave burst load. Its signature lesson is survivorship bias: raw latency of
successful requests understates degradation under overload, because the slow requests
timed out and are missing from the sample. Effective latency (timeouts counted at SLA)
is the honest metric. The distinctive Tier-2 check asserts the survivorship gap appears.
"""

from __future__ import annotations

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from harness import RunSummary, CheckRunner          # noqa: E402
from harness.invariants import (                      # noqa: E402
    assert_work_conservation,
    assert_no_overload_loss,
    assert_nonnegative,
)
from server_sim import run, Config                   # noqa: E402


# Healthy baseline = no burst (MODEL.md smoke test uses burst_multiplier=1.0).
BASE_CFG = Config(burst_multiplier=1.0)
BASE = run(BASE_CFG)


def adapt(cfg: Config, r: dict) -> RunSummary:
    completed = r["completed_ok"]
    rejected = r["dropped_buffer"]      # admission cap; off by default
    overload = r["dropped_timeout"]     # SLA miss — congestion loss
    arrival = cfg.base_arrival_rate     # burst=1 -> constant base rate
    return RunSummary(
        offered=arrival * cfg.sim_time,
        completed=completed,
        rejected=rejected,
        dropped_overload=overload,
        in_flight=r["total_arrivals"] - completed - rejected - overload,
        arrival_rate=arrival,
        throughput=r["throughput_rps"],
        success_rate=r["success_rate"],
        sim_time=cfg.sim_time,
        saturated=False,                # workers cap 1250 >> base 100
        label="PowerSearch queries (burst=1 baseline)",
    )


SUMMARY = adapt(BASE_CFG, BASE)

runner = CheckRunner("PowerSearch / queries")


@runner.register("Tier-1: work conservation (ledger balance)")
def _conservation() -> None:
    assert_work_conservation(SUMMARY)


@runner.register("Tier-1: no congestion loss without saturation")
def _no_overload() -> None:
    assert_no_overload_loss(SUMMARY)


@runner.register("Tier-1: non-negative ledger, success_rate in [0,1]")
def _nonneg() -> None:
    assert_nonnegative(SUMMARY)


@runner.register("Tier-2: baseline latency well under SLA (healthy verification)")
def _baseline_sla() -> None:
    # Verification, not the research verdict: at the deliberately-healthy baseline the
    # latency pipeline must produce a sane value comfortably under the SLA. (Whether the
    # system meets SLA *under load* is the sweep's output, not asserted here.)
    eff_p95 = BASE["eff_latency_p95"]
    assert eff_p95 < BASE_CFG.sla_seconds, (
        f"baseline eff p95 {eff_p95:.3f} not under SLA {BASE_CFG.sla_seconds}"
    )


@runner.register("Tier-2: survivorship bias appears under overload (eff p95 > raw p95)")
def _survivorship() -> None:
    # The PowerSearch signature. Under overload, surviving requests are a biased (optimistic)
    # sample; effective latency (timeouts at SLA) must exceed raw latency of successes. If
    # they coincide, effective-latency is not counting timeouts -> survivorship bias hidden.
    over = run(Config(num_search_workers=10))           # cap 500; burst peak 500 -> overload
    raw_p95 = over["latency_p95"] or 0.0
    eff_p95 = over["eff_latency_p95"]
    assert over["dropped_timeout"] > 0, "no timeouts at the chosen overload point — pick a harder one"
    assert eff_p95 > raw_p95, (
        f"survivorship bias not captured: eff p95 {eff_p95:.3f} <= raw p95 {raw_p95:.3f} "
        f"despite {over['dropped_timeout']} timeouts"
    )


if __name__ == "__main__":
    sys.exit(runner.run())
