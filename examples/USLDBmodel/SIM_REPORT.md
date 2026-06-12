# USLDBmodel — Performance Simulation Report

**Date:** 2026-06-11
**Models:** SimPy discrete-event simulation; USL-degraded CPU (inherited from USLmodel) + M/M/c database connection pool
**Data source:** re-run of committed code (`sweep.py` defaults; plus a pool-size comparison run); stochastic — exact values vary between runs, regimes do not
**Repository:** `examples/USLDBmodel/` (strict extension of `examples/USLmodel/`)

## Context

The USLmodel server extended with one new contended resource: a database connection pool.
Two questions: **(1) regression — does the extension leave baseline behavior intact when
the pool is generous? (2) where does the bottleneck move when the pool is starved?**
This example is the exhibit of Step 11 of the methodology: extend by composition —
one new resource, two new config fields, nothing else changed.

## Model summary

DB pool is a `Resource(capacity=db_pool_size)`; query duration ~ Exp(db_query_mean),
no degradation on the DB side (pool is a pure concurrency cap, M/M/c). Theoretical pool
ceiling = pool_size / db_query_mean. See `MODEL.md`.

### Parameters

| Parameter | Value | Justification / source |
|---|---|---|
| inherited CPU/USL params | as USLmodel | see USLmodel report |
| db_pool_size | 8 (default); 1 in starvation run | **Assumption** — sized so pool is not the bottleneck at defaults |
| db_query_mean | 0.05 s | **Assumption** — fast query |

## Sweep design

1. Arrival rate 1 → 20 rps at default pool = 8 (regression vs USLmodel).
2. Arrival rate 3 → 8 rps at pool = 1 vs pool = 8 (bottleneck shift).

## Results

See `sweep.png`, `sweep_2.png`. Key numbers:

**Regression (pool = 8):** p50 at low load ≈ 0.35 s = USLmodel 0.30 s + db_query_mean 0.05 s;
peak ≈ 6 rps; collapse beyond — curve shape indistinguishable from baseline. ✓

**Pool starvation (pool = 1 vs 8):**

| rate, rps | succ (pool=1) | succ (pool=8) |
|---|---|---|
| 5 | 1.00 | 1.00 |
| 6 | **0.27** | **1.00** |
| 7 | 0.15 | 0.13 |

## Interpretation

The regression result confirms the composition rule: a generous pool adds a constant
0.05 s to latency and changes nothing else. Validation criterion 1 of `MODEL.md` holds.

The starvation result contains the non-obvious finding. The theoretical ceiling of a
single connection is 1 / 0.05 = **20 rps** — on paper, pool = 1 should be comfortable at
6 rps. In the simulation it collapses there (success 0.27 vs 1.00). Mechanism: near CPU
saturation the USL term inflates in-flight count; in-flight requests then serialize on
the single connection; time spent waiting for the pool burns the SLA budget; timeouts
cascade. **Component ceilings do not compose additively — the bottleneck emerges from
the interaction of two resources, at a load where neither is saturated in isolation.**
This is precisely the class of effect that back-of-envelope capacity math misses and
intuition mispredicts.

## Conclusions & recommendations

- With pool ≥ 8 the database is invisible: size the system by the CPU knee (≈ 5 rps safe).
- Pool sizing by per-component ceiling math is unsafe near CPU saturation; budget pool
  capacity against **in-flight count at the knee**, not against average query rate.
- When diagnosing a production collapse at loads "below every component's limit,"
  look for resource-interaction serialization of exactly this kind.

## Risks & sensitivity

Sensitive to db_query_mean: a 0.3 s query (loaded cluster) drops the single-connection
ceiling to ~3 rps and moves the interaction collapse well below the CPU knee — the DB
becomes the primary bottleneck. Re-measure before reuse.

## Limitations

No query cost variance, no cache, no replication, no DB-side degradation — see
`MODEL.md`. Most likely next extension: USL term on the DB side (contention inside
the database).
