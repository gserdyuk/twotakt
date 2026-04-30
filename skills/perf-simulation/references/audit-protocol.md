# Phase 1 — Audit Protocol

The audit is a structured conversation that produces a draft
`MODEL.md` capturing the user's intent. **Ask the questions in the
order below.** The order matters: each answer constrains the next
question. Do not paraphrase the order.

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

### Q5 — What kinds of degradation do they want the model to encode?

This is the most important question. Walk through the list and for
each, ask whether it is in scope:

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
becomes the Phase 7 validation criterion.

## After the audit

Write the draft `MODEL.md` from `templates/MODEL.md`. Present it to
the user. Wait for explicit confirmation. Only then proceed to
Phase 2.

If the user wants to change something in the draft, change it and
re-present. Iterate until they are satisfied.

The audit is the cheapest part of the project. Spend time here. The
cost of a misaligned spec compounds through every subsequent phase.
