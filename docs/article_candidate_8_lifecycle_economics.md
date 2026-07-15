# Article candidate #8 — Lifecycle economics after the price drop: same phases, different pie

> **Type: reasoning** — corpus: append/compact, not synced · born 2026-07-14

*Status: candidate. Series-adjacent: companion to **AI Influence on the Architectural
Landscape** (S1 = #5, S2 = #6), but **not** the S3 "TCO as an experiment" item in
TODO — S3 is infrastructure TCO of the *modeled system* (a postprocessor over
sweep_results, COCOMO-class dev-cost estimation explicitly out of its scope); this
candidate is the development-lifecycle economics of *building software with AI*.
Origin: author-led conversation 2026-07-14 (the financial lifecycle model).
The executable price model sketched in §6 will likely live in a **separate project**
(author's call, 2026-07-14: "не хочется смешивать") — the sketch is recorded here
until that home is decided.*

---

## 1. Baseline: the two loops and where the money was

Classic industry numbers (Boehm; Lientz & Swanson; Glass): maintenance + evolution
consume 60–80% of full lifecycle cost; primary development 20–40%. Within primary
development: analysis ~10–15%, design+code ~40–50%, testing ~30–40%, deploy ~5–10%.
Within maintenance: perfective ~50–55%, adaptive ~20–25%, corrective ~20% — and
~50% of any modification's effort is *comprehension* of existing code.

The lifecycle is two loops: primary development (runs once) and the modification
loop (runs for years). The second loop dominates TCO not because one iteration is
expensive but because it repeats.

## 2. The recomputation (primary loop)

Apply AI coefficients per phase — unevenly, which is the whole point (F29):

| phase          | was | coefficient | becomes | new share |
|----------------|-----|-------------|---------|-----------|
| analysis       | 10  | ×1          | 10      | ~29%      |
| development    | 50  | ×5          | 10      | ~29%      |
| testing        | 40  | see below   | 15      | **~43%**  |
| deploy         | ~0  | —           | ~0      | —         |
| **total**      | 100 |             | **~35** |           |

Testing is not homogeneous — the load-bearing split of the argument:

- **Execution** (runs, click-throughs, regression): ×5, like codegen.
- **Oracle** (deciding *what* to check and what counts as correct): ≤×1.5. "Ask the
  AI to click through the app from its description" works exactly as well as the
  description — and if AI wrote the code and AI tests it, the errors are correlated:
  a model that misread a requirement mis-checks it too.

The oracle/execution split inside testing is the single most consequential unsettled
parameter: uniform ×5 gives three roughly equal shares; the split above makes
testing the largest line. It should be an explicit model parameter, not a baked-in
coefficient.

Two structural readings of the table:

- **Denominator collapse.** Analysis went 10% → ~29% without costing a cent more —
  everything under it shrank. Shares must not be read as "X got expensive"; X fell
  slower.
- **Amdahl's law over the lifecycle (F29).** The unaccelerated human fraction
  (analysis + oracle, ~20 of the old 100) caps total speedup at ~×5 *no matter how
  much better codegen gets*. Further model progress on code barely moves TCO; the
  asymptote is held by the human residue.

## 3. Redistribution on a shrunken base

The economics redistributed **on ~30% of the old number, not on 100%** (author's
point). Consequences:

- The project-viability threshold fell ~3× — software that never paid for itself
  now does. Jevons: total industry spend need not fall; its *composition* shifts
  toward analysis and verification.
- Symmetrically: cloning a product got cheaper by the same factor. The defensible
  assets are the ones that did *not* get cheap — domain knowledge, the spec, the
  verification harness, calibrated models.

## 4. The maintenance loop inverts the expectation

Naive expectation: AI helps less on modification (METR: experienced devs ~19%
*slower* on their own mature repos). Author's field experience: multi-x *faster* on
foreign code, mid-size project (5-person team), even on 200k-context models a year
ago. Both are true — the reconciliation is F30: **AI gain is inversely proportional
to the context already in the maintainer's head.** Comprehension is ~50% of a
modification and is AI's strongest mode; on your own code that term was already
near zero. So in the maintenance loop — where comprehension dominates — development
falls *more* than in greenfield, not less.

Testing in the loop: regression *execution* collapses (automatable), the oracle
problem persists, and here architecture enters.

## 5. Architecture as a multiplier, and the four unglued boundaries

Architecture is not a cost line of the model; it is a **multiplier on the AI
coefficients** (F31), via two mechanisms:

1. **Context locality.** A modular codebase means the change-relevant slice fits
   the window entirely — AI works fully informed. Tangled dependencies mean it sees
   a fragment and hallucinates the rest. The one-context rule replaces the
   two-pizza rule: module size is set by a comprehension boundary, not a team or
   deploy boundary.
2. **Blast radius.** Good seams → change is local → the regression surface is small
   and cheaply executable. Hidden state and coupling → the *oracle* part of testing
   (what must even be re-checked?) balloons — the part that does not get cheap.

Corrections that sharpened this (author, in order):

- **Modularity ≠ microservices; monolith ≠ spaghetti.** The window and reasoning
  depth care about the dependency structure, not the deployment boundary. A
  well-partitioned monolith is attention-local. You need *services* — code that
  fits in context — not MICROservices.
- **Batch changes by module locality, not arrival time.** Loading a module's
  context is paid once per batch; prompt caching makes this literal pricing
  (cache hits are multiples cheaper). "Sprint per module" beats "sprint per
  feature list". Batch size is a divisor on context-load cost in the model.
- **The convention caveat.** In a monolith the module boundary is held by
  discipline; AI generates at a speed that erodes convention-held boundaries.
  Partitioning suffices *only* with machine-enforced boundaries (import rules,
  build-level visibility, CI lint) — cheap insurance, but mandatory.

Microservices glued **four** distinct boundaries (F32); the landscape shift is that
they no longer have to travel together:

| boundary       | bounds                                  | cheap mechanism            |
|----------------|------------------------------------------|----------------------------|
| comprehension  | fits the window / the head              | partitioning               |
| verification   | re-check volume after a change          | contracts + module specs   |
| deployment     | operational failure, scaling            | process/service only       |
| team           | Conway, autonomy                        | org decision, not technical|

AI economics is sensitive to the first two only — and both are achievable inside a
monolith. The honest residual case for services is row three: a leaking module in a
monolith takes down its neighbors regardless of interface purity. Row four was never
technical.

On window growth (sparse attention, subquadratic): it shifts the constant, not the
gradient (F33). Nominal ≠ effective context (multi-hop reasoning degrades before the
limit); sparsity prunes exactly the long-range pairs that tangled code needs; and
token economics keep locality paying even when it stops being mandatory. Above all:
**the spec is a context-compression format** — a neighbor enters the window as its
MODEL.md (~1k tokens), not its implementation (~100k), a ~100:1 ratio invariant to
any future window size. The same spec makes the re-verification radius *definable*
(without it the rational radius is "everything" — maximal price). Audit-first thus
serves both economies with one artifact.

## 6. The price model (sketch — likely a separate project)

A deterministic analytical model; twotakt discipline applies (REQUIREMENTS +
MODEL.md before code) even though it is not a SimPy study.

- **Base unit: person-hours.** Currencies (USD/JPY/AED/…) are a rate table × hours —
  one multiplication, the trivial layer.
- **Two cost carriers.** AI does not delete work; it converts person-hours into
  tokens at some exchange rate. Both rates drift (wages by geography; inference
  prices falling) — the model is honestly dynamic.
- **Parameters** (all surfaced by this conversation): baseline phase distribution
  (Boehm/Glass); AI coefficients per phase × per loop (primary vs modification);
  the oracle/execution split inside testing; architecture multiplier α on the AI
  coefficients; change-batch size (divides context-load cost); system lifetime;
  iteration frequency; iteration-cost growth (entropy).
- **Outputs:** TCO(t); sensitivity analysis (prime suspects: oracle share and α);
  "price of bad architecture" = Δ between two runs differing only in α.

## Related findings

F29–F33 (born here); F12 (the economic engine), F20 (relevance as an experiment),
F27 (S1: modularity/distribution unglued — refined by F31/F32), F28 (S2:
re-verification surface — refined by F33). Candidates: #5 (S1), #6 (S2), #4 (the
trust machinery that makes cheap verification real), #1 (audit-first — the spec that
§5 prices).
