# twotakt — Architecture (v2)

## What this document is

This document describes the structural arrangement of twotakt v2 —
the files, folders, conventions and the role of the agent. It
complements `docs/concept.md` (the *why*) by explaining the *how* at
the level of project organisation.

This document is **not** the place for modelling concepts (degradation
laws, theoretical frameworks, queue theory, metric definitions).
Those live in `examples/<name>/MODEL.md` per example,
`skills/perf-simulation/references/theory-glossary.md`,
`skills/perf-simulation/references/metric-checklist.md`. Architecture
here means project structure, not modelling structure.

The previous architecture (`docs/archive/architecture-v1.md`) was
built around an MCP server that hid SimPy behind a custom DSL. v2
abandons that abstraction layer and uses SimPy directly. Mappings
from v1 to v2 are listed in the dedicated table below.

## Overview

twotakt is a workspace, not a runtime. There is no daemon, no API,
no MCP server. Everything is files on disk under git, plus a Cowork
skill that loads on demand to drive an LLM agent through the
methodology.

```
                ┌─────────────────────────────┐
                │  user                       │
                │  (NL description, audit     │
                │   answers, parameter and    │
                │   visualisation choices)    │
                └──────────────┬──────────────┘
                               │
                               ▼
                ┌─────────────────────────────┐
                │  agent (Cowork)             │
                │  with perf-simulation skill │
                └──┬──────────────┬───────────┘
                   │              │
                   │              │
        ┌──────────▼──┐    ┌──────▼──────────┐
        │  templates/ │    │  examples/      │
        │  (skeletons)│    │  (library)      │
        └──────────┬──┘    └─────────────────┘
                   │
                   ▼
        ┌──────────────────────────┐
        │  new example folder      │
        │  on disk, under git      │
        └──────────┬───────────────┘
                   │
                   ▼
        ┌──────────────────────────┐
        │  python (SimPy + matplotlib) │
        │  invoked locally             │
        └──────────┬───────────────┘
                   │
                   ▼
        ┌──────────────────────────┐
        │  dev-log entry           │
        └──────────────────────────┘
```

The agent is the only active component. Python and its libraries are
invoked from the generated code, not from the agent. Nothing runs in
the background.

## Layers

twotakt has four layers today and one planned.

### Layer 1 — Methodology (`examples/METHODOLOGY.md`)

The 12-step protocol that produces every example. Plain English
prose. No machine-readable form. The methodology is the
specification; everything else exists to make it easier to follow
and harder to deviate from.

### Layer 2 — Skill (`skills/perf-simulation/`, `perf-simulation.skill`)

The methodology compiled into a Cowork skill. The skill is what
makes an LLM agent capable of executing the protocol end to end. It
encodes the methodology as a sequence of gates (audit before code,
smoke test before sweep, validation before metric critique,
`MODEL.md` sync after every code change), and bundles the
references (audit protocol, theory glossary, metric checklist) and
the templates (Layer 3).

The skill is the v2 analogue of v1's MCP server — it is what makes
the agent capable of driving the workflow — but it operates by
*loading context*, not by *exposing tools*. There are no endpoints,
no schemas, no daemons.

### Layer 3 — Templates (`skills/perf-simulation/templates/`)

Skeleton files for `server_sim.py`, `sweep.py`, `plot_sweep.py`,
`MODEL.md`, `requirements.txt`. Templates are runnable as-is (they
encode the v2 baseline) so a new example always starts from a known
working point. Templates are versioned with the skill: when the
methodology evolves, templates evolve with it, and the skill bundle
re-packages both together.

### Layer 4 — Examples library (`examples/`)

The growing collection of worked models. Each example is a sibling
folder following the same structural shape (`server_sim.py`,
`sweep.py`, `plot_sweep.py`, `MODEL.md`, `requirements.txt`,
`sweep.png`). The shape is a contract: keeping it consistent is
what makes copy-and-extend a mechanical operation, which in turn is
what makes "the examples folder is the library" actually work.

When a pattern recurs in three or more examples (rule of three) it
becomes a candidate for extraction into a real library module.
Until then the duplication is intentional.

### Layer 5 — Calibration (planned)

A future layer that ingests real-system telemetry (logs, Prometheus,
CloudWatch, APM, probes) and uses it to fit model parameters. See
`docs/concept.md` for the user-facing description. Architecturally
it will appear as a new top-level folder (e.g. `calibration/`) with
per-source ingest tools, plus additions to the skill (a new audit
question, a new reference document, a new metric in the critique
checklist).

It is a planned **new layer**, not a new abstraction inside the
existing layers.

## How a new example is created

1. The user describes a system in natural language.
2. The agent triggers the perf-simulation skill (or the user invokes
   it explicitly).
3. The skill loads its `SKILL.md` body and forces Phase 1 — Audit:
   eight structured questions in order.
4. From the audit answers the agent drafts a `MODEL.md` using the
   template. The user confirms or edits.
5. The agent generates the example code from the templates.
6. The agent runs the smoke test, the validation sweep, and the
   metric critique. Outputs are saved to the new example folder.
7. The agent appends a `dev-log.md` entry summarising what was
   created, with tags.

The new example folder is the artefact. Everything about it is text
on disk under git. There is no separate runtime state.

## How an existing example is extended

Extension is a *new* audit (Phase 11), shorter than the initial one
but governed by the same gate. The structural rule is **copy and
extend**:

1. Copy the parent example folder to a new sibling folder.
2. Run the extension audit (`extension-audit.md`).
3. Apply the surgical diff in the copy: new `Config` fields, new
   `Resource` on `Server`, new acquire–hold–release in `_serve`.
   Nothing else changes in the parent's code.
4. Rewrite the new `MODEL.md` to reference the parent and describe
   only the diff.

`USLDBmodel` was built from `USLmodel` exactly this way and is the
canonical worked example of the extension workflow.

## Persistence and history

There is no separate workspace concept (v1 had `~/.twotakt/workspaces/`
with `model.json` and `benches/`). Persistence in v2 is the git
working tree itself:

- The model spec is `examples/<name>/MODEL.md`.
- The model code is `examples/<name>/server_sim.py` and siblings.
- Each sweep result is `examples/<name>/sweep.png`; rerunning is
  cheap so we do not store raw sweep tables.
- Cross-example evolution is in `dev-log.md` — append-only,
  chronological, tagged. This is the v2 analogue of v1's
  `list_workspaces` / `load_workspace`: instead of a database of
  workspaces, a single readable narrative under version control.
- Sharing: the entire repository is a git repo. Push to a remote
  and collaborators have everything — examples, methodology, skill,
  history.

## Component boundaries

| Component                     | Responsibility                                                                |
|-------------------------------|-------------------------------------------------------------------------------|
| User                          | NL description, audit answers, parameter and visualisation choices            |
| Agent (Cowork) + skill        | Methodology execution, audit dialog, code generation, critique, plot framing  |
| `templates/`                  | Skeleton code and document forms                                              |
| `examples/`                   | Library of worked models, double as copy-templates for new work               |
| Python + SimPy + matplotlib   | Local execution of generated code (third-party libraries)                     |
| `dev-log.md`                  | Project-level history                                                         |
| (planned) calibration ingest  | Pull observed metrics, prepare them for fitting                               |

The agent is the only active driver. Templates, library and log are
passive text. Third-party libraries are invoked from the generated
code, not from the agent.

## What v1 architectural ideas survive in v2

Only the *structural* mappings are listed here. Modelling-level
mappings (DSL primitives, degradation engines, etc.) are not part
of architecture and are not included.

| v1 architectural element             | v2 form                                                                       |
|--------------------------------------|-------------------------------------------------------------------------------|
| MCP server (`twotakt-mcp`)           | Cowork skill (`perf-simulation`) — context-loading instead of tool-exposing   |
| `build_model` MCP tool               | Audit dialog + template-driven code generation by the agent                   |
| `run_bench` MCP tool                 | `sweep.py` script per example                                                 |
| `show_model` MCP tool                | `MODEL.md` (prose spec) + `plot_sweep.py` (sweep visual)                      |
| `save_workspace` / `load_workspace`  | Git working tree; cross-example history in `dev-log.md`                       |
| `~/.twotakt/workspaces/` directory   | `examples/` directory, one folder per example, all under repo git             |
| "Real metrics ingestion" out-of-scope | Promoted to planned Layer 5 (calibration)                                    |
| Custom DSL for portability           | Dropped. SimPy directly is portable enough with LLM assistance                |

## Out of scope (structural)

These are *structural* omissions — things the project deliberately
does not have at the architecture level today. Modelling omissions
(multi-instance topologies, time-varying arrival, etc.) belong in
the per-example MODEL.md "what this model deliberately does not
include" sections, not here.

- **No daemon, server, or API surface.** Everything is files on
  disk plus an agent.
- **No GUI / web frontend.** The agent + an editor + a terminal
  are the interface. Anything richer is premature.
- **No distribution outside Cowork.** The methodology itself is
  client-agnostic, but the audit gate is enforced via the skill
  mechanism, which is Cowork-specific today.
- **No plugin marketplace.** Examples are first-class folders in
  the repo, not installable third-party artefacts.
- **No multi-user collaboration features beyond git.** Concurrent
  edits, review workflows, comment threads — git and standard
  forge tools cover these; twotakt does not add its own.
