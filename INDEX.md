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
- [articles/](articles/index.md) — published EN long-form articles (frozen records): #3 fail-fast/slow, #7 LLM-wiki staleness; `_config.yml` makes GitHub Pages serve README + articles only (corpus excluded)

## Research corpus (accumulates; contradictions are dated history)

- [dev-log.md](dev-log.md) — the lab journal: append-only, dated, `#tag`-greppable
- [findings.md](findings.md) — the findings register: F-numbered claims + pointers to long forms
- [docs/verifiability.md](docs/verifiability.md) — theory (DRAFT): the map (model kinds, gates A/B/C, solvers) + the verifiability-by-construction doctrine
- [docs/article_candidate_4_vv.md](docs/article_candidate_4_vv.md) — article #4 long form (lead candidate): invariant/intent verification for LLM-generated simulations
- [docs/article_candidate_1_audit_first.md](docs/article_candidate_1_audit_first.md) — article #1 short form: audit-first, spec is primary ("when they diverge, the code is the bug")
- [docs/article_candidate_2_interaction_bottleneck.md](docs/article_candidate_2_interaction_bottleneck.md) — article #2 short form: component ceilings don't compose (USLDBmodel, F10)
- [docs/article_candidate_3_fail_fast_slow.md](docs/article_candidate_3_fail_fast_slow.md) — article #3 short form: same success rate, opposite failure UX (FaxRx; admission vs congestion loss)
- [docs/linkedin_post_3_fail_fast_slow.md](docs/linkedin_post_3_fail_fast_slow.md) — approved LinkedIn draft for #3: first post of the warm-up series (order #3 → #2 → #1; #4 reserved for long form); companion diagram `docs/linkedin_post_3_architecture.png`
- [docs/dou_article_3_fail_fast_slow.md](docs/dou_article_3_fail_fast_slow.md) — DOU.ua longread draft for #3 (Ukrainian): the full story incl. Erlang B, honest metrics, limitations; publish 1–2 weeks after the LinkedIn post
- [docs/article_candidate_5_ai_architectural_landscape.md](docs/article_candidate_5_ai_architectural_landscape.md) — series "AI Influence on the Architectural Landscape" S1: microservices = modularity + distribution; AI removes the first reason
- [docs/article_candidate_6_reverification_surface.md](docs/article_candidate_6_reverification_surface.md) — series S2: unit of architecture = unit of re-verification; #4 is the precondition of "just regenerate it"
- [docs/article_candidate_8_lifecycle_economics.md](docs/article_candidate_8_lifecycle_economics.md) — series-adjacent (≠ S3 infra-TCO): uneven AI compression of lifecycle phases, Amdahl residue = analysis+oracle (F29), architecture as coefficient multiplier (F31), four unglued boundaries (F32), spec as context compression (F33); price-model sketch — likely a separate project
- [docs/article_candidate_7_passports_corpus_surface.md](docs/article_candidate_7_passports_corpus_surface.md) — meta: staleness solved by not promising currency; passports + corpus/surface vs the LLM-wiki thread's pain
- [docs/linkedin_post_7_llm_wiki_staleness.md](docs/linkedin_post_7_llm_wiki_staleness.md) — approved drafts for #7: gist field-report comment + LinkedIn note (jumps ahead of S1)
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
- 2026-07-24 — DOU #3 review pass: success rate = on-time rate, not delivery (F34); FaxRx count vs tail bound by different cascaded bottlenecks (F35); article corrected (T1/E1, metric reframing, title = success-rate paradox); FaxRx code + ARCHITECTURE.md:117 "overnight baseline" wording parked, not fixed
- 2026-07-29 — USLDBmodel re-verification for article #2: single-seed exhibit killed (F36), USL closed-form ceiling ~7.2 (F37), pool binds only past crossover db_query > c/X_cpu* (F38); article #2 reframed "bottleneck is a regime, not a component", RU draft [docs/article_2_bottleneck_regime_rus.md](docs/article_2_bottleneck_regime_rus.md)
