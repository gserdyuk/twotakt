---
name: simpy-protocol
description: >-
  Methodology and templates for building SimPy simulations of servers, queues,
  and any system that degrades under concurrent load. Use whenever the user
  wants to model server behaviour, request handling, throughput, latency,
  queueing, bottlenecks, capacity, thread-per-request servers, connection
  pools, M/M/1 or M/M/c queues, Universal Scalability Law (USL), thrashing,
  or extending an existing simulation with a new component (database, cache,
  downstream service). Also use when the user mentions simulation, performance,
  degradation, узкое место, очередь, нагрузка, throughput, or asks what
  happens to a server when load grows. Enforces an audit-first protocol —
  never write simulation code before the audit gate is passed and a model
  specification is approved. Bundles methodology, code templates, a theory
  glossary, and a metric-critique checklist that catches survivorship bias
  and other common measurement mistakes. Default examples library lives at
  the user examples directory, for instance twotakt/examples.
---

# Performance Simulation Methodology

This skill encodes a disciplined way of building SimPy performance
simulations. It exists because the natural failure mode of these
projects is to write code first, get a curve, and ship it — at which
point the model is encoding whatever degradation the implementation
accidentally produced, not what the modeller intended.

## Core principle

**Specification is primary, code is downstream.**

The model spec (`MODEL.md`) is the source of truth. The code
(`server_sim.py` and friends) is its implementation. If the spec and
the code disagree, the spec is the specification and the code is the
bug. Every step of this protocol either updates the spec, updates the
code in service of the spec, or validates that the code still honours
the spec.

## When to invoke this skill

Trigger this skill whenever the user is asking to model performance
of a system under load: web servers, queue processors, microservices,
scheduling, capacity planning, "what if we get 10x traffic", "why
does our p99 spike", and so on. Also trigger when the user wants to
**extend** an existing simulation with a new component — extensions
go through their own (shorter) audit, see Phase 9 below.

Before triggering the full protocol, check if the question can be
answered with a quick M/M/c calculation: `ceiling = capacity /
service_time_mean`, or utilization ρ = λ / (c·μ). If that suffices —
answer directly. Run the full protocol when the user wants to explore
system behaviour under varying load, or when the question cannot be
answered analytically.

## Input signature

This skill requires two inputs before the protocol begins:

**1. ТЗ — technical requirements** (what the system must do)
Performance targets (throughput, latency SLAs), capacity goals, constraints,
operational context. This is the *why* — it explains motivation and defines
success criteria for the simulation.

**2. Architecture** (how the system is built)
Components, resources, topology, service interactions. This is the *what* —
the structural decisions already made by a system architect.

**Important:** the transition from ТЗ to Architecture is non-trivial design
work — it is the architect's job and is explicitly out of scope for this skill.
This skill audits and refines an existing architecture for simulation purposes.
It does not derive architecture from requirements.

- If Architecture does not yet exist: stop. Engage a system architect first.
- If Architecture is incomplete or informal: the audit (Phase 1) will surface
  the gaps. Filling them is a joint effort with the architect — not a
  unilateral decision by this skill.

**Output of the full protocol:** `MODEL.md` + SimPy model + sweep plots.
`MODEL.md` is the compiled form of both inputs, structured for simulation —
the single source of truth from which all code flows.

## The protocol

Each phase below is a **gate**. Do not open the next gate until the
current one has been completed and (where indicated) confirmed with
the user. The gate-driven structure is the entire value of this
skill — skipping a gate defeats the point.

### Phase 1 — ARCHITECTURE AUDIT (BLOCKING)

**Require both inputs before proceeding:** ТЗ and Architecture. If either is
missing, ask the user to provide it. Do not substitute one for the other.

Read the architecture document first. Then read the ТЗ for context —
especially the performance targets and operational constraints that motivate
the architecture decisions.

Then conduct a structured audit. Read `references/audit-protocol.md` and work
through the questions in order. The goal is not to interrogate the user but to
clarify the architecture for simulation purposes: identify the scarce resources,
the request lifecycle phases, the degradation mechanisms, the failure modes.

Do not ask questions the architecture document already answers — cite the doc
and ask the user to confirm. Surface gaps and ambiguities; resolve them jointly.
If a gap requires an architectural decision (not just a simulation parameter),
flag it explicitly: *"this is an architectural question, outside this skill's
scope — how did the architect resolve it?"*

The audit produces a draft `MODEL.md`. Do not proceed to Phase 2 until the
user has confirmed the draft.

The audit is a core requirement — it is what stops the simulation from encoding
accidental semantics. If the user does not want an audit, they can skip this
skill. If they use the skill, the audit gate applies.

### Phase 2 — Structural decomposition

Decompose the architecture into simulation-relevant entities. Produce a table
in MODEL.md with three parts:

**Entities and instances** — every component that processes, holds, or routes
requests. For each: name, multiplicity (how many instances), role.

**Signal flow** — how requests move through the system. A simple directed graph
or ordered list: arrival → entity A → entity B → … → departure. Include
branches and merges if they exist.

**Control flow** — how the architecture manages itself: admission control,
timeouts, retries, circuit breakers, backpressure. These are often invisible
in the architecture document but critical for behaviour under overload. Ask
explicitly: "what happens when entity X is saturated?"

This decomposition is the direct translation of architecture into simulation
structure. No model choices yet — only observation and mapping.

### Phase 3 — Choose model per entity

For each entity identified in Phase 2, decide what SimPy primitive and
mathematical model it maps to. Read `references/theory-glossary.md` for the
menu.

Common mappings:

| Entity type | SimPy primitive | Mathematical model |
|---|---|---|
| Worker pool / thread pool | `simpy.Resource(capacity=N)` | M/M/c |
| Single bottleneck server | `simpy.Resource(capacity=1)` | M/M/1 |
| System with coordination overhead | `simpy.Resource` + degradation | USL |
| Bounded queue with drop | `simpy.Resource` + queue-length check | M/M/c/K |
| Timeout / SLA enforcement | `simpy.timeout` + interrupt | — |

For each entity, justify the choice in MODEL.md: which phenomenon does this
model capture that a simpler one does not? If the answer is "nothing" — pick
the simpler model.

**Distribution choice (CV check):** before accepting `expovariate` as the
default service time for any entity, check CV = σ/μ from available samples.
CV > 1.5 → exponential underestimates p99 by 2–10×. Decision tree:
`modeling-jain/references/distributions.md`. If no samples exist, note the
assumption and plan a sensitivity run with CV > 1 as a stress case.

The control flow elements from Phase 2 (timeouts, retries, circuit breakers)
also need model decisions here. Anything not in the table above: note it
explicitly and decide whether to include or defer.

### Phase 4 — Build the system model

Use the templates in `templates/` as the skeleton. Build the system model only —
the bench comes in Phase 6.

- `Config` dataclass — system parameters (capacities, service times, pool sizes).
  Bench parameters (arrival rate, sweep range, SLA thresholds) go in Phase 6.
- `Server` class — one `simpy.Resource` per entity identified in Phase 2,
  with the primitive chosen in Phase 3. Do not add a resource Phase 2 did
  not identify; do not collapse two distinct entities into one for convenience.
- `_serve` method — the request lifecycle following the signal flow from Phase 2,
  one acquire→work→release block per entity in signal-flow order. Control flow
  elements (timeouts, retries) from Phase 2 go here if Phase 3 included them.

Resist the urge to add anything Phases 1–3 did not call for. No
priorities, no preemption, no retries, no graceful degradation logic
unless Phase 2 control flow explicitly listed them.

### Phase 5 — Document parameter sources

Every parameter in `Config` must have a documented source. Three valid sources:

- **Measurement** — value derived from real system monitoring (`modeling-jain`).
  Record: what was measured, over what window, with what tool.
- **Design decision** — value set by the architect or requirements
  ("thread pool will be 16", "timeout is 500ms per SLA").
  Record: who decided, where it is documented.
- **Assumption** — value estimated or guessed. Record: the assumption explicitly,
  and add it to the sensitivity list for Phase 9 (sweep it).

Parameters with undocumented sources are hidden assumptions — they will
silently shape results and be invisible in the report. Every magic number
must live on `Config` and carry its source as a comment or MODEL.md entry.

### Phase 6 — Build the test bench

Build the experimental wrapper around the system model.

- `arrival_process` — workload generator. Arrival rate and distribution come
  from the ТЗ (bench spec), not the system architecture.
- Sweep parameters — what to vary and over what range. Determined by the
  question in the ТЗ: "how does the system behave as load grows from X to Y?"
- SLA thresholds — the pass/fail criteria from the ТЗ. These become the
  reference lines on plots and the verdict column in SIM_REPORT.md.

The bench drives the model; it does not change the model. If defining the bench
reveals a gap in the model (e.g. "what happens when the queue is full?"), go
back to Phase 2/3 and resolve it there before continuing.

### Phase 7 — Verification & Validation (V&V)

*Ref: Sargent, R.G. "Verification and Validation of Simulation Models", Journal of Simulation, 2013.*

Two questions, one gate:

**Verification** — "are we building the model right?" Does the code correctly
implement MODEL.md? Run once with default parameters. Expected outcome: healthy
baseline — throughput equal to arrival rate, latency p50 close to sum of phase
means, no drops, success rate 100%. If the baseline is already pathological,
the defaults are wrong (not the model) — adjust arrival rate until a healthy
point exists. The defaults should demonstrate the model works, not stress-test it.

**Validation** — "are we building the right model?" Does the simulation exhibit
the behavior predicted by the law chosen in Phase 3? Run over a load range and
inspect the curve shape:
- USL: three regimes — linear scaling → knee → declining throughput
- M/M/1: hyperbolic latency rise toward saturation
- M/M/c: throughput plateau within ~5% of analytical ceiling `capacity / service_time_mean`

If the curve does not match: debug the model — a degradation coefficient is
zero, a Resource has wrong capacity, or the service-time draw is wrong.

Apply `references/metric-checklist.md` as a mandatory lens on both checks.
Critical rule: latency-of-successful-requests is not safe beyond saturation —
surviving requests are a biased sample. Always track **effective latency**
(timeouts counted as SLA seconds) and **success rate** alongside latency.
If the user has not asked for these, add them and explain why.

Do not proceed to Phase 8 until both verification and validation pass.

### Phase 8 — Behavioral analysis

Run the simulation and analyze system behavior against the questions from the ТЗ.
Visualization is one tool — the number of plots and panels is determined by the
question, not by a fixed rule. Use `templates/plot_sweep.py` as the skeleton.

The goal is to understand behavior, not to produce charts. Ask: does the system
satisfy the requirements from the ТЗ? Where is the knee? Which entity saturates
first?

Analysis produces one of two conclusions — both lead to Phase 9:
- **Model is wrong** → refinement: structure or parameters do not reflect
  reality, return to Phase 2/3/4.
- **Model is correct** → optimization: explore parameter space to find
  configurations that satisfy requirements.

### Phase 9 — Iterate

Every iteration — whether refinement or optimization — has two mandatory
properties:

**Mini-audit before any change.** Before touching `Config`, `Server`, or
`_serve`: which entities, resources, and signal-flow phases does this change
affect? Read `references/extension-audit.md`. The audit scope is proportional
to the change — a parameter tweak is light; a new entity is a full Phase 2/3
pass. On folder structure: copy the parent folder for a clean exhibit of one
idea; edit in place for iterative development of one model.

**MODEL.md sync after any change.** Any change that touches `Config`,
`Server.__init__`, or `_serve` requires a MODEL.md update in the same step.
The spec-is-primary principle collapses if the spec drifts from the code.

**Refinement path** — model structure is wrong:
Return to Phase 2 (re-examine entities and signal flow) or Phase 3 (re-choose
model per entity). Treat it as a scoped re-run of those phases, not a full
restart. Then rebuild (Phase 4) and re-analyze (Phase 8).

**Optimization path** — model is correct, exploring parameter space:
Vary the parameter of interest and re-run Phase 8 (behavioral analysis).
A sweep is Phase 8 repeated across a range of values — not a separate
concept. Use `templates/sweep.py` (1D) or `templates/sweep_2d.py` (2D) to
automate the repetition. The interesting result is rarely "did it work" —
it is "where does the bottleneck shift, and at what value does a new entity
start to bind."

For any result that will be reported: r ≥ 10 seeds, discard warm-up fraction,
report `ȳ ± t(r−1, 0.025) · s/√r` at 95% confidence. Use
`modeling-jain/templates/ci_calc.py`. Flag any metric where CI half-width /
mean > 10%. Rule of thumb: r ≥ 20 for p95 latency, r ≥ 10 for throughput.

### Phase 10 — SIM_REPORT.md (optional)

After sweep plots are produced and validated, ask the user whether a
formal report is needed. Sometimes plots and console output are sufficient;
sometimes a standalone document is the actual deliverable.

If a report is needed, use `templates/SIM_REPORT.md` as the form.
The report must stand alone — a reader who has not seen the code or
the audit should be able to understand the conclusions and their limits.

The template (`templates/SIM_REPORT.md`) suggests five sections that
worked for PowerSearch — adapt to the project's needs:

1. **Context** — what system, what models, what questions were asked.
2. **Parameters and assumptions** — every number with its justification.
3. **Graph interpretation** — what each panel shows, where the knee is.
4. **Requirements table** — one row per requirement, with a verdict.
5. **Sensitivity and risks** — which assumptions, if wrong by 2×, flip a verdict.

Do not write the report before the plots exist and are validated.

## The library

The user's examples folder (default: `twotakt/examples/`) is the
working library. Before writing a new model from scratch, look at the
existing examples for the closest match and treat it as a copy
template. Each example must follow the same structural shape (same
filenames, same class layout) so that copying is mechanical.

When the same pattern appears in three or more examples (rule of
three), suggest extracting it into a small library module. Until
that, accept the duplication — it is the price of not over-abstracting
prematurely.

## Maintaining this skill

This skill is built from real simulation projects. Each project may reveal
gaps, wrong defaults, or new patterns worth capturing.

**During a project:** if you notice something the skill gets wrong or doesn't
cover, record it in memory as a pending skill update. Don't stop the project
to fix it — just note it.

**At the end of a project:**
1. Review the pending updates from memory.
2. Discuss with the user: which are worth adding, which were project-specific.
3. Add agreed changes and record them in `CHANGELOG.md` with the source project.

`CHANGELOG.md` lives in this skill directory. Each entry: what changed,
which project it came from, what gap or failure motivated it.

## Anti-patterns to actively prevent

These are the failure modes this skill exists to prevent. Watch for
them and intervene if the user (or you) drift toward any of them:

- **Writing code before completing the audit.** Encodes accidental
  semantics. The audit gate is non-negotiable.
- **Adding features the audit did not list.** Defer priorities,
  preemption, retries, etc. until a sweep proves they matter.
- **Trusting `latency-of-successes` under overload.** It will lie.
  Always plot it together with success rate and effective latency.
- **Adding `simpy.Resource` objects the audit did not identify, or merging
  two distinct scarce resources into one.** Resources are determined by
  Phase 2 (structural decomposition), not by the template.
- **Hard-coded numbers in function bodies.** Every knob lives on
  `Config`.
- **Single-curve plots when the system has a failure mode.**
  Three-panel minimum.
- **Letting MODEL.md drift from the code.** Sync on every intent
  change, in the same step.

## Reference files

- `references/audit-protocol.md` — Phase 1 audit, full Q&A in order.
- `references/extension-audit.md` — Phase 9 iteration mini-audit.
- `references/theory-glossary.md` — M/M/1, M/M/c, USL formulas and when to use each.
- `references/metric-checklist.md` — Phase 7 V&V metric lens.
- `references/methodology.md` — full prose methodology, the long form of this protocol.

## Templates

- `templates/server_sim.py` — Config + Server + _serve skeleton.
- `templates/sweep.py` — 1D sweep (vary one parameter, e.g. arrival rate).
- `templates/sweep_2d.py` — 2D sweep (vary two parameters; use when Q4b calls for it).
- `templates/plot_sweep.py` — three-panel plot skeleton.
- `templates/MODEL.md` — model specification template.
- `templates/SIM_REPORT.md` — simulation report template (Phase 10).
- `templates/requirements.txt` — minimal dependencies.
