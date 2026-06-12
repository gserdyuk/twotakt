# USLmodel — Performance Simulation Report

**Date:** 2026-06-11
**Models:** SimPy discrete-event simulation; M/M/1 baseline with USL degradation multiplier
**Data source:** re-run of committed code (`sweep.py`, sim_time = 300 s, SLA = 10 s, max_threads = 500); stochastic — exact values vary between runs, regimes do not
**Repository:** `examples/USLmodel/`

## Context

A single server processing requests with alternating CPU-burst and I/O-wait phases.
The question: **how does throughput and latency behave as offered load grows — and where
is the safe operating point?** This is the baseline exhibit of the methodology: it must
reproduce the rise–peak–decline curve that real servers show and a pure M/M/1 model cannot.

## Model summary

CPU is a `Resource(capacity=1)`; each request is a process holding the CPU during bursts
and releasing it during I/O. Burst time is inflated by the USL factor
`1 + α(N−1) + β·N(N−1)` evaluated at the current in-flight count N. See `MODEL.md`.

### Parameters

| Parameter | Value | Justification / source |
|---|---|---|
| cpu_burst_mean | 0.05 s | **Assumption** |
| io_wait_mean | 0.10 s | **Assumption** |
| n_phases | 2 | Design assumption |
| α / β | 0.02 / 0.001 | **Assumption** — illustrative contention/coherency levels |
| sla_seconds | 10 s | Sweep parameter |

## Sweep design

Arrival rate swept 1 → 20 rps. The range deliberately crosses saturation so all three
regimes appear (validation criterion from `MODEL.md`).

## Results

See `sweep.png` (three panels: throughput vs ideal, success rate, effective vs ok-only latency).
Key points from the run:

| rate, rps | throughput, rps | p95 eff, s | timeouts |
|---|---|---|---|
| 4 | 4.05 | 0.86 | 0 |
| 5 | 5.30 | 0.93 | 0 |
| 6 | 2.42 | 2.7 → SLA | 1088 |
| 8 | 0.41 | pegged at SLA | 2219 |
| 20 | 0.07 | pegged at SLA | 5855 |

## Interpretation

Three regimes, as theory demands:

1. **Linear scaling** (≤ 5 rps): throughput tracks the ideal y = x line; latency grows mildly.
2. **Saturation knee** (~5–6 rps): peak throughput ≈ 5.3 rps.
3. **Thrashing** (> 6 rps): throughput *collapses* rather than plateaus — the USL β term
   at work. Every admitted request inflates service time for all others; the server does
   progressively less useful work as load grows. An M/M/1 model would show a flat plateau
   here; the collapse is the signature of coherency cost.

**Survivorship bias check:** beyond the knee, ok-only p50 stays at 1–2 s while effective
latency is pegged at the 10 s SLA. A dashboard showing only successful-request latency
would report a healthy system at 0.4 rps goodput. Raw latency of successes is not a
decision-grade metric under overload.

## Conclusions & recommendations

- Peak throughput ≈ **5.3 rps**; the collapse beyond it is steep, not gradual.
- Safe operating point: **≤ 4 rps** (~75–80 % of peak) — beyond it the system is one
  burst away from the cliff.
- Any production deployment of a system with this profile needs **admission control**:
  past the knee, rejecting excess load preserves goodput; admitting it destroys goodput
  for everyone.

## Risks & sensitivity

Conclusions are most sensitive to **β**: with β → 0 the collapse becomes a plateau and
admission control becomes less critical. If a real system shows a plateau instead of a
decline, re-fit α/β from measurements before reusing these conclusions.

## Limitations

Single CPU, no retries, no priorities, fixed two-phase request shape — see
"deliberately does not include" in `MODEL.md`. Most likely next extension: a second
contended resource (done in `USLDBmodel`).
