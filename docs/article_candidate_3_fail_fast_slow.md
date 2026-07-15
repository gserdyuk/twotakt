# Article candidate #3 — Fail-fast vs fail-slow: same success rate, opposite failure experience

> **Type: reasoning** — corpus: append/compact, not synced · born 2026-07-13

*Status: candidate. Target form: practitioner article / pitch demo (the FaxRx sweep
is already the demo). The one-line version lives in `TODO.md` under "Article / pitch
material".*

---

## Thesis

A success-rate number does not identify an architecture's failure mode — evaluate
*where* a design fails, not only how much it carries. In FaxRx at 10× burst, the
small-front-door architecture (A, `sip=270`) and the open-front-door architecture
(B, `sip=2565`) have statistically the same success rate (0.54 vs 0.52), but opposite
user experiences:

- **A fails fast and honestly** — Erlang-B blocking rejects at the door (busy signal,
  redial); everything admitted is served on time (p95 flat ≈ 285 s).
- **B fails slow and silently** — blocking vanishes, the backlog drowns OCR, p95
  climbs to the 1-hour SLA ceiling; the fax was accepted, then died an hour later.

The punchline: **the undersized front door is admission control, not a deficiency.**
Admitting work you cannot finish converts fast, honest failures into slow, hidden
ones — without improving the success rate. Capacity scaling (C, OCR 5×) delays the
slow-failure mode but does not change its nature.

Underlying distinction (from the harness work): two *kinds* of loss — admission loss
(rejected by design, Erlang-B) vs congestion loss (accepted, then expired). Metrics
that pool them, or count only completions, cannot tell A from B.

## Supporting material

- `examples/FaxRx/README.md` ## Result / ## Lesson — the narrative version;
  `SIM_REPORT.md` for the full table (3 architectures × 11 burst levels).
- `examples/FaxRx/verify.py` — the two loss kinds encoded as distinct ledger entries
  (blocked = admission, by design; expired = congestion).
- `sweep.png` — the three-panel exhibit (success / block rate / p95 vs burst) is
  already pitch-ready.

## Related findings

F7 (the FaxRx class bent the "universal" contract — completed≈offered assumed short
requests). Related candidates: #2 is the same genre on the composition axis; the
survivorship-bias line in #1 is the metric-level cousin (both are "the flattering
number hides the failure").
