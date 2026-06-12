# USLDBmodel — Simulation Model

This document describes the *simulation model* — how the architecture is
translated into SimPy, which mathematical laws are applied, and what the
model deliberately excludes. Read `ARCHITECTURE.md` (and `USLmodel/ARCHITECTURE.md`)
first; this document assumes familiarity with both.

This model is a strict extension of `USLmodel`. Everything in
`USLmodel/MODEL.md` continues to hold. This document describes only
**what is added on top** of that baseline.

If this description and the code disagree, this description is the
specification and the code is the bug.

## From architecture to SimPy

| Architectural element | SimPy primitive | Mathematical model |
|---|---|---|
| CPU (single shared resource) | `simpy.Resource(capacity=1)` | M/M/1 baseline; USL multiplier on service time |
| OS thread (in-flight request) | SimPy process | — |
| DB connection pool | `simpy.Resource(capacity=db_pool_size)` | M/M/c: bounded concurrency, FIFO wait, no intra-DB degradation |
| Admission control (thread cap) | check on `active` counter | — |
| SLA timeout | `simpy.timeout` + `process.interrupt()` | fires during CPU wait, I/O wait, or DB pool wait |

## Mathematical model

### CPU phases (inherited from USLmodel)

    effective_burst = base_burst × (1 + α·(N−1) + β·N·(N−1))

where N is the number of in-flight requests. See `USLmodel/MODEL.md` for
derivation and rationale.

### Database phase

Query duration is drawn from `Exp(1 / db_query_mean)`. There is no
degradation multiplier on the DB side — concurrent queries do not slow each
other down. The pool acts purely as a concurrency cap (M/M/c model).

Theoretical throughput ceiling of the pool:

    db_ceiling = db_pool_size / db_query_mean

With defaults (pool=8, mean=0.05 s): ceiling = 160 rps — well above the
CPU ceiling of ~10 rps, so the CPU saturates first under defaults.

## Parameter sources

| Parameter | Default | Source |
|---|---|---|
| `cpu_count` | 1 | Architecture decision (inherited from USLmodel) |
| `n_phases` | 2 | Design assumption (inherited from USLmodel) |
| `cpu_burst_mean` | 0.05 s | Assumption (inherited from USLmodel) |
| `io_wait_mean` | 0.10 s | Assumption (inherited from USLmodel) |
| `alpha` | 0.02 | Assumption (inherited from USLmodel) |
| `beta` | 0.001 | Assumption (inherited from USLmodel) |
| `arrival_rate` | 4.0 rps | Bench parameter — below saturation for healthy baseline |
| `sla_seconds` | None (10.0 s in sweep) | Off by default; sweep uses 10.0 s |
| `max_threads` | None | Architecture: no admission control by default |
| `db_pool_size` | 8 | **Assumption** — chosen so pool is not the bottleneck at defaults; reduces to 1–4 to study pool exhaustion |
| `db_query_mean` | 0.05 s | **Assumption** — fast query, adds ~0.05 s additive baseline latency |

All numeric assumptions should be treated as illustrative. Use
`skills/modeling-jain/references/workload.md` (from repo root) to replace
assumptions with measurements when a real system is available.

## What this model deliberately does not include

All omissions from USLmodel, plus:

- Variable query cost (no cheap-vs-expensive query distinction)
- A cache layer in front of the database
- Per-query locking, transactional conflicts, or hot-row contention
- Replication topology (single conceptual database)
- USL-style degradation on the database side — concurrent queries do not
  slow each other down (that would be the natural next extension)

## Verification & Validation criteria

**Verification** (smoke test at defaults):
- throughput ≈ arrival rate (4.0 rps)
- latency p50 ≈ USLmodel p50 + db_query_mean ≈ 0.30 + 0.05 = 0.35 s
- success rate ≈ 1.0 (no drops at low load; no SLA configured at defaults)

**Validation** (sweeps):

1. **Regression** — with `db_pool_size` large (≥ 100), the throughput/latency
   curve must be indistinguishable from USLmodel. If it differs, the DB
   integration is broken.

2. **Pool exhaustion** — with `db_pool_size = 1`, breakdown must occur earlier
   than in USLmodel and the success-rate decline must be steeper. If the curves
   are identical for all pool sizes, the pool resource is not being exercised.

3. **Three regimes** — same as USLmodel: linear scaling, saturation knee,
   thrashing. All three must appear in the primary arrival-rate sweep.
