# twotakt

A workspace for automatic generation of discrete-event models of architected systems,
with an audit-first methodology and an installable Cowork skill.

## Layout

- `examples/` — worked SimPy models, each with `server_sim.py`, `sweep.py`,
  `plot_sweep.py`, `MODEL.md` (specification) and a `sweep.png`.
- `examples/METHODOLOGY.md` — 12-step protocol used to build the examples,
  plus a list of recurring anti-patterns.
- `skills/simpy-protocol/` — the methodology packaged as a Cowork skill
  (audit-first protocol, theory glossary, metric checklist, code templates).
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

Anywhere discrete-event simulation under load is the right tool: IT
capacity planning, fleet scheduling, patient flow, warehouse throughput.
The examples currently in the workspace target IT systems (single-CPU
server with USL degradation; same with a database connection pool).
