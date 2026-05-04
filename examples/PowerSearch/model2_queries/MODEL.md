# PowerSearch User Query Pipeline — Model 2

> The intent of this document is to capture *modelling intent* in human prose
> so a reader does not have to reconstruct it from the code. If this description
> and the code disagree, this description is the specification and the code is
> the bug.

## What real system is being modelled

Single-region PowerSearch user query pipeline. Users send full-text or faceted
search requests. Search workers accept requests and issue Elasticsearch queries.
The business SLA is p95 response time < 500 ms, including during periodic burst
episodes where traffic spikes to 5× the base rate for 30 seconds.

## What is scarce / shared in this system

- **Search worker pool** (`num_search_workers`, primary sweep variable): each slot
  accepts a request, prepares, and dispatches the ES query, then releases.
  Corresponds to `simpy.Resource(capacity=num_search_workers)`.
- **Elasticsearch query connection pool** (`es_query_pool_size`, default 100): each
  slot executes one search query, then releases.
  Corresponds to `simpy.Resource(capacity=es_query_pool_size)`.

## What a request looks like

1. User search request arrives (Poisson base + square-wave burst modulation).
2. Waits for a free search worker slot.
3. Worker prepares and dispatches the ES query
   (exponential, mean = `search_time_mean` = 0.02 s).
4. Releases search worker slot.
5. Waits for a free ES query connection.
6. ES executes search (exponential, mean = `es_query_time_mean` = 0.08 s).
7. Releases ES connection. Response returned to user.
   Total elapsed time = response latency.

## Workload

Base Poisson arrivals at `base_arrival_rate` (default 100 req/s), with square-wave
burst modulation superimposed:

```
rate = base_arrival_rate × burst_multiplier   when  env.now % burst_interval < burst_duration
rate = base_arrival_rate                       otherwise
```

Default burst parameters: `burst_multiplier=5`, `burst_duration=30 s`,
`burst_interval=120 s` → 25% burst duty cycle, 5 burst episodes per 600 s run.

| Phase | Duration | Rate |
|---|---|---|
| Steady | 90 s | 100 req/s |
| Burst | 30 s | 500 req/s |

Sweep: `base_arrival_rate` from 10 to 300 req/s, with `num_search_workers` as the
curve family. Simulation duration: 600 s (≥ 5 burst episodes).

## How the system degrades under load

Two cascaded M/M/c queues. Under base load the search worker pool is the primary
bottleneck; with sufficient workers the ES query pool becomes the ceiling. During
burst episodes both pools experience simultaneous pressure: the burst rate of
500 req/s (at base = 100) requires ≥ 50 search workers to absorb without queueing.

Effective latency — treating timed-out requests as 0.5 s — is the correct SLA metric.
Raw latency of successful requests understates degradation during bursts because
successful requests are a biased sample (they completed; the slow ones timed out).

## Backpressure and safety

SLA timeout: 0.5 seconds (`sla_seconds=0.5`). Timed-out requests counted as
`dropped_timeout`; their contribution to effective latency is `sla_seconds`.
No admission cap (`max_threads=None`) by default.

## Lifecycle of a single request

1. Arrive → append `RequestRecord(arrival=env.now)`
2. Admission check (skipped when `max_threads=None`)
3. Acquire `search_workers` slot → `rec.start = env.now`
4. `yield timeout(Exp(search_time_mean))` — query preparation
5. Release `search_workers` slot
6. Acquire `es_query_pool` slot
7. `yield timeout(Exp(es_query_time_mean))` — ES query execution
8. Release `es_query_pool` slot
9. `rec.outcome = "ok"`, `rec.finish = env.now`

SLA timer wraps steps 3–9; interrupt on expiry → `dropped_timeout`.

## What the operator can dial

**Workload**
- `base_arrival_rate` — Poisson base rate in req/s (default 100.0)
- `burst_multiplier` — arrival rate multiplier during burst episodes (default 5.0)
- `burst_duration` — length of each burst episode in seconds (default 30.0)
- `burst_interval` — time between burst episode starts in seconds (default 120.0)
- `sim_time` — simulation duration in seconds (default 600)
- `seed` — random seed (default 42)

**Per-request work**
- `search_time_mean` — mean worker preparation time in seconds (default 0.02)
- `es_query_time_mean` — mean ES query time in seconds (default 0.08)

**Pools**
- `num_search_workers` — search worker pool size; primary sweep variable (default 25)
- `es_query_pool_size` — ES query connections (default 100)

**Degradation (reserved)**
- `alpha` — USL linear contention coefficient (default 0.0)
- `beta` — USL quadratic coherency coefficient (default 0.0)

**Backpressure**
- `max_threads` — admission cap; `None` = unlimited (default None)
- `sla_seconds` — response time SLA in seconds (default 0.5)

## What this model deliberately does not include

- CDN, SSR rendering, API Gateway (each adds < 5 ms; not a shared bottleneck)
- User authentication and session management (once per session, not per query)
- Product detail requests (different request type; separate model if needed)
- Multi-region routing (single region only)
- Elasticsearch shard routing or replica selection latency
- Result caching / hot vs cold query distinction (lumped into `es_query_time_mean`)
- Retry and circuit-breaker behaviour
- Burst arrival shape beyond square-wave (e.g., gradual ramp, stochastic spikes)

## What success looks like when running this model

**Smoke test** (`base_arrival_rate=100`, `num_search_workers=25`, `burst_multiplier=1.0`):
Expected: `success_rate ≈ 0.997`, `wait_mean ≈ 0.0`, `eff_latency_p95` ≈ 0.26 s — well under 500 ms.
The small fraction of timeouts (< 0.3%) are pure exponential-tail events: service time > 0.5 s
occasionally even with idle workers. Zero queueing confirms the system is not saturated.
Worker capacity = 25 / 0.02 s = 1 250 req/s >> 100 req/s base, so the 5× burst (500 req/s)
also absorbs with no visible queue at these default settings.
Three-phase degradation appears in the sweep at lower worker counts (10–20) or higher base rates.

**Sweep validation** — three phases must appear as `base_arrival_rate` increases:
1. **Healthy**: `eff_p95 < SLA`, `success_rate ≈ 1.0`
2. **Knee**: `eff_p95` approaches 500 ms, small `dropped_timeout` count appears
3. **Degraded**: `success_rate` drops, `eff_p95 ≥ SLA`

**Burst validation**: `eff_p95` must exceed `raw_p95` of successful requests under
burst load, confirming survivorship bias is correctly captured. The minimum
`num_search_workers` needed to pass SLA during bursts must be higher than what
suffices at base load alone.
