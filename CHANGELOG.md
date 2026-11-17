# twotakt — changelog

Release-level changes of the kit as a whole. The version lives in one place,
`pyproject.toml`; each release is a git tag `v<version>` on the commit that sets it.
Semantic versioning, read for a methodology: **major** = an example or a study built
to the previous version may no longer pass (the protocol or the trust floor got
stricter); **minor** = new skills, examples or checks that do not break existing ones;
**patch** = fixes and docs. Per-skill history stays in each skill's `CHANGELOG.md`;
the reasoning behind changes is in `dev-log.md`.

---

## 3.0.1 — 2026-11-17 — local pre-push gate

### Added
- **`tools/git-hooks/pre-push`** — runs `python -m harness verify-all --no-mutants`
  (~20 s) before every push and refuses a red example (or a machine with no python +
  simpy). Enable once per clone: `git config core.hooksPath tools/git-hooks`. The full
  run with mutants stays in CI. Patch: no example's pass/fail changes.

### Decided
- The GitLab mirror gets no CI of its own; GitHub Actions on the canonical repository
  is the one CI witness (see `dev-log.md`).

---

## 3.0.0 — 2026-11-17 — the trust floor is repeatable

**Breaking.** An example is now complete only with a `mutants.py` next to its
`verify.py`, and "green" means `python -m harness verify-all` passes: every check
green *and* every check shown, on this run, to go red on a planted bug. An example
built to 2.x (verify.py only) fails `verify-all` until it gets a mutation suite.

### Added
- **Persistent negative tests.** `harness/mutation.py` + one `mutants.py` per example
  (44 mutants across the six suites): realistic bugs planted into `executable_model`,
  each naming the checks it must turn red. Fails on a surviving mutant, an unguarded
  check, a crashing mutant or a stale waiver. `WAIVED` declares checks that
  structurally cannot fail, reported on every run.
- **`python -m harness verify-all`** — every example, checks + mutants, prints the kit
  version; `python verify.py --mutants` for one example.
- **CI**: `.github/workflows/verify.yml` runs `verify-all` on Python 3.11 and 3.14.
- **Pinned environment**: `requirements-verify.txt` (exact simpy), `constraints.txt`
  (versions the examples were last verified with).
- `skills/verification-validation/templates/mutants.py`.

### Found
- **F40**: RadioMonitoring's per-stage work-conservation checks are identities and
  can never fail; WAIVED with the reason (see `findings.md`).

### Changed
- Version numbering unified: `pyproject.toml` said `0.2.0` while the last tag was
  `v2.0`; both now follow this file.

---

## 2.0 — 2026-04-30

Tag `v2.0`: the skill-based kit (methodology rather than a program) — the history up
to 3.0.0 is in `dev-log.md`.
