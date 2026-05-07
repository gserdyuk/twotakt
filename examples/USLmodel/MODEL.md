# USLmodel — Simulation Model

This document describes the *simulation model* — how the architecture is
translated into SimPy, which mathematical laws are applied, and what the
model deliberately excludes. Read `ARCHITECTURE.md` first; this document
assumes familiarity with the system structure.

If this description and the code disagree, this description is the
specification and the code is the bug.

## From architecture to SimPy

| Architectural element | SimPy primitive | Mathematical model |
|---|---|---|
| CPU (single shared resource) | `simpy.Resource(capacity=1)` | M/M/1 baseline; USL multiplier on service time |
| OS thread (in-flight request) | SimPy process | — |
| Admission control (thread cap) | check on `cpu.count + len(cpu.queue)` | — |
| SLA timeout | `simpy.timeout` + `process.interrupt()` | — |

## Mathematical model

The CPU burst duration is multiplied by the USL degradation factor:

    effective_burst = base_burst × (1 + α·(N−1) + β·N·(N−1))

where N is the number of currently in-flight requests, α captures linear
contention (Amdahl serialization, context switches), and β captures
quadratic inter-thread interference (cache coherency, lock convoys).

Setting α = β = 0 recovers the pure M/M/1 model — useful as a baseline.

I/O wait duration is **not** subject to the USL multiplier. I/O happens
off-CPU and does not contribute to thread-on-thread interference.

## Parameter sources

| Parameter | Default | Source |
|---|---|---|
| `cpu_count` | 1 | Architecture decision (single CPU, see ARCHITECTURE.md) |
| `num_phases` | 2 | Design assumption: "parse → call backend → respond" ≈ 2 phase pairs |
| `cpu_burst_mean` | 0.05 s | **Assumption** — no real system measured; chosen so saturation ≈ 10 rps with USL visible before that |
| `io_wait_mean` | 0.10 s | **Assumption** — 2:1 IO:CPU ratio; I/O dominates to make CPU contention visible by contrast |
| `alpha` | 0.02 | **Assumption** — mild linear contention; sweep to explore |
| `beta` | 0.001 | **Assumption** — light quadratic effect; sweep to explore |
| `arrival_rate` | 4.0 rps | Bench parameter — below saturation for healthy baseline |
| `sla_seconds` | None (10.0 s in sweep) | Off by default; sweep uses 10.0 s to observe the full timeout-driven decline curve |
| `max_threads` | None | Architecture: no admission control by default |

All numeric assumptions should be treated as illustrative. Use
`modeling-jain/references/workload.md` to replace assumptions with
measurements when a real system is available.

## What this model deliberately does not include

- Multiple cores (one-line change; omitted to keep contention story visible)
- Heterogeneous request types (single distribution)
- A separate application-level queue or load balancer
- Memory pressure and OOM as discrete events
- Garbage collection as discrete pauses
- Network or disk capacity limits
- Anything downstream of the server — that is what `USLDBmodel` adds

These omissions are not because they don't matter; each belongs in its
own derived model so it can be examined in isolation.

## Verification & Validation criteria

**Verification** (smoke test at defaults):
- throughput ≈ arrival rate (4.0 rps)
- latency p50 ≈ num_phases × (cpu_burst_mean + io_wait_mean) = 2 × (0.05 + 0.10) = 0.30 s
- success rate ≈ 1.0 (no drops at low load; no SLA configured at defaults)

**Validation** (sweep over arrival rate 1–20 rps):
Three regimes must appear:
1. **Linear scaling** — throughput tracks arrival rate, latency stable
2. **Saturation knee** — throughput plateaus, p99 rises
3. **Thrashing** — throughput *falls*, SLA timeouts dominate

If any regime is absent the model is mis-tuned, not the theory.
Setting α = β = 0 must produce a pure M/M/1 plateau (no decline) —
this is the baseline sanity check for the USL implementation.
