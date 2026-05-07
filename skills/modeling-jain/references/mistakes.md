# Common Mistakes in Performance Analysis

Source: Raj Jain, "The Art of Computer Systems Performance Analysis", Chapter 2.
Use as a checklist before starting and after completing any performance study.

---

## Phase 1 — Goal and scope mistakes

**M1 — No goals.**
Starting without a clear objective. Metrics, workload, and methodology all
depend on the goal. "Measure performance" is not a goal.
Fix: state the question the study must answer before touching any tool.

**M2 — Biased goals.**
Choosing metrics and workloads that make your own system look good rather
than finding the right metrics for the use case.
Fix: define metrics before knowing which system wins.

**M3 — Unsystematic approach.**
Picking parameters, factors, and workloads arbitrarily — tweaking things
until the result looks reasonable.
Fix: use experimental design (2^k factorial); vary one factor at a time
only when the others are truly independent.

**M4 — Wrong performance metric.**
Optimizing throughput when the user cares about latency. Reporting mean
when p99 is what matters for SLA.
Fix: trace the metric to the user-visible effect. Ask "what does the user
experience when this number changes?"

---

## Phase 2 — Workload mistakes

**M5 — Unrepresentative workload.**
The benchmark or synthetic workload does not match real production traffic.
A system can look excellent under a uniform Poisson workload and fail under
the real bursty, skewed, long-tailed load.
Fix: characterize the real workload first (see workload.md). Validate that
synthetic workload matches real workload on key parameters: arrival rate,
service time distribution, CV, mix of request types.

**M6 — Wrong workload parameters.**
Using the right workload type but with wrong numbers: arrival rate taken
from peak hour but service time from a different run, or vice versa.
Fix: measure all workload parameters from the same time window.

---

## Phase 3 — Measurement mistakes

**M7 — Probe effect.**
The measurement tool itself consumes resources and changes what is being
measured. A software monitor that logs every event adds CPU and I/O overhead.
Fix: estimate probe overhead. If > 1% of the measured quantity, use a
less invasive monitor or a hardware monitor.

**M8 — Ignoring variability.**
Reporting only the mean. The mean of a bimodal distribution (fast cache
hits + slow cache misses) tells you nothing useful. p95 and CV reveal
the distribution shape.
Fix: always report at minimum: mean, standard deviation, and at least
two percentiles (p50, p95 or p99). Report CV = σ/μ.

**M9 — Single-number summary under overload.**
Reporting "average latency = 50 ms" while 30% of requests time out.
The average is computed over the survivors (survivorship bias).
Fix: always report success rate alongside latency. This is Rules 1–2
of simpy-protocol metric-checklist — see that file for detail.

**M10 — Ignoring correlation.**
Treating autocorrelated samples as independent. Consecutive latency
measurements in a simulation are correlated; treating them as i.i.d.
underestimates variance and produces overconfident confidence intervals.
Fix: use batch means or independent replications (see output-analysis.md).

**M11 — Comparing systems under different conditions.**
System A tested at 100 req/s, system B at 200 req/s, conclusion "B is faster."
Fix: test both systems at the same offered load, or show curves across the
full load range.

---

## Phase 4 — Analysis mistakes

**M12 — No error analysis.**
Reporting a single number (mean latency = 47 ms) with no confidence interval.
A single simulation run at a stochastic knee has high variance — the true
mean could be 30 ms or 80 ms.
Fix: always report results as x̄ ± CI (see output-analysis.md).

**M13 — Ignoring the transient.**
Starting data collection from time 0 in a simulation that starts empty.
The initial ramp-up inflates or deflates results depending on direction.
Fix: detect and remove the warm-up period (see output-analysis.md).

**M14 — Arithmetic mean of ratios.**
Comparing two systems by averaging their speedup ratios using arithmetic
mean. Arithmetic mean of ratios is not invariant to which system is the
baseline. Use geometric mean for ratios.
  Correct:  geometric_mean(a/b) = geometric_mean(b/a)^(−1)
  Wrong:    arithmetic_mean(a/b) ≠ 1 / arithmetic_mean(b/a)

**M15 — Assuming the model is the system.**
A simulation or analytical model is an approximation. Conclusions valid for
the model may not hold for the real system if key mechanisms are absent.
Fix: validate the model against at least one real measurement point before
using it for predictions.

**M16 — No sensitivity analysis.**
Publishing "the system handles 500 req/s" without asking: what if the
service time is 2× what we assumed? If the conclusion flips, the study
is fragile.
Fix: re-run ABA/MVA/simulation with ±2× on the key assumption. Report
which parameters the conclusion is sensitive to.

---

## Phase 5 — Presentation mistakes

**M17 — Ignoring non-stationarity.**
Plotting mean response time over a run that includes burst episodes without
distinguishing burst vs. steady-state periods. The mean hides the structure.
Fix: plot time series of the metric. Label burst windows. Compute statistics
separately for burst and non-burst periods.

**M18 — Axes that start at non-zero.**
A bar chart where the y-axis starts at 450 ms makes a 1% difference look
like a 10× difference.
Fix: always start the y-axis at 0, or explicitly label that it does not.

**M19 — Too many significant figures.**
Reporting "mean latency = 47.3821 ms" when the confidence interval is
±15 ms. False precision misleads readers.
Fix: round to the precision implied by the CI.

---

## Quick pre-study checklist (5 questions)

Before starting any study, answer these:
1. What is the exact question this study answers?
2. What metric directly reflects user experience for this question?
3. Is the workload representative of real production? (CV, mix, burst pattern)
4. How will results be validated against at least one real data point?
5. Which assumption, if wrong by 2×, would change the conclusion?

If any answer is "I don't know", resolve it before collecting data.
