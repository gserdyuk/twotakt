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

Each example folder typically contains: `server_sim.py`, `sweep.py`,
`plot_sweep.py`, `MODEL.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`, and `sweep.png`.
Not every example has all files (FaxRx lacks `plot_sweep.py` / `sweep.png` — in progress).

## Local skills

This project ships three skills in the `skills/` directory. They are **not**
installed globally — Claude must read them from disk. When a relevant task
arises, read the corresponding `SKILL.md` and follow the protocol it defines.

| Skill | Path | When to use |
|-------|------|-------------|
| `simpy-protocol` | `skills/simpy-protocol/SKILL.md` | Building or extending a SimPy simulation; modeling throughput, latency, queues, bottlenecks under load. **Always start here.** Requires ТЗ + Architecture as inputs. |
| `queueing-lazowska` | `skills/queueing-lazowska/SKILL.md` | Analytical answers without simulation: capacity planning, utilization, bottleneck device, "how many servers?" |
| `modeling-jain` | `skills/modeling-jain/SKILL.md` | Statistical rigour for simulation inputs and outputs. |

### Trigger words

Load **simpy-protocol** when the user mentions: simulation, SimPy, throughput,
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
