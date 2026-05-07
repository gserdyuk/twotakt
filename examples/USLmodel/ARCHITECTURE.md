# USLmodel — Architecture

## System

A CPU-bound HTTP server with **thread-per-request** architecture. Each
incoming request spawns a dedicated OS thread that runs the request to
completion and then exits. There is no application-level queue.

The server has **one CPU**. This simplification is deliberate — it makes
contention visible without multi-core scheduling complexity. Generalizing
to N cores is a one-line change but does not change the essential dynamics.

## Components

| Component | Role | Instances |
|---|---|---|
| CPU | Shared compute resource; only one thread executes at a time | 1 |
| OS thread | One per in-flight request; competes for CPU | 0…N (dynamic) |

## Signal flow

Each thread alternates between two kinds of work:

- **CPU burst** — running application code. Only one thread can use the CPU
  at a time; others queue implicitly via OS scheduling.
- **I/O wait** — waiting for network or disk. The CPU is *released* during
  this phase; other threads can run. I/O subsystems are not a shared
  bottleneck at the volumes considered here.

```
Request arrives
    → [admission control]
    → thread spawned
    → for each phase:
          CPU burst  (exclusive CPU access)
          I/O wait   (CPU released)
    → thread exits, response returned
```

## Control flow

- **Admission control:** optional cap on in-flight threads. Requests arriving
  when the cap is exceeded are rejected immediately ("503-style" drop).
- **SLA timeout:** optional per-request deadline. If elapsed time exceeds the
  SLA before the last phase completes, the thread is interrupted and the
  request is counted as a timeout.

## Degradation mechanism

Past a certain number of concurrent in-flight threads, **each unit of work
becomes slower**. The causes:
- Context-switch overhead (linear in N)
- Cache coherency traffic and lock contention (quadratic in N)
- Memory pressure and GC pauses

This is the **Universal Scalability Law** phenomenon — a property of the real
system, not a modelling choice. The consequence is a characteristic
rise–peak–decline throughput curve: throughput grows, peaks, then *falls* as
load increases further.

## Why thread-per-request and not an event loop

Thread-per-request exposes degradation most dramatically: every additional
in-flight request is an additional OS thread, an additional set of stack
pages, and an additional participant in CPU scheduling and lock contention.
An event loop or fiber-based runtime has a gentler degradation curve.
Thread-per-request remains a common deployment pattern and serves as a
clear worst-case scenario for contention analysis.
