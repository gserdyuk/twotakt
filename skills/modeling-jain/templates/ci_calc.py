"""
Confidence interval computation for SimPy sweep results.
Source: Raj Jain, "The Art of Computer Systems Performance Analysis", Ch. 25.

Usage
-----
Import and call ci() on a list of per-replication values, or use
summarize_replications() on a list of run() result dicts.

Example
-------
    from ci_calc import ci, summarize_replications
    from server_sim import run, Config

    results = [run(Config(seed=s)) for s in range(10, 30)]
    print(summarize_replications(results, metrics=["throughput_rps", "eff_latency_p95"]))
"""

from __future__ import annotations

import math
import statistics


# t-distribution critical values for 95% CI (two-tailed, alpha=0.05)
# t(df, 0.025) — precomputed for common df values
_T_TABLE = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447,  7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    19: 2.093, 24: 2.064, 29: 2.045, 39: 2.021, 59: 2.000,
    119: 1.980,
}


def t_critical(df: int, alpha: float = 0.05) -> float:
    """Two-tailed t critical value at given degrees of freedom."""
    if df >= 120:
        return 1.960  # normal approximation
    # find nearest df in table
    keys = sorted(_T_TABLE.keys())
    best = min(keys, key=lambda k: abs(k - df))
    return _T_TABLE[best]


def ci(values: list[float], confidence: float = 0.95) -> dict:
    """Compute mean and confidence interval for a list of replication values.

    Parameters
    ----------
    values     : one value per replication (e.g. throughput from each seed)
    confidence : CI level (default 0.95 = 95%)

    Returns
    -------
    dict with keys: mean, std, ci_half, ci_low, ci_high, n, relative_error
    """
    n = len(values)
    if n < 2:
        raise ValueError("Need at least 2 replications for a CI")

    mean = statistics.mean(values)
    std = statistics.stdev(values)      # sample std dev
    alpha = 1.0 - confidence
    t = t_critical(n - 1, alpha)
    half = t * std / math.sqrt(n)

    return {
        "mean":           mean,
        "std":            std,
        "ci_half":        half,
        "ci_low":         mean - half,
        "ci_high":        mean + half,
        "n_replications": n,
        "relative_error": half / mean if mean != 0 else float("inf"),
        "confidence":     confidence,
    }


def summarize_replications(
    results: list[dict],
    metrics: list[str] | None = None,
    confidence: float = 0.95,
    warn_relative_error: float = 0.10,
) -> dict:
    """Compute CI for each metric across a list of run() result dicts.

    Parameters
    ----------
    results              : list of dicts returned by server_sim.run()
    metrics              : which keys to summarize (None = all numeric keys)
    confidence           : CI level
    warn_relative_error  : warn if CI_half / mean exceeds this threshold

    Returns
    -------
    dict: metric → CI dict (from ci())
    """
    if not results:
        return {}

    if metrics is None:
        # auto-detect numeric metrics (exclude 'config', 'arrival_rate', etc.)
        sample = results[0]
        metrics = [
            k for k, v in sample.items()
            if isinstance(v, (int, float)) and v is not None and k != "seed"
        ]

    summary = {}
    warnings = []

    for metric in metrics:
        vals = [r[metric] for r in results if r.get(metric) is not None]
        if len(vals) < 2:
            continue
        c = ci(vals, confidence=confidence)
        summary[metric] = c
        if c["relative_error"] > warn_relative_error:
            warnings.append(
                f"  WARNING: {metric} CI is wide "
                f"(±{c['relative_error']*100:.1f}% relative error). "
                f"Add more replications."
            )

    if warnings:
        print("=== CI Warnings ===")
        for w in warnings:
            print(w)

    return summary


def print_summary(summary: dict) -> None:
    """Pretty-print the CI summary."""
    print(f"  {'Metric':30s}  {'Mean':>10}  {'±CI':>8}  {'Rel.err':>8}  n")
    print("  " + "-" * 65)
    for metric, c in summary.items():
        print(
            f"  {metric:30s}  {c['mean']:10.4f}  "
            f"{c['ci_half']:8.4f}  "
            f"{c['relative_error']*100:7.1f}%  "
            f"{c['n_replications']}"
        )


# ---------------------------------------------------------------------------
# Example: run 15 replications of a SimPy model and report CI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Adapt imports to your project:
    # from server_sim import run, Config

    # Synthetic example: pretend we have 15 replication results
    import random as _rand
    _rand.seed(0)
    fake_results = [
        {
            "throughput_rps":   _rand.gauss(140, 8),
            "success_rate":     _rand.gauss(0.97, 0.02),
            "eff_latency_p95":  _rand.gauss(0.42, 0.05),
        }
        for _ in range(15)
    ]

    summary = summarize_replications(
        fake_results,
        metrics=["throughput_rps", "success_rate", "eff_latency_p95"],
    )
    print_summary(summary)
    print()
    print("Interpretation example:")
    c = summary["throughput_rps"]
    print(
        f"  throughput = {c['mean']:.1f} ± {c['ci_half']:.1f} req/s "
        f"(95% CI, n={c['n_replications']})"
    )
