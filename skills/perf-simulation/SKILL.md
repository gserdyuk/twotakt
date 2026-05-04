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

Before triggering the full protocol, check if the question can be
answered with a quick M/M/c calculation: `ceiling = capacity /
service_time_mean`, or utilization ρ = λ / (c·μ). If that suffices —
answer directly. Run the full protocol when the user wants to explore
system behaviour under varying load, or when the question cannot be
answered analytically.

## The protocol

Each phase below is a **gate**. Do not open the next gate until the
current one has been completed and (where indicated) confirmed with
the user. The gate-driven structure is the entire value of this
skill — skipping a gate defeats the point.

### Phase 1 — AUDIT (BLOCKING)

Before any code, scan the project directory for existing documentation
(ARCHITECTURE.md, README, design docs). If spec answers are already there,
cite them and ask the user to confirm — do not ask questions the docs already answer.

Then conduct a structured audit with the user. Read
`references/audit-protocol.md` and ask the questions there in the
order listed. Do not paraphrase the order. The audit produces a draft
`MODEL.md` capturing the user's intent. Do not proceed to Phase 2
until the user has confirmed the draft.

The audit is a core requirement of this skill — it is what stops the
simulation from encoding accidental semantics. If the user does not
want an audit, they can skip this skill. If they use the skill, the
audit gate applies.

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
- `Server` class — `simpy.Resource` instances as determined by Q2.
  The task defines the resources, not the template. Do not add a pool
  the audit did not identify; do not collapse two distinct scarce
  resources into one for convenience.
- `_serve` method — the request lifecycle as a sequence of phases, one
  acquire→work→release block per phase listed in Q3, in Q3 order.
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

When the user wants to add a new component, run an impact audit before
coding: which `Config` fields, `Resource` instances, and `_serve` phases
does this change touch? Read `references/extension-audit.md` — the
audit scope is proportional to the change.

**On folder structure** — decide based on the user's intent:
- If the goal is a **clean exhibit of one idea** (library/example):
  copy the parent folder; each example stays independent.
- If the goal is **iterative development of one model**: editing in
  place is acceptable.

After the code change, update MODEL.md to reflect the diff.

### Phase 12 — Explore the parameter space

Sweep the new component's defining parameter (e.g. `db_pool_size = 1,
2, 4, 8`) and save the resulting plots side-by-side. The interesting
result is rarely "did it work" — it is "where does the bottleneck
shift, and at what value of the parameter does the new component
start to bind."

**Sweep dimensionality** is determined by the audit (Q4b), not by
convenience. Choose the minimum that answers the question:

- **1D** (arrival rate only): use `templates/sweep.py`. Fine for a
  single "how does the system degrade?" question.
- **2D** (e.g. arrival rate × pool size): use `templates/sweep_2d.py`.
  Produces a family of curves — one per value of the second parameter.
  **Runtime warning:** a grid of `N × M × seeds` runs can be slow.
  A 10 × 7 × 3 grid = 210 simulations. Choose grid sizes deliberately;
  start coarse, refine only where the knee appears.
- **Higher dimensions**: dimensionality is determined by the task.
  Alternatives to full grids: fix secondary parameters at a few
  representative values, run multiple 2D sweeps, or use Monte Carlo
  sampling for high-dimensional spaces.

Always average over at least 2 seeds per grid cell to stabilise p95
estimates. Record both the averaged result and, if important, variance.

### Phase 13 — SIM_REPORT.md (optional)

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
  two distinct scarce resources into one.** Resources are determined by Q2,
  not by the template.
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
- `templates/sweep.py` — 1D sweep (vary one parameter, e.g. arrival rate).
- `templates/sweep_2d.py` — 2D sweep (vary two parameters; use when Q4b calls for it).
- `templates/plot_sweep.py` — three-panel plot skeleton.
- `templates/MODEL.md` — model specification template.
- `templates/SIM_REPORT.md` — simulation report template (Phase 13).
- `templates/requirements.txt` — minimal dependencies.
