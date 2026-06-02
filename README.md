# twotakt

**An AI-native methodology for performance simulation — IT systems and beyond.**
*Two phases: Audit together. Simulate autonomously.*

twotakt models how systems behave under load — servers, queues, pipelines, connection pools, and any resources that are shared and contended for. The simulation engine is [SimPy](https://simpy.readthedocs.io/) (Python discrete-event simulation); the methodology is what makes the model accurate.

---

> *"I have an IT architecture. Where does it break under load?"*

That is the question twotakt answers — before production, before load tests, before the architecture is locked.

## How it works

twotakt is structured as two phases:

**Phase 1 — Audit (dialogue)**
You and Claude work through the architecture together: what is scarce, what queues, what degrades under load. The output is a reviewed and approved `MODEL.md` — the specification. No simulation code is written before this is confirmed.

**Phase 2 — Simulation (three agents)**
```
MODEL.md → [Build] → [Sweep] → [Report]
```
- **Build:** generates `server_sim.py`, runs smoke test, fixes until green
- **Sweep:** runs the model across load scenarios, saves results
- **Report:** produces `SIM_REPORT.md` with bottleneck analysis and SLA verdicts

If sweep results reveal a model mismatch, you return to the audit. The loop is explicit, not accidental.

## Getting started

**Option A — explore an existing model**
Open any example in `examples/` and read `ARCHITECTURE.md` → `MODEL.md` → `server_sim.py` in order. Run the smoke test:
```bash
cd examples/USLmodel
pip install simpy
python server_sim.py
```

**Option B — model your own system**
1. Clone this repo and open it in Claude Code
2. Prepare two documents: your system's architecture and its requirements
   (see `examples/USLmodel/ARCHITECTURE.md` and `examples/USLmodel/REQUIREMENTS.md` as examples)
3. Tell Claude: *"I have an architecture. Let's model it."*
4. Claude runs the audit (Phase 1) — you answer questions, confirm `MODEL.md`
5. Claude builds, sweeps, and reports (Phase 2)

The `CLAUDE.md` at the repo root loads the methodology skills automatically.

## Layout

- `skills/` — the methodology as Claude skills:
  - `simpy-protocol/` — 10-phase audit-to-report protocol
  - `queueing-lazowska/` — analytical queueing theory (M/M/c, MVA, operational laws)
  - `modeling-jain/` — statistical rigour for model inputs and outputs
- `examples/` — worked models at increasing complexity:
  - `USLmodel/` — single CPU server with USL degradation
  - `USLDBmodel/` — same, with a database connection pool added
  - `PowerSearch/` — real system: two pipelines (ingestion + queries)
  - `FaxRx/` — real system: worldwide fax reception with Erlang B + OCR
- `CLAUDE.md` — tells Claude how to behave in this workspace (loads skills automatically)
- `dev-log.md` — append-only log of project evolution.

## Approach

The central proposition is speed of assessment. Writing a SimPy simulation
from scratch takes days; twotakt reduces this to a single session. The methodology
reads the project's architecture document, conducts a structured audit, and
generates `MODEL.md`, `server_sim.py`, sweep scripts, and a `SIM_REPORT.md`
with bottleneck analysis and SLA feasibility verdicts. The user provides the
architecture and makes decisions; the technical work is automated.

twotakt does **not** hide SimPy. The user sees the code; the methodology
ensures the code honestly encodes the intended model. The audit-first protocol
is the central commitment — no simulation code is written before the model
specification (`MODEL.md`) is approved. Modern LLMs make working with SimPy
directly tractable even without deep prior knowledge of the library, so
abstracting it away is not necessary.

**What "AI-native" means here:** Claude is not a code generator bolted on top. It is a participant in the audit (asking the right questions, flagging gaps) and the driver of Phase 2 (building, running, and reporting autonomously). The methodology is designed for this collaboration — the skills, the document structure, and the agent boundaries all assume Claude is in the loop.

## Use cases

Wherever there are shared resources, queues, and contention — IT capacity planning, fleet scheduling, patient flow, warehouse throughput. The examples in this repo are IT systems (servers, pipelines, connection pools), but the methodology is not IT-specific.
