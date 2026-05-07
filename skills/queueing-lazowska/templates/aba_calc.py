"""
Asymptotic Bound Analysis (ABA) — Lazowska et al., QSP Chapter 5.

Usage
-----
1. Fill in DEVICES and THINK_TIME below.
2. Run: python aba_calc.py
3. Inspect the printed table and the saved plot.

Service demands D_k are in seconds per system-level job.
Think time Z = 0 for batch or open workloads.
"""

from __future__ import annotations

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Model parameters — edit these
# ---------------------------------------------------------------------------

DEVICES: dict[str, float] = {
    "CPU":     0.050,   # service demand in seconds
    "Disk":    0.150,
    "Network": 0.020,
}
THINK_TIME: float = 5.0    # Z, mean think time in seconds (0 = batch)
N_MAX: int = 80            # plot range: 1 .. N_MAX users


# ---------------------------------------------------------------------------
# ABA computation
# ---------------------------------------------------------------------------

def aba(devices: dict[str, float], Z: float, N_max: int) -> dict:
    D_sum = sum(devices.values())
    D_max = max(devices.values())
    bottleneck = max(devices, key=lambda k: devices[k])
    N_star = (D_sum + Z) / D_max

    ns = list(range(1, N_max + 1))
    X_bound, R_bound = [], []
    for n in ns:
        x = min(n / (D_sum + Z), 1.0 / D_max)
        r = max(D_sum, n * D_max - Z)
        X_bound.append(x)
        R_bound.append(r)

    return {
        "devices": devices,
        "Z": Z,
        "D_sum": D_sum,
        "D_max": D_max,
        "bottleneck": bottleneck,
        "N_star": N_star,
        "ns": ns,
        "X_bound": X_bound,
        "R_bound": R_bound,
    }


def print_summary(r: dict) -> None:
    print("=== ABA Summary ===")
    print(f"  Devices:")
    for name, d in r["devices"].items():
        mark = " <- bottleneck" if name == r["bottleneck"] else ""
        print(f"    {name:12s}  D = {d:.4f} s{mark}")
    print(f"  D_sum   = {r['D_sum']:.4f} s  (minimum response time)")
    print(f"  D_max   = {r['D_max']:.4f} s  ({r['bottleneck']})")
    print(f"  Z       = {r['Z']:.4f} s  (think time)")
    print(f"  N*      = {r['N_star']:.1f}  (saturation point)")
    print(f"  X_max   = {1/r['D_max']:.2f} jobs/s  (throughput ceiling)")
    print()
    print(f"  {'N':>5}  {'X_bound':>10}  {'R_bound':>10}")
    for i, n in enumerate(r["ns"]):
        if n % 10 == 0 or n == 1 or abs(n - r["N_star"]) < 1:
            print(f"  {n:5d}  {r['X_bound'][i]:10.3f}  {r['R_bound'][i]:10.3f}")


def plot(r: dict, output: str = "aba_plot.png") -> None:
    ns = r["ns"]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
    fig.suptitle("Asymptotic Bound Analysis")

    # throughput
    ax1.plot(ns, r["X_bound"], "b-", label="X upper bound")
    ax1.axhline(1.0 / r["D_max"], color="r", linestyle="--",
                label=f"X_max = 1/D_max = {1/r['D_max']:.2f}")
    ax1.axvline(r["N_star"], color="gray", linestyle=":", label=f"N* = {r['N_star']:.1f}")
    ax1.set_ylabel("Throughput (jobs/s)")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # response time
    ax2.plot(ns, r["R_bound"], "g-", label="R lower bound")
    ax2.axhline(r["D_sum"], color="gray", linestyle="--",
                label=f"D_sum = {r['D_sum']:.3f} s")
    ax2.axvline(r["N_star"], color="gray", linestyle=":", label=f"N* = {r['N_star']:.1f}")
    ax2.set_xlabel("Number of users N")
    ax2.set_ylabel("Response time (s)")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output, dpi=120)
    print(f"Plot saved to {output}")


if __name__ == "__main__":
    result = aba(DEVICES, THINK_TIME, N_MAX)
    print_summary(result)
    plot(result)
