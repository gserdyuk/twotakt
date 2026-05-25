# twotakt

A workspace for building discrete-event simulations of systems under load, with an audit-first methodology and an installable Cowork skill.

Before a system goes into production — or before architectural changes are committed — it helps to know how it will behave under load. Where do bottlenecks appear? How does latency degrade as concurrency grows? Does the queue stabilize, or run away? Live load testing answers these questions late and expensively, and only for systems that already exist. twotakt is a workspace for answering them earlier.

You sketch the architecture in a short specification (`MODEL.md`), build a small executable model of it in SimPy, and run that model under varying load to observe how the system behaves. The audit-first methodology is the central commitment: the specification is reviewed and approved **before** any simulation code is written, so the model honestly encodes what you intended — not whatever the implementation happened to produce.

## Layout

- `examples/` — worked SimPy models. Each contains `server_sim.py`, `sweep.py`, `plot_sweep.py`, `MODEL.md` (specification), and a `sweep.png`. The `METHODOLOGY.md` file in this folder describes the step-by-step protocol used to build the examples, along with recurring anti-patterns.
- `skills/perf-simulation/` — the methodology packaged as a Cowork skill (audit-first protocol, theory glossary, metric checklist, code templates).
- `perf-simulation.skill` — installable bundle of the skill above.
- `dev-log.md` — append-only log of project evolution.
- `docs/concept.md` — vision, problem, key differentiator, planned calibration direction.
- `docs/architecture.md` — structural arrangement: layers, workflow, persistence, component boundaries.
- `docs/archive/` — earlier vision documents (v1 — MCP-centric design).

## Approach

twotakt uses SimPy — a mature Python library for discrete-event simulation — and deliberately does **not** wrap it in a higher-level abstraction. You see and edit the simulation code directly. This is a design choice, not an oversight: hiding SimPy behind a DSL or builder API would mean asking you to trust that the abstraction faithfully translates your model into events, resources, and timeouts. With SimPy in plain view, what you see is what runs, and the model stays auditable end-to-end.

The cost of that transparency — having to understand SimPy primitives — has dropped sharply. Modern LLMs work with SimPy idioms well enough that you can use the library directly without a long learning curve, especially with the methodology and templates loaded into context. The installable skill (`perf-simulation.skill`) carries that methodology with you when you work in Cowork, so you don't reinvent the protocol each time.

The workflow itself is a clear sequence: write the specification, review it against a checklist of anti-patterns and theory traps, *then* implement it in SimPy, sweep over load levels, plot, and interpret. The audit step at the start is the most valuable — catching a misconceived model in prose is much cheaper than debugging a simulation that converges to the wrong answer.

## Use cases

Anywhere discrete-event simulation under load is the right tool: IT capacity planning, fleet scheduling, patient flow, warehouse throughput. The examples currently in the workspace target IT systems — a single-CPU server with Universal Scalability Law (USL) degradation, and the same with a database connection pool — but the methodology applies wherever shared resources, queues, and contention are in play.
