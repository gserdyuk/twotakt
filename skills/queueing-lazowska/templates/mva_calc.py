"""
Mean Value Analysis (MVA) — exact, single class.
Algorithm: Reiser & Lavenberg (1980). Source: Lazowska et al., QSP Chapter 6.

Gives the exact throughput, response time, and queue lengths for a closed,
single-class, product-form queueing network.

Usage
-----
1. Fill in DEVICES and THINK_TIME below.
2. Run: python mva_calc.py
3. Inspect the printed table and the saved plot.
"""

from __future__ import annotations

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Model parameters — edit these
# ---------------------------------------------------------------------------

DEVICES: dict[str, float] = {
    "CPU":     0.050,   # service demand D_k in seconds per system job
    "Disk":    0.150,
    "Network": 0.020,
}
THINK_TIME: float = 5.0    # Z, mean think time in seconds (0 = batch)
N_MAX: int = 80            # compute for N = 1 .. N_MAX


# ---------------------------------------------------------------------------
# MVA algorithm
# ---------------------------------------------------------------------------

def mva(devices: dict[str, float], Z: float, N_max: int) -> dict:
    """Exact single-class MVA.

    Returns per-N arrays: throughput, response time, utilizations, queue lengths.
    """
    keys = list(devices.keys())
    D = [devices[k] for k in keys]
    K = len(D)

    # initialization: empty system
    Q = [0.0] * K   # Q_k(0) = 0

    results = {"N": [], "X": [], "R": [], "U": {k: [] for k in keys},
               "Q": {k: [] for k in keys}}

    for n in range(1, N_max + 1):
        # Step 1: residence time (arrival theorem)
        R_k = [D[i] * (1.0 + Q[i]) for i in range(K)]

        # Step 2: throughput
        X = n / (Z + sum(R_k))

        # Step 3: queue lengths
        Q = [X * R_k[i] for i in range(K)]

        R = sum(R_k)
        results["N"].append(n)
        results["X"].append(X)
        results["R"].append(R)
        for i, k in enumerate(keys):
            results["U"][k].append(X * D[i])
            results["Q"][k].append(Q[i])

    results["devices"] = devices
    results["Z"] = Z
    results["bottleneck"] = max(devices, key=lambda k: devices[k])
    return results


def print_table(r: dict, step: int = 5) -> None:
    print("=== MVA Results ===")
    print(f"  Bottleneck: {r['bottleneck']}  (D = {r['devices'][r['bottleneck']]:.4f} s)")
    print()
    header = f"  {'N':>5}  {'X':>8}  {'R':>8}  " + \
             "  ".join(f"U_{k[:4]:4s}" for k in r["devices"])
    print(header)
    for i, n in enumerate(r["N"]):
        if n % step == 0 or n == 1:
            utils = "  ".join(f"{r['U'][k][i]:8.3f}" for k in r["devices"])
            print(f"  {n:5d}  {r['X'][i]:8.3f}  {r['R'][i]:8.3f}  {utils}")


def plot(r: dict, output: str = "mva_plot.png") -> None:
    ns = r["N"]
    D_max = max(r["devices"].values())
    D_sum = sum(r["devices"].values())

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 10), sharex=True)
    fig.suptitle("Mean Value Analysis — Exact Single-Class MVA")

    # Throughput
    ax1.plot(ns, r["X"], "b-", label="X(N) MVA")
    ax1.axhline(1.0 / D_max, color="r", linestyle="--",
                label=f"X_max = {1/D_max:.2f} (1/D_max)")
    ax1.set_ylabel("Throughput (jobs/s)")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Response time
    ax2.plot(ns, r["R"], "g-", label="R(N) MVA")
    ax2.axhline(D_sum, color="gray", linestyle="--",
                label=f"D_sum = {D_sum:.3f} s (min R)")
    ax2.set_ylabel("Response time (s)")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    # Utilizations
    for k in r["devices"]:
        ax3.plot(ns, r["U"][k], label=k)
    ax3.axhline(1.0, color="r", linestyle="--", label="U = 1 (saturation)")
    ax3.set_xlabel("Number of users N")
    ax3.set_ylabel("Utilization")
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output, dpi=120)
    print(f"Plot saved to {output}")


if __name__ == "__main__":
    result = mva(DEVICES, THINK_TIME, N_MAX)
    print_table(result)
    plot(result)
