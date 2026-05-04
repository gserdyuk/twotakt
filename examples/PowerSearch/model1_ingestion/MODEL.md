# PowerSearch Ingestion Pipeline — Model 1

> The intent of this document is to capture *modelling intent* in human prose
> so a reader does not have to reconstruct it from the code. If this description
> and the code disagree, this description is the specification and the code is
> the bug.

## What real system is being modelled

Single-region PowerSearch ingestion pipeline. Crawlers emit item-update events to
a Kafka queue. Processing workers read these events, normalise the reseller schema,
deduplicate, detect price or availability changes, and write the result to
Elasticsearch. The business SLA is: any price change must be queryable within 10
seconds of the crawler fetching the page.

## What is scarce / shared in this system

- **Processing worker pool** (`num_workers`, primary sweep variable): each slot reads
  one Kafka event, normalises + deduplicates + detects changes, then releases.
  Corresponds to `simpy.Resource(capacity=num_workers)`.
- **Elasticsearch indexing connection pool** (`es_pool_size`, default 200): each slot
  performs one ES document write, then releases.
  Corresponds to `simpy.Resource(capacity=es_pool_size)`.

## What a request looks like

1. Kafka event arrives (Poisson at `num_resellers × update_rate_per_reseller` events/s).
2. Waits for a free processing worker slot.
3. Normalise + dedup + detect change (exponential, mean = `processing_time_mean` = 0.05 s).
4. Releases worker slot.
5. Waits for a free ES indexing connection.
6. ES document write (exponential, mean = `es_indexing_time_mean` = 0.15 s).
7. Releases ES connection. Item is now visible. Total elapsed time = pipeline latency.

## Workload

Poisson arrivals at rate = `num_resellers × update_rate_per_reseller`.
Default `update_rate_per_reseller` = 10.0 events/s (fast continuous crawl; 10 K items
crawled per reseller in ~17 minutes).

| Scale | Resellers | Arrival rate |
|---|---|---|
| Year 1 | 15 | 150 events/s |
| Year 3 | 55 | 550 events/s |
| Year 5 | 115 | 1 150 events/s |
| Beyond | 130 | 1 300 events/s |

Sweep: `num_resellers` from 15 to 130, with `num_workers` as secondary variable.
Simulation duration: 600 s per configuration.

## How the system degrades under load

Two cascaded M/M/c queues (pure queueing theory). No USL degradation (`alpha=beta=0`):
processing workers are I/O-bound (Kafka read + ES write) with no shared in-process
state that would cause coherency or lock-convoy degradation.

The first pool (workers) is the primary bottleneck when undersized. Once workers are
sufficient, the ES indexing pool becomes the ceiling. At Year 5 load (1 150 events/s),
the ES pool needs ≥ 173 connections to avoid being the binding constraint.

## Backpressure and safety

SLA timeout: 10 seconds. Requests exceeding the SLA are counted as `dropped_timeout`;
their latency is set to `sla_seconds` in effective latency calculations. No admission
cap (`max_threads=None`) by default.

## Lifecycle of a single request

1. Arrive → append `RequestRecord(arrival=env.now)`
2. Admission check (skipped when `max_threads=None`)
3. Acquire `workers` slot → `rec.start = env.now`
4. `yield timeout(Exp(processing_time_mean))` — normalise + dedup + detect
5. Release `workers` slot
6. Acquire `es_pool` slot
7. `yield timeout(Exp(es_indexing_time_mean))` — ES write
8. Release `es_pool` slot
9. `rec.outcome = "ok"`, `rec.finish = env.now`

SLA timer wraps steps 3–9; interrupt on expiry → `dropped_timeout`.

## What the operator can dial

**Workload**
- `num_resellers` — number of resellers crawled; sweep variable (default 15)
- `update_rate_per_reseller` — Kafka events/s per reseller (default 10.0)
- `sim_time` — simulation duration in seconds (default 600)
- `seed` — random seed (default 42)

**Per-event work**
- `processing_time_mean` — mean worker service time in seconds (default 0.05)
- `es_indexing_time_mean` — mean ES write time in seconds (default 0.15)

**Pools**
- `num_workers` — processing pool size; secondary sweep variable (default 10)
- `es_pool_size` — ES indexing connections (default 200)

**Degradation (reserved)**
- `alpha` — USL linear contention coefficient (default 0.0)
- `beta` — USL quadratic coherency coefficient (default 0.0)

**Backpressure**
- `max_threads` — admission cap; `None` = unlimited (default None)
- `sla_seconds` — pipeline SLA in seconds (default 10.0)

## What this model deliberately does not include

- Kafka consumer group rebalancing or partition replication lag
- Elasticsearch shard routing, replica selection, or indexing refresh delay
- Deduplication as a separate resource (lumped into `processing_time_mean`)
- PostgreSQL canonical write (order of magnitude faster than ES write; never binds)
- Crawler cycle time (pages/hour per reseller) — only arrival rate to Kafka matters
- Cross-region Elasticsearch replication
- Failure, retry, and circuit-breaker behaviour
- Multiple request types (all events treated identically)
- Zero-downtime deployment mechanics

## What success looks like when running this model

**Smoke test** (`num_resellers=15`, `num_workers=10`, `es_pool_size=200`):
arrival rate = 150 events/s; worker capacity = 200 events/s; ES capacity = 1 333 events/s.
Expected: `success_rate ≈ 1.0`, `throughput_rps ≈ 150`, `eff_latency_p95` well under 10 s.

**Sweep validation**: as `num_resellers` grows from 15 to 130, the minimum `num_workers`
required to hold `success_rate ≥ 0.99` should rise approximately linearly with the
arrival rate. A plot of (`num_resellers`, `min_workers_at_SLA_boundary`) must show a
roughly straight line, confirming that the M/M/c model correctly captures linear
capacity scaling. When workers are sufficient, a secondary failure mode appears when
the ES pool becomes the binding constraint.
