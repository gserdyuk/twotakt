# PowerSearch — Architecture v1

## What this system does

PowerSearch is a unified clothes price aggregator. It continuously crawls
well-known brand resellers, normalises their catalogues into a single search
index, and lets end-users find the best price or delivery option for any item.
Users are redirected to the reseller site to complete the purchase; no
transaction happens on the PowerSearch side.

## Scope and scale assumptions

| Parameter | Year 1 | Year 5 |
|---|---|---|
| Resellers | 15 | 115 (+20/year) |
| Items per reseller | 10 000 | 10 000 |
| Total indexed items | 150 000 | 1 150 000 |
| Registered + anonymous users | — | 1 000 000 |
| Deployment | 3 regions (NA / EU / APAC) | same |

## Two subsystems

### 1. Data Platform

Responsible for discovering price changes on reseller sites and making them
queryable within 10 seconds of the crawler fetching the changed page.

```
Reseller sites
      │
      ▼
 Crawler fleet  ──►  Kafka (regional)  ──►  Processing workers
 (continuous,                                    │
  hot-path)                               normalize + deduplicate
                                          detect price change
                                                 │
                                    ┌────────────┴────────────┐
                                    ▼                         ▼
                             Elasticsearch            PostgreSQL
                             (search index,           (canonical
                              cross-region             catalogue +
                              replicated)              reseller config)
```

**Crawler design.** Crawlers run continuously; there is no batch window. Each
crawler worker fetches a reseller page, parses the HTML, and emits an item-update
event to Kafka. The 10-second SLA is *pipeline latency*: the time from the
moment the crawler fetches the page to the moment the updated item is queryable
in Elasticsearch. Crawler cycle time (how often each page is re-visited) is a
fleet-sizing concern outside the pipeline SLA.

**Integration mode.** Crawler-only. No push API from resellers, no pull API.
All three Connector types (push / pull / crawl) discussed during design were
eliminated in favour of a single uniform crawler path to reduce operational
complexity.

**Agile configuration.** All reseller-specific parameters — site URL, CSS
selectors for price and item fields, crawl rate limits, authentication if
required — are stored as records in PostgreSQL, not in code. Adding or
reconfiguring a reseller requires only a database record change; no code
deployment is needed.

**Processing workers** form a horizontally scalable pool. Each worker:
1. Reads one item-update event from Kafka.
2. Normalises the reseller-specific schema to the unified product schema.
3. Deduplicates against existing catalogue records.
4. Detects whether price or availability changed.
5. Writes the updated document to Elasticsearch and the canonical record to
   PostgreSQL.

### 2. User Platform

Serves end-users with search, product detail, and price comparison. Does not
include real-time price-push to connected clients (removed to reduce scope).

```
CDN  ──►  SSR Web App (Next.js, responsive: mobile / tablet / desktop)
                │
                ▼
          API Gateway  (routing, rate limiting, auth)
           │        │         │
     Search      Product    User
     Service     Service    Service
        │           │       (social login:
        ▼           ▼        Facebook / Twitter)
  Elasticsearch  PostgreSQL
  (search index)  replica
```

**Search** is backed by Elasticsearch with full-text and faceted filtering
(brand, category, size, price range, reseller).

**Product detail** returns the current price from all resellers for an item,
sourced from PostgreSQL (canonical) and optionally a Redis cache for the
hottest items. Users click through to the reseller site directly.

**User accounts** are optional. Anonymous browsing is supported. Registered
users can save favourites and receive email alerts. Social login via Facebook
and Twitter/X uses OAuth 2.0.

## Multi-region deployment (3 regions)

Each region is a full, independent stack: crawler fleet, Kafka, processing
workers, Elasticsearch shard, PostgreSQL replica, and user-facing API tier.
Users are routed to their nearest region by DNS geo-routing.

**Crawlers are regional.** Each region crawls the resellers geographically
closest to it, reducing network round-trip time to target sites and respecting
geo-blocking rules.

**Elasticsearch** uses cross-region replication: one primary cluster writes,
two replica clusters serve reads. Replication lag is an accepted trade-off;
it does not affect the 10-second SLA definition, which is measured within a
single region.

**Failure handling.** If a region becomes unavailable, DNS geo-routing shifts
its traffic to the next nearest region. Regions are active-active; no region
is a cold standby.

## Zero downtime

Zero downtime is an operational constraint, not a load characteristic, so it
has no effect on either simulation model. The mechanisms are:

- Kubernetes rolling deployments with `maxUnavailable=0` and readiness probes.
- Graceful shutdown: pods drain in-flight work before terminating; Kafka
  ensures no events are lost during crawler restarts.
- Expand-contract database migrations: schema changes are additive before any
  code is deployed that depends on them.

## What is explicitly out of scope (v1)

- Real-time price-push to connected browser sessions (WebSocket / SSE).
- Push or pull API integration modes (crawler-only is the integration path).
- Transaction processing (checkout happens on the reseller site).
- Personalisation, recommendations, or ML ranking.
- Price history analytics beyond detecting whether a price changed.

## Simplified model

For load-testing and capacity planning, most architectural elements do not
affect arrival rates, queue depths, service times, or SLA outcomes. The table
below records what is kept and what is dropped, and why.

### Removed from the model

| Element | Reason for removal |
|---|---|
| CDN | Serves static assets; never touches the API or ingestion path |
| SSR rendering (Next.js) | Per-request client-side cost, not a shared contended resource |
| API Gateway | Near-zero latency pass-through; rate limiting not the studied bottleneck |
| User Service / social login | Auth is once-per-session; negligible share of total requests |
| Product Service + PostgreSQL replica | Separate request type (item detail); not part of search throughput |
| PostgreSQL canonical write (ingestion) | PG write is an order of magnitude faster than ES indexing; never the binding constraint |
| Deduplication step | Internal to the processing worker; lumped into `processing_time_mean` |
| Cross-region Elasticsearch replication | Single-region simulation; replication is symmetric and does not change intra-region load shape |
| DNS geo-routing | Determines which region a user hits, not what happens inside a region |
| Agile configuration DB reads | Read once at crawler startup; negligible share of total load |
| Zero downtime mechanisms | Operational constraint; no effect on arrival rates or service times |
| Failure handling / active-active topology | HA design; does not change steady-state load shape within a region |

### Kept in the model

| Element | Why it stays |
|---|---|
| Crawler fleet | Source of all ingestion load; arrival rate = `num_resellers × update_rate_per_reseller` |
| Kafka queue | Buffer between crawlers and workers; queue depth is the leading indicator that the SLA is at risk |
| Processing worker pool | First bounded resource in the ingestion path; primary sweep variable |
| Elasticsearch indexing pool | Second bounded resource; determines the system capacity ceiling when workers are sufficient |
| User arrivals (base + burst) | Source of all query load; burst shape drives the interesting failure modes |
| Search worker pool | First bounded resource in the query path; sweep variable for Model 2 |
| Elasticsearch query pool | Second bounded resource; becomes the ceiling once enough search workers are provisioned |

### Resulting model structures

Both models reduce to two cascaded bounded resource pools — the same
structure as `USLDBmodel`.

**Model 1 — Ingestion pipeline:**
```
Crawlers → [Kafka buffer] → Processing workers → ES indexing pool → item visible
                             pool, sweep this      pool, bounded      SLA: 10 s
```

**Model 2 — User query pipeline:**
```
User arrivals (Poisson + burst) → Search workers → ES query pool → response
                                   pool, sweep this  pool, bounded   SLA: p95 < 500 ms
```

## Simulation models

Two SimPy models will be built against this architecture. Each simulates a
single region; multi-region is symmetric scaling and does not change the load
shape within a region.

### Model 1 — Ingestion pipeline

Models the path: crawler emits event → Kafka buffer → processing workers →
Elasticsearch indexing pool → item visible.

**Sweep variable:** `num_resellers` from 15 to 130 (year 1 to beyond year 5).
**Secondary variable:** `num_workers` (processing pool size).
**SLA:** 10 seconds end-to-end within the pipeline.
**Key question:** How many processing workers are required to meet the 10-second
SLA as the reseller count grows from 15 to 115?

### Model 2 — User query pipeline

Models the path: user search request → API Gateway → Search Service →
Elasticsearch query pool → response.

**Sweep variable:** arrival rate, with periodic burst episodes (5× base rate
for 30 seconds) superimposed on a steady Poisson base.
**SLA:** p95 response time < 500 ms.
**Key question:** At what burst multiplier and base load does the system begin
to miss the p95 SLA, and how many search workers are needed to absorb the burst?
