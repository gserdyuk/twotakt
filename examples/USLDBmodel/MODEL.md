# USLDBmodel — what this model represents

This document describes the *intent* of the model. The code in
`server_sim.py` is a faithful encoding of what is described here, but a
reader should not have to read the code to understand the modelling
choices. If the description and the code disagree, the description is
the specification and the code is the bug.

This model is a strict extension of `USLmodel`. Everything in
`USLmodel/MODEL.md` continues to hold. This document only describes
**what is added on top** of that baseline. Read the USLmodel
description first.

## What is added relative to USLmodel

The server now talks to a backend **database**. Every request, after
finishing its application-level work (the CPU/IO phases inherited from
`USLmodel`), issues a single query to the database and waits for the
result before returning to the client.

The database is modelled as **a fixed-size connection pool** and
nothing more. This is the simplest of the database performance models
discussed in the project, and it captures the single most common
failure mode of real services: pool exhaustion under load. More
elaborate models (cache hit/miss, USL on the database itself,
read/write split, WAL fsync bottleneck) are deliberately deferred so
that the effect of a bounded pool can be studied in isolation.

## What a "database" means here

The database is treated as an opaque service with two properties:

1. It accepts at most **N concurrent connections** at any moment.
   N is a configurable parameter (`db_pool_size`). Once N queries are
   in flight, every additional query must wait for one of them to
   finish before it can start. This waiting is automatic and FIFO; it
   is the same mechanism that limits CPU access in `USLmodel`.
2. Each query takes a **random duration** drawn from an exponential
   distribution with a configurable mean (`db_query_mean`). The query
   duration does **not** depend on how many other queries are running
   in parallel. Inside the database itself there is no degradation
   model — this is the simplification that makes "model 1" model 1.

Crucially, **nothing else** about the database is represented: no
notion of locks, transactions, caches, read replicas, write paths, or
storage devices. From the simulation's point of view, a connection is
a token; holding it for the query duration is the entire act of
"querying the database."

## How the database changes the request lifecycle

The lifecycle of a request is the one described in `USLmodel/MODEL.md`,
extended with one new phase at the end:

1. (Unchanged) Poisson arrival, admission control.
2. (Unchanged) The CPU/IO phase loop runs to completion.
3. (New) The thread requests a connection from the database pool. If
   the pool has a free connection it acquires one immediately;
   otherwise it joins the FIFO wait queue for the pool. While waiting
   for a connection, the thread does not hold the CPU — it is in the
   same off-CPU state as during an I/O wait.
4. (New) Once a connection is acquired, the thread holds it for the
   query duration and then releases it.
5. (Unchanged) The request completes successfully, or the SLA timeout
   fires at any point during steps 1–4 and the request is killed.

The database phase is at the **end** of the request. This is the
simplest realistic placement and matches a "render then commit"
pattern. Placing the database call in the middle (between two CPU
phases, "render after read") would change the dynamics in interesting
ways but is not what this model investigates.

## What new failure modes appear

In `USLmodel` there is exactly one bottleneck: the CPU. In this model
there are now **two** potentially binding constraints, the CPU and the
database pool, and the interesting question is which one binds first
under a given configuration.

The pool's theoretical throughput ceiling is `db_pool_size /
db_query_mean` queries per second. With the default parameters
(`pool_size = 8`, `query_mean = 0.05`) that ceiling is 160 rps —
comfortably above the CPU's effective ceiling of about 5 rps from the
USL model. Under defaults the database is **not** the bottleneck, and
the system fails for the same reasons as `USLmodel`: CPU contention
followed by USL-style thrashing.

When the pool is tightened (for example `db_pool_size = 1`), the
pool's ceiling drops to `1 / 0.05 = 20` rps. This is still above the
CPU ceiling, but the database becomes a **second** source of queueing.
The result is that the system breaks slightly earlier than in the
pure-CPU case, and the success rate falls more steeply once it does,
because requests can now time out either waiting for the CPU or
waiting for the connection.

## What the operator can dial (in addition to USLmodel knobs)

- **`db_pool_size`** — how many concurrent connections the database
  accepts. The single most important knob: it determines whether the
  database is a hard ceiling, a contributory bottleneck, or
  effectively invisible.
- **`db_query_mean`** — mean duration of a query in seconds. Multiplied
  with the pool size it gives the database's theoretical throughput
  ceiling.

## What this model deliberately still does not include

- Variable query cost (no cheap-vs-expensive query distinction).
- A cache layer in front of the database.
- Per-query locking, transactional conflicts, or hot-row contention.
- Replication topology (single conceptual database).
- USL-style degradation on the database side itself — concurrent
  queries do not slow each other down here. (That is the natural next
  extension and would be `USLDBmodel` with a USL multiplier on the
  query duration.)

## What success looks like when running this model

The default sweep should look very similar to `USLmodel`'s sweep,
plus an additive baseline latency of roughly `db_query_mean`. With
`db_pool_size = 1` the breakdown should occur slightly earlier on the
arrival-rate axis and the success rate should drop more sharply once
overload begins, because two queues (CPU and pool) are now feeding
timeouts in parallel. If the curve is identical to `USLmodel`'s for
all pool sizes you try, the database integration is broken: the model
is not exercising the new resource.
