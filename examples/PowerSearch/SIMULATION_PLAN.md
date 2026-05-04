# PowerSearch — Performance Simulation Plan

## Context

Two SimPy simulation models for the PowerSearch clothes price aggregator.
ARCHITECTURE.md in `examples/PowerSearch/` already answers all 8 audit questions
(Q1–Q8), so the audit phase is complete from the spec doc. Both models reduce to
**two cascaded M/M/c queues** (same structural pattern as `examples/USLDBmodel/`).

Theoretical framework for both: **pure M/M/c** (no USL). Workers in both pipelines
are I/O-bound (Kafka read + ES write for ingestion; ES query for user-facing). There
is no shared in-process CPU state that would cause USL-style coherency degradation.
`alpha=beta=0.0` is correct by default; the fields are kept on `Config` for future
exploration.

---

## Audit answers (from ARCHITECTURE.md)

| Q | Answer |
|---|---|
| Q1 — Real system | PowerSearch price aggregator, single region |
| Q2 — Scarce resources | (M1) processing workers + ES indexing pool; (M2) search workers + ES query pool |
| Q3 — Request lifecycle | Sequential two-phase: acquire first pool → do work → release → acquire second pool → do work → release |
| Q4 — Workload | (M1) Poisson at `num_resellers × update_rate_per_reseller`; (M2) Poisson base + square-wave burst 5× for 30 s every 120 s |
| Q5 — Degradation | Pure M/M/c; I/O-bound workers, no CPU thrashing, alpha=beta=0 |
| Q6 — Backpressure | SLA timeout only: 10 s (ingestion), 0.5 s (queries). No admission cap by default |
| Q7 — Out of scope | See MODEL.md drafts below |
| Q8 — Success | See MODEL.md drafts below |

---

## File structure to create

```
examples/PowerSearch/
  model1_ingestion/
    MODEL.md
    server_sim.py
    sweep.py
    plot_sweep.py
    requirements.txt
  model2_queries/
    MODEL.md
    server_sim.py
    sweep.py
    plot_sweep.py
    requirements.txt
```

---

## MODEL.md — Model 1: Ingestion Pipeline

```
## What real system is being modelled
Single-region PowerSearch ingestion pipeline. Crawlers emit item-update events to a
Kafka queue. Processing workers read these events, normalise the reseller schema,
deduplicate, detect price or availability changes, and write the result to
Elasticsearch. The business SLA is: any price change must be queryable within 10
seconds of the crawler fetching the page.

## What is scarce / shared in this system
- Processing worker pool (num_workers, primary sweep variable):
  each slot reads one Kafka event, normalises + deduplicates + detects change.
- Elasticsearch indexing connection pool (es_pool_size, default 50):
  each slot performs one ES document write.

## What a request looks like
1. Kafka event arrives (Poisson at num_resellers × update_rate_per_reseller events/s).
2. Waits for a free processing worker slot.
3. Normalise + dedup + detect change (exponential, mean = processing_time_mean = 0.05 s).
4. Releases worker slot.
5. Waits for a free ES indexing connection.
6. ES document write (exponential, mean = es_indexing_time_mean = 0.15 s).
7. Releases ES connection. Item is now visible. Total elapsed time = pipeline latency.

## Workload
Poisson arrivals at rate = num_resellers × update_rate_per_reseller.
Default update_rate_per_reseller = 10.0 events/s (fast continuous crawl).
At 15 resellers (Year 1): 150 events/s. At 115 resellers (Year 5): 1150 events/s.
Sweep: num_resellers from 15 to 130, with num_workers swept as secondary variable.
Simulation duration: 600 s per configuration.

## How the system degrades under load
Two cascaded M/M/c queues (pure queueing theory). No USL degradation (alpha=beta=0):
processing is I/O-bound with no shared in-process memory state. The first pool
(workers) is the primary bottleneck when undersized; the ES indexing pool becomes
the ceiling when enough workers are provisioned.

## Backpressure and safety
SLA timeout: 10 seconds. Requests exceeding the SLA are counted as pipeline misses
(outcome = dropped_timeout, effective latency = 10 s). No admission cap by default.

## Lifecycle of a single request
1. arrive → append RequestRecord (arrival = env.now)
2. check admission cap (none by default)
3. acquire workers slot → rec.start = env.now
4. yield timeout(Exp(processing_time_mean))  — normalise + dedup + detect
5. release workers slot
6. acquire es_pool slot
7. yield timeout(Exp(es_indexing_time_mean))  — ES write
8. release es_pool slot
9. rec.outcome = "ok", rec.finish = env.now
(SLA timer wraps steps 3–9; interrupt on expiry → dropped_timeout)

## What the operator can dial
Workload:
  num_resellers           number of resellers crawled (sweep variable, default 15)
  update_rate_per_reseller  Kafka events/s per reseller (default 3.0)
  sim_time                simulation duration in seconds (default 600)
  seed                    random seed (default 42)
Work:
  processing_time_mean    mean worker service time in seconds (default 0.05)
  es_indexing_time_mean   mean ES write time in seconds (default 0.15)
Pools:
  num_workers             processing pool size (secondary sweep, default 10)
  es_pool_size            ES indexing connections (default 200)
Degradation (reserved):
  alpha                   USL linear coefficient (default 0.0)
  beta                    USL quadratic coefficient (default 0.0)
Backpressure:
  max_threads             admission cap; None = unlimited (default None)
  sla_seconds             pipeline SLA in seconds (default 10.0)

## What this model deliberately does not include
- Kafka consumer group rebalancing or replication lag
- ES shard routing, replica selection, or indexing refresh delay
- Deduplication as a separate resource (lumped into processing_time_mean)
- PostgreSQL canonical write (order of magnitude faster than ES write; never binds)
- Crawler cycle time (pages/hour per reseller) — only arrival rate to Kafka matters
- Cross-region Elasticsearch replication
- Failure, retry, and circuit-breaker behaviour
- Multiple request types (all events treated identically)

## What success looks like when running this model
Smoke test (num_resellers=15, num_workers=10, es_pool_size=200):
  arrival rate = 150 events/s; worker cap = 200/s; ES cap = 1333/s.
  success_rate ≈ 1.0, throughput ≈ 150/s, p95 latency well under 10 s.
Sweep validation:
  As num_resellers grows from 15 to 130, the minimum num_workers required to hold
  success_rate ≥ 0.99 should rise approximately linearly with arrival rate.
  A plot of (num_resellers, min_workers_at_SLA_boundary) must show a roughly straight
  line, confirming the M/M/c model correctly captures linear capacity scaling.
```

---

## MODEL.md — Model 2: User Query Pipeline

```
## What real system is being modelled
Single-region PowerSearch user query pipeline. Users send full-text or faceted search
requests. Search workers accept requests and issue Elasticsearch queries. The business
SLA is p95 response time < 500 ms, including during periodic burst episodes where
traffic briefly spikes to 5× the base rate.

## What is scarce / shared in this system
- Search worker pool (num_search_workers, primary sweep variable):
  each slot accepts a request and prepares + dispatches the ES query.
- Elasticsearch query connection pool (es_query_pool_size, default 100):
  each slot executes one search query against the index.

## What a request looks like
1. User search request arrives (Poisson base + square-wave burst modulation).
2. Waits for a free search worker slot.
3. Worker prepares and dispatches ES query (exponential, mean = search_time_mean = 0.02 s).
4. Releases search worker slot.
5. Waits for a free ES query connection.
6. ES executes query (exponential, mean = es_query_time_mean = 0.08 s).
7. Releases ES connection. Response returned to user.

## Workload
Base: Poisson arrivals at base_arrival_rate (default 100 req/s).
Burst: arrival rate switches to base_arrival_rate × burst_multiplier (default 5×)
for burst_duration (default 30 s) at the start of every burst_interval (default 120 s).
Implementation: square-wave modulation — arrival_process reads env.now % burst_interval
and picks the appropriate rate.
Sweep: base_arrival_rate from 10 to 300 req/s. Simulation duration: 600 s (≥ 5 burst
episodes per run to produce stable statistics).

## How the system degrades under load
Two cascaded M/M/c queues. Under base load the search worker pool is the primary
bottleneck; with enough workers the ES query pool becomes the ceiling. During burst
episodes both pools experience simultaneous pressure, and p95 SLA misses first appear
here. Effective latency (treating timed-out requests as 0.5 s) is the correct metric
for SLA compliance; raw latency of successful requests understates degradation during bursts.

## Backpressure and safety
SLA timeout: 0.5 seconds. Timed-out requests counted as dropped_timeout; their latency
is set to 0.5 s in effective latency calculations. No admission cap by default.

## Lifecycle of a single request
1. arrive → append RequestRecord
2. acquire search_workers slot → rec.start = env.now
3. yield timeout(Exp(search_time_mean))  — query preparation
4. release search_workers slot
5. acquire es_query_pool slot
6. yield timeout(Exp(es_query_time_mean))  — ES query execution
7. release es_query_pool slot
8. rec.outcome = "ok", rec.finish = env.now
(SLA timer wraps steps 2–8)

## What the operator can dial
Workload:
  base_arrival_rate       Poisson base rate in req/s (default 100.0)
  burst_multiplier        arrival rate multiplier during burst episodes (default 5.0)
  burst_duration          length of each burst episode in seconds (default 30.0)
  burst_interval          time between burst episode starts in seconds (default 120.0)
  sim_time                simulation duration in seconds (default 600)
  seed                    random seed (default 42)
Work:
  search_time_mean        mean worker preparation time in seconds (default 0.02)
  es_query_time_mean      mean ES query time in seconds (default 0.08)
Pools:
  num_search_workers      search worker pool size (primary sweep variable, default 25)
  es_query_pool_size      ES query connections (default 100)
Degradation (reserved):
  alpha                   USL linear coefficient (default 0.0)
  beta                    USL quadratic coefficient (default 0.0)
Backpressure:
  max_threads             admission cap; None = unlimited (default None)
  sla_seconds             p95 SLA threshold in seconds (default 0.5)

## What this model deliberately does not include
- CDN, SSR rendering, API Gateway (each adds < 5 ms; not a shared bottleneck)
- User authentication and session management (once per session, not per query)
- Product detail requests (different request type; separate model if needed)
- Multi-region routing (single region only)
- Elasticsearch shard routing or replica selection
- Result caching / hot vs cold query distinction (lumped into es_query_time_mean)
- Retry and circuit-breaker behaviour

## What success looks like when running this model
Smoke test (base_arrival_rate=100, num_search_workers=25, no burst):
  success_rate = 1.0, eff_latency_p95 well under 500 ms.
Sweep validation (three phases must appear as base_arrival_rate increases):
  1. Healthy: eff_p95 < SLA, success_rate ≈ 1.0.
  2. Knee: eff_p95 approaches 500 ms, small timeout count appears.
  3. Degraded: success_rate drops, eff_p95 ≥ SLA.
Burst validation: burst episodes must be visible as spikes in the latency trace.
The minimum num_search_workers to survive a 5× burst at a given base rate must be
higher than the workers needed to handle the base load alone.
```

---

## Implementation sequence (per skill phases 1–12)

Phases 1–3 are done (audit complete, M/M/c framework chosen, mechanisms listed).

### Model 1 — Ingestion

| Step | Action |
|---|---|
| 4 | Write `model1_ingestion/MODEL.md` from draft above |
| 4 | Write `model1_ingestion/server_sim.py` — Config + IngestionServer (workers + es_pool) + _serve (two sequential resource acquires) + arrival_process (Poisson) + run/summarize |
| 4 | Write `model1_ingestion/requirements.txt` (simpy, matplotlib, numpy) |
| 6 | Smoke test: `python server_sim.py` with num_resellers=15, num_workers=10. Verify success_rate=1.0, p95 well under 10 s |
| 6 | If not healthy, adjust defaults (not model logic) |
| 7 | Write `model1_ingestion/sweep.py` — 2D grid (num_resellers × num_workers), emit JSON results |
| 7 | Run sweep, verify curve: at fixed num_workers, increasing num_resellers eventually causes SLA misses |
| 8 | Confirm effective latency + success_rate columns are present (Phase 8 checklist) |
| 9 | Write `model1_ingestion/plot_sweep.py` — three-panel plot (throughput, success_rate, eff_p95 latency) with one curve per num_workers value, x-axis = num_resellers |
| 10 | Sync MODEL.md if any parameter changed during calibration |

### Model 2 — Queries

| Step | Action |
|---|---|
| 4 | Write `model2_queries/MODEL.md` from draft above |
| 4 | Write `model2_queries/server_sim.py` — Config + QueryServer (search_workers + es_query_pool) + _serve + burst-aware arrival_process (square-wave: `env.now % burst_interval < burst_duration`) |
| 4 | Write `model2_queries/requirements.txt` |
| 6 | Smoke test: base_arrival_rate=100, num_search_workers=25, no burst. success_rate=1.0, eff_p95 < 500 ms |
| 7 | Write `model2_queries/sweep.py` — sweep base_arrival_rate for several num_search_workers values |
| 7 | Validate three phases (healthy → knee → degraded) and visible burst spikes |
| 8 | Effective latency present; survivorship bias check: compare eff_p95 vs raw p95 during overload |
| 9 | Write `model2_queries/plot_sweep.py` — three-panel, x=base_arrival_rate, curve family=num_search_workers, shade burst intervals |
| 10 | Sync MODEL.md |

---

## Critical files (to modify or create)

- `examples/PowerSearch/model1_ingestion/server_sim.py` — new file from template
- `examples/PowerSearch/model1_ingestion/MODEL.md` — new file from draft
- `examples/PowerSearch/model2_queries/server_sim.py` — new file, adds burst arrival_process
- `examples/PowerSearch/model2_queries/MODEL.md` — new file from draft
- `skills/perf-simulation/templates/server_sim.py` — read-only reference (do not modify)
- `examples/USLDBmodel/server_sim.py` — read-only reference (copy pattern)

---

## Default parameters — rationale

**Model 1**
- `update_rate_per_reseller = 10.0` events/s: fast continuous crawl (10 K items / ~17 min).
  At 15 resellers: 150 events/s total. At 115 resellers: 1150 events/s.
- `processing_time_mean = 0.05` s: normalization + dedup is CPU-light; 50 ms is generous.
- `es_indexing_time_mean = 0.15` s: ES single-document indexing is typically 10–200 ms.
- `es_pool_size = 200` (raised from 50): at 115 resellers the ES pool needs ≥ 173 connections
  to avoid being the binding constraint; 200 gives headroom to observe both bottlenecks.
  At Year 1 (150 events/s) even es_pool_size=50 is fine (cap = 333 events/s).

**Model 2**
- `base_arrival_rate = 100.0` req/s: Year-5 peak for one region ≈ 1M users × 10 searches/day
  / 3 regions / 28800 peak-hour seconds × 3× peak factor ≈ 116 req/s.
- `search_time_mean = 0.02` s: query preparation (parse, build ES query) is fast.
- `es_query_time_mean = 0.08` s: Elasticsearch full-text query with facets, warm index.
- `burst_interval = 120` s, `burst_duration = 30` s: 25% burst duty cycle, 5 bursts per
  600-second simulation run — enough data to compute stable p95 within bursts.

---

## Verification end-to-end

1. `cd examples/PowerSearch/model1_ingestion && pip install -r requirements.txt`
2. `python server_sim.py` → smoke test output; success_rate should be 1.0
3. `python sweep.py` → JSON/CSV of results grid
4. `python plot_sweep.py` → three-panel PNG; verify curve shapes
5. Repeat steps 1–4 in `model2_queries/`
6. For Model 2 specifically: inspect that eff_p95 > raw_p95 under burst load (confirms survivorship bias is being captured)
