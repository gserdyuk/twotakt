# twotakt — INDEX

> **Type: register** — the catalog: pointers only, pruned at compaction · born 2026-07-10

The catalog: one line per thing worth finding again — a pointer and a hook, **never
content**. Triggers: new file → line here; important dev-log entry → line here; new
finding → entry in [findings.md](findings.md) (big clusters get their own doc + a
line here). Curated, not exhaustive: dev-log answers "what happened" (greppable by
`#tags`); this file answers "what does the project have and know". Pruned at
compaction time, same rhythm as findings.md.

## Product surface (small, synchronized, contradiction-free)

- [README.md](README.md) — the outward face: what/why/how to start; takts↔phases map
- [CLAUDE.md](CLAUDE.md) — how Claude works here: skills, key constraints, locked vocabulary
- [TODO.md](TODO.md) — plans and state; the single project-wide backlog (skills carry only CHANGELOGs)
- [docs/twotakt-one-pager.md](docs/twotakt-one-pager.md) / [RU](docs/twotakt-one-pager-rus.md) — pitch one-pagers (EN canonical)
- `skills/` — the method itself: `simstudy-protocol` (entry point), `verification-validation`, `queueing-lazowska`, `modeling-jain`
- [harness/](harness/README.md) — executable Tier-1 conservation + runner; what "green" means (and does not) in its README

## Research corpus (accumulates; contradictions are dated history)

- [dev-log.md](dev-log.md) — the lab journal: append-only, dated, `#tag`-greppable
- [findings.md](findings.md) — the findings register: F-numbered claims + pointers to long forms
- [docs/verifiability.md](docs/verifiability.md) — theory (DRAFT): the map (model kinds, gates A/B/C, solvers) + the verifiability-by-construction doctrine
- [docs/article_candidate_4_vv.md](docs/article_candidate_4_vv.md) — article #4 long form (lead candidate): invariant/intent verification for LLM-generated simulations
- [docs/concept.md](docs/concept.md) — vision-only: problem / differentiator / landscape / calibration direction
- [docs/critique.md](docs/critique.md) — dated adversarial review with response statuses + the five-point external critique
- `docs/archive/` — superseded scenes: concept-v1, architecture-v1/v2, architecture-llm-layers essay; future findings-vN

## Examples (worked evidence; per-example `## Lesson` holds the finding)

- `examples/USLmodel` — USL degradation, three regimes; survivorship-bias / effective-latency lesson
- `examples/USLDBmodel` — the interaction bottleneck: pool=1 collapses at ~6 rps despite ~20 rps component ceilings (F10)
- `examples/PowerSearch` — two pipelines; composition topologies lesson: series vs fan-in (F11)
- `examples/FaxRx` — Erlang-B blocking; fail-fast vs fail-slow lesson
- `examples/RadioMonitoring` — DRAFT project, parked for rework; the independent build→verify experiment that caught a real bug (article #4's Figure-1 candidate)

## Key decisions (pointers into dev-log)

- 2026-06-15 — spec = goal, not invariant (F1); the tier structure by authorship → article #4
- 2026-06-17 — harness folded into the skill as executable Phase 7; verifier independence codified; sign-off gates defined
- 2026-07-06..08 — release prep: skill renamed to simstudy-protocol, vocabulary locked, methodology.md retired (F24), "ТЗ" eliminated from English
- 2026-07-08 — the project speaks ISO/IEC 42010: performance = the current concern; viewpoint-vs-perspective is school-dependent (framing later kept internal-only)
- 2026-07-09 — verifiability.md written (the theory day: F12–F23); scope paragraphs added to README/one-pagers, then deliberately removed (concern → attribute → deletion)
- 2026-07-09 — prior-art verdicts: "verifiability by construction" usable (cite CbC + Design for Verification); "design for modelability" free but SEI PACC is the close program
- 2026-07-10 — V&V extracted into its own skill; RadioMonitoring declared DRAFT project; stale docs archived, concept.md rewritten vision-only (F25)
- 2026-07-10 — research-project reframing: corpus/surface split, findings.md + INDEX.md created, findings ladder in CLAUDE.md
