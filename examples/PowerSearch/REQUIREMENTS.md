# PowerSearch — Requirements

## What this system does

PowerSearch is a unified clothes price aggregator. It continuously crawls
well-known brand resellers, normalises their catalogues into a single search
index, and lets end-users find the best price or delivery option for any item.
Users are redirected to the reseller site to complete the purchase; no
transaction happens on the PowerSearch side.

The system has two subsystems that generate independent load and are therefore
modelled as two separate simulations:

- **Ingestion (Data Platform)** — crawler emits item-update event → Kafka →
  processing workers (normalise, deduplicate, detect change) → Elasticsearch.
- **User queries (User Platform)** — user search request → search workers →
  Elasticsearch query → response.

## Target scale

| Parameter | Year 1 | Year 5 |
|---|---|---|
| Resellers | 15 | 115 (+20/year) |
| Items per reseller | 10 000 | 10 000 |
| Total indexed items | 150 000 | 1 150 000 |
| Registered + anonymous users | — | 1 000 000 |
| Deployment | 3 regions (NA / EU / APAC) | same |

**Ingestion load.** Arrival rate = `num_resellers × update_rate_per_reseller`.
At Year 1 (15 resellers, continuous crawl): ≈ 150 events/s. At Year 5
(115 resellers): ≈ 1 150 events/s.

**Query load.** Per-region base ≈ 100 req/s (Year-5 peak: 1M users × ~10
searches/day / 3 regions / peak-hour seconds × peak factor). Periodic burst
episodes spike traffic to 5× the base rate for 30 s.

Each region is a full, independent stack; multi-region is symmetric scaling and
does not change the load shape within a region. Both models simulate a single
region.

## SLA

| Pipeline | SLA |
|---|---|
| Ingestion | A price change must be queryable within **10 seconds** of the crawler fetching the changed page (pipeline latency, measured within one region) |
| User query | **p95 response time < 500 ms**, including during 5× burst episodes |

## Questions this model must answer

**Ingestion pipeline:**

1. How many processing workers are required to meet the 10-second SLA as the
   reseller count grows from 15 to 115?
2. Which resource saturates first under load — the processing worker pool or the
   Elasticsearch indexing pool?

**User query pipeline:**

3. At what base load and burst multiplier does the system begin to miss the
   p95 < 500 ms SLA?
4. How many search workers are needed to absorb a 5× burst, beyond what the
   base load alone requires?

## Required behaviour

| Load condition | Expected outcome |
|---|---|
| Ingestion, Year 1 (≈ 150 events/s) | success_rate ≈ 1.0; p95 pipeline latency well under 10 s |
| Ingestion, growing resellers | min workers to hold success_rate ≥ 0.99 rises ≈ linearly with arrival rate |
| Query, base load, no burst | success_rate ≈ 1.0; effective p95 well under 500 ms |
| Query, rising base load | three regimes visible: healthy → knee (p95 approaches SLA) → degraded (success_rate drops) |
| Query, 5× burst | burst episodes visible as latency spikes; workers needed exceed base-load requirement |

## Sweep

**Ingestion:** primary `num_resellers` from 15 to 130 (Year 1 to beyond Year 5);
secondary `num_workers` (processing pool size). Simulation duration 600 s per
configuration.

**Queries:** primary `base_arrival_rate` from 10 to 300 req/s; secondary
`num_search_workers`. Periodic 5× burst (30 s every 120 s) superimposed on the
Poisson base. Simulation duration 600 s per configuration (≥ 5 burst episodes
per run).

## Out of scope for simulation

- CDN, SSR rendering (Next.js), API Gateway — each adds negligible latency and
  is not a shared contended resource
- User authentication and social login (once per session, not per query)
- Product detail requests (separate request type; separate model if needed)
- PostgreSQL canonical write on ingestion (order of magnitude faster than ES
  indexing; never the binding constraint)
- Deduplication as a separate resource (lumped into `processing_time_mean`)
- Result caching / hot vs cold query distinction (lumped into
  `es_query_time_mean`)
- Multi-region routing and DNS geo-routing (single-region simulation)
- Cross-region Elasticsearch replication (symmetric; does not change intra-region load)
- Zero-downtime mechanisms, failure handling, active-active topology
  (operational constraints; no effect on steady-state load shape)
- Retry and circuit-breaker behaviour
