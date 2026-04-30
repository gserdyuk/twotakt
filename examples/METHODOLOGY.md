# Methodology: Building SimPy Models of Server Degradation

This document captures the step-by-step approach used to build the
`USLmodel` and `USLDBmodel` examples. The goal is to make the *process*
reproducible — when adding a new component (cache, replica, scheduler,
etc.) the next person should follow the same steps in the same order.

The principle: **each step has a deliverable that must be honest before
the next step is allowed to start.** No premature optimization, no
unmotivated knobs.

---

## Step 1. Identify entities before writing code

Map the real system onto SimPy primitives before touching the keyboard.
For our scenario the mapping was:

- **Environment** — virtual clock, one per simulation.
- **Process** — anything that has duration. The arrival generator is one
  long-running process; each request is a short-lived process. Modeling
  a request *as* a process (not as a passive record sitting in a queue)
  is what makes the body of a request read like its real life:
  acquire something → do work → release.
- **Resource** — anything scarce and shared. CPU is a resource. A
  connection pool is a resource. Anything with a bounded capacity that
  multiple processes compete for.
- **Store / Container** — usually *not* needed. A `Resource` already
  manages its own FIFO queue. Reach for `Store` only when the queue
  semantics differ (priorities, bounded buffer with drops, custom
  selection).

If you cannot name the SimPy primitive for each part of the system,
you are not ready to write code.

## Step 2. Pick the analytical model before the code model

A simulation is only as honest as the math behind it. For server
degradation the relevant body of theory is small:

- **M/M/1 queue** — gives the classic hyperbolic latency curve as
  utilization approaches 1. It captures *queueing*, nothing else. A
  pure M/M/1 system never degrades below saturation throughput.
- **Universal Scalability Law (USL)** — adds two coefficients:
  α (linear, for contention / Amdahl-style serialization) and β
  (quadratic, for coherency / cache / lock interaction). USL predicts
  the **rise–peak–decline** throughput curve that real servers
  exhibit. M/M/1 cannot do this.

Decide which effect you want the model to reproduce. We chose USL
because it captures the realistic "thrashing zone" past saturation.

## Step 3. Decompose real behaviour into orthogonal effects

Before writing the degradation function, list the mechanisms it should
encode and the order of their growth in N (concurrent threads):

| Mechanism                     | Order   |
|------------------------------|---------|
| CPU time-sharing             | linear  |
| Context-switch overhead      | linear  |
| Lock / cache-line contention | quadratic |
| GC pauses, memory pressure   | non-linear bursts |
| I/O                           | independent of N (until its own limit) |

The USL multiplier `1 + α(N−1) + β·N·(N−1)` is the smallest expression
that covers both the linear and quadratic growth terms. That is enough
for the first iteration.

## Step 4. Build the minimum viable model

Implement only what Steps 1–3 demanded. For our case:

1. CPU as `Resource(capacity=1)`.
2. Each request = a sequence of `(CPU burst, IO wait)` phases.
   During the CPU burst the process holds the resource; during IO it
   releases it (matching how a real thread releases the core during
   `epoll_wait` or disk I/O).
3. The CPU burst time is multiplied by the USL factor evaluated at the
   current number of in-flight requests.

Resist the urge to add features (priorities, preemption, retries) here.

## Step 5. Parameterize everything

Every magic number becomes a field on a `Config` dataclass: arrival
rate, simulation duration, phase count, burst means, α and β, and any
optional features (SLA timeout, thread cap). This is what makes the
model usable for sweeps later. No constants in function bodies.

## Step 6. Record per-entity data

Define a `RequestRecord` per arriving request: arrival time, start
time, finish time, outcome (`ok` / `dropped_buffer` / `dropped_timeout`).
Keep them in a list. Aggregate later — don't aggregate while the
simulation is running. This separation is what makes the metric
revisions in Step 9 cheap.

## Step 7. Smoke test, then sanity-check the defaults

Run once. If the smoke test shows the system already in a pathological
state under the default config, the defaults are wrong — pick numbers
that produce a healthy baseline (utilisation around 0.4–0.5). The
defaults should demonstrate the model *works*, not stress-test it.

## Step 8. Validate against theory before trusting

Run a small sweep across arrival rates and check the curve against
expectations: with USL it must rise, peak, then decline. If it only
saturates flat, the β term is doing nothing and the model has degraded
to M/M/1 — debug before going further.

## Step 9. Question your metrics, especially under overload

Latency-of-successful-requests is *not* a safe metric beyond saturation.
Successful requests under overload are a biased sample — those that
happened to hit a brief lull when many neighbours had just timed out.
Add **effective latency** (count timeouts as SLA seconds) and
**success rate** (fraction of requests that completed). Plot both the
honest and the biased latency together so the gap is visible.

## Step 10. Visualize in panels, not single curves

A throughput chart alone hides the failure mode. The minimum useful
plot is three stacked panels sharing an x-axis: throughput, success
rate, latency. The relationships only become legible when seen
together.

## Step 11. Extend by composition, not rewrite

When adding a new component (database, cache, downstream service),
**copy the project to a new folder** rather than editing the existing
one. Each example stays a clean exhibit of one idea. The change inside
that copy is small and surgical:

- Add new `Config` fields for the component's parameters.
- Add a new `Resource` (or whatever primitive Step 1 selected) on the
  `Server`.
- Add a new phase or wrap an existing phase with the new
  acquire/release.

`USLDBmodel` was built from `USLmodel` exactly this way: one new
resource (`self.db`), two new config fields (`db_pool_size`,
`db_query_mean`), and one new acquire–hold–release block at the end of
`_serve`. Nothing else changed.

## Step 12. Explore the parameter space, then write down what you saw

After the new model exists, sweep the parameter that defines the new
component (e.g. `db_pool_size = 1, 2, 4, 8`). Save the resulting plots
side-by-side (`sweep.png`, `sweep_2.png`, ...). The interesting result
is usually not "did it work" but "where does the bottleneck shift."

---

## Recurring anti-patterns to avoid

- **Writing code before the analytical model is chosen.** You will
  encode whatever degradation the implementation accidentally produces,
  not the one you intended.
- **Adding features the smoke test does not need.** Priorities,
  preemption, retries — defer until a sweep proves they matter.
- **Trusting latency-of-successes under overload.** This will lie to
  you; always plot it next to success rate.
- **Editing an existing example to add a new component.** Each example
  should illustrate one idea cleanly. Copy and extend instead.
- **Hard-coded numbers in function bodies.** Every knob belongs in
  `Config`.
