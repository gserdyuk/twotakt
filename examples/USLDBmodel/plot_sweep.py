"""
Run the arrival-rate sweep and produce sweep.png next to this file.

Three panels:
  1. throughput vs arrival rate (with ideal y=x reference)
  2. success rate vs arrival rate (fraction of requests that completed)
  3. latency percentiles vs arrival rate, log-y:
        solid  = effective (timeouts counted as latency = SLA)
        dashed = ok-only  (the misleading "survivorship" metric)
     The gap between solid and dashed visualizes how badly survivorship
     bias misrepresents reality under overload.

Usage:
    pip install -r requirements.txt
    python plot_sweep.py
"""

import os

import matplotlib.pyplot as plt

from server_sim import Config, run
from sweep import RATES  # single source of truth for the rate list


def collect():
    rows = []
    for rate in RATES:
        r = run(Config(
            arrival_rate=rate,
            sim_time=300.0,
            sla_seconds=10.0,
            max_threads=500,
        ))
        rows.append({
            "rate": rate,
            "thr": r["throughput_rps"],
            "success": r["success_rate"] or 0.0,
            "p50":     r["latency_p50"]     or 0.0,
            "p95":     r["latency_p95"]     or 0.0,
            "p99":     r["latency_p99"]     or 0.0,
            "eff_p50": r["eff_latency_p50"] or 0.0,
            "eff_p95": r["eff_latency_p95"] or 0.0,
            "eff_p99": r["eff_latency_p99"] or 0.0,
        })
        print(f"  rate={rate:5.1f}  thr={r['throughput_rps']:6.2f}  "
              f"succ={r['success_rate']:.2%}  "
              f"eff_p99={r['eff_latency_p99']:.3f}  "
              f"ok_p99={r['latency_p99'] or 0:.3f}")
    return rows


def plot(rows, out_path):
    rates    = [r["rate"]    for r in rows]
    thr      = [r["thr"]     for r in rows]
    success  = [r["success"] for r in rows]
    p50, p95, p99             = [[r[k] for r in rows] for k in ("p50","p95","p99")]
    e50, e95, e99             = [[r[k] for r in rows] for k in ("eff_p50","eff_p95","eff_p99")]

    fig, axes = plt.subplots(3, 1, figsize=(8, 9), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1.5, 3]})
    ax_thr, ax_suc, ax_lat = axes

    # --- throughput ---
    ax_thr.plot(rates, rates, "--", color="gray", linewidth=1, label="ideal (y=x)")
    ax_thr.plot(rates, thr, "o-", color="#1f77b4", linewidth=2, label="throughput")
    ax_thr.set_ylabel("throughput, rps")
    ax_thr.set_title("USL server: throughput vs offered load")
    ax_thr.grid(True, alpha=0.3)
    ax_thr.legend(loc="upper left")

    # --- success rate ---
    ax_suc.plot(rates, success, "o-", color="#9467bd", linewidth=2)
    ax_suc.set_ylabel("success rate")
    ax_suc.set_ylim(-0.05, 1.05)
    ax_suc.axhline(1.0, color="gray", linewidth=0.6, linestyle=":")
    ax_suc.grid(True, alpha=0.3)

    # --- latency: solid = effective, dashed = ok-only ---
    colors = {"p50": "#2ca02c", "p95": "#ff7f0e", "p99": "#d62728"}
    ax_lat.plot(rates, e50, "o-", label="p50 effective", color=colors["p50"])
    ax_lat.plot(rates, e95, "s-", label="p95 effective", color=colors["p95"])
    ax_lat.plot(rates, e99, "^-", label="p99 effective", color=colors["p99"])
    ax_lat.plot(rates, p50, "o--", color=colors["p50"], alpha=0.45, label="p50 ok-only")
    ax_lat.plot(rates, p95, "s--", color=colors["p95"], alpha=0.45, label="p95 ok-only")
    ax_lat.plot(rates, p99, "^--", color=colors["p99"], alpha=0.45, label="p99 ok-only")
    ax_lat.set_yscale("log")
    ax_lat.set_xlabel("arrival rate, rps")
    ax_lat.set_ylabel("latency, s (log)")
    ax_lat.set_title("Latency: effective (solid) vs ok-only (dashed)")
    ax_lat.grid(True, which="both", alpha=0.3)
    ax_lat.legend(loc="upper left", ncol=2, fontsize=8)

    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    print(f"\nSaved: {out_path}")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "sweep.png")
    rows = collect()
    plot(rows, out)


if __name__ == "__main__":
    main()
