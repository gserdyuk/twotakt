"""
Mutation suite for RadioMonitoring's verify.py (see harness/mutation.py).

Each mutant plants one realistic bug in executable_model and names the checks
that must go red. `python verify.py --mutants` proves every check still bites.

Tier-1 runs per category (voice, digital) and per stage (record, decode), so the
bookkeeping mutants are generated for each of the four ledgers.
"""

from __future__ import annotations

import dataclasses

from harness.mutation import Mutant, patch_result

CATS = ("voice", "digital")
BASELINE_POI = "Tier-2: baseline voice POI ~ 100% (healthy verification)"
POI_DECLINES = "Tier-2 (metamorphic): raising load lowers POI (a knee exists)"
ASYMMETRY = "Tier-2 (Erlang-A signature): under load voice POI > digital POI"


def _t1(cat: str, stage: str, what: str) -> str:
    return {
        "overload": f"Tier-1 [{cat}/{stage}]: no congestion loss without saturation",
        "nonneg": f"Tier-1 [{cat}/{stage}]: non-negative ledger, success_rate in [0,1]",
        "resid": f"Tier-1 [{cat}/{stage}]: in-flight residual small (work not vanishing/stuck)",
        "cons": f"Tier-1 [{cat}/{stage}]: work conservation (ledger balance)",
    }[what]


# --- stage 1 (record): blocks -> intercepted + buckets A..E -----------------

def _record_bug(cat: str, kind: str):
    def edit(cfg, r):
        d = r["by_category"][cat]
        if kind == "overload":      # intercepted blocks also booked as hop-gap losses
            moved = d["intercepted"] // 10
            d["intercepted"] -= moved
            d["A_hop_gap"] += moved
        elif kind == "nonneg":      # each intercepted block counted twice
            d["intercepted"] *= 2
        elif kind == "resid":       # intercepted blocks lost without a bucket
            d["intercepted"] -= d["intercepted"] // 10
        if d["blocks"]:
            d["poi"] = d["intercepted"] / d["blocks"]
    return lambda m: patch_result(m, edit)


# --- stage 2 (decode): intercepted -> decoded + G ---------------------------

def _decode_bug(cat: str, kind: str):
    def edit(cfg, r):
        d = r["by_category"][cat]
        if kind == "overload":      # decoded items also booked as queue overflow
            moved = d["decoded"] // 10
            d["decoded"] -= moved
            d["decode_dropped_G"] += moved
        elif kind == "nonneg":      # each decoded item counted twice
            d["decoded"] *= 2
        elif kind == "resid":       # decoded items lost without a bucket
            d["decoded"] -= d["decoded"] // 10
        if d["intercepted"]:
            d["decode_yield"] = d["decoded"] / d["intercepted"]
    return lambda m: patch_result(m, edit)


_BUG_TEXT = {
    "overload": "{what} also booked as congestion loss",
    "nonneg": "each {what} counted twice",
    "resid": "{what} silently lost (no bucket)",
}


def _bookkeeping_mutants():
    out = []
    for cat in CATS:
        for stage, make, what in (("record", _record_bug, "intercepted block"),
                                  ("decode", _decode_bug, "decoded item")):
            for kind in ("overload", "nonneg", "resid"):
                out.append(Mutant(
                    name=f"{cat}-{stage}-{kind}",
                    bug=f"{cat}: " + _BUG_TEXT[kind].format(what=what),
                    kills=(_t1(cat, stage, kind),),
                    apply=make(cat, kind),
                ))
    return out


# --- Tier-2: behavioural bugs ------------------------------------------------

def _replace_cfg(**fields):
    def apply(m):
        original = m.Server.__init__

        def init(self, env, cfg):
            original(self, env, dataclasses.replace(cfg, **fields))
        m.Server.__init__ = init
    return apply


def _poi_over_captured(m):
    def edit(cfg, r):
        for d in r["by_category"].values():
            # bug: POI denominator is the captured blocks, not all blocks on air
            d["poi"] = 1.0 if d["intercepted"] else None
    patch_result(m, edit)


MUTANTS = _bookkeeping_mutants() + [
    Mutant("sdr-pools-hardcoded",
           "SDR pool sizes taken from built-in defaults (2/4), n_sdr_* never read",
           (BASELINE_POI,), _replace_cfg(n_sdr_lower=2, n_sdr_upper=4)),
    Mutant("poi-over-captured", "POI computed over captured blocks only (always 100%)",
           (POI_DECLINES,), _poi_over_captured),
    Mutant("voice-impatient", "voice record window read from the digital field (0.5 s)",
           (ASYMMETRY,), _replace_cfg(rec_voice=0.5)),
]

_IDENTITY = ("offered is the stage's own count and in_flight is derived as the residual "
             "of that same count, so the ledger balances by construction; the "
             "'in-flight residual small' check is what actually guards this stage")

WAIVED = {
    _t1(cat, stage, "cons"): _IDENTITY
    for cat in CATS for stage in ("record", "decode")
}
