"""
Sweep burst multiplier (1× → 10×) over the FaxRx simulation and print results.

Two secondary dimensions explored:
  - sip_channels: 270 (average-load sizing) vs 2565 (10× burst sizing)
  - num_ocr_workers: default (35) vs scaled (175 = 35 × 5×)

Run:
    python sweep.py
"""

import json
from server_sim import Config, run

BURST_MULTIPLIERS = [1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

SCENARIOS = [
    {"label": "sip=270  ocr=35",  "sip_channels": 270,  "num_ocr_workers": 35},
    {"label": "sip=2565 ocr=35",  "sip_channels": 2565, "num_ocr_workers": 35},
    {"label": "sip=2565 ocr=175", "sip_channels": 2565, "num_ocr_workers": 175},
]

SIM_TIME = 7200.0       # 2 hours — enough for burst episode + steady state


def main():
    results = []

    for scenario in SCENARIOS:
        print(f"\n=== {scenario['label']} ===")
        print(f"  {'burst':>6}  {'thr':>7}  {'block%':>7}  "
              f"{'succ%':>7}  {'pl_p95':>8}  {'ocr_p95':>9}  {'to':>6}")

        for mult in BURST_MULTIPLIERS:
            r = run(Config(
                sim_time=SIM_TIME,
                burst_multiplier=mult,
                sip_channels=scenario["sip_channels"],
                num_ocr_workers=scenario["num_ocr_workers"],
            ))
            print(f"  {mult:6.1f}x"
                  f"  {r['throughput_fps']:7.2f}"
                  f"  {(r['pstn_block_rate'] or 0)*100:7.2f}%"
                  f"  {(r['success_rate'] or 0)*100:7.2f}%"
                  f"  {(r['plain_eff_p95'] or 0):8.1f}s"
                  f"  {(r['ocr_eff_p95'] or 0):9.1f}s"
                  f"  {r['dropped_timeout']:6d}")

            results.append({
                "scenario": scenario["label"],
                "burst_multiplier": mult,
                **r,
            })

    with open("sweep_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved: sweep_results.json")


if __name__ == "__main__":
    main()
