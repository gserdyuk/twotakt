# Distribution Selection and Fitting

Source: Raj Jain, "The Art of Computer Systems Performance Analysis", Part V (Chapters 26–29).

When to use exponential, and what to do when it is wrong.

---

## The exponential assumption and when it holds

Our SimPy models use `random.expovariate(1/mean)` everywhere. This is
correct when the service time has CV ≈ 1. It is wrong — and the error
compounds — when CV is substantially different from 1.

**Key property of exponential:** memoryless. The remaining service time
is independent of how long a job has already been running. This makes
M/M/c analytically tractable. Real systems often violate this.

---

## Distribution selection by CV

### CV ≈ 1 → Exponential

    random.expovariate(1.0 / mean)

Use for: I/O-bound service where duration is dominated by a single
unpredictable event (network round trip, disk seek + transfer).
Product-form queueing theory applies exactly.

### CV < 1 → Erlang or hypo-exponential

Service time is the sum of k exponential stages, each with rate k/mean.
Less variable than exponential; tail is lighter.

    # Erlang-k: sum of k exponential samples
    def erlang(k, mean):
        return sum(random.expovariate(k / mean) for _ in range(k))

Use for: CPU-bound jobs with multiple sequential phases of similar duration.
M/E_k/c has lower queueing than M/M/c at the same utilization.

### CV > 1 → Pareto or log-normal

**Pareto (power-law tail):**

    # Pareto with shape α and minimum x_min
    # Mean = α * x_min / (α - 1),  CV² = 1 / (α-2)  (for α > 2)
    random.paretovariate(alpha) * x_min   # Python's paretovariate returns x_min=1

Use for: file sizes, web request sizes, computation time in heterogeneous jobs.
When α < 2, variance is infinite — no finite mean for queueing.
When 2 < α < 3, variance is finite but mean of max grows without bound.
Queueing delay under Pareto is dramatically worse than M/M/c predicts.

**Log-normal:**

    import math
    math.exp(random.gauss(mu, sigma))   # log-normal

Use for: response times of complex multi-step operations where many small
random multiplicative factors combine (Central Limit Theorem in log space).

---

## How to test which distribution fits

**Step 1 — Compute CV from your data:**

    CV = std(samples) / mean(samples)

CV < 0.5: likely Erlang. CV ≈ 1: likely exponential. CV > 1.5: likely Pareto/log-normal.

**Step 2 — Q-Q plot:**
Plot quantiles of your data against quantiles of the candidate distribution.
A straight line = good fit. Upward curve at the right tail = real tail is
heavier than the candidate (common: data is Pareto, candidate is exponential).

**Step 3 — Chi-square goodness-of-fit:**
Bin the data; compare observed vs. expected counts under the candidate
distribution. Chi-square statistic = Σ (O_i − E_i)² / E_i.
If p-value < 0.05, reject the candidate.

**Step 4 — Log-log plot for power-law detection:**
Plot log(1 − CDF) vs. log(x). A straight line on this plot = Pareto tail.
Slope = −α (the shape parameter).

---

## Practical decision tree

    Measure CV of service time samples
        │
        ├─ CV < 0.5  →  Erlang-k  (k ≈ 1/CV²)
        │
        ├─ 0.7 < CV < 1.3  →  Exponential  ← M/M/c applies
        │
        ├─ 1.3 < CV < 3  →  Log-normal (check with Q-Q plot)
        │
        └─ CV > 3  →  Pareto (check with log-log CDF plot)
                      Verify α > 2 (finite variance) before using M/M/c bounds.
                      If α < 2: simulation only, no closed-form queueing.

---

## Impact on model accuracy

Using exponential when CV > 2 causes:
- p99 latency underestimated by 2–10× (the heavy tail contributes long jobs
  that dominate the tail but are invisible in the mean)
- Throughput ceiling unaffected (depends on mean, not distribution)
- Queue length underestimated at moderate utilization

**Rule:** if CV of service time > 1.5, run sensitivity: compare exponential
model vs. Pareto model. If p99 differs by > 2×, report both and note the
model is sensitive to distribution choice.

---

## Arrival process

Most of our models use Poisson arrivals (exponential inter-arrival times,
CV = 1). This is justified when:
- Requests arrive from many independent sources (law of rare events)
- No batch arrivals or synchronized clients

When Poisson is wrong:
- **Bursty arrivals (CV > 1):** use square-wave burst modulation (already
  in simpy-protocol Q4a) or a compound Poisson process.
- **Regular arrivals (CV < 1):** D/M/c — less queueing than M/M/c at same load.
- **Correlated arrivals:** requires simulation; analytical models break.
