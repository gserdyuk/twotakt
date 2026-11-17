# verification-validation skill — changelog

Changes are recorded per project. Each entry: what was added or changed,
which project motivated it, what gap or failure it addresses.

---

## 2026-11  Negative tests made persistent: the mutation suite

### Added
- **`mutants.py` per example + `harness/mutation.py`.** Negative testing was a
  one-off act (break the model by hand, see red, note it in the dev-log); after
  the next edit nobody knew whether a check still bites. Now each example keeps
  its broken models as code: named, realistic bugs, each claiming the checks it
  must turn red. `python verify.py --mutants` fails on a surviving mutant, an
  unguarded check, or a crashing mutant. `WAIVED` declares checks that
  structurally cannot fail - reported on every run, never silent.
- **`python -m harness verify-all`** (checks + mutants, every example), exact
  engine pin `requirements-verify.txt`, `constraints.txt`, and a GitHub Actions
  workflow running it on every push.
- `templates/mutants.py`.
  Motivation: repeatability of the trust floor itself. Also the method's first
  machine-found finding: RadioMonitoring's per-stage work-conservation checks are
  identities (in_flight is the residual of the same count) and can never fail -
  now WAIVED with the reason; the residual check is what guards those stages.
  Source project: twotakt's own examples (all six suites written at once).

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
