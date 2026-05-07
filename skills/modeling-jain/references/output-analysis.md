# Simulation Output Analysis

Source: Raj Jain, "The Art of Computer Systems Performance Analysis", Chapter 25.

Replaces the ad-hoc "use 3 seeds" approach with a statistically rigorous
method for computing confidence intervals and determining run length.

---

## The two problems

**Problem 1 — Initialization bias (transient):**
The simulation starts empty (or in some artificial state). Early observations
are unrepresentative of steady state. Including them biases the mean.

**Problem 2 — Autocorrelation:**
Consecutive latency samples in a single long run are correlated. Treating
them as independent underestimates variance → confidence intervals are too
narrow → false confidence.

---

## Solution A — Independent replications (recommended for most cases)

Run r independent replications with different random seeds. Discard warm-up
from each run. Compute the mean of each run's target metric. These r means
are (approximately) independent — apply standard CI formula.

**Algorithm:**
1. Determine warm-up period W (see below).
2. Run r replications, each of duration T >> W. Use different seeds.
3. For each replication i, compute Y_i = statistic over [W, T].
4. Compute: ȳ = mean(Y_i), s = std(Y_i)
5. Confidence interval: ȳ ± t(r−1, α/2) × s / √r

**How many replications r?**
Start with r = 10. Check if CI width is acceptable.
If not: r_new = r × (CI_actual / CI_target)². The number of replications
grows as the square of precision required.

Rule of thumb for p95 latency: r ≥ 20 to stabilise the tail estimate.
For mean latency and throughput: r ≥ 10 is usually enough.

---

## Solution B — Batch means (for very long runs)

When a single run is expensive to restart and must be long, divide it into
b batches of length m. Discard the first batch (warm-up). Use the remaining
b−1 batch means as independent observations.

**Requirements:**
- Batch length m must be long enough that consecutive batch means are
  approximately uncorrelated. Check: lag-1 autocorrelation of batch means
  should be < 0.1.
- Minimum b = 20 usable batches (after warm-up discard).

**Algorithm:**
1. Run simulation for total time T = b × m.
2. Discard first m time units (warm-up batch).
3. Compute mean of metric within each remaining batch.
4. Apply the same CI formula as for independent replications.

---

## Warm-up period detection

**Method 1 — Visual inspection (recommended):**
Plot the cumulative moving average of the metric vs. simulation time.
The warm-up period ends when the moving average stabilises (no longer
trending). Set W = stabilisation time × 2 for safety.

**Method 2 — Rule of thumb:**
W ≈ 10 × (mean inter-arrival time) × (mean queue length at knee).
For our models: if at N* users the mean queue length is 5, then
W ≈ 10 × (1/λ) × 5. Verify visually.

**Method 3 — Relative stability:**
Divide the run into windows of length w. Warm-up is over when:
|moving_avg(t) − moving_avg(t − w)| / moving_avg(t) < ε (e.g. ε = 0.05).

---

## Confidence interval formula

For r independent observations Y_1, …, Y_r:

    ȳ = Σ Y_i / r
    s² = Σ (Y_i − ȳ)² / (r − 1)
    CI = ȳ ± t(r−1, α/2) × s / √r

For 95% CI (α = 0.05) and r replications:

| r | t(r−1, 0.025) |
|---|---|
| 5  | 2.776 |
| 10 | 2.262 |
| 20 | 2.093 |
| 30 | 2.045 |
| ∞  | 1.960 |

CI half-width = t × s / √r. To halve the CI, quadruple the replications.

---

## Integration with simpy-protocol

Current simpy-protocol sweep uses `seeds = [42, 43, 44]` and reports
`mean ± std`. Replace with:

1. Choose r = 10–20 seeds.
2. Remove warm-up: set `warmup_fraction = 0.2` and discard first 20%
   of each run's records before computing statistics.
3. Compute CI using `ci_calc.py`.
4. Report: `ȳ ± CI_halfwidth` at 95% confidence level.
5. If CI halfwidth / ȳ > 0.1 (10% relative error): add more replications.

In sweep.py: make `seeds` a list of length r; add `warmup_time` parameter
to Config; in `summarize()`, filter records where `arrival > warmup_time`.

---

## What to report

Every sweep result should include:
- N_replications: how many seeds
- warmup_time: what was discarded
- For each metric: mean, CI_halfwidth, CI_level (95%)
- Flag any point where CI_halfwidth / mean > 0.1

Example: "throughput = 143 ± 8 req/s (95% CI, r=10 replications,
warmup=60 s discarded from 600 s runs)"
