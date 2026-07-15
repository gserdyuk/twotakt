# Article candidate #1 — Audit-first: the model spec is the artifact, the code is its implementation

> **Type: reasoning** — corpus: append/compact, not synced · born 2026-07-13

*Status: candidate. Target form: practitioner article / blog post.*
*Origin: the founding methodology of this repo (simstudy-protocol Phase 1); the
one-line version lives in `TODO.md` under "Article / pitch material" ("Article #1",
90-day plan, month 2).*

*Numbering note: "#1" is the label TODO gave it in the 90-day plan. Candidate #4
(`article_candidate_4_vv.md` §9) argues it should lead **ahead of** this one — the
number is the order of appearance, not the publication order.*

---

## Thesis

No simulation code before a human-approved model spec (`MODEL.md`). The spec is
primary; the code is its implementation — **when they diverge, the code is the bug**
("specification vs bug" line). AI collapsed the cost of *writing* the code (F12), so
the scarce resource is no longer construction but justification: the audit of what is
about to be built. Hence the audit gate is the first, non-negotiable phase — the model
spec is what the human actually reviews, and the only artifact a human *can* review
before any code exists.

## Supporting material

- **The audit gate in practice** — `skills/simstudy-protocol/SKILL.md` Phase 1: audit
  before code, spec approved by the user, sync rules keeping MODEL.md and Config
  aligned.
- **Survivorship-bias example (PowerSearch)** — the flagship demonstration of what the
  audit-first metric discipline catches: under overload, ok-only (raw) p95 stays low
  while effective p95 (timeouts counted at SLA) is pinned at the ceiling — raw metrics
  create the illusion of a healthy system exactly at saturation.
  → `examples/PowerSearch/SIM_REPORT.md` (both pipelines), `examples/USLmodel/README.md`,
  `skills/verification-validation/references/metric-checklist.md` Rules 1–10.
- **Why spec-first holds here but not everywhere** — F24: spec-first works for a
  per-project artifact a human re-approves each run; a prose methodology nobody
  re-approves rots (methodology.md died of this). The article should draw this
  boundary explicitly.

## Related findings

F12 (construction cost collapsed, justification did not), F24 (spec-first holds for
the model, not the method). Related candidates: #4 covers the machine-side trust
mechanism *after* the audit; this one covers the human-side gate *before* the code.
