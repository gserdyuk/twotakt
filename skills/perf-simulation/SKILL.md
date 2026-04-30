---
name: perf-simulation
description: >-
  Methodology and templates for building SimPy simulations of servers, queues,
  and any system that degrades under concurrent load. Use whenever the user
  wants to model server behaviour, request handling, throughput, latency,
  queueing, bottlenecks, capacity, thread-per-request servers, connection
  pools, M/M/1 or M/M/c queues, Universal Scalability Law (USL), thrashing,
  or extending an existing simulation with a new component (database, cache,
  downstream service). Also use when the user mentions simulation, perfomance,
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
go through their own (shorter) audit, see Phase 11 below.

When in doubt, trigger. The cost of running this protocol on a
non-perf task is small; the cost of writing a misleading simulation
is large.

## The protocol

Each phase below is a **gate**. Do not open the next gate until the
current one has been completed and (where indicated) confirmed with
the user. The gate-driven structure is the entire value of this
skill — skipping a gate defeats the point.

### Phase 1 — AUDIT (BLOCKING)

Before any code, conduct a structured audit with the user. Read
`references/audit-protocol.md` and ask the questions there in the
order listed. Do not paraphrase the order. The audit produces a draft
`MODEL.md` capturing the user's intent. Do not proceed to Phase 2
until the user has confirmed the draft.

This is the single most important phase. If the user pushes to "just
write the code", explain that the audit is what stops the simulation
from being misleading, and proceed with the audit anyway.

### Phase 2 — Choose theoretical framework

Decide which queueing/scaling law the model will encode. Read
`references/theory-glossary.md` for the menu (M/M/1, M/M/c, USL,
custom). Justify the choice in MODEL.md in one or two sentences:
which phenomenon does this law capture that the simpler one does not?

If the answer to that question is "nothing", pick the simpler law.

### Phase 3 — Decompose mechanisms

List the real-world mechanisms the model is meant to encode and
their order of growth in N (number of concurrent requests). A small
table in MODEL.md is the right form. This is what tells you whether
your law from Phase 2 is sufficient — if you have quadratic effects
listed and chose M/M/1, you have a mismatch.

### Phase 4 — Build the minimum viable model

Use the templates in `templates/` as the skeleton. Fill in:

- `Config` dataclass — every parameter the audit identified.
- `Server` class — one `simpy.Resource` per scarce shared thing.
- `_serve` method — the request lifecycle as a sequence of phases.
- `arrival_process` — the workload generator.

Resist the urge to add anything Phases 1–3 did not call for. No
priorities, no preemption, no retries, no graceful degradation logic
unless the audit explicitly listed them.

### Phase 5 — Parameterize everything

Every magic number must live on `Config`. Constants in function
bodies are a code smell — they hide assumptions and prevent
parameter sweeps. This is non-negotiable; future phases depend on it.

### Phase 6 — Smoke test, then calibrate defaults

Run once with the defaults. Expected outcome: a healthy baseline —
throughput equal to arrival rate, latency p50 close to the sum of
phase means, no drops, success rate at 100%. If the smoke test shows
the system already in a pathological state, **the defaults are
wrong**, not the model. Adjust the defaults (usually arrival rate
or one of the degradation coefficients) until a healthy baseline
exists. The defaults should *demonstrate the model works*, not
stress-test it.

### Phase 7 — Validate the curve shape

Run a small sweep over arrival rate and inspect the curve. If you
chose USL: there must be three regimes (linear scaling → knee →
declining throughput). If you chose M/M/1: there must be a hyperbolic
latency rise toward saturation. If the curve does not match the
chosen law, debug the model — usually a degradation coefficient is
zero or a Resource has the wrong capacity.

### Phase 8 — Apply the metric critique

Read `references/metric-checklist.md` and apply every rule. The
critical one to remember: latency-of-successful-requests is not a
safe metric beyond saturation, because successful requests under
overload are a biased sample. Always pair latency with
**effective latency** (timeouts counted as SLA seconds) and
**success rate** (fraction of arrivals that completed).

If the user has not asked for these metrics, add them anyway and
explain why.

### Phase 9 — Visualize in panels

The minimum useful plot is **three stacked panels** sharing an x-axis:

1. Throughput (with ideal y=x reference)
2. Success rate (fraction completed, 0–1 scale)
3. Latency percentiles (log-y; effective solid, ok-only dashed)

A throughput chart on its own hides the failure mode. Use the
`templates/plot_sweep.py` skeleton — it already has the three-panel
layout.

### Phase 10 — Sync MODEL.md with code

After every code change that affects intent, update MODEL.md. This is
not optional. The whole "spec is primary" principle collapses if the
spec drifts from the code. A mechanical rule: any change that touches
`Config`, `Server.__init__`, or `_serve` requires a corresponding
MODEL.md edit in the same step.

### Phase 11 — Extension (when adding components)

When the user wants to add a new component (database, cache,
downstream service, scheduler, replica), this is a **new audit**, not
a code change. Read `references/extension-audit.md` for the shorter
extension audit protocol. Two structural rules:

1. **Copy the example folder, do not edit in place.** The new
   component lives in a sibling example (e.g. `USLDBmodel` is a copy
   of `USLmodel` with a database added). Each example stays a clean
   exhibit of one idea.
2. **The change inside the copy is surgical.** New `Config` fields,
   new `Resource` on the `Server`, new acquire–hold–release block in
   `_serve`. Nothing else.

After the extension code exists, MODEL.md in the new folder must
reference its parent and describe only the diff. Do not duplicate the
parent's content.

### Phase 12 — Explore the parameter space

Sweep the new component's defining parameter (e.g. `db_pool_size = 1,
2, 4, 8`) and save the resulting plots side-by-side. The interesting
result is rarely "did it work" — it is "where does the bottleneck
shift, and at what value of the parameter does the new component
start to bind."

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

## Anti-patterns to actively prevent

These are the failure modes this skill exists to prevent. Watch for
them and intervene if the user (or you) drift toward any of them:

- **Writing code before completing the audit.** Encodes accidental
  semantics. The audit gate is non-negotiable.
- **Adding features the audit did not list.** Defer priorities,
  preemption, retries, etc. until a sweep proves they matter.
- **Trusting `latency-of-successes` under overload.** It will lie.
  Always plot it together with success rate and effective latency.
- **Editing an existing example to add a new component.** Copy the
  folder. Each example is a clean exhibit of one idea.
- **Hard-coded numbers in function bodies.** Every knob lives on
  `Config`.
- **Single-curve plots when the system has a failure mode.**
  Three-panel minimum.
- **Letting MODEL.md drift from the code.** Sync on every intent
  change, in the same step.

## Reference files

- `references/audit-protocol.md` — Phase 1 audit, full Q&A in order.
- `references/extension-audit.md` — Phase 11 extension audit, shorter.
- `references/theory-glossary.md` — M/M/1, M/M/c, USL formulas and when to use each.
- `references/metric-checklist.md` — Phase 8 critique rules.
- `references/methodology.md` — full prose methodology, the long form of this protocol.

## Templates

- `templates/server_sim.py` — Config + Server + _serve skeleton.
- `templates/sweep.py` — text-mode sweep skeleton.
- `templates/plot_sweep.py` — three-panel plot skeleton.
- `templates/MODEL.md` — model specification template.
- `templates/requirements.txt` — minimal dependencies.
