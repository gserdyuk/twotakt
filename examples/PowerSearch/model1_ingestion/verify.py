"""
verify.py — executable form of the "What success looks like" (V&V) section of this
submodel's MODEL.md. Run standalone:

    cd examples/PowerSearch/model1_ingestion
    python verify.py

PowerSearch ingestion = a cascade of two M/M/c queues in series (processing workers
-> ES indexing pool), no USL. The interesting behaviour is bottleneck *migration*:
the worker pool binds when undersized; once workers are ample the ES pool becomes the
ceiling. Two metamorphic relations test that both stages are wired.

Note: the two PowerSearch pipelines (ingestion / queries) are modelled as INDEPENDENT
systems — each has its own ES pool; the shared-Elasticsearch coupling is deliberately
out of scope (MODEL.md). So there is no inter-pipeline edge to conserve; the composition
here is *within* the pipeline (series cascade), not between pipelines.
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


CFG = Config()
BASE = run(CFG)


def adapt(cfg: Config, r: dict) -> RunSummary:
    completed = r["completed_ok"]
    rejected = r["dropped_buffer"]      # admission cap overflow (max_threads); off by default
    overload = r["dropped_timeout"]     # SLA miss — congestion loss
    return RunSummary(
        offered=r["arrival_rate"] * cfg.sim_time,
        completed=completed,
        rejected=rejected,
        dropped_overload=overload,
        in_flight=r["total_arrivals"] - completed - rejected - overload,
        arrival_rate=r["arrival_rate"],
        throughput=r["throughput_rps"],
        success_rate=r["success_rate"],
        sim_time=cfg.sim_time,
        saturated=False,                # defaults: workers cap 200 > arrival 150
        label="PowerSearch ingestion (default)",
    )


SUMMARY = adapt(CFG, BASE)
BASE_THR = BASE["throughput_rps"]
MIN_EFFECT = 0.1


def throughput_at(**overrides) -> float:
    return run(Config(**overrides))["throughput_rps"]


runner = CheckRunner("PowerSearch / ingestion")


@runner.register("Tier-1: work conservation (ledger balance)")
def _conservation() -> None:
    assert_work_conservation(SUMMARY)


@runner.register("Tier-1: no congestion loss without saturation")
def _no_overload() -> None:
    assert_no_overload_loss(SUMMARY)


@runner.register("Tier-1: non-negative ledger, success_rate in [0,1]")
def _nonneg() -> None:
    assert_nonnegative(SUMMARY)


@runner.register("Tier-2 (metamorphic): undersizing the worker pool binds (stage 1)")
def _worker_binds() -> None:
    thr_small = throughput_at(num_workers=5)            # cap 100 < arrival 150
    assert thr_small < BASE_THR * (1.0 - MIN_EFFECT), (
        f"worker pool not exercised: throughput {thr_small:.0f} at workers=5 "
        f"not below default {BASE_THR:.0f}"
    )


@runner.register("Tier-2 (metamorphic): undersizing the ES pool binds (stage 2)")
def _es_binds() -> None:
    thr_small = throughput_at(es_pool_size=10)          # cap 67 < arrival 150
    assert thr_small < BASE_THR * (1.0 - MIN_EFFECT), (
        f"ES pool not exercised: throughput {thr_small:.0f} at es_pool_size=10 "
        f"not below default {BASE_THR:.0f}"
    )


if __name__ == "__main__":
    sys.exit(runner.run())
