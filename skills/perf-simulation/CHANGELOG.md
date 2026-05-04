# perf-simulation skill — changelog

Changes are recorded per project. Each entry: what was added or changed,
which project motivated it, what gap or failure it addresses.

---

## 2026-05  PowerSearch (model1_ingestion + model2_queries)

### Added
- **Rule 11 (Little's Law pool ceiling check)** — `metric-checklist.md`
  Discovered when ES pool=50 would have saturated before workers at Year 5
  load (1150 ev/s, need ≥ 173 connections). Check ceiling = capacity /
  service_time_mean for every pool before running any sweep.

- **Phase 13 — SIM_REPORT** — `SKILL.md`, `templates/SIM_REPORT.md`
  Emerged organically at project end. Formalized as an optional step:
  ask if a formal report is needed; if yes, use the template.

- **Q4a burst modulation, Q4b sweep dimensionality** — `audit-protocol.md`
  Model 2 used square-wave burst (5× base, 30 s every 120 s). Added explicit
  sub-questions to Q4 for burst shape and grid dimensionality.

- **sweep_2d.py template** — `templates/sweep_2d.py`
  Model 1 required a 2D grid (num_resellers × num_workers). Template added
  with explicit warning: runtime = |DIM1| × |DIM2| × seeds.

- **Q5 CPU/IO decision gate for USL** — `audit-protocol.md`, `theory-glossary.md`
  Both PowerSearch pipelines are I/O-bound (alpha=beta=0, USL never applied).
  Added gate at top of Q5: confirm CPU-bound vs I/O-bound before choosing USL.

- **Directory-first audit rule** — `audit-protocol.md`, `SKILL.md` Phase 1
  ARCHITECTURE.md already answered Q1–Q8, eliminating the need for Q&A.
  Scan project directory before asking questions.

- **Rule: simpy.Resource count = Q2 answer count** — `server_sim.py`, `SKILL.md`
  Explicit rule against adding phantom pools or merging distinct resources.

- **"Maintaining this skill" section** — `SKILL.md`
  Convention for capturing pending updates during work and reviewing at project end.

### Changed
- `templates/server_sim.py` alpha/beta defaults: 0.02/0.001 → 0.0/0.0
  Non-zero defaults were wrong for I/O-bound workers (the more common case).

### Source projects
- `examples/PowerSearch/model1_ingestion/`
- `examples/PowerSearch/model2_queries/`

---

## 2024–2025  USLmodel + USLDBmodel (foundation)

### Established
- Core 12-phase protocol (audit-first, spec-before-code)
- MODEL.md as source of truth; code is its implementation
- USL framework (alpha/beta coefficients, CPU-bound degradation)
- Cascaded M/M/c pattern — USLDBmodel: workers + DB connection pool
- Survivorship bias / effective latency — metric-checklist Rules 1–10
- Three-panel plot standard (throughput / success rate / latency log-y)
- Anti-pattern list (write code before audit, hard-coded numbers, single-curve plots)

### Source projects
- `examples/USLmodel/`
- `examples/USLDBmodel/`
