"""
verify.py — independent verification of the RadioMonitoring model using the shared
harness (this verifier did NOT author the model). Run standalone:

    cd examples/RadioMonitoring
    python verify.py

Mapping the model onto the contract:
- Multi-class (voice / digital) -> one RunSummary per category (like FaxRx).
- The model's 6 loss buckets map onto the ledger:
    completed        = intercepted (ok)
    rejected         = E (below sensitivity — can't receive; admission-like)
    dropped_overload = A + B + C + D (hop gap / PC wait / no free SDR / starved — congestion)
    in_flight        = blocks - everything-above (blocks straddling the sim cutoff)
- offered = blocks is the model's OWN count, so the ledger balance is near-tautological;
  the meaningful Tier-1 checks here are non-negativity (catches over-count -> in_flight<0)
  and a small in-flight residual (catches under-count / vanished blocks).
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


def cat_summary(cfg: Config, r: dict, cat: str, saturated: bool) -> RunSummary:
    d = r["by_category"][cat]
    completed = d["intercepted"]
    rejected = d["E_sensitivity"]
    overload = d["A_hop_gap"] + d["B_pc_wait"] + d["C_no_sdr"] + d["D_starved"]
    blocks = d["blocks"]
    return RunSummary(
        offered=blocks,
        completed=completed,
        rejected=rejected,
        dropped_overload=overload,
        in_flight=blocks - completed - rejected - overload,
        success_rate=d["poi"] if d["poi"] is not None else 0.0,
        sim_time=cfg.sim_time,
        saturated=saturated,
        label=f"RadioMonitoring {cat}",
    )


# Healthy baseline: light load + generous, BALANCED resources (MODEL.md smoke says
# "generous C and pools"). All three stages must be ample, scaled together:
#   - pools must be generous (default 2/4 is saturated at any load: an 8 s voice record
#     alone offers ~2.67 Erlang to 2 lower SDRs);
#   - decode workers matched to the receiver count (you cannot record faster than you
#     decode — an 8.5 s voice decode on 2 workers is saturated at any load too).
N_RX = 20 + 20
BASE_CFG = Config(lambda_mult=0.1, n_sdr_lower=20, n_sdr_upper=20,
                  n_pc_slots=32, n_decode_workers=N_RX)
BASE = run(BASE_CFG)
V = cat_summary(BASE_CFG, BASE, "voice", saturated=False)
D = cat_summary(BASE_CFG, BASE, "digital", saturated=False)


def decode_summary(cfg: Config, r: dict, cat: str, saturated: bool) -> RunSummary:
    # Stage 2: the recorded blocks (intercepted) are offered to the decode pipeline.
    d = r["by_category"][cat]
    offered = d["intercepted"]
    decoded = d["decoded"]
    dropped = d["decode_dropped_G"]          # queue overflow — congestion loss
    return RunSummary(
        offered=offered,
        completed=decoded,
        dropped_overload=dropped,
        in_flight=offered - decoded - dropped,   # backlog still in the queue at sim end
        success_rate=d["decode_yield"] if d["decode_yield"] is not None else 0.0,
        sim_time=cfg.sim_time,
        saturated=saturated,
        label=f"RadioMonitoring {cat} / decode",
    )


VX = decode_summary(BASE_CFG, BASE, "voice", saturated=False)
DX = decode_summary(BASE_CFG, BASE, "digital", saturated=False)

# Stressed point (nominal hardware, high load) for the Erlang-A signature.
STRESS_CFG = Config(lambda_mult=10.0)
STRESS = run(STRESS_CFG)

runner = CheckRunner("RadioMonitoring")


# --- Tier-1 per category, BOTH stages (record -> decode) --------------------
# Stage 1 (record): blocks -> intercepted + A..E. Stage 2 (decode): intercepted ->
# decoded + G. Verifying only stage 1 would be blind to a broken decode pipeline.
for _stage, _name, _s in (("record", "voice", V), ("record", "digital", D),
                          ("decode", "voice", VX), ("decode", "digital", DX)):
    @runner.register(f"Tier-1 [{_name}/{_stage}]: work conservation (ledger balance)")
    def _cons(s=_s) -> None:
        assert_work_conservation(s)

    @runner.register(f"Tier-1 [{_name}/{_stage}]: no congestion loss without saturation")
    def _noov(s=_s) -> None:
        assert_no_overload_loss(s)

    @runner.register(f"Tier-1 [{_name}/{_stage}]: non-negative ledger, success_rate in [0,1]")
    def _nn(s=_s) -> None:
        assert_nonnegative(s)

    @runner.register(f"Tier-1 [{_name}/{_stage}]: in-flight residual small (work not vanishing/stuck)")
    def _resid(s=_s) -> None:
        assert s.in_flight <= 0.02 * s.offered, (
            f"large unaccounted residual: in_flight {s.in_flight} of offered {s.offered:.0f} "
            f"(>2%) — work neither completed nor accounted (stage starved / queue backlog)"
        )


# --- Tier-2: healthy verification + Erlang-A signature ----------------------
@runner.register("Tier-2: baseline voice POI ~ 100% (healthy verification)")
def _baseline_poi() -> None:
    assert V.success_rate > 0.95, f"voice POI at healthy baseline only {V.success_rate:.2%}"


@runner.register("Tier-2 (metamorphic): raising load lowers POI (a knee exists)")
def _poi_declines() -> None:
    poi_lo = BASE["by_category"]["voice"]["poi"]
    poi_hi = STRESS["by_category"]["voice"]["poi"]
    assert poi_hi < poi_lo * (1.0 - 0.1), (
        f"voice POI did not decline under 10x load: {poi_lo:.2%} -> {poi_hi:.2%}"
    )


@runner.register("Tier-2 (Erlang-A signature): under load voice POI > digital POI")
def _deadline_asymmetry() -> None:
    poi_v = STRESS["by_category"]["voice"]["poi"]
    poi_d = STRESS["by_category"]["digital"]["poi"]
    assert poi_v > poi_d, (
        f"deadline asymmetry absent: voice POI {poi_v:.2%} not above digital {poi_d:.2%} "
        f"(voice 8s patient should beat digital 0.5s impatient)"
    )


if __name__ == "__main__":
    sys.exit(runner.run())
