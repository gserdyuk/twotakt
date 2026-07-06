# twotakt — Claude instructions

## Project overview

Workspace for building discrete-event SimPy simulations with an audit-first
methodology. No simulation code is written before the model spec (`MODEL.md`)
is approved by the user.

## Layout

```
skills/              ← local Claude skills (see below)
examples/            ← worked SimPy models (PowerSearch, USLmodel, USLDBmodel, FaxRx)
docs/                ← concept, architecture, critique
dev-log.md           ← append-only project log
```

Each example folder typically contains: `README.md`, `executable_model.py`, `sweep.py`,
`plot_sweep.py`, `MODEL.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`, `SIM_REPORT.md`,
and `sweep.png`. PowerSearch additionally splits into `model1_ingestion/` and
`model2_queries/` subfolders, each with its own model files.

## Local skills

This project ships three skills in the `skills/` directory. They are **not**
installed globally — Claude must read them from disk. When a relevant task
arises, read the corresponding `SKILL.md` and follow the protocol it defines.

| Skill | Path | When to use |
|-------|------|-------------|
| `simstudy-protocol` | `skills/simstudy-protocol/SKILL.md` | Building or extending a SimPy simulation; modeling throughput, latency, queues, bottlenecks under load. **Always start here.** Requires REQUIREMENTS + Architecture as inputs. |
| `queueing-lazowska` | `skills/queueing-lazowska/SKILL.md` | Analytical answers without simulation: capacity planning, utilization, bottleneck device, "how many servers?" |
| `modeling-jain` | `skills/modeling-jain/SKILL.md` | Statistical rigour for simulation inputs and outputs. |

### Trigger words

Load **simstudy-protocol** when the user mentions: simulation, SimPy, throughput,
latency, queue, bottleneck, capacity, p99, overload, degradation, M/M/1, M/M/c,
USL, "what happens under load", узкое место, очередь, нагрузка.

Load **queueing-lazowska** when the user wants a quick analytical estimate without
running code: "how many servers do I need", "which device saturates first",
"what is the throughput ceiling".

Load **modeling-jain** when the user wants to: parameterize a model from real
monitoring data; choose a service-time distribution; compute confidence intervals
for sweep results; or audit a performance study for common measurement mistakes.

## Key constraints

- **Audit gate is non-negotiable.** Never write simulation code before Phase 1
  (audit) is complete and the user has approved the `MODEL.md` draft.
- **Spec is primary.** `MODEL.md` is the source of truth; the code is its
  implementation. When they diverge, the code is the bug.
- Every numeric parameter lives on `Config` — no magic numbers in function bodies.
- Plots must show throughput, success rate, and latency together — the number of panels is determined by the question, not by a fixed rule.
- Sync `MODEL.md` after every code change that touches `Config`, `Server.__init__`,
  or `_serve`.
- **ASCII only in code.** Use plain ASCII in Python source — especially in any
  string printed to stdout. The Windows console is cp1251 and crashes
  (`UnicodeEncodeError`) on non-ASCII like `①②→`. Markdown docs (`.md`) may use
  Unicode; console output and code must not.
- **Vocabulary is locked.** `MODEL.md` = **the model** (spec, human-verified);
  `executable_model` (file `executable_model.py`) = **the code** (machine-verified
  against the model); `simulation` = **the run** (a process, not an artifact — never
  name a file "the simulation"). Bare "model" always means `MODEL.md`; the code is
  always `executable_model`. "SimPy model" is fine as descriptive prose for an actual
  SimPy example.
- **dev-log discipline.** After any significant change (a rename, a new example, a
  methodology or spec decision, a policy call), append a dated entry to `dev-log.md`
  capturing the *why*, not just the *what*. Append-only — never edit past entries.
- **Example policy.** Example folder names are the author's free choice (the *internal*
  file layout is the convention, not the folder name). An in-progress example lives in
  `examples/` but stays out of `README.md` and the one-pagers until it is ready — a
  folder present but unlisted is intentional, not a documentation gap.
- **No "ТЗ" in English.** In English docs and code, the input document is **Requirements**
  (file `REQUIREMENTS.md`) — never the Russism "ТЗ". Do not use "Spec" for it either: that
  word is reserved for `MODEL.md` (the model spec). Russian-language docs (e.g. the RU
  one-pager) may keep "ТЗ".

## Working rules

New conventions that emerge during work go in the **Key constraints** section above —
`CLAUDE.md` is loaded every session, so rules Claude must always follow belong here (not
in memory, which surfaces only selectively). Machine- or account-specific details (e.g.
git identity) do **not** go here — this file is committed to a public repo; keep those in
memory instead.
