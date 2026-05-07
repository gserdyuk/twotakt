# USLDBmodel — Educational Requirements

This is an educational example. It is a strict extension of `USLmodel` — read
that model's requirements first. The questions below concern only what the
database layer adds.

## System under study

The same HTTP server as USLmodel (thread-per-request, single CPU), now with a
backend database reached through a bounded connection pool. Every request issues
exactly one query after completing its CPU/IO work.

## Questions this model must answer

1. When the DB pool is large (effectively unlimited), does the system behave
   identically to USLmodel? (Regression / baseline check.)
2. When the pool is small, does pool exhaustion appear as a second source of
   queueing on top of CPU contention?
3. Which resource saturates first — CPU or pool — and under what configuration
   does that answer change?
4. How does adding a bounded pool change the shape of the success-rate decline
   compared to USLmodel?

## Required behaviour

| Condition | Expected behaviour |
|---|---|
| `db_pool_size` large (≥ 100) | Curve matches USLmodel: CPU dominates |
| `db_pool_size` tight (e.g. 1) | Success rate drops earlier and more steeply than USLmodel |
| Any pool size, low load | Additive baseline latency of ≈ `db_query_mean` vs USLmodel |

## SLA

p99 < 10 seconds at load ≤ 50% of the saturation point (consistent with USLmodel sweep).

## Sweep

Primary: arrival rate 1–20 rps.
Secondary: `db_pool_size` values (e.g. 1, 4, 8, large) to show the transition
from pool-bound to CPU-bound behaviour.
