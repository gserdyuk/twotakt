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

### Sync pass (from 2026-06 reviews)

- [ ] **Phase 2 honesty:** "currently runs as a gated Claude session following the
      10-phase protocol; the three-agent split is the target architecture"
- [ ] "Real system" → "realistic case study" (PowerSearch: from an architecture
      whiteboarding scenario; FaxRx: based on a production fax platform the author worked on)
- [ ] Narrow positioning: drop "and beyond" from header; shrink Use cases to one line
      ("examples are IT systems; the methodology itself only assumes shared resources,
      queues and contention")
- [ ] Align speed claim with one-pager ("days to weeks" vs "недели" — pick one)
- [ ] Reading path Option A: ARCHITECTURE → MODEL → **SIM_REPORT** (code for those who
      want the machinery); `pip install -r requirements.txt` instead of bare simpy
- [ ] Reuse one-pager framing where useful ("architects don't model — and were right",
      example-library list)
- [ ] Consider promoting "Audit together. Simulate autonomously." into the one-pager

---

## P1 — before IPRI / mentor pilot (blocking)

### Bring examples up to the current skill standard

> The skill already prescribes this (templates have `seed` on Config; Phase 9 mandates
> r ≥ 10 replications, warm-up discard, t-based CI via `modeling-jain/templates/ci_calc.py`).
> The examples predate it — they lag the skill, not the other way around.

- [ ] Retrofit `seed` into every example `Config`; thread through all random draws
- [ ] Sweeps: r ≥ 10 replications per point (r ≥ 20 for p95), report mean ± 95% CI
- [ ] Pin dependency versions in every `requirements.txt`
- [ ] Save the full run `Config` alongside results (into `sweep_results.json`)

### Verification harness

- [ ] One command (`make verify` / `verify.py`) that runs Phase 7 V&V (smoke test +
      validation criteria from `MODEL.md`) for every example. Turns examples into
      regression-tested exhibits; practical answer to "can generated code be trusted".
      Natural pairing with the future Build agent's "only ships green" rule.

### Pilot-facing docs

- [ ] **WORKFLOW.md** (or README section): map the two takts to the 10 phases —
      artifacts at each step, where the human confirmation gates stand. Bridges the
      README vocabulary (takts) and the skill vocabulary (phases); a pilot user must
      see their role without asking.
- [ ] Commit `SIM_REPORT.md` to USLmodel, USLDBmodel, FaxRx (drafts ready 2026-06-11 —
      review interpretations first)
- [ ] Replace `skills/simpy-protocol/templates/SIM_REPORT.md` with the merged template
      (merged draft ready — adds Data source header, Sweep design, Limitations; fixes
      stale "Phase 13" ref). Do NOT keep a second copy at repo root.

---

## FaxRx — remaining work

- [ ] `plot_sweep.py` — sweep visualisation (4 panels)
- [ ] Run plot, verify curves are readable
- [ ] `SIM_REPORT.md` — draft ready (2026-06-11, from committed sweep_results.json) —
      review interpretations (esp. fail-fast vs fail-slow framing and the redial
      limitation), then commit

---

## P2 — skills & repo hygiene (before any public visit)

### simpy-protocol skill

- [ ] Fix stale phase references after renumbering: "see Phase 12 below" (extension
      audit is Phase 9), "sensitivity list for Phase 13" (no Phase 13), "a sweep is
      Phase 10 repeated" (sweep is Phase 8; Phase 10 is the report)
- [ ] Fix typo "perfomance" in YAML `description` — it is a trigger string
- [ ] Rebuild `perf-simulation.skill` package from the current skill (stale: old name,
      no sweep_2d, no SIM_REPORT template, no CHANGELOG) — or delete it until packaging
      is automated

### CLAUDE.md

- [ ] Add FaxRx to the examples list in Layout
- [ ] Fix "each example folder contains" (FaxRx lacks plot_sweep/sweep.png; list also
      omits ARCHITECTURE.md / REQUIREMENTS.md)
- [ ] Rewrite the plots rule unambiguously: "throughput, success rate, latency are
      mandatory metrics; panel layout is determined by the question"
- [ ] modeling-jain row: write actual trigger words instead of "see SKILL.md"

### Repo-wide

- [ ] Define ТЗ once for non-Slavic readers ("REQUIREMENTS (ТЗ — tech spec)"), align
      naming with examples' `REQUIREMENTS.md`
- [ ] `.gitignore`: `__pycache__/`, `*.pyc` (committed in skill templates now)
- [ ] Single source for methodology: keep `skills/simpy-protocol/references/methodology.md`,
      root `METHODOLOGY.md` becomes a pointer (or vice versa — pick one)
- [ ] Language policy = English everywhere: translate `PowerSearch/SIM_REPORT.md`
- [ ] Re-encode `PowerSearch/Whiteboarding scenario-plus-asr.txt` to UTF-8; CRLF → LF
- [ ] Verify the `modeling-jain/references/workload.md` reference in
      `USLDBmodel/MODEL.md` resolves as a relative path from the example
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

---

## Product positioning

- [x] Name justified: twotakt = Phase 1 (audit) + Phase 2 (simulation)
- [x] Form: GitHub + README (lab project)
- [x] Entry point defined: "I have an architecture — find the bottlenecks"
- [x] Claude dependency: not a problem at this stage
- [x] README written
