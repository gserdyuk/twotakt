# twotakt — TODO

## Identity (locked)

**Name:** twotakt
**Tagline:** An AI-native methodology for building simulation models
**Subtitle:** Two phases: Audit together. Simulate autonomously.

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
      result / lesson / files) + template at `skills/simpy-protocol/templates/README.md`,
      registered in `SKILL.md`
- [x] `## Lesson` section in each README — standalone (no cross-linking), with a precise
      statement plus an "In plain terms:" expansion for outside readers
- [x] Root `README.md` synced to the two-input dichotomy; per-example README named as the
      entry point
- [ ] Still open: use the captured lessons as a concrete proof/result line in the one-pager
      (raw material now lives in the per-example README `## Lesson` sections)

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

        *Make it ONE process (the gap: build sessions verify "by prose, as they like";
        the harness is a separate practice not in the skill):*
        - [ ] Fold the harness into the skill as the **executable form of Phase 7**:
          `templates/verify.py` + the shared lib (`run_summary.py`, `invariants.py`)
          referenced from `SKILL.md`. Today Phase 7 is prose and there is no verify
          template, so nobody following the skill produces a `verify.py`.
        - [ ] **Codify independence** — Phase 7 run by a *separate* session/agent from the
          builder (the §4 correlated-blind-spots principle); the file boundary is the
          hand-off. Currently manual.
        - [ ] **Define sign-off = three human gates**, and write it into README WORKFLOW +
          skill: ① approve `MODEL.md` (intent); ② **sign off the verified model before
          sweeps** (consent / cost safeguard — gated on a green harness; green certifies
          *correctness* automatically, the human authorizes the *spend*); ③ accept
          `SIM_REPORT` (findings). Clarify the README Build→Sweep gate accordingly;
          note the fully-autonomous "green-auto, no human in the middle" as a future
          relaxation.

        *Harness mechanics:*
        - [ ] Repo-wide aggregator (`make verify`) vs keep example-level.
        - [ ] Wire into the future Build agent's "ships only green" gate.
        - [ ] Loss taxonomy: the 2-way split (`rejected`/`dropped_overload`) is coarser
          than some models' native buckets (RadioMonitoring has 6: A–E + G). Contract holds
          for Tier-1 but loses diagnostic resolution — decide whether to enrich.
        - [ ] Shared Tier-2 shape helpers — rule-of-three did **not** trigger (only USL×2;
          FaxRx/PowerSearch/RadioMonitoring use other laws). Decide: extract for the two USL
          models, or leave the small duplication.

        *Coverage gaps (untested claims surfaced by the holistic analysis):*
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
- [x] Replace `skills/simpy-protocol/templates/SIM_REPORT.md` with the merged template —
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

## RadioMonitoring (Model #5) — remaining work (NOT finished)

> Built fresh through the full protocol in a separate session; validation harness green
> (19/19, record + decode × voice/digital). The *model* is only **temporarily** considered
> done — not final. The *example* is not integrated into the library yet.

- [ ] **Model not final** — temporarily parked. Revisit modelling decisions still in flux
      (e.g. the classify/decode reading, stage-2 decode provisioning, drone/radar handling).
- [ ] **Behavioural analysis (Phase 8) not done** — the actual question (POI by category as
      density grows; what binds first, SDR pool or decode/PC) has not been answered via a
      proper sweep. Needs `sweep.py` + plot, then the verdict.
- [ ] **Integrate as a full example** — `README.md` (per template) and `SIM_REPORT.md`;
      add to the README Layout list and `CLAUDE.md` examples list (both currently name only
      four). `ARCHITECTURE.md` + `REQUIREMENTS.md` + `MODEL.md` + `verify.py` already exist.
- [ ] Decide whether the `MODEL.ru.md` duplicate stays (English-everywhere policy) and fix
      the stale "DRAFT — awaiting approval before any code" status line in `MODEL.md`.

---

## P2 — skills & repo hygiene (before any public visit)

### simpy-protocol skill

- [x] Fix stale phase references: Phase 12→9, Phase 13→9, Phase 10→8 (done 2026-06-12)
- [x] Fix typo "perfomance" in YAML `description` (done 2026-06-12)
- [ ] Rebuild `perf-simulation.skill` package from the current skill (stale: old name,
      no sweep_2d, no SIM_REPORT template, no CHANGELOG) — or delete it until packaging
      is automated

### CLAUDE.md

- [x] Add FaxRx to the examples list in Layout (done 2026-06-12)
- [x] Fix "each example folder contains" (done 2026-06-12)
- [x] Plots rule already unambiguous in current CLAUDE.md
- [x] modeling-jain row: actual trigger words added (done 2026-06-12)

### Repo-wide

- [x] Align naming with examples' `REQUIREMENTS.md` (done 2026-06-15 — PowerSearch got a
      `REQUIREMENTS.md`; all four examples now carry `ARCHITECTURE.md` + `REQUIREMENTS.md`).
      Still open: define ТЗ once for non-Slavic readers ("REQUIREMENTS (ТЗ — tech spec)")
- [x] `.gitignore`: `__pycache__/`, `*.pyc` — already present in `.gitignore`
- [ ] Pin dependency versions in every `requirements.txt` (deferred — low real risk; no venv enforcement planned)
- [ ] Single source for methodology: keep `skills/simpy-protocol/references/methodology.md`,
      root `METHODOLOGY.md` becomes a pointer (or vice versa — pick one)
- [x] Language policy = English everywhere: translate `PowerSearch/SIM_REPORT.md`
      (done 2026-06-15 — translated RU → EN; all four reports now in English)
- [ ] Re-encode `PowerSearch/Whiteboarding scenario-plus-asr.txt` to UTF-8; CRLF → LF
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
- [ ] Build agent: writes server_sim.py, runs smoke test, self-fixes — only ships green
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
