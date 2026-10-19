---
name: Twotakt — Architecture Performance Simulation
description: "Audit-first performance modeling: an architecture description and a requirement list go in; a human-approved MODEL.md, an executable SimPy model machine-checked against it, and a bottleneck report come out."
owner: Gennadiy Serdyuk
authors:
  - "Gennadiy Serdyuk <gennadiy_serdyuk@epam.com>"
install_script: "git clone https://github.com/gserdyuk/twotakt.git"
install_script_unix: "git clone https://github.com/gserdyuk/twotakt.git"
sdlc_phase: Architecture & Design
support_level: Self-Serve
use_cases:
  - Capacity planning and bottleneck analysis before load tests
  - Comparing architecture options under identical load scenarios
  - Character of degradation at 10x load
---

# Twotakt — Architecture Performance Simulation

A kit for building a discrete-event performance model of an IT architecture with an
AI assistant: a method, four Claude skills, a validation harness and four worked
models. Two documents go in — the architecture and the requirements — and what comes
out is a `MODEL.md` the architect has read and approved, a SimPy program machine-checked
against it, and a report on where the system breaks under load. The question it answers
is **"I have an architecture; where does it break under load?"** — before production,
before load tests, before the architecture is locked.

It is not a load-testing tool and not a wrapper that hides the simulator. The SimPy
code is visible and is meant to be read; the method is what makes it trustworthy.

## Why it exists

Architects largely do not model, and until recently that was a rational calculation: a
model cost weeks of specialist work and went stale with the architecture, load testing
needs a finished system, and spreadsheets cannot see queues or cascading degradation.
At that price of verification, intuition was the cheaper instrument.

An AI assistant drops the cost of building and checking a model by an order of
magnitude, which changes the calculation rather than the arithmetic. What it does not
drop is the cost of a *wrong* model: a program that produces a plausible curve while
encoding degradation nobody intended. The whole factory is built around that single
risk.

## What runs — two takts, ten phases

**Takt 1 — audit, together with the human.** The architecture becomes a model and the
requirements become a testbench (the same split as in hardware verification: the design
and the bench). Output: `MODEL.md` — entities, flows, parameters, assumptions — plus the
load scenarios and acceptance criteria. **No simulation code exists yet.**

**Takt 2 — simulate, autonomously.** The approved model is compiled into
`executable_model.py` (SimPy), checked against the model by an executable verifier,
swept across the scenarios, and reported: throughput, latency, queues, bottleneck order,
character of degradation.

Ten gated phases in all (`skills/simstudy-protocol/`): inputs → architecture audit →
structural decomposition → model per entity → build → parameter sources → testbench →
verification & validation → behavioral analysis → iterate → report. The phases are many;
the moments that need the human are few.

## The audit gate — read before running anything

**No simulation code is written before the human has approved `MODEL.md`.** This is the
one rule the factory is built on, and it is not a style preference. Remove it and the
assistant will still produce a model, a curve and a report — they just stop meaning
anything, because the artifact being trusted is then code nobody specified, and the
mismatch between what the architect meant and what the program does is invisible in a
plot.

Two verifications, two verifiers, and they are not interchangeable:

- **The human certifies the intent.** `MODEL.md` is the spec and the source of truth.
  When the code and the model disagree, the code is the bug.
- **The machine certifies that the code honours it.** `verify.py` plus the shared
  harness in `harness/`: Tier-1 conservation invariants (nothing created or lost),
  Tier-2 law-shape checks and metamorphic toggles, and negative tests that must fail
  on a deliberately broken model. Green means *the code implements the model*; it
  never means *the model is right about the world*.

A second human gate sits after the verifier and before the sweeps — the verifier
certifies correctness automatically, the human authorizes the spend.

## Components

Four skills, usable together or on their own:

| Skill | What it is for |
|-------|----------------|
| `simstudy-protocol` | The entry point: the audit-first ten-phase protocol from inputs to report. |
| `verification-validation` | The executable trust check between building a model and paying for sweeps. |
| `queueing-lazowska` | Analytical answers without simulation — M/M/c, MVA, operational laws, "how many servers?". |
| `modeling-jain` | Statistical rigour on the way in and out: distribution choice, confidence intervals, measurement-mistake audit. |

The last two are standalone instruments: a capacity question that closed-form queueing
theory answers in a minute should not be simulated at all.

## How to use

1. `git clone https://github.com/gserdyuk/twotakt.git`
2. Open the clone in Claude Code **with the session starting in the repository root** —
   the root `CLAUDE.md` is what loads the skills. (Sanity check: ask "What is this
   project?"; the answer should mention Twotakt and audit-first.)
3. To see the method before using it, open any folder in `examples/` and read its
   `README.md`, then `ARCHITECTURE.md` + `REQUIREMENTS.md` → `MODEL.md` → `SIM_REPORT.md`.
4. To model your own system: bring the architecture and the requirements, say "I have an
   architecture, let's model it", answer the audit's questions and approve `MODEL.md`.

Requires Python 3.10+ and Claude Code. Worked models in `examples/`: **USLmodel**
(a single server with Universal Scalability Law degradation), **USLDBmodel** (the same
with a database connection pool — cascaded bottlenecks), **PowerSearch** (a search
aggregator, two pipelines, capacity planning), **FaxRx** (worldwide fax reception,
Erlang B plus OCR, built on a production platform).

## Standing and limits

- **A workspace, not an installable package.** Today the skills are read from disk by
  the repository's `CLAUDE.md`, so the method is used by moving into a clone rather than
  from inside your own project. Packaging it (skills as a Claude Code plugin, the
  harness as a pip package) is a known, deliberately deferred step; one consequence is
  visible in `simstudy-protocol`, whose description still points at `twotakt/examples`.
- **No production outcome is claimed.** The examples are models, including one built on
  a real platform (FaxRx); none is a prediction that was later scored against a measured
  production result. The published write-up of the FaxRx result — the success-rate
  paradox, fail fast or fail slow — is in `articles/fail-fast-or-fail-slow.md`.
- **Approximate by design.** The factory does not offer exact numbers. It answers the
  questions that survive error: what breaks first, option A or B on identical scenarios,
  what the degradation looks like at 10x load. Those are the questions intuition answers
  worst, because queues and cascades are nonlinear.
- The three-agent split of Takt 2 (Build / Sweep / Report as separate agents) is the
  target architecture and is not implemented; Takt 2 runs today as one gated session.

## Further reading

- [`README.md`](README.md) — what the thing is, the phase table, how to start.
- [`skills/simstudy-protocol/SKILL.md`](skills/simstudy-protocol/SKILL.md) — the protocol itself.
- [`harness/`](harness/) — what the automatic "green" covers, and what it does not.
- [`docs/`](docs/) — concept and roadmap, the critique, the verifiability argument.
- [`findings.md`](findings.md) — the register: *why* it is built this way.

License: Apache 2.0, copyright Gennadiy Serdyuk. Canonical repository:
https://github.com/gserdyuk/twotakt
