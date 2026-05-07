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

**Variant — M/D/c (deterministic service time):** replace the
exponential service draw with `yield env.timeout(constant)`. Reduces
variance; the knee shifts slightly right versus M/M/c at the same mean.
Use when service time is tightly bounded (e.g. a fixed-duration batch step).
*(Source: ccfelius/queueing MDN.py, yinchi/simpy-examples ex06_mdkk.py)*

## Priority queue (PriorityResource)

**Phenomenon captured:** shorter (or higher-priority) jobs are served
first, reducing mean latency for the priority class at the expense of
lower-priority requests.

**Implementation in SimPy:** `simpy.PriorityResource(env, capacity=c)`.
Pass `priority=` to each `request()` call (lower value = higher
priority). Shortest-Job-First: pass estimated service time as priority.

**Use when:** the audit identifies multiple request classes with
different SLAs or costs, or when SJF dispatch is a plausible policy.

*(Source: ccfelius/queueing MM1_SJ.py — SJF via PriorityResource)*

## Universal Scalability Law (USL)

**Applies to CPU-bound systems only.** If workers are I/O-bound
(waiting on network / DB / disk), set alpha=beta=0 — the formula
collapses to M/M/c and the degradation call in `_serve` is dead code.
Confirm this in audit Q5 before choosing USL.

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

**Variant — M/M/k/k (no queue, immediate drop):** when all c slots
are busy, new arrivals are rejected rather than queued. Check
`resource.capacity == len(resource.users)` before `request()`; if
true, increment a drop counter and return without acquiring.
Use for real-time or stateless services where queuing is unacceptable.
*(Source: yinchi/simpy-examples ex04_mmkk.py)*

## Cache hit / miss (bimodal duration)

Each request's duration is drawn from a mixture: with probability
p_hit, fast (cache hit); otherwise slow (cache miss). Captures the
"vertical bar" appearance in latency histograms that real services
exhibit. Implementation: `random.random() < p_hit` choose between
two distributions.

## Abandonment / customer impatience

**Phenomenon captured:** a request that has been waiting in queue
voluntarily cancels after a patience timeout — *before* a server slot
is acquired. Distinct from SLA timeout (which fires during service).

**Implementation in SimPy:**

    req = resource.request()
    result = yield req | env.timeout(patience)
    if req not in result:
        resource.release(req)   # cancel the pending request
        record.outcome = "abandoned"
        return

Abandonment is self-limiting: as load grows, more callers give up,
which keeps the active count lower. This can mask true saturation —
the server looks healthy while many callers are silently failing.
Always track abandonment rate alongside success rate.

*(Source: yinchi/simpy-examples ex03_mmk_abandonment.py)*

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
