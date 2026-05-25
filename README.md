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

The central proposition is speed of assessment. Writing a SimPy simulation
from scratch takes days; twotakt reduces this to a single session. The skill
reads the project's architecture document, conducts a structured audit, and
generates `MODEL.md`, `server_sim.py`, sweep scripts, and a `SIM_REPORT.md`
with bottleneck analysis and SLA feasibility verdicts. The user provides the
architecture and makes decisions; the technical work is automated.

twotakt does **not** hide SimPy. The user sees the code; the methodology
and the skill ensure the code honestly encodes the intended model. The
audit-first protocol is the central commitment — no simulation code is
written before the model specification (`MODEL.md`) is approved. Modern
LLMs make working with SimPy directly tractable even without deep prior
knowledge of the library, so abstracting it away is not necessary.

## Use cases

Anywhere discrete-event simulation under load is the right tool: IT capacity planning, fleet scheduling, patient flow, warehouse throughput. The examples currently in the workspace target IT systems — a single-CPU server with Universal Scalability Law (USL) degradation, and the same with a database connection pool — but the methodology applies wherever shared resources, queues, and contention are in play.
