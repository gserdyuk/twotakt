# twotakt

**Twotakt helps architects turn architecture descriptions into executable simulation models.**

**An AI-native methodology for performance simulation of IT systems.**

*In Two phases: Audit together. Simulate autonomously.*

twotakt models how systems behave under load — servers, queues, pipelines, connection pools, and any resources that are shared and contended for. The simulation engine is [SimPy](https://simpy.readthedocs.io/) (Python discrete-event simulation); the methodology is what makes the model accurate.

---

> *"I have an IT architecture. Where does it break under load?"*

That is the question twotakt answers — before production, before load tests, before the architecture is locked.

## How it works

Two documents go in, each with a distinct role:
- **Architecture** (components, pools, queues, flows) → defines the **model**.
- **Requirements** (load, SLA, questions to answer) → defines the **testbench and acceptance criteria**.

This is the same split as hardware verification: the architecture is the design, the requirements are the testbench. The requirements document is not an artifact invented for the tool — it is your system's original requirements.

twotakt is structured as two phases:

**Phase 1 — Audit (dialogue)**
You and Claude work through the architecture together: what is scarce, what queues, what degrades under load. The output is a reviewed and approved `MODEL.md` — the specification. No simulation code is written before this is confirmed.

**Phase 2 — Simulation**
```
MODEL.md → [Build] → [Sweep] → [Report]
```
- **Build:** generates `server_sim.py`, runs smoke test, fixes until green
- **Sweep:** runs the model across load scenarios, saves results
- **Report:** produces `SIM_REPORT.md` with bottleneck analysis and SLA verdicts

If sweep results reveal a model mismatch, you return to the audit. The loop is explicit, not accidental.

### Takts ↔ phases

The two takts above are the user-facing view. Under the hood the skill
(`skills/simpy-protocol/`) runs 10 phases. The map — and where *you* have to act:

| Takt | Step | Phase | Artifact in / out | Human gate |
|------|------|-------|-------------------|------------|
| **1 — Audit** | — | **0. Inputs** | in: `ARCHITECTURE.md` + `REQUIREMENTS.md` (ТЗ) | ✋ you supply both documents |
| **1 — Audit** | Audit | **1. Architecture audit** (blocking) | out: *draft* `MODEL.md` | ✋ you confirm the draft |
| **1 — Audit** | Audit | **2. Structural decomposition** | `MODEL.md` (entities, signal/control flow) | — |
| **1 — Audit** | Audit | **3. Model per entity** | `MODEL.md` (SimPy primitive + math model) | ✋ MODEL.md approved → cross into Takt 2 |
| **2 — Sim** | Build | **4. Build system model** | out: `server_sim.py` | — |
| **2 — Sim** | Build | **5. Parameter sources** | `Config` tags: measurement / decision / assumption | — |
| **2 — Sim** | Build | **6. Test bench** | `sweep.py` (arrivals, range, SLA — from ТЗ) | — |
| **2 — Sim** | Build | **7. Verification & Validation** | green smoke run (baseline + law-shape) | — |
| **2 — Sim** | Sweep | **8. Behavioral analysis** | `sweep.png` | ✋ you read the result, say "go" |
| **2 — Sim** | Sweep | **9. Iterate** | `sweep_results.json` (r ≥ 10 seeds, 95% CI) | ✋ refinement may return to Takt 1 |
| **2 — Sim** | Report | **10. SIM_REPORT.md** (optional) | out: `SIM_REPORT.md` | ✋ you read the final deliverable |

The phases are many; the moments that need **you** are few — supply both inputs,
confirm `MODEL.md` (the audit gate, non-negotiable), then say "go" at each Takt-2
transition (Build → Sweep → Report) and whenever a sweep sends you back to audit.
Everything between these gates is Claude's to execute.

> **Current state:** Phase 2 runs as a gated Claude session following the 10-phase protocol in `skills/simpy-protocol/`. The three-agent split (Build / Sweep / Report as separate agents) is the target architecture — not yet implemented.

## Getting started

**Option A — explore an existing model**
Open any example in `examples/` and start with its `README.md` — a one-page map (input / model / how to run / result). Then read `ARCHITECTURE.md` + `REQUIREMENTS.md` → `MODEL.md` → `SIM_REPORT.md` in order. For the code details, continue to `server_sim.py`. Run the smoke test:
```bash
cd examples/USLmodel
pip install -r requirements.txt
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
  - `PowerSearch/` — realistic case study: two pipelines (ingestion + queries), from an architecture whiteboarding scenario
  - `FaxRx/` — realistic case study: worldwide fax reception with Erlang B + OCR, based on a production platform
- `CLAUDE.md` — tells Claude how to behave in this workspace (loads skills automatically)
- `dev-log.md` — append-only log of project evolution.

## Approach

The central proposition is speed of assessment. Writing a proper simulation
from scratch takes days to weeks; twotakt reduces this to a single session. The methodology
reads the project's architecture and requirements documents, conducts a structured audit, and
generates `MODEL.md`, `server_sim.py`, sweep scripts, and a `SIM_REPORT.md`
with bottleneck analysis and SLA feasibility verdicts. The user provides the
architecture and requirements and makes decisions; the technical work is automated.

twotakt does **not** hide SimPy. The user sees the code; the methodology
ensures the code honestly encodes the intended model. The audit-first protocol
is the central commitment — no simulation code is written before the model
specification (`MODEL.md`) is approved. Modern LLMs make working with SimPy
directly tractable even without deep prior knowledge of the library, so
abstracting it away is not necessary.

**What "AI-native" means here:** Claude is not a code generator bolted on top. It is a participant in the audit (asking the right questions, flagging gaps) and the driver of Phase 2 (building, running, and reporting autonomously). The methodology is designed for this collaboration — the skills, the document structure, and the agent boundaries all assume Claude is in the loop.

## Why now

Architects don't model — and until recently they were right. Building a simulation required weeks of specialist work and went stale with every architecture change. The cost of verification was higher than the cost of being wrong.

That cost just dropped by an order of magnitude. twotakt is the methodology for using that shift: the examples are IT systems, and the methodology assumes only shared resources, queues, and contention.
