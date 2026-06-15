"""
Plot the FaxRx burst sweep from sweep_results.json into sweep.png.

Unlike the other examples, the FaxRx sweep is expensive (sim_time = 7200 s ×
33 runs), so this reads the committed results rather than re-running. Run
`python sweep.py` first if sweep_results.json is missing or stale.

Three panels, shared X axis = burst multiplier (1× → 10×), one curve per
architecture (A/B/C):
  1. success rate — fraction of faxes delivered within SLA
  2. PSTN block rate — fraction of calls rejected at the Erlang B front door
  3. p95 effective latency (log-y): OCR path (solid) vs non-OCR path (dashed),
     with the two SLA ceilings (600 s / 3600 s) drawn as references.

The contrast between panels 2 and 3 is the point: architecture A trades a high
block rate (panel 2) for flat, healthy latency (panel 3) — fast, honest failure
at the door — while architecture B shows zero blocking but latency climbing to
the OCR SLA ceiling — slow, hidden failure inside.

Usage:
    pip install -r requirements.txt
    python plot_sweep.py
"""

import json
import os

import matplotlib.pyplot as plt

# Plain (non-OCR) and OCR SLA ceilings, seconds — see server_sim.Config.
SLA_PLAIN = 600.0
SLA_OCR = 3600.0

# Scenario label (as written by sweep.py) → display label + colour.
SCENARIOS = [
    ("sip=270  ocr=35",  "A: sip=270, ocr=35 (front door = avg load)",   "#1f77b4"),
    ("sip=2565 ocr=35",  "B: sip=2565, ocr=35 (door open 10×)",      "#ff7f0e"),
    ("sip=2565 ocr=175", "C: sip=2565, ocr=175 (door open + OCR 5×)", "#2ca02c"),
]


def load(path):
    with open(path) as f:
        rows = json.load(f)
    by_scenario = {}
    for r in rows:
        by_scenario.setdefault(r["scenario"], []).append(r)
    for series in by_scenario.values():
        series.sort(key=lambda r: r["burst_multiplier"])
    return by_scenario


def plot(by_scenario, out_path):
    fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True,
                             gridspec_kw={"height_ratios": [3, 2, 3]})
    ax_suc, ax_blk, ax_lat = axes

    for key, label, color in SCENARIOS:
        rows = by_scenario.get(key)
        if not rows:
            continue
        burst = [r["burst_multiplier"] for r in rows]
        succ  = [(r["success_rate"]   or 0.0) for r in rows]
        block = [(r["pstn_block_rate"] or 0.0) * 100 for r in rows]
        ocr95 = [(r["ocr_eff_p95"]    or 0.0) for r in rows]
        pl95  = [(r["plain_eff_p95"]  or 0.0) for r in rows]

        ax_suc.plot(burst, succ, "o-", color=color, linewidth=2, label=label)
        ax_blk.plot(burst, block, "o-", color=color, linewidth=2, label=label)
        ax_lat.plot(burst, ocr95, "s-", color=color, linewidth=2,
                    label=f"{label.split(':')[0]} OCR p95")
        ax_lat.plot(burst, pl95, "o--", color=color, alpha=0.5,
                    label=f"{label.split(':')[0]} plain p95")

    # --- success rate ---
    ax_suc.set_ylabel("success rate")
    ax_suc.set_ylim(-0.05, 1.05)
    ax_suc.axhline(1.0, color="gray", linewidth=0.6, linestyle=":")
    ax_suc.set_title("FaxRx: delivery success vs burst")
    ax_suc.grid(True, alpha=0.3)
    ax_suc.legend(loc="lower left", fontsize=8)

    # --- PSTN block rate ---
    ax_blk.set_ylabel("PSTN block rate, %")
    ax_blk.set_title("Erlang B blocking at the front door")
    ax_blk.grid(True, alpha=0.3)

    # --- latency ---
    ax_lat.axhline(SLA_PLAIN, color="gray", linewidth=0.8, linestyle="--")
    ax_lat.text(1.0, SLA_PLAIN * 1.05, "plain SLA 600 s", fontsize=7, color="gray")
    ax_lat.axhline(SLA_OCR, color="red", linewidth=0.8, linestyle="--")
    ax_lat.text(1.0, SLA_OCR * 1.03, "OCR SLA 3600 s", fontsize=7, color="red")
    ax_lat.set_yscale("log")
    ax_lat.set_xlabel("burst multiplier (× average load)")
    ax_lat.set_ylabel("p95 effective latency, s (log)")
    ax_lat.set_title("Latency: OCR path (solid) vs non-OCR path (dashed)")
    ax_lat.grid(True, which="both", alpha=0.3)
    ax_lat.legend(loc="upper left", ncol=3, fontsize=7)

    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    print(f"Saved: {out_path}")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    results = os.path.join(here, "sweep_results.json")
    if not os.path.exists(results):
        raise SystemExit("sweep_results.json not found — run `python sweep.py` first.")
    plot(load(results), os.path.join(here, "sweep.png"))


if __name__ == "__main__":
    main()
