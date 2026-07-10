# verification-validation skill — changelog

Changes are recorded per project. Each entry: what was added or changed,
which project motivated it, what gap or failure it addresses.

---

## 2026-07  Extracted from simstudy-protocol (skill modularity)

### Added
- **Skill created** by extracting Phase 7 V&V out of `simstudy-protocol`:
  the two-questions protocol (verification/validation), the executable
  `verify.py` form (Tier-1 conservation reused from `harness/`, Tier-2
  per-model law-shape + metamorphic toggles), negative-test-first,
  independence via the file boundary, the proportionality razor.
  Moved in: `references/metric-checklist.md`, `templates/verify.py`.
  Motivation: V&V techniques accumulate (verification levels,
  compositional verification are expected next) — plain modularity says
  no single skill should grow unbounded. The gate stays with the caller:
  `simstudy-protocol` Phase 7 is now a thin gate that invokes this skill;
  the technique lives here. Same split as measurement/statistics into
  `modeling-jain`.
- **Naming:** descriptive (`verification-validation`), not
  `<topic>-<author>` — the author scheme fits skills that wrap one
  published method (Lazowska, Jain); here the method is in-house and
  growing, Sargent is a source, not the owner. Backlog stays in the
  project-wide `TODO.md` (per-skill backlogs = drift), only changes are
  recorded here.

### Source
- The five-model validation-harness build-out (USLmodel, USLDBmodel,
  FaxRx, PowerSearch ×2, RadioMonitoring) — see `dev-log.md` 2026-06-17
  and `docs/article_candidate_4_vv.md`.
