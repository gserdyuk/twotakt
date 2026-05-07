# Workload Characterization

Source: Raj Jain, "The Art of Computer Systems Performance Analysis", Part II (Chapters 5–9).

How to go from a real running system to the model inputs that ABA, MVA,
and SimPy need: D_k (service demand), Z (think time), arrival rate λ,
and service time distribution.

---

## What a workload model needs

| Parameter | Symbol | How obtained |
|---|---|---|
| Arrival rate | λ (open) or N, Z (closed) | monitoring: request log |
| Service demand at device k | D_k | monitoring: utilization + throughput |
| Service time distribution | — | profiling + distribution fitting |
| Think time | Z | log: time between user requests |
| Burst parameters | multiplier, duration, interval | log: time-series analysis |

---

## Step 1 — Classify the workload

**Open vs. closed:**
- **Open:** users arrive independently of system state (web server, API).
  Model parameter: arrival rate λ (requests/second).
- **Closed:** fixed population of users think, then request (interactive
  terminal, browser session with think time Z).
  Model parameters: N (users), Z (mean think time).

Check: if the arrival rate is independent of how many requests are in-flight,
use open. If users wait for the response before sending the next request, use closed.

**Identifying workload components:**
Cluster requests by type if they have meaningfully different service demands.
Rule of thumb: if two classes differ in D_k by more than 2×, model them
separately (Jain Ch. 6). If similar, collapse into one.

---

## Step 2 — Measure D_k from monitoring

**The direct method (most reliable):**

    D_k = U_k / X

Where U_k = utilization of device k during the measurement window, and
X = system-level throughput (completed requests/sec) during the same window.

Requires: simultaneous measurement of utilization and throughput.
Both must be from the same time interval.

**The indirect method (when utilization is not available):**

    D_k = V_k × S_k

Where V_k = mean visits to device k per request (from profiling/tracing),
and S_k = mean service time per visit.

**Validation:** Σ_k U_k = Σ_k X × D_k should equal total CPU busy fraction.
If not, a device is missing from the model.

---

## Step 3 — Measure arrival rate and think time

**Arrival rate (open system):**
λ = (number of requests in window) / (window duration in seconds)
Measure at several time windows; note variation across time-of-day.

**Think time (closed system):**
Z = (session duration) / (requests per session) − R_measured
Or directly: Z = time between "response received" and "next request sent"
in session logs.

**Burst detection:**
Plot arrival rate as a time series with 1-second resolution. If the series
shows periodic spikes (ratio > 2× baseline), note:
- burst_multiplier = peak_rate / base_rate
- burst_duration = time spike is above 1.5× baseline
- burst_interval = time between spike starts

---

## Step 4 — Characterize variability

**Coefficient of Variation (CV):**

    CV = σ / μ       (standard deviation / mean)

CV is the single most important descriptor of a distribution's shape.

| CV value | Distribution shape | Implication for model |
|---|---|---|
| CV ≈ 0 | Deterministic (constant) | Use M/D/c, not M/M/c |
| CV ≈ 1 | Exponential | M/M/c is appropriate |
| CV > 1 | Heavy-tailed (Pareto, log-normal) | Exponential underestimates tail |
| CV < 1 | Hypo-exponential (Erlang) | Less variable than exponential |

Compute CV for: inter-arrival times, service times at each device.
If CV of service time ≫ 1, the M/M/c assumption is wrong and p99 will
be much worse than the model predicts. See distributions.md.

---

## Step 5 — Validate representativeness

The workload model is representative if it matches the real system on:
1. **Mean throughput X** — simulated ≈ measured within 10%
2. **Mean utilizations U_k** — per device, within 10%
3. **CV of inter-arrival times** — within 20%
4. **Request mix** (if multiple types) — fraction of each type within 5%

If any of these fail, the model is missing something.
The most common culprit: using mean service time when the actual distribution
has a long tail (CV ≫ 1), causing the model to underestimate queueing.

---

## Common workload characterization mistakes

- **Single snapshot:** measuring D_k during a 5-minute window that happens
  to be unusually quiet or busy. Fix: measure over several representative
  periods (multiple days, multiple hours of day).
- **Peak hour ≠ average:** parameterizing the model with peak utilization
  but running it at average arrival rate. Fix: use consistent window.
- **Ignoring request mix:** treating all requests as identical when reads
  and writes have 3× different service times. Fix: cluster by type first.
- **Forgetting think time:** building a closed model with no Z, which makes
  every user immediately re-submit — wildly inflates arrival rate.
