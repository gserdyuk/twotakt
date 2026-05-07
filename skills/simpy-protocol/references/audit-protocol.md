# Phase 1 — Audit Protocol

The audit produces a draft `MODEL.md` — the compiled form of the
system's architecture and requirements, structured for simulation.

## Why ТЗ and Architecture are required

The questions Q1–Q8 below need answers. The expected source of those
answers is two documents the user brings:

**ТЗ (technical requirements)** — answers the *why*: performance targets,
SLA thresholds, capacity goals, operational constraints. Primary source
for Q4 (workload), Q8 (success criteria).

**Architecture** — answers the *what*: components, resources, topology,
request lifecycle, backpressure mechanisms. Primary source for Q1, Q2,
Q3, Q5, Q6.

**Before starting Q1–Q8:** ask the user to provide both documents (or
point to their location in the project directory). Scan the project for
existing docs: ARCHITECTURE.md, README, design docs, ADRs — real projects
accumulate specs.

If answers to Q1–Q8 are already present in the documents:
1. Read and cite the relevant sections.
2. Present them as draft answers.
3. Ask the user to confirm or correct — not to answer from scratch.
Only ask a question from scratch if the answer is genuinely absent.

**If Architecture does not exist:** do not proceed without it. Two options:
- Stop and ask the user to produce an architecture document first.
- Offer to draft a minimal architecture together in this session based
  on the ТЗ — then treat that draft as the Architecture input and
  document it explicitly before continuing.

In either case: the architecture must be explicit and confirmed before
Q1–Q8 can be answered reliably.

After all questions are answered, write the draft `MODEL.md` (use
`templates/MODEL.md` as the form) and present it to the user for
confirmation. Do not proceed to Phase 2 until the user has approved
the draft, even if they signal eagerness to "just write the code".

## The questions

### Q1 — What real system is being modelled?

Get a one-paragraph description of the actual thing. Not the
SimPy primitives, not the math — the real system. "A web server",
"a payment processor", "a job scheduler". If the user is fuzzy here,
press for specifics: which component, which deployment, which traffic
pattern.

The answer goes in MODEL.md under "What real system is being
modelled".

### Q2 — What is scarce / shared / contended in this system?

For each scarce thing, also ask: how much of it is there? CPU cores?
Worker threads? Memory? Connection slots? Disk bandwidth? Network
sockets? Database connections?

This list will become the `simpy.Resource` instances in the code. If
the user names something that is not really scarce (e.g. RAM in a
small-data system), challenge it — adding a Resource that never
becomes the bottleneck is wasted modelling complexity.

### Q3 — What does a single request / unit of work look like?

Get the lifecycle. Does it use CPU? Wait for I/O? Call downstream
services? In what order? How many phases? How long does each phase
take on average?

This becomes the `_serve` method's structure.

### Q4 — What is the workload shape?

Arrival rate? Constant or bursty? Poisson is the safe default unless
the user has a reason otherwise. What load range do they want to
explore in sweeps? (This sets the smoke-test default and the sweep
range.)

**Q4a — Burst modulation.** Is there a periodic burst pattern? If yes:
multiplier, duration, interval, shape (square-wave / ramp / stochastic spike).
Square-wave is the safe default for "prime-time" or "marketing burst" scenarios.

**Q4b — Sweep dimensionality.** How many parameters need to be swept
independently?

- **1D sweep** (default): vary arrival rate, hold all else constant.
  Use `templates/sweep.py`. Runtime scales linearly.
- **2D sweep**: vary two parameters independently, e.g. arrival rate ×
  number of workers. Use `templates/sweep_2d.py`. Runtime scales as
  `|dim1| × |dim2| × seeds` — warn the user that a 10×7×3 grid is
  210 simulation runs. Choose grid sizes deliberately.
- **3D and beyond**: almost never justified. Each added dimension
  multiplies runtime. Prefer fixing secondary parameters at a few
  representative values and running multiple 2D sweeps.

**Q4c — Multiple arrival streams.** Are there meaningfully different
request classes (reads vs writes, premium vs best-effort, different
tenant types)? If yes: do the classes share the same resource path,
or does each need separate pools? Can they collapse to one stream
with a mixed service-time distribution?

Use separate arrival generators only when the classes have different
resource paths or SLAs that the audit says matter. Pattern: parallel
`env.process(arrival_process_A(...))` + `env.process(arrival_process_B(...))`
sharing the same `Resource`. For most systems one stream is sufficient.
*(Source: yinchi/simpy-examples ex09_mmc_two_priorities.py, ex10_mmc_two_classes.py)*

### Q5 — What kinds of degradation do they want the model to encode?

**First: are the workers CPU-bound or I/O-bound?**
- **I/O-bound** (waiting on network, DB, disk): USL does not apply. Set
  alpha=beta=0 and remove the `degradation_multiplier` call from `_serve`.
  M/M/c is the correct model. Skip the list below.
- **CPU-bound** (compute, in-process lock contention, cache coherency):
  USL applies. Continue with the list below.

For CPU-bound workers, walk through the list and for each ask whether
it is in scope:

- **CPU time-sharing** under N concurrent threads
- **Context-switch overhead** growing with N
- **Lock or cache-coherency contention** (quadratic in N)
- **Memory pressure / GC pauses**
- **Disk or network saturation**
- **Connection pool exhaustion**
- **Cache hit rate dropping under load**
- **Lock convoys on hot keys**

For each "yes", note its order of growth (linear, quadratic,
threshold). The collection of "yes" answers determines the
theoretical framework in Phase 2.

### Q6 — What backpressure / safety mechanisms exist?

SLA / per-request timeout? Maximum in-flight cap? Admission control?
Retry on failure? Circuit breaker? Queue size limit?

These become optional features on `Config` (`sla_seconds`,
`max_threads`, etc.). Default to "off" unless the audit says otherwise.

### Q7 — What does the user explicitly want to leave OUT of scope?

This is just as important as what is in scope. A model with an
honest "what we deliberately do not include" section is far more
trustworthy than one that pretends to be comprehensive.

Examples of common omissions: multiple cores, heterogeneous request
types, network/disk capacity limits, GC as discrete events,
downstream services. Write these into MODEL.md verbatim.

### Q8 — What does success look like?

What sweep, what plot, what observed behaviour would convince the
user the model is doing its job? "Three regimes visible: linear,
saturation knee, decline" is a typical answer for USL. "Latency
hyperbola climbing as utilization approaches 1" is typical for M/M/1.

Write this as the "What success looks like" section of MODEL.md. It
becomes the validation criterion for Phase 7 (V&V).

**Smoke test floor:** when setting the healthy-baseline expectation,
account for the exponential tail. With exponential service times and
a hard SLA timeout, a small fraction of requests will timeout even
with zero queue depth — this is not a bug. The expected residual rate:

    ε ≈ exp(−sla_seconds / service_time_mean)

State the smoke-test expectation as `success_rate ≈ 1 − ε`, not `1.0`.
Verify health by checking `wait_mean ≈ 0`, not `success_rate = 1.0`.

## After the audit

Write the draft `MODEL.md` from `templates/MODEL.md`. Present it to
the user. Wait for explicit confirmation. Only then proceed to
Phase 2.

If the user wants to change something in the draft, change it and
re-present. Iterate until they are satisfied.

When the system is undocumented, the audit is cheaper than coding
without understanding — a misaligned spec compounds through every
subsequent phase. When docs already exist, the audit is mostly
confirmation. In either case: understand before coding.
