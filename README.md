# Twotakt — Audit together. Simulate autonomously.

**AI turns an architecture description into an executable simulation model — in hours, not weeks.**

For IT-system architects: performance modeling, capacity planning, bottleneck analysis. The simulation engine is [SimPy](https://simpy.readthedocs.io/) (Python discrete-event simulation); the methodology is what makes the model trustworthy.

> *"I have an IT architecture. Where does it break under load?"*

That is the question Twotakt answers — before production, before load tests, before the architecture is locked.

## Architects don't model. And until now they were right.

Performance decisions are made on experience and intuition, bottlenecks are discovered in production, capacity planning is done in spreadsheets. This was a rational calculation — each alternative had its own cost:

- a **model** required weeks of specialist work and went stale along with the architecture;
- **load testing** requires an already-finished system;
- **spreadsheets** can't see queues and cascading degradations.

At that cost of verification, the architect justifiably relied on intuition.

**The cost of verification just dropped by an order of magnitude. The calculation is due for a rethink.** Twotakt is the methodology for using that shift.

## How Twotakt works

Two documents go in, each with its own role:

- **Architecture** — components, pools, queues, flows: how the system is built. The architect produces it. **Architecture produces the model.**
- **Requirements** — load, SLA, questions about the system. This is your original spec, not a new document created for the tool; the AI helps shape it in conversation. **Requirements produce the testbench and the acceptance criteria.**

The same split as in hardware verification: the architecture is the design, the requirements are the testbench.

Then:

1. The AI builds an executable model from the architecture and records it in **MODEL.md**: components, flows, assumptions, parameters.
2. From the requirements it assembles load scenarios and acceptance criteria — what the model is checked against.
3. **You confirm both the model and the criteria — before any simulation code is written.** Misunderstandings are visible and fixed here.
4. The model is compiled into a simulation (SimPy), verified against the spec with an executable check battery, and run across the scenarios from the requirements.
5. Report: throughput, latencies, queues, bottlenecks, degradation under load — against your acceptance criteria.

If the runs reveal a model mismatch, you return to the audit. The loop is explicit, not accidental.

The principle is **audit-first**: you trust not the AI, but the model you verified yourself. The AI speeds up construction; the decision about correctness stays with the human.

## "Models are only approximate anyway"

True — which is why Twotakt doesn't offer exact numbers. It answers questions that are robust to error: **what breaks first** (the order of bottlenecks), **option A or B** (a comparison on identical scenarios), **what happens at 10× load** (the character of degradation). These are exactly the questions intuition answers worst — queues and cascades are nonlinear.

And one more thing: an architect's intuition is also a model, just an implicit one. MODEL.md makes it explicit and presentable: "I'm confident — here's the model and the run" is more convincing in an architecture review board than "I'm confident because of experience."

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
4. Claude runs the audit — you answer questions, confirm `MODEL.md`
5. Claude builds, verifies, sweeps, and reports

The `CLAUDE.md` at the repo root loads the methodology skills automatically.

## Under the hood: two takts, ten phases

The two takts — audit together, simulate autonomously — are the user-facing view.
Under the hood the skill (`skills/simstudy-protocol/`) runs 10 gated phases:

| Takt | Step | Phase | Artifact in / out | Human gate |
|------|------|-------|-------------------|------------|
| **1 — Audit** | — | **0. Inputs** | in: `ARCHITECTURE.md` + `REQUIREMENTS.md` | ✋ you supply both documents |
| **1 — Audit** | Audit | **1. Architecture audit** (blocking) | out: *draft* `MODEL.md` | ✋ you confirm the draft |
| **1 — Audit** | Audit | **2. Structural decomposition** | `MODEL.md` (entities, signal/control flow) | — |
| **1 — Audit** | Audit | **3. Model per entity** | `MODEL.md` (SimPy primitive + math model) | ✋ MODEL.md approved → cross into Takt 2 |
| **2 — Sim** | Build | **4. Build system model** | out: `server_sim.py` | — |
| **2 — Sim** | Build | **5. Parameter sources** | `Config` tags: measurement / decision / assumption | — |
| **2 — Sim** | Build | **6. Test bench** | `sweep.py` (arrivals, range, SLA — from requirements) | — |
| **2 — Sim** | Build | **7. Verification & Validation** | `verify.py` green (conservation + law-shape / metamorphic toggles) | ✋ green = correctness (**auto**); **you sign off** before sweeps |
| **2 — Sim** | Sweep | **8. Behavioral analysis** | `sweep.png` | ✋ you read the result, say "go" |
| **2 — Sim** | Sweep | **9. Iterate** | `sweep_results.json` (r ≥ 10 seeds, 95% CI) | ✋ refinement may return to Takt 1 |
| **2 — Sim** | Report | **10. SIM_REPORT.md** (optional) | out: `SIM_REPORT.md` | ✋ you read the final deliverable |

The phases are many; the moments that need **you** are few — supply both inputs,
confirm `MODEL.md` (the audit gate, non-negotiable), sign off the verified model
before sweeps (the validation harness certifies *correctness* automatically; you
authorize the *spend*, since sweeps can be expensive), then say "go" at Sweep →
Report and whenever a sweep sends you back to audit. Everything between these
gates is Claude's to execute.

> **Current state:** Takt 2 runs as a gated Claude session following the 10-phase protocol in `skills/simstudy-protocol/`. The three-agent split (Build / Sweep / Report as separate agents) is the target architecture — not yet implemented.

## What's in the repo

- `skills/` — the methodology as Claude skills:
  - `simstudy-protocol/` — the audit-first, 10-phase audit-to-report protocol (the entry point)
  - `queueing-lazowska/` — analytical queueing theory (M/M/c, MVA, operational laws)
  - `modeling-jain/` — statistical rigour for model inputs and outputs
- `harness/` — shared validation harness for Phase 7: conservation invariants + runner (what "green" means — and does not mean — is in its README)
- `examples/` — worked models, four classes of systems so far:
  - `USLmodel/` — single CPU server with USL degradation
  - `USLDBmodel/` — same, with a database connection pool added: cascaded bottlenecks
  - `PowerSearch/` — search aggregator case study: two pipelines (ingestion + queries), capacity planning
  - `FaxRx/` — worldwide fax reception with Erlang B + OCR, based on a production platform
- `docs/` — concept, architecture, critique, one-pagers
- `CLAUDE.md` — tells Claude how to behave in this workspace (loads skills automatically)
- `dev-log.md` — append-only log of project evolution

## What "AI-native" means here

Claude is not a code generator bolted on top. It is a participant in the audit (asking the right questions, flagging gaps) and the driver of the simulation takt (building, verifying, running, and reporting autonomously). The methodology is designed for this collaboration — the skills, the document structure, and the gate boundaries all assume Claude is in the loop.

Twotakt does **not** hide SimPy. The user sees the code; the methodology ensures the code honestly encodes the intended model. Modern LLMs make working with SimPy directly tractable even without deep prior knowledge of the library, so abstracting it away is not necessary.

## Try it on your system

**Give it your system's architecture and requirements — and two hours of your time.**

The output: a MODEL.md of your system and a bottleneck report. The model will either confirm your expectations — and they turn into a document you can show your team and your client — or reveal something you didn't expect. Before production, not in production.

Gennadiy Serdyuk — gserdyuk@gmail.com / https://www.linkedin.com/in/gserdyuk
