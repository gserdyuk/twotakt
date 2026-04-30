# Theory Glossary

A short reference for the queueing and scaling laws this skill
supports. Use this in Phase 2 to choose the framework that matches
the mechanisms identified in Phase 3.

The general principle: pick the **simplest** law whose phenomenology
covers what you want to show. A more complex law that you cannot
parameterize confidently is worse than a simpler one whose limits you
understand.

## M/M/1 — single-server queue

**Phenomenon captured:** queueing delay rising hyperbolically as
utilization approaches 1.

**Formula (mean time in system):**

    T = (1/μ) / (1 - ρ)        where  ρ = λ/μ

λ = arrival rate, μ = service rate. ρ is utilization.

**What it does NOT capture:** thrashing past saturation. M/M/1
asymptotically maxes out at throughput = μ; it never *declines*
beyond that. Real systems do.

**Implementation in SimPy:** `simpy.Resource(env, capacity=1)`,
service time drawn from any distribution, requests acquire and
release the resource. The hyperbolic latency curve appears
automatically.

**Use when:** the only effect you want to show is "queues build up
near saturation". Often a fine baseline before adding USL.

## M/M/c — c-server queue

Generalization to c parallel servers. Same shape of curve, but
saturation at λ = cμ instead of λ = μ.

**Implementation:** `simpy.Resource(env, capacity=c)`. Use for thread
pools, worker pools, connection pools where the only relevant effect
is bounded concurrency.

## Universal Scalability Law (USL)

**Phenomenon captured:** the realistic throughput curve — rises,
peaks, then **declines** as concurrency grows. M/M/c cannot do this.

**Formula (relative throughput at concurrency N):**

    X(N) = N · X(1) / (1 + α(N-1) + β·N·(N-1))

α = linear contention coefficient (Amdahl-style serialization,
context-switch overhead, basic locking).

β = quadratic coherency coefficient (cache coherency traffic, lock
convoys, GC pressure, anything that grows like N²).

For latency modelling, the convenient inversion is to multiply the
**effective service time** by `1 + α(N-1) + β·N·(N-1)`, where N is
the number of currently in-flight requests.

**Use when:** the user wants the model to reproduce the thrashing
zone past saturation, or wants to investigate "why does throughput
*decrease* under heavy load?" Set β = 0 to recover an Amdahl-only
model; set α = β = 0 to recover M/M/1.

**Implementation in SimPy:** apply the multiplier inside the CPU /
shared-resource hold time, evaluated at the current count of
in-flight requests.

## Poisson arrivals

The default workload model. Inter-arrival times are exponentially
distributed with mean 1/λ. In SimPy:

    yield env.timeout(random.expovariate(rate))

Use this unless the user explicitly says the workload is bursty,
periodic, or driven by some other process.

## Connection pool / bounded resource

Conceptually an M/M/c queue, but the value is in modelling
**exhaustion**: when all c slots are in use, new requests either
queue or are rejected. SimPy's `Resource(capacity=c)` already
implements the queueing variant. For the rejection variant, check
`len(resource.queue) >= max_buffer` before requesting.

## Cache hit / miss (bimodal duration)

Each request's duration is drawn from a mixture: with probability
p_hit, fast (cache hit); otherwise slow (cache miss). Captures the
"vertical bar" appearance in latency histograms that real services
exhibit. Implementation: `random.random() < p_hit` choose between
two distributions.

## SLA timeout (deadline)

Not a degradation law per se, but a measurement and backpressure
mechanism. A request that does not finish within `sla_seconds` is
killed. In SimPy:

    result = yield inner_process | env.timeout(sla)
    if inner_process not in result:
        inner_process.interrupt()

The SLA changes both the success rate (some requests now fail
explicitly) and the effective latency distribution (timed-out
requests have known latency = SLA).

## How the laws compose

These laws are usually combined, not picked one-of:

- USL on a CPU resource + connection pool + SLA timeout = the
  baseline web server model.
- M/M/1 on a single shared lock + USL on the worker pool = a
  coordination-bound service.
- Cache hit/miss on top of any of the above adds bimodality.

Each composition step is its own modelling decision. Justify each in
MODEL.md.
