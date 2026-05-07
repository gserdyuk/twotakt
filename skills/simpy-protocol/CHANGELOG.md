# simpy-protocol skill — changelog

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

## 2026-05  SimPy ecosystem research (yinchi/simpy-examples + ccfelius/queueing)

### Added
- **M/D/c variant** — `theory-glossary.md` M/M/c section
  Deterministic service time (`env.timeout(constant)` vs `expovariate`).
  Lower variance; knee shifts right vs M/M/c at same mean.
  *(Source: ccfelius/queueing MDN.py, yinchi/simpy-examples ex06_mdkk.py)*

- **PriorityResource / priority queue** — `theory-glossary.md` new section
  `simpy.PriorityResource` enables SJF or multi-class priority dispatch.
  Not in any previous project; added because it appeared in ccfelius/queueing
  and covers a gap for multi-SLA systems.
  *(Source: ccfelius/queueing MM1_SJ.py)*

- **M/M/k/k finite-capacity (no-queue) variant** — `theory-glossary.md` connection pool section
  When all servers are busy, reject immediately without queuing.
  Pattern: check `resource.capacity == len(resource.users)` before request.
  *(Source: yinchi/simpy-examples ex04_mmkk.py)*

- **Abandonment / customer impatience** — `theory-glossary.md` new section
  Request cancels *while waiting in queue* (patience timeout), before server
  acquires it. Self-limiting effect: masks saturation by reducing queue length.
  Track abandonment rate separately from SLA timeout count.
  *(Source: yinchi/simpy-examples ex03_mmk_abandonment.py)*

- **Q4c — Multiple arrival streams** — `audit-protocol.md` Q4
  Sub-question for parallel `arrival_process` generators (e.g. reads vs writes,
  priority vs best-effort). Default: one stream. Use multiple only when classes
  have distinct resource paths or SLAs.
  *(Source: yinchi/simpy-examples ex09_mmc_two_priorities.py, ex10_mmc_two_classes.py)*

- **Phase 7 analytical ceiling validation** — `SKILL.md`
  After sweep: compare simulated plateau against `capacity / service_time_mean`.
  >5% gap → secondary pool binding or wrong service-time draw.
  *(Source: ccfelius/queueing — models include analytical formulas for direct comparison)*

### Not added (noted for future)
- MiSim (retry, circuit breaker, fault injection) — currently out of scope (Q7).
  Review before extending the skill with resilience mechanisms.

### Source
- github.com/yinchi/simpy-examples
- github.com/ccfelius/queueing

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
