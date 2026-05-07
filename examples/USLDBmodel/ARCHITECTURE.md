# USLDBmodel — Architecture

This model is a strict extension of `USLmodel`. The server architecture is
unchanged — read `USLmodel/ARCHITECTURE.md` first. This document describes
only what is added.

## Additional component: Database

| Component | Role | Instances |
|---|---|---|
| Database connection pool | Bounded concurrency gate to the database | 1 pool of N connections |

The database is treated as an **opaque service** with a single observable
property: it accepts at most `db_pool_size` concurrent queries. Queries that
arrive when all connections are occupied wait in a FIFO queue. Each query
occupies one connection for a random duration and then releases it.

Nothing inside the database is modelled — no locks, transactions, caches,
replication, or write paths. A connection is a token; holding it for the query
duration is the entire act of "querying the database."

## Extended signal flow

```
Request arrives
    → [admission control]
    → thread spawned
    → for each CPU/IO phase:
          CPU burst  (exclusive CPU access)
          I/O wait   (CPU released)
    → DB query:
          wait for connection from pool  (CPU released)
          hold connection for query_time
          release connection
    → thread exits, response returned
```

The database phase is at the **end** of the request lifecycle. This matches a
"render then commit" pattern. The CPU is **not** held during the DB wait —
the thread is off-CPU while queuing for a connection and while the query runs.

## Two competing bottlenecks

In USLmodel there is one bottleneck: the CPU. Here there are two:

- **CPU**: theoretical ceiling ≈ `1 / (n_phases × cpu_burst_mean)`, degraded
  by USL contention as load rises.
- **DB pool**: theoretical ceiling = `db_pool_size / db_query_mean`.

With the default parameters (`db_pool_size=8`, `db_query_mean=0.05 s`) the
pool ceiling is 160 rps — far above the CPU ceiling of ~10 rps. Under defaults
the database is **not** the bottleneck. Reducing `db_pool_size` to 1–2 brings
the pool ceiling close to or below the CPU ceiling, creating a second source
of queueing and earlier failure.

## Control flow

Same as USLmodel: optional `max_threads` admission cap and optional
`sla_seconds` per-request timeout. The SLA fires at any point in the request
lifecycle, including while the thread is waiting for a DB connection.
