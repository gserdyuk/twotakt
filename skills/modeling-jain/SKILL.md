---
name: modeling-jain
description: >-
  Measurement, workload characterization, distribution fitting, and simulation
  output analysis — the Raj Jain methodology. Use when: (1) parameterizing a
  model from real system monitoring data; (2) deciding which distribution to use
  for service times; (3) computing proper confidence intervals for SimPy sweep
  results; (4) auditing a performance study for common mistakes. Complements
  simpy-protocol (provides inputs and validates outputs) and queueing-lazowska
  (provides D_k when measured from real system monitoring). Source: Raj Jain — "The Art of
  Computer Systems Performance Analysis" (Wiley, 1991).
  Free: archive.org/details/artofcomputersys0000jain
---

# Jain — Measurement and Output Analysis Methodology

This skill captures the four parts of Jain's book that fill gaps in
simpy-protocol and queueing-lazowska:

1. **Common mistakes** — checklist to audit any performance study before and after.
2. **Workload characterization** — how to get model inputs (D_k, arrival rate,
   service time distributions) from real system measurements.
3. **Distribution fitting** — when is exponential appropriate? What to do when it's not.
4. **Simulation output analysis** — warm-up period, confidence intervals,
   number of runs. Replaces the ad-hoc "use 3 seeds" approach.

## What Jain uniquely provides

These three capabilities are absent from both queueing-lazowska and simpy-protocol:

**1. The real-system → model bridge**
When a real system exists, Jain provides the measurement method for model
parameters: `D_k = U_k / X` — utilization divided by throughput, measured
simultaneously from the same monitoring window. This is one of five valid
parameter sources (see queueing-lazowska "Source of D_k"); it is the most
accurate when the system is already running. Without explicit sourcing,
parameters are hidden assumptions. Read `references/workload.md`.

**2. CV check before choosing a distribution**
`CV = σ/μ` of service time samples is the single decision that determines tail
accuracy. CV ≈ 1 → exponential valid (M/M/c applies). CV > 1.5 → Pareto or
log-normal → p99 underestimated by 2–10× if you keep `expovariate`. simpy-protocol
defaults to `expovariate` everywhere; Jain tells you when that default is wrong.
Read `references/distributions.md`.

**3. Proper confidence intervals instead of "3 seeds"**
The default sweep pattern reports `mean ± std` over 3 seeds. That is wrong: wrong
distribution (needs t, not normal), no warm-up removal, denominator off. Jain
replaces it with: r ≥ 10 replications, discard warmup fraction, report
`ȳ ± t(r−1, 0.025) · s/√r`. `templates/ci_calc.py` implements this exactly.
Read `references/output-analysis.md`.

## When to use this skill

| Situation | Use |
|---|---|
| Building a model from scratch — where do D_k come from? | workload.md |
| Choosing between exponential and something else | distributions.md |
| Asking "how many seeds is enough?" | output-analysis.md |
| Computing CI for SimPy p95 latency results | output-analysis.md + ci_calc.py |
| Reviewing a performance study for errors | mistakes.md |
| Ratio comparison (system A vs B) | mistakes.md — ratio games section |

## Position in the toolkit

    Real system (if it exists)
        │
        ▼  workload.md: measure D_k, arrival rate, service time distributions
    Model inputs
        │
        ├──▶ queueing-lazowska: ABA/MVA (fast analytical answer)
        │
        └──▶ simpy-protocol:
               Phase 5  ← parameter sources (D_k, service times, distributions)
               Phase 7  ← CV check before choosing distribution (V&V)
                  │
                  ▼  SimPy model + bench
                  │
               Phase 9  ← output-analysis.md (CI, warm-up, seeds)
                  │
                  ▼
              Validated results

Jain sits at the input end (Phase 5, Phase 7) and the output end (Phase 9).
QSP and simpy-protocol are the middle.
When no real system exists, Jain's output analysis (Phase 9) still applies —
the measurement part (workload.md) does not.

## The checklist habit

Before starting any performance study: read `references/mistakes.md`.
After getting results: read it again. Half the value of Jain's book is
this list — the mistakes are easy to make and invisible until named.

## Reference files

- `references/mistakes.md` — 27 common mistakes, organized by phase
- `references/workload.md` — workload characterization: measuring D_k from real systems
- `references/distributions.md` — distribution selection and fitting
- `references/output-analysis.md` — simulation output: warm-up, CI, number of runs

## Templates

- `templates/ci_calc.py` — confidence interval computation for SimPy sweep results
