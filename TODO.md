# twotakt — TODO

## Identity (locked)

**Name:** twotakt (repo / paths) · **TwoTakt** (display / brand)
**Tagline:** An AI-native methodology for building simulation models
**Subtitle:** Two phases: Audit together. Simulate autonomously.
**Entry-point skill:** `simstudy-protocol` (renamed 2026-07 from `simpy-protocol` —
SimPy is a swappable engine, not the method; audit-first lives in the description, not the name)
**Vocabulary (locked 2026-07):** `MODEL.md` = the model (spec, human-verified) ·
`executable_model` = the code (machine-verified against the model) · `simulation` = the run
(a process). Bare "model" always means MODEL.md; the code is always `executable_model`.
**Example naming:** deliberately free (author's choice); the internal file layout is the convention.

---

## Release prep (done 2026-07)

- [x] Skill renamed `simpy-protocol` → `simstudy-protocol` (commit 29d28b8; rationale in the
      skill `CHANGELOG.md`). Name says what it is; audit-first is the description's first line.
- [x] Code artifact renamed `server_sim.py` → `executable_model.py` repo-wide, and the
      model / executable_model / simulation vocabulary unified across README, skill, and both
      one-pagers (commits d6a2a3a, cc2fc8f). "SimPy model" left as descriptive prose where it
      names an actual SimPy example.
- [x] README rebuilt from the one-pager (1dad4c9) + getting-started vocab fix (ee47e28).
- [x] Methodology schema diagram — `docs/methodology.svg` (self-contained, phase-numbered),
      referenced under "Under the hood" (d9147b0, 8ea8f0c).
- [x] Git history rewritten to a single author identity (gserdyuk@gmail.com); stale merged
      branches pruned; repo-local git config set (do NOT set global — work machine).
- [x] Policy: in-progress examples stay in-repo but out of README / one-pagers until ready
      (RadioMonitoring is currently in-repo, intentionally not listed).

---

## README (done — needs sync pass)

### What README should convey in 2 minutes

- What this is (methodology + tool, not just SimPy templates)
- Why (audit-first: understand the system before writing code)
- How to start (entry point)
- Structure (skills/ + examples/)

### Entry points

**A. You have an architecture:**
> "I have a service architecture — I want to find the bottlenecks under load"
→ Open Claude + twotakt → run audit → get model → see where it breaks

**B. You are designing a system:**
> "I'm designing a system — I want to estimate capacity before writing code"
→ Same flow, at design time

Entry phrase for README:
> *"I have an architecture. Where does it break under load?"*

### Sync pass (done 2026-06-12)

- [x] Phase 2 honesty: note added (gated Claude session; three-agent split is target)
- [x] "Real system" → "realistic case study" for PowerSearch and FaxRx
- [x] Drop "and beyond" from header; Use cases → "Why now" section (one-pager framing)
- [x] Speed claim: "days to weeks" (aligned with one-pager)
- [x] Reading path: ARCHITECTURE → MODEL → SIM_REPORT; `pip install -r requirements.txt`
- [x] "Architects don't model" framing added as "Why now" section
- [x] "Audit together. Simulate autonomously." promoted into one-pager title

### Positioning + example-library pass (done 2026-06-15)

- [x] One-pager rewritten around the two-input dichotomy (architecture → model,
      requirements → testbench/acceptance criteria); AWS reference dropped; reasons
      turned into a list; offer names both documents
- [x] One-pager translated to English: `docs/twotakt-one-pager.md` (EN, canonical name);
      RU original → `docs/twotakt-one-pager-rus.md`
- [x] Per-example `README.md` for all four examples (input / model / how to run / output /
      result / lesson / files) + template at `skills/simstudy-protocol/templates/README.md`,
      registered in `SKILL.md`
- [x] `## Lesson` section in each README — standalone (no cross-linking), with a precise
      statement plus an "In plain terms:" expansion for outside readers
- [x] Root `README.md` synced to the two-input dichotomy; per-example README named as the
      entry point
- [x] Use a captured lesson as a concrete proof/result line in both one-pagers (done 2026-07):
      the USLDBmodel interaction-bottleneck (pool=1 collapses at ~6 rps despite a ~20 ceiling)
      added to "What exists now" / "Что есть сейчас".

---

## P1 — before IPRI / mentor pilot (blocking)

### Bring examples up to the current skill standard

> The skill already prescribes this (templates have `seed` on Config; Phase 9 mandates
> r ≥ 10 replications, warm-up discard, t-based CI via `modeling-jain/templates/ci_calc.py`).
> The examples predate it — they lag the skill, not the other way around.

- [x] Retrofit `seed` into every example `Config`; thread through all random draws — already present in all four examples
- [ ] Sweeps: r ≥ 10 replications per point (r ≥ 20 for p95), report mean ± 95% CI
- [x] Save the full run `Config` alongside results (into `sweep_results.json`) — done 2026-06-12: USLmodel/USLDBmodel теперь сохраняют JSON; FaxRx включает config; PowerSearch добавляет config + seeds в каждую строку

### Verification harness

- [ ] One command (`make verify` / `verify.py`) that runs Phase 7 V&V (smoke test +
      validation criteria from `MODEL.md`) for every example. Turns examples into
      regression-tested exhibits; practical answer to "can generated code be trusted".
      Natural pairing with the future Build agent's "only ships green" rule.
      - `harness/` package (RunSummary contract + Tier-1 conservation invariants +
        per-example check runner). `verify.py` done for **all four examples / five models**:
        USLmodel (6/6), USLDBmodel (7/7), FaxRx (6/6), PowerSearch ingestion (5/5) +
        queries (5/5) — all green, each negative-tested. FaxRx (Erlang-B, multi-class)
        forced a contract refactor: `dropped` → `rejected` (admission, by design) +
        `dropped_overload` (congestion); backward compatible. Cross-model trend + the
        PowerSearch prediction test recorded in `docs/article_candidate_4_vv.md` §9b.
      - **RadioMonitoring (Model #5)** added — built fresh through the full protocol in a
        *separate* session (independence), verified cold here. Independent verifier caught a
        real bug (digital uncapturable: classification gated recording, t_class = block
        length); architect reworked (concurrent classify + a stage-2 decode pipeline);
        re-verify 19/19 green (record + decode × voice/digital). Loop closed end-to-end.
        See `dev-log.md` 2026-06-17.
      - **Still open — V&V / process (consolidated):**

        *Make it ONE process (done 2026-06-17 — harness folded into the skill):*
        - [x] Harness is the **executable form of Phase 7** — `SKILL.md` Phase 7 rewritten
          to prescribe an executable `verify.py` (Tier-1 conservation reused + Tier-2
          per-model metamorphic toggles, negative-tested); `templates/verify.py` added and
          registered; a "Validation harness" section points to `harness/` + `harness/README.md`.
        - [x] **Independence codified** — Phase 7 now says "prefer running V&V in a separate
          session/agent from the builder" (file boundary = hand-off).
        - [x] **Sign-off defined in the skill** — Phase 7→8 gate = green certifies correctness
          automatically ("ships only green") + human sign-off before sweeps (consent/cost).
          ① MODEL.md approval is the Phase 1 gate; ③ report acceptance is Phase 10.
        - [x] Sign-off / gate wording mirrored into the **README WORKFLOW** takts↔phases table
          (done 2026-06-17): Phase 7 gate = green-auto correctness + human sign-off before
          sweeps; "moments that need you" updated; autonomous green-auto noted as a future
          relaxation. README and skill now say the same thing.
        - [x] **Shared-lib location — resolved: keep repo-root `harness/`.** twotakt IS the
          workspace (users model their own system inside `examples/`), so there is no cross-repo
          need. Vendoring the lib is only relevant if/when the skill is packaged for global
          install — folded into the existing "rebuild the `.skill` package" item (P2), not a
          live decision.

        *Harness mechanics (now owned by the `verification-validation` skill —
        backlog stays here, project-wide TODO):*
        - [ ] Repo-wide aggregator (`make verify`) vs keep example-level.
        - [ ] Wire into the future Build agent's "ships only green" gate.
        - [ ] Loss taxonomy: the 2-way split (`rejected`/`dropped_overload`) is coarser
          than some models' native buckets (RadioMonitoring has 6: A–E + G). Contract holds
          for Tier-1 but loses diagnostic resolution — decide whether to enrich.
        - [ ] Shared Tier-2 shape helpers — rule-of-three did **not** trigger (only USL×2;
          FaxRx/PowerSearch/RadioMonitoring use other laws). Decide: extract for the two USL
          models, or leave the small duplication.

        *Coverage gaps (untested claims surfaced by the holistic analysis; owned by
        the `verification-validation` skill, backlog stays here):*
        - [ ] `generated` ledger term is built but never exercised — a generating system
          (keep-alive / heartbeat) would test it (and the self-amplification → emergence
          boundary).
        - [ ] Shared-resource / **fan-in interference** never modelled or tested (the
          PowerSearch shared-Elasticsearch gap) — the most interesting untested coupling.
        - [ ] Domain boundary: continuous / non-DES model (mass-balance) — principle
          generalizes, harness *code* does not. Confirm or refute.

        *Article:*
        - [x] Fold the Model-#5 independent build→verify result into
          `docs/article_candidate_4_vv.md` §8 (evidence) — done 2026-06-17: §8 gained the
          RadioMonitoring "strongest evidence" line, and §9c "Conclusions from the 5-model
          build-out" was added (Model-#5 + whole validation-harness conclusions + limits).

### Pilot-facing docs

- [x] **Takts ↔ phases map** (done 2026-06-15): added as a README section, not a
      separate file — a separate WORKFLOW.md was written then dropped (third source
      of the same truth = third source of drift; pilots read README, not a standalone
      doc). The section maps Takt 1 (Audit) = Phases 1–3, Takt 2 (Sim) = Phases 4–10
      (Build 4–7 / Sweep 8–9 / Report 10) with a per-phase artifact in/out + human-gate
      table. Bridges README (takts) ↔ skill (phases).
- [x] Commit `SIM_REPORT.md` to USLmodel, USLDBmodel, FaxRx (done 2026-06-12)
- [x] Replace `skills/simstudy-protocol/templates/SIM_REPORT.md` with the merged template —
      root copy deleted; skills template is canonical (done 2026-06-12)

---

## FaxRx — remaining work

- [x] `plot_sweep.py` — sweep visualisation (done 2026-06-15; 3 panels: success rate /
      PSTN block rate / p95 eff vs burst, one curve per architecture; reads committed
      `sweep_results.json` since the 7200 s × 33 sweep is slow to re-run)
- [x] Run plot, verify curves are readable (done 2026-06-15 — `sweep.png` generated,
      matches the report's fail-fast/fail-slow narrative)
- [x] `SIM_REPORT.md` — committed 2026-06-12; stale "no plot" repo-note replaced with a
      Plot section (2026-06-15)

---

## RadioMonitoring (Model #5) — DRAFT project, will be reworked

> **Status decided 2026-07-10: the whole example is a DRAFT project — parked, to be
> reworked.** First build-out complete (full protocol in a separate session, verify
> 19/19 green, Phase 8 sweep + plots); the modelling decisions are being revisited
> (classify/decode reading, stage-2 provisioning, core-contention when co-located,
> drone/radar handling; user gathering real params). Marked as draft in the example's
> `README.md` and `MODEL.md`. Per-item cleanups (SIM_REPORT.md, `MODEL.ru.md`
> keep/drop) are moot until the rework — they will be redone with it. Deliberately
> not listed in README / one-pagers (showcase-when-ready policy).

---

## P2 — skills & repo hygiene (before any public visit)

### simstudy-protocol skill

- [x] Fix stale phase references: Phase 12→9, Phase 13→9, Phase 10→8 (done 2026-06-12)
- [x] Fix typo "perfomance" in YAML `description` (done 2026-06-12)
- [x] Stale root `perf-simulation.skill` package **deleted** (2026-07) — it was named two
      renames ago and missing the whole V&V/harness layer. Source of truth is
      `skills/simstudy-protocol/`; build a fresh `simstudy-protocol.skill` from it (a zip of
      the skill folder) only when/if packaging for global install is needed — and automate it
      then, so it can't drift again.

### CLAUDE.md

- [x] Add FaxRx to the examples list in Layout (done 2026-06-12)
- [x] Fix "each example folder contains" (done 2026-06-12)
- [x] Plots rule already unambiguous in current CLAUDE.md
- [x] modeling-jain row: actual trigger words added (done 2026-06-12)

### Repo-wide

- [x] Align naming with examples' `REQUIREMENTS.md` (done 2026-06-15 — PowerSearch got a
      `REQUIREMENTS.md`; all four examples now carry `ARCHITECTURE.md` + `REQUIREMENTS.md`).
      "ТЗ" eliminated from English docs (done 2026-07): the Russism was replaced by
      **Requirements** repo-wide (SKILL.md, audit-protocol, examples, article, CLAUDE.md);
      "Spec" deliberately NOT used for it (reserved for MODEL.md). RU one-pager keeps ТЗ.
      Rule recorded in CLAUDE.md Key constraints.
- [x] `.gitignore`: `__pycache__/`, `*.pyc` — already present in `.gitignore`
- [ ] Pin dependency versions in every `requirements.txt` (deferred — low real risk; no venv enforcement planned)
- [x] Single source for methodology (done 2026-07): `examples/METHODOLOGY.md` was a
      byte-identical duplicate (same SHA256) — deleted; the skill copy
      `skills/simstudy-protocol/references/methodology.md` is canonical; docs
      (architecture, concept, architecture-llm-layers, critique) repointed to it.
- [x] **methodology.md resolved (done 2026-07): retired (Option A).** The stale 12-step doc
      was deleted, not rewritten — the reason: we had tried to run "spec is primary" one level
      up (a prose methodology as the source, the skill as its compilation), and it inverted and
      rotted (the skill evolved, the doc didn't). Lesson: spec-first holds for *the model* (a
      per-project artifact a human re-approves), not for *the method* (no one re-approves it
      each run). SKILL.md is now the single source of the protocol.
- [ ] **RATIONALE for all four skills.** `skills/simstudy-protocol/RATIONALE.md` created as
      the human "why" companion to SKILL.md (phase-by-phase reasons/failure-modes) — DRAFT,
      user is adding their own reasons iteratively (open `> NOTE:` on the trust chain — the
      heart of the pitch — still to be written by the author).
      `skills/verification-validation/RATIONALE.md` created 2026-07-10 (technique-why moved
      there with the skill split; simstudy Phase 7 rationale keeps only the gate-why).
      Then mirror the pattern (shorter, tailored) to `queueing-lazowska` and `modeling-jain`,
      whose "why" is thinner (they wrap external published methods: when-to-use, assumptions,
      where-it-breaks — not failure-per-gate).
- [x] **Split V&V into its own skill (done 2026-07-10): `skills/verification-validation/`.**
      Extracted out of `simstudy-protocol`: Phase 7 detail, `references/metric-checklist.md`,
      `templates/verify.py`, the pointer to the shared `harness/` package. Phase 7 stays in
      simstudy-protocol as a thin *gate* that invokes the V&V skill (the gate belongs to the
      protocol; the technique belongs to its own skill). **Why:** many V&V techniques will
      accumulate (verification levels, compositional verification) — modularity, no skill
      grows unbounded. **Naming decided:** descriptive `verification-validation`, NOT
      `<topic>-<author>` — the author scheme fits skills wrapping one published method
      (Lazowska, Jain); here the method is in-house and growing, Sargent is a source, not
      the owner. **Backlog stays project-wide** (this file) — per-skill backlogs = drift;
      skills carry only CHANGELOGs. CLAUDE.md / README / cross-refs synced same day.
- [x] **Stale architecture/concept docs — resolved by archiving, not refreshing (2026-07-10).**
      Lesson applied (third time): current-state descriptions always lose the race with
      SKILL.md + README. `docs/architecture.md` → `docs/archive/architecture-v2.md` (kept for
      the v1→v2 decision record: why MCP/DSL were dropped); `docs/architecture-llm-layers.md`
      → archive (its top priority — externalize validation — was since implemented as the
      harness; unharvested ideas moved to P3 below). `docs/concept.md` → rewritten as a
      vision-only doc (problem / differentiator / competitive landscape / reverse-simulation
      calibration direction) — vision rots slowly, cheap to keep. `docs/critique.md` stays
      as-is: it is a dated external-critique record with statuses (dev-log-like), not a
      current-state description.
- [x] Language policy = English everywhere: translate `PowerSearch/SIM_REPORT.md`
      (done 2026-06-15 — translated RU → EN; all four reports now in English)
- [x] Re-encode `PowerSearch/Whiteboarding scenario-plus-asr.txt` to UTF-8; CRLF → LF
      (done 2026-07 — was Windows-1252 with CRLF; recovered to clean ASCII/UTF-8, LF only)
- [x] Fix `modeling-jain/references/workload.md` reference in `USLDBmodel/MODEL.md` —
      corrected to `skills/modeling-jain/references/workload.md` from repo root (done 2026-06-12)
- [ ] **REPRODUCIBILITY position** (METHODOLOGY or separate doc): MODEL.md is the
      determinism boundary. Above it AI variability is acceptable (human confirmation
      selects one model, as between two engineers); below it everything is deterministic
      and behavior-verified (fixed seeds, replications + CI, V&V harness). Include the
      canned Q&A answer for pilots.

---

## Agent architecture — next step

### Design: one dialogue + three agents

```
[Dialogue: audit] ←────────────────────────┐
        ↓                                   │ (if model is wrong)
     MODEL.md → [Agent: build] → [Agent: sweep] → [Agent: report]
      ↑ gate           ↑____________________↑
    human         bugs fixed inside agents
```

- [ ] Phase 2 = three agents: Build → Sweep → Report
- [ ] Each agent: clear input (file) + clear output (file)
- [ ] Build agent: writes executable_model.py, runs smoke test, self-fixes — only ships green
      (= verification harness as its exit criterion)
- [ ] Sweep agent: runs sweep, saves JSON
- [ ] Report agent: writes SIM_REPORT.md from JSON + MODEL.md (merged
      `templates/SIM_REPORT.md` is the output contract)
- [ ] Human reads artifact at each transition and says "go"
- [ ] Return to audit if sweep reveals model mismatch

### Future improvements

- [ ] Auto-orchestrator (remove human from transitions 2→3→4)
- [ ] Living model — agent connected to monitoring, updates parameters via Jain

---

## P3 — queued after pitch (timeboxed)

- [ ] **Multi-generation experiment** (timebox 10–15 h): regenerate each example 3–5×
      from the same description; diff MODEL.md structurally (components / resources /
      laws — not wording); run V&V on every variant. Side effect: MODEL.md divergence
      points = ambiguity detector for the source description. Candidate for article #2.
- [ ] **RAG over a curated textbook corpus** (harvested from the archived
      architecture-llm-layers essay, 2026-07-10): Lazowska + Jain as the starting pair;
      grounds theory answers in the canon with citations instead of model weights.
      Sizeable (weeks), separable stages.
- [ ] **Deterministic style checkers / spec-drift linter** (same source): AST check for
      magic numbers outside `Config`; diff `Config` fields ↔ MODEL.md parameter table;
      plot-structure check (throughput + success rate + latency present). Complements the
      V&V harness: the harness checks *behavior*, these check *form* — the CLAUDE.md rules
      that today hold only by discipline. Cheap (each checker tens of lines).

---

## Verifiability doc — open threads (from `docs/verifiability.md`, 2026-07-09)

> `docs/verifiability.md` (DRAFT) is the map+doctrine layer above article #4. Three
> follow-ups of different nature and weight: one protects external *wording*, one
> builds a *tool*, one tests the *theory itself*. Independent of each other; natural
> order = by increasing weight. The third is the one that matters: the first two
> improve the document, the third checks whether it lies.

- [x] **Prior-art check (done 2026-07-09).** "Verifiability by construction": no named
      method owns it; scattered descriptive uses (AI, e-voting crypto). Closest concepts,
      both now cited in verifiability.md: correct-by-construction (the parent rhyme —
      we promise *checkability*, not correctness) and **Design for Verification**
      (MEMOCODE'05 panel) — ours = DFV applied to simulation models in the
      no-oracle/AI context. Caveat: in e-voting "verifiability" is a different
      established property — footnote it for security-adjacent audiences.
      "Design for modelability": phrase free; **the program partially exists — SEI's
      "Predictability by Construction" / PACC** (Predictable Assembly from Certifiable
      Components: certified components -> predictable assemblies ≈ our §4 certificates
      + §5). Cite PACC; our delta = modelability incl. the observational half
      (calibratability) + the AI-asymmetry driver. Follow-up: read the PACC reports
      before making external novelty claims about verifiability.md §5.

- [ ] **Frame-compliance prototype in ONE example's SIM_REPORT (~1 day).**
      verifiability.md §7 (the per-run verdict) is only words so far; build it by hand
      once *before* legislating it in the skill. Why prototype-first — the project's own
      lesson, learned twice: methodology.md rotted because rules were written ahead of
      practice, and negative-test-first (article #4 §9c) showed every check's *first*
      version is wrong (doesn't bite, or bites the healthy model) — no reason frame
      monitors are the exception. Candidate example: USLmodel (simplest) or
      RadioMonitoring (richest). The work: add monitors to the run — actual
      per-component rho, observed input characteristics vs the certified frame, config
      point inside/outside the validated region — and emit a **"Frame compliance"
      section in SIM_REPORT.md**: a table of assumption / certified range / observed /
      verdict, with *directional* notes where the bias direction is known (e.g. rho in
      the amplification zone -> "top-of-sweep latencies: optimistic, treat with
      caution"). Deliverable: one worked example + a lessons list (what bit, what
      didn't) -> only then decide what enters the skill and in what form.

- [ ] **Stress-test the map on a static/stochastic example (largest — a full
      mini-example).** The whole map (the 2x2, gates A/B/C, the doctrine) was built
      from ONE cell's experience: dynamic/stochastic (DES + queueing). Its generality
      claim is untested. verifiability.md §9 records the testable prediction (i):
      transferring the methodology to a new model kind is *cheap* — layer A (audit
      gate, MODEL.md discipline) carries over unchanged, only the B/C gate tables get
      rewritten; if a real attempt finds nothing transfers, the map is wrong. The test:
      take a problem from the static/stochastic cell — **single-measurement
      direction-finder bearing error** (error budget, Monte Carlo error propagation),
      with CRLB as the analytic oracle in the role M/M/1 plays for DES. Small scope
      deliberately: one measurement, not the whole DF system. The result is an honest
      per-layer record: did A transfer unchanged? did the B table write itself from the
      doc's per-kind recipe, or need invention? did C (CI width, N sufficiency, seeds —
      Jain mechanics) carry over? All three outcomes are valuable: transfers = map
      confirmed; doesn't = honest negative result; partial = the boundary gets located.

---

## Article / pitch material (actions from captured findings)

- [ ] Article candidate: **interaction bottleneck** (USLDBmodel — component ceilings
      don't compose; pool=1 collapses at 6 rps despite a 20 rps paper ceiling)
- [ ] Article / pitch demo candidate: **fail-fast vs fail-slow** (FaxRx — same success
      rate at 10× burst, qualitatively different failure UX; undersized front door as
      admission control)
- [ ] Article #1 (90-day plan, month 2): MODEL.md / audit-first approach; reuse the
      "specification vs bug" line and the survivorship-bias example (PowerSearch)
- [ ] **Article candidate #4 — intent/consistency verification for LLM-generated
      simulations** (strongest; lead candidate). Thesis: with no oracle, trust comes from
      checking mutual consistency among independent expressions of intent. Three tiers by
      authorship: Tier 1 human-fixed conservation laws, Tier 2 spec-driven law-shape, Tier 3
      generator-authored model bounds — generator must *never* author its own trust floor
      (correlated blind spots). Tier 3 = coverage not guarantee (catches self-contradiction,
      not silent agreement); recurring Tier-3 promotes to Tier-1 by rule of three. Law-shape
      assertable only up to the *emergence boundary* (beyond it = asserting the research
      result, same trap as asserting the spec/goal). Novelty is the LLM-code angle, not
      invariant/intent testing itself. Evidence = P1 harness + multi-gen experiment (Fig 1) —
      already on the roadmap. Full reasoning: `docs/article_candidate_4_vv.md`.

---

## Product positioning

- [x] Name justified: twotakt = Phase 1 (audit) + Phase 2 (simulation)
- [x] Form: GitHub + README (lab project)
- [x] Entry point defined: "I have an architecture — find the bottlenecks"
- [x] Claude dependency: not a problem at this stage
- [x] README written
