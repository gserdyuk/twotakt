# USLmodel — what this model represents

This document describes the *intent* of the model. The code in
`server_sim.py` is a faithful encoding of what is described here, but a
reader should not have to read the code to understand the modelling
choices. If the description below and the code disagree, the description
is the specification and the code is the bug.

## What real system is being modelled

A single web server that handles incoming requests in a
**thread-per-request** style. Each arriving request is handed to its
own physical thread which runs the request to completion and then
exits. There is no application-level queue; the only queueing happens
implicitly as threads compete for shared resources.

The server has **one CPU**. The simplification to a single core is
deliberate — it makes the contention story visible without obscuring it
with multi-core scheduling. Generalizing to N cores is a one-line
change but changes nothing essential about the dynamics.

Each thread alternates between two kinds of work:

1. **CPU bursts** — running application code on the core. While a
   thread is executing CPU work, no other thread can use the CPU at
   the same time. Multiple CPU-hungry threads compete for the single
   core, and the operating system time-slices between them.
2. **I/O waits** — waiting for the network or disk to return. While a
   thread is in an I/O wait, the CPU is *released* and other threads
   can run on it. The I/O subsystems (NIC, SSD) are not modelled as
   scarce — every thread can wait for I/O simultaneously without
   interfering with anyone else's I/O. This is deliberately
   optimistic, but it is also realistic for modern SSDs and network
   stacks at the volumes we care about.

Each request consists of a configurable number of `(CPU, IO)` phase
pairs. Two phases roughly approximates "parse request → call backend →
render response" without committing to a specific shape.

## Why thread-per-request and not an event loop

Thread-per-request is the model where degradation under load is most
dramatic and easiest to reason about: every additional in-flight
request is an additional OS thread, an additional set of stack pages,
an additional participant in CPU scheduling and lock contention. An
event loop or a fiber-based runtime would have a different — usually
gentler — degradation curve. We chose the harsher model because it
exposes the failure modes most clearly and because it remains a common
deployment pattern in real services.

## How the server degrades

A real server does not just queue requests up to its theoretical
saturation point and then refuse new work. Past a certain
concentration of in-flight threads, **each unit of work itself becomes
slower** — context switches multiply, caches start missing, locks are
held longer, the garbage collector (where applicable) pauses more
often. We capture this with the **Universal Scalability Law**: the
effective duration of a CPU burst is multiplied by

    1 + α·(N − 1) + β·N·(N − 1)

where N is the number of currently in-flight requests in the system,
α captures linear contention (Amdahl-style serialization, context
switches), and β captures the quadratic effect of inter-thread
interference (cache coherency traffic, lock convoys).

The consequence is the characteristic USL **rise–peak–decline**
throughput curve: as offered load increases the server initially keeps
up, then plateaus, then *the throughput actually falls* because every
extra in-flight thread makes every other thread slower.
This is the real-world phenomenon a pure M/M/1 queue cannot reproduce.

I/O time is **not** subject to this multiplier. I/O happens off-CPU
and does not contribute to thread-on-thread interference in our
abstraction.

## Lifecycle of a single request

1. The request arrives at a Poisson-distributed instant.
2. Admission control: if a thread cap is configured and is currently
   exceeded, the request is rejected immediately (a "503"-style
   `dropped_buffer` outcome). Otherwise a thread is created.
3. The thread performs its sequence of phases. Each CPU burst stalls
   on the CPU resource until it is its turn, then runs for
   *base_burst × USL_multiplier(N)* simulated seconds. Each I/O wait
   simply elapses simulated time without holding the CPU.
4. The whole request is wrapped in an optional SLA deadline. If the
   wall-clock time from arrival exceeds the SLA before the last phase
   finishes, the request is killed (`dropped_timeout` outcome) and the
   thread is interrupted cleanly.
5. On normal completion (`ok` outcome) the thread exits.

## What the operator can dial

- **Workload shape**: arrival rate, number of phases per request, mean
  CPU and I/O durations.
- **Degradation character**: α (linear) and β (quadratic). Setting
  both to zero recovers the pure M/M/1 model and serves as a useful
  baseline.
- **Backpressure**: optional cap on in-flight threads (admission
  control) and optional per-request SLA deadline.

## What this model deliberately does not include

- Multiple cores.
- Heterogeneous request types (everything is drawn from the same
  distributions).
- A separate application-level request queue or load balancer.
- Memory pressure and OOM, modelled as a hard event.
- Garbage collection as discrete pauses.
- Network or disk capacity limits.
- Anything downstream of the server (database, cache, downstream
  service) — this is what `USLDBmodel` adds.

These omissions are not because they don't matter; they are because
this model is the **smallest** thing that already shows the central
phenomenon (USL-shaped degradation). Each additional concern belongs in
its own derived model so it can be examined in isolation.

## What success looks like when running this model

The smoke-test config (defaults) should produce a healthy baseline:
throughput equal to arrival rate, latency p50 close to the sum of CPU
and I/O means, p99 within a small multiple, no drops. A sweep over
arrival rate should show three regimes: a linear scaling region, a
saturation knee, and a thrashing region where throughput *falls* and
the system loses requests to SLA timeouts. If any of these three
regions is missing, the model is mis-tuned, not the theory.
