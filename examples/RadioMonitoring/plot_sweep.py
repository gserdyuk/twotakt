"""
Four-panel behavioral plot (Phase 8) for the two-stage RadioMonitoring model.

  1. LOAD   — POI vs load, by category (+ 50% target line). Stage ① degradation.
  2. LOAD   — decode-yield and end-to-end (POI x yield) vs load. Stage ② collapse.
  3. SDR    — POI vs SDR pool size @ x1, generous decode (isolates stage ①):
              how many receivers for POI >= 50%.
  4. DECODE — decode-yield vs decode workers @ x1, generous SDR (isolates stage ②):
              how many workers to clear the queue.

Usage:
    pip install -r requirements.txt
    python plot_sweep.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sweep import (run_avg, LAMBDA_MULTS, SDR_SIZES, DECODE_WORKERS,
                   GEN_DECODE, GEN_SDR)

VCOL, DCOL = "#1f77b4", "#d62728"          # voice, digital


def _mh(rows, cat, metric):
    m = [o[cat][metric][0] for o in rows]
    h = [o[cat][metric][1] for o in rows]
    return m, h


def collect():
    load = [run_avg(lambda_mult=x) for x in LAMBDA_MULTS]
    sdr = [run_avg(n_sdr_lower=k, n_sdr_upper=k, n_decode_workers=GEN_DECODE)
           for k in SDR_SIZES]
    dec = [run_avg(n_sdr_lower=GEN_SDR, n_sdr_upper=GEN_SDR, n_decode_workers=w)
           for w in DECODE_WORKERS]
    return load, sdr, dec


def plot(load, sdr, dec, out_path):
    fig, ((a1, a2), (a3, a4)) = plt.subplots(2, 2, figsize=(12, 9))

    # 1. LOAD — POI by category
    for cat, col in ((("voice"), VCOL), ("digital", DCOL)):
        m, h = _mh(load, cat, "poi")
        a1.errorbar(LAMBDA_MULTS, m, yerr=h, fmt="o-", color=col, label=f"{cat} POI", capsize=3)
    a1.axhline(0.5, ls="--", color="gray", lw=1, label="50% target")
    a1.set_xscale("log"); a1.set_xticks(LAMBDA_MULTS); a1.set_xticklabels([f"x{m:g}" for m in LAMBDA_MULTS])
    a1.set_ylim(0, 1.02); a1.set_xlabel("load (lambda multiplier)"); a1.set_ylabel("POI")
    a1.set_title("Stage 1 — interception (POI) vs load  [nominal 2/4 SDR]")
    a1.grid(alpha=0.3); a1.legend()

    # 2. LOAD — decode-yield and end-to-end
    for cat, col in (("voice", VCOL), ("digital", DCOL)):
        m, h = _mh(load, cat, "yield")
        a2.errorbar(LAMBDA_MULTS, m, yerr=h, fmt="o-", color=col, label=f"{cat} decode-yield", capsize=3)
        e, _ = _mh(load, cat, "e2e")
        a2.plot(LAMBDA_MULTS, e, "s--", color=col, alpha=0.5, label=f"{cat} end-to-end")
    a2.set_xscale("log"); a2.set_xticks(LAMBDA_MULTS); a2.set_xticklabels([f"x{m:g}" for m in LAMBDA_MULTS])
    a2.set_ylim(0, 1.02); a2.set_xlabel("load (lambda multiplier)"); a2.set_ylabel("fraction")
    a2.set_title("Stage 2 — decode-yield & end-to-end vs load  [2 decode workers]")
    a2.grid(alpha=0.3); a2.legend(fontsize=8)

    # 3. SDR sizing
    for cat, col in (("voice", VCOL), ("digital", DCOL)):
        m, h = _mh(sdr, cat, "poi")
        a3.errorbar(SDR_SIZES, m, yerr=h, fmt="o-", color=col, label=f"{cat} POI", capsize=3)
    a3.axhline(0.5, ls="--", color="gray", lw=1, label="50% target")
    a3.axvline(2, ls=":", color="black", lw=1, label="nominal (2)")
    a3.set_ylim(0, 1.02); a3.set_xlabel("SDR per band (lower = upper)"); a3.set_ylabel("POI")
    a3.set_title("Stage 1 sizing — POI vs SDR count  [x1, generous decode]")
    a3.grid(alpha=0.3); a3.legend()

    # 4. DECODE sizing
    for cat, col in (("voice", VCOL), ("digital", DCOL)):
        m, h = _mh(dec, cat, "yield")
        a4.errorbar(DECODE_WORKERS, m, yerr=h, fmt="o-", color=col, label=f"{cat} decode-yield", capsize=3)
    a4.axhline(0.95, ls="--", color="gray", lw=1, label="95%")
    a4.axvline(2, ls=":", color="black", lw=1, label="nominal (2)")
    a4.set_ylim(0, 1.02); a4.set_xlabel("decode workers"); a4.set_ylabel("decode-yield")
    a4.set_title("Stage 2 sizing — decode-yield vs workers  [x1, generous SDR]")
    a4.grid(alpha=0.3); a4.legend()

    fig.suptitle("RadioMonitoring — two-stage behavior (POI x decode-yield = end-to-end)",
                 fontsize=13, y=1.00)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    print(f"Saved: {out_path}")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    load, sdr, dec = collect()
    plot(load, sdr, dec, os.path.join(here, "sweep.png"))


if __name__ == "__main__":
    main()
