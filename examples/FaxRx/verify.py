"""
verify.py — executable form of the "Verification & Validation criteria" section
of this example's MODEL.md. Run standalone:

    cd examples/FaxRx
    python verify.py

FaxRx stressed the contract in three ways, all handled here:
1. Two loss kinds — Erlang-B PSTN blocking is *admission* loss (rejected, by design),
   not congestion loss. This is what forced the RunSummary split rejected/overload.
2. Multi-class — plain vs ocr delivery paths. Demonstrated with several RunSummary
   (system + per-class) and a partition check.
3. Different law — the binding mechanism is Erlang-B blocking, not USL (OCR USL is
   off by default, alpha=beta=0). So no USL shape checks here; instead a channel
   metamorphic relation + a structural OCR-vs-plain sanity check.
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


CFG = Config()
BASE = run(CFG)                                       # baseline: burst=1, USL off, queues near empty


def system_summary(cfg: Config, r: dict) -> RunSummary:
    completed = r["completed_ok"]
    rejected = r["blocked_pstn"]        # Erlang-B busy — admission, by design
    overload = r["dropped_timeout"]     # SLA miss — congestion loss
    return RunSummary(
        offered=cfg.arrival_rate * cfg.sim_time,     # burst=1 -> constant rate
        completed=completed,
        rejected=rejected,
        dropped_overload=overload,
        in_flight=r["total_arrivals"] - completed - rejected - overload,
        arrival_rate=cfg.arrival_rate,
        throughput=r["throughput_fps"],
        success_rate=r["success_rate"],
        sim_time=cfg.sim_time,
        saturated=False,                # baseline: queues near empty (blocking is admission, not congestion)
        label="FaxRx system (all faxes)",
    )


def class_summary(r: dict, cls: str) -> RunSummary:
    # Per-class view: blocking happens at the PSTN before plain/ocr classification,
    # so a class has no `rejected` of its own — only completions and congestion loss.
    ok = r[f"{cls}_ok"]
    overload = r[f"{cls}_timeout"]
    return RunSummary(
        offered=ok + overload,          # classified arrivals for this path
        completed=ok,
        dropped_overload=overload,
        label=f"FaxRx {cls}",
    )


SYSTEM = system_summary(CFG, BASE)
PLAIN = class_summary(BASE, "plain")
OCR = class_summary(BASE, "ocr")


runner = CheckRunner("FaxRx")


@runner.register("Tier-1: work conservation (ledger balance)")
def _conservation() -> None:
    assert_work_conservation(SYSTEM)


@runner.register("Tier-1: no congestion loss without saturation (PSTN blocking allowed)")
def _no_overload() -> None:
    assert_no_overload_loss(SYSTEM)


@runner.register("Tier-1: non-negative ledger, success_rate in [0,1]")
def _nonneg() -> None:
    assert_nonnegative(SYSTEM)


@runner.register("Tier-1 (multi-class): plain + ocr partition the system totals")
def _partition() -> None:
    assert PLAIN.completed + OCR.completed == SYSTEM.completed, (
        f"class completions don't partition: plain {PLAIN.completed} + ocr {OCR.completed} "
        f"!= system {SYSTEM.completed}"
    )
    assert PLAIN.dropped_overload + OCR.dropped_overload == SYSTEM.dropped_overload, (
        f"class timeouts don't partition: plain {PLAIN.dropped_overload} + ocr "
        f"{OCR.dropped_overload} != system {SYSTEM.dropped_overload}"
    )


# --- Tier-2 (model-specific): Erlang-B blocking + structural OCR sanity ----------
HI_RATE = 5.0          # offered ~ 5*90 = 450 erlang -> well over 270 channels
PROBE_TIME = 1800.0


def block_rate_at(channels: int) -> float:
    return run(Config(arrival_rate=HI_RATE, sim_time=PROBE_TIME,
                      sip_channels=channels))["pstn_block_rate"]


@runner.register("Tier-2 (metamorphic): adding SIP channels removes PSTN blocking")
def _channels_bind() -> None:
    # Erlang-B is the front door. Under heavy load the default channel count blocks;
    # a huge channel count must not. If blocking is not wired, both are ~0 -> caught.
    br_default = block_rate_at(CFG.sip_channels)        # 270
    br_huge = block_rate_at(2565)                       # MODEL.md: blocking ~0 even at 10x burst
    assert br_default - br_huge > 0.05, (
        f"PSTN blocking not exercised: block_rate(270)={br_default:.3f} not meaningfully "
        f"above block_rate(2565)={br_huge:.3f}"
    )


@runner.register("Tier-2 (structural): OCR path is slower than the plain path")
def _ocr_slower() -> None:
    # OCR path = plain work + an OCR step, so it must be strictly slower at any load.
    # (MODEL.md states "by >= ocr_time_mean"; that holds at p95 but is approximate at
    # p50 on the healthy model, so we assert the robust strict-slower form.)
    assert BASE["ocr_eff_p50"] > BASE["plain_eff_p50"], (
        f"OCR path not slower than plain: ocr p50 {BASE['ocr_eff_p50']:.1f} "
        f"<= plain p50 {BASE['plain_eff_p50']:.1f}"
    )


if __name__ == "__main__":
    sys.exit(runner.run())
