# twotakt — development log

> **Type: journal** — corpus: append-only, never edited · born 2026-04-30

Append-only log of project evolution. Newest entries at the bottom.
Tag entries with `#tag` so the log is greppable later.

Conventions:
- Date in `YYYY-MM-DD` format.
- One header per entry, describing the change in one line.
- Body explains what, why, and where the artifact lives.
- Tags at the end of the body.

---

## 2026-04-30 — examples/USLmodel created

First worked example. Single-CPU thread-per-request server simulated in
SimPy with USL-based degradation (linear α + quadratic β
coefficients applied as a multiplier to CPU bursts). Three-panel plot
(throughput / success rate / latency). Effective latency metric added
after we noticed survivorship bias in ok-only percentiles under
overload.

Lives at `examples/USLmodel/` with `server_sim.py`, `sweep.py`,
`plot_sweep.py`, `requirements.txt`, `MODEL.md`, `sweep.png`.

`#example #model #USL #v1`

## 2026-04-30 — examples/USLDBmodel created

Extension of USLmodel adding a database connection pool (model #1
from the database modelling menu — bounded concurrency, FIFO queue,
fixed query duration). Built by copying USLmodel and surgically
adding `db_pool_size` / `db_query_mean` to Config, a `self.db`
Resource on Server, and a new acquire-hold-release block at the end
of `_serve`. Two sweeps saved (`sweep.png` for default pool=8, and
`sweep_2.png` for pool=1).

Lives at `examples/USLDBmodel/`. `MODEL.md` references its parent
and describes only the diff.

`#example #extension #model #database`

## 2026-04-30 — examples/METHODOLOGY.md written

12-step methodology document capturing the path that produced the
two examples, plus a list of recurring anti-patterns. Intended as a
working protocol for future examples, not a historical record.

`#methodology #docs`

## 2026-04-30 — per-model MODEL.md spec documents

Wrote `MODEL.md` inside both example folders. They describe the
*intent* of each model in human prose so a reader does not need to
read the code to understand modelling choices. Established the rule:
spec is the specification, code is its implementation; if they
disagree, the code is the bug.

`#docs #spec`

## 2026-04-30 — perf-simulation skill v1 packaged

Packaged the methodology + audit protocol + theory glossary + metric
checklist + code templates as a Cowork skill (`perf-simulation`).
Encodes the audit-first protocol as a blocking gate so future
modelling sessions cannot skip the audit before writing code. The
user's `examples/` directory is treated as the working library —
when a pattern recurs three times across examples, candidate for
extraction into a real library module (rule of three).

Skill v1 has draft quality only — no test cases run, no iteration
cycle. Decision: ship as-is, iterate later if needed.

Artifacts:
  - source: `skills/perf-simulation/` (editable folder for future iteration)
  - package: `perf-simulation.skill` (24 KB, installable bundle)

`#skill #release #v1 #methodology`

## 2026-04-30 — pivot from MCP-centric to skill-and-templates approach (v2)

The original vision (`docs/archive/architecture-v1.md`,
`docs/archive/concept-v1.md`) was an MCP server (`twotakt-mcp`) that
exposed simulation through declarative tools (`build_model`,
`run_bench`, `show_model`, etc.) and hid SimPy behind a generic
Resource/Activity/Step abstraction. After building two worked examples
(`USLmodel`, `USLDBmodel`) and packaging the methodology as the
`perf-simulation` skill, we converged on a different position:

- Don't hide SimPy. The user sees the code.
- The skill provides discipline (audit-first, metric checklist,
  templates, theory glossary) so direct SimPy use stays honest.
- Modern LLMs make SimPy tractable for users without deep library
  knowledge, removing the original justification for the MCP fasade.
- First prove the approach on real cases; polishing for non-technical
  users is a later concern.

Cleanup performed:
- `architecture.md` → `docs/archive/architecture-v1.md`
- `concept.md`     → `docs/archive/concept-v1.md`
- `pyproject.toml` stripped of `mcp` dependency and `twotakt-mcp`
  script; bumped to `0.2.0`.
- `.mcp.json` reset to empty `mcpServers` (effectively disabled).
- `README.md` rewritten to describe v2 layout and approach.

Manual cleanup still needed (Windows ACL prevented Linux-side
deletion): remove the `twotakt/` Python package directory (containing
the now-unused `twotakt/mcp/server.py`) and optionally the orphaned
`uv.lock`.

`#pivot #v2 #cleanup #methodology`

## 2026-04-30 — docs/concept.md (v2 vision)

Re-introduced a concept document, this time aligned with v2. Recovers
the strong v1 ideas that were not actually tied to the MCP
architecture (vision tagline, problem statement, insight, competitive
landscape, positioning) and reframes architecture/user-journey for
the skill-and-templates approach.

Adds a dedicated *Reverse Simulation* section describing the planned
calibration mechanism — the future direction we agreed deserves more
than a passing mention. Sources of calibration data prioritised in
this order: application logs, Prometheus / OpenMetrics, AWS
CloudWatch, APM (Datadog / New Relic / Honeycomb), synthetic probes.

Calibration becomes a planned extension to the methodology in two
places: a new audit question (Q9 — "do you have observed metrics
from a similar production system?") and a new metric-critique rule
(deviation between simulated and observed must fall within tolerance
before extrapolation is trusted). A new Phase 7.5 — *Calibration* —
sits between validation sweep and metric critique.

Roadmap stated: forward simulation now → Prometheus calibration next
→ logs and APM later → CloudWatch and probes later still → continuous
calibration eventually.

README updated with a link to `docs/concept.md`.

`#concept #vision #v2 #calibration #reverse-simulation #roadmap`

## 2026-04-30 — docs/architecture.md (v2 structure)

Re-introduced the architecture document for v2. Describes the
project structurally — files, folders, layers, workflow, persistence,
component boundaries. Explicitly does not include modelling-level
content (degradation laws, theoretical frameworks, metric
definitions); those live in `concept.md`, in the skill's references,
and in per-example `MODEL.md`.

Structure: methodology (Layer 1) → skill (Layer 2) → templates
(Layer 3) → examples library (Layer 4) → planned calibration
(Layer 5). Workflows for new-example creation and existing-example
extension are documented at architecture level. Persistence is the
git working tree; cross-example history is `dev-log.md`. Mappings
from v1 architecture are listed for structural elements only;
modelling-level v1 ideas are intentionally omitted from this
document.

README updated with a link to `docs/architecture.md`.

`#architecture #v2 #structure`

## 2026-04-30 — critique.md and Tier 1 review

Wrote `docs/critique.md` — adversarial review of the project sorted
by severity (Tiers 1–4), with an honest competitive landscape and a
top-concerns action list. Strengths to preserve listed first to
avoid overcorrection.

Conducted Tier 1 review in discussion. Each of the six Tier 1
concerns now carries a *Response (reviewed)* block summarising the
agreed disposition. Summary by item:

- 1.1 (heavy methodology) — **accepted with fix**: examples library
  becomes the fast path; add minimal discoverability artefact
  (`examples/INDEX.md` or per-example "when to use" summary).
- 1.2 (direct LLM obviates methodology) — **accepted as risk**:
  position explicitly to users who want methodology; defer measured
  eval of no-methodology failure modes.
- 1.3 (no calibration → "trust me") — **deferred**: calibration in
  next iteration; MVP path is one source × one example end-to-end;
  meanwhile reposition as "framework today, calibration in
  development".
- 1.4 (Cowork-only) — **counter-action**: portability via portable
  Markdown bundle now, MCP server (exposing methodology, not
  simulation) later; and credibility via grounding the audit in
  established literature (ATAM, ARID, C4, USE, Gunther, Menasce).
- 1.5 (no success stories) — **ongoing**.
- 1.6 (USL voodoo) — **counter-action**: make M/M/c the template
  default; reclassify USL as advanced (fitted parameters);
  preserve `USLmodel` / `USLDBmodel` as advanced demos; build a
  USL fitting routine which doubles as the first calibration
  primitive.

Action-list table at the end of `critique.md` now has a Status
column with the Tier 1 dispositions; Tier 2 rows remain Pending.

Tier 2 review will be the next discussion.

`#critique #tier-1 #review #pivot-not-required #actions`

## 2026-04-30 — Tier 2 critique review

Conducted Tier 2 review. Each of the nine items now carries a
*Response (reviewed)* block. The action-list table extended with
rows 11–15 covering Tier 2; Status column shows the agreed
disposition. Key dispositions:

- 2.1 (audit assumes user knowledge) — **accepted with Q0 split**:
  two paths at start of audit (extract intent vs walk-through with
  simplest model). User chooses; methodology educates about
  consequences.
- 2.2 + 2.3 (theory-first, not tuned defaults) — **accepted**:
  Phase 6 "tune defaults until healthy" removed; defaults are
  fitted (when calibration available) or theoretical assumptions
  (and labelled as such). Converges with calibration roadmap.
- 2.4 (spec-code drift) — **counter-action E**: rejected
  regex-driven CI (variant A) because it would impose structured
  format on natural-language docs. Adopted variant E — periodic
  LLM-driven audit with activity-based reminders, no enforcement.
  Detailed implementation deferred.
- 2.5 (all-IT examples) — **accepted**: clinic patient-flow as
  first non-IT example.
- 2.6 (multi-seed) — **reframed**: seed strategy is part of source
  model, not methodological enforcement. Audit makes it an explicit
  user choice alongside arrival pattern and service distribution.
- 2.7 (unrealistic distribution defaults) — **accepted**:
  distribution choice is an explicit audit topic; methodology
  educates about consequences; calibration replaces assumptions
  with empirical distributions.
- 2.8 (no team workflow) — **deferred**: acknowledged limitation;
  designing team workflow postponed to a later revision.
- 2.9 (AI capability advancement) — **accepted with refinement**:
  position methodology as way-of-thinking; monitored each major
  model release; not solvable finally.

Tier 3 (friction-tier concerns) is the next discussion.

`#critique #tier-2 #review #source-model #periodic-audit #actions`

## 2026-04-30 — Tier 3 and Tier 4 deferred

Tier 3 (friction that compounds over time — 7 items: cognitive
load, vocabulary expansion, three-panel-plot opinionatedness,
skill-template versioning, anti-patterns descriptive,
hard-coded paths, no discoverability tooling) and Tier 4 (minor or
monitor-only — unevaluated skill bundle, dev-log discipline, phase
numbering, no warmup, requirements duplication, capacity=1
everywhere, no-LLM path) are noted in `critique.md` with a
"Pending review" preamble. Responses will be added in a later
session.

The *Competitive landscape — honestly assessed* section and the
final *Top concerns as a single action list* table are also noted
as pending review: the competitive-landscape entries should be
checked for completeness and our defensive position against each
discussed; the action-list table is partially populated (Tier 1
and Tier 2 rows complete) and will receive Tier 3 and Tier 4 rows
once those tiers are reviewed.

`#critique #tier-3 #tier-4 #competitive-landscape #action-list #deferred`

## 2026-06-12 — validation architecture design notes (archaeology from archived chats)

Design notes from earlier discussions, recorded here before the verification harness
(see TODO P1) is implemented — these decisions should inform the harness design.

**Hybrid validator, single contract.** Structural / deterministic rules → Python
checkers (run every time, cheap: pre-commit, CI, on save). Semantic rules →
LLM-as-judge (run rarely and deliberately: before approving MODEL.md, before release).
Expose both behind one validation function so callers see one contract.

**Don't use an LLM for what code checks deterministically** — loss of precision,
speed, and money. Reserve the judge for genuinely semantic checks.

**Judge hygiene:**
- Small, hot context: spec slice + code slice + the one rule being checked (not the whole project).
- One judge = one concern; several narrow judges beat one "check everything".
- Calibrate on known-good and known-bad examples to learn false-positive / false-negative rates.
- Cache same-code vs same-spec results; double-judge critical checks (two prompts or two models,
  accept only on agreement).

**Correlated blind spots.** An LLM judge checking an LLM generator can miss what the
generator missed — shared training, shared blind spots. Mitigation: use a different model
(or at least a different version) as judge for the checks that matter most.

Operational fit for twotakt: the deterministic half → Build agent's "only ships green" exit
criterion (runnable on every commit); the LLM-judge half → attaches to the human confirmation
gate (MODEL.md approval), where slow and deliberate is the point anyway.

`#validation #harness #llm-judge #architecture #v2`

## 2026-06-15 — one-pager rewrite around the two-input dichotomy

Reviewed and rewrote `docs/twotakt-one-pager.md`. The central clarification: the
methodology has **two** inputs, not one, with distinct roles —
**architecture → the model**, **requirements → the testbench and acceptance
criteria** (the same split as hardware verification: design vs testbench). The
requirements document is the system's *original* requirements, not an artifact
invented for the tool; this is what closes the "where do the numbers come from"
objection and keeps the "two hours" offer honest (the architect already has the
requirements doc).

Edits: the "why architects don't model" reasons turned into a list; the
unsourced AWS reference removed (the argument "load testing needs a finished
system" stands on its own); the offer now names both documents. Deliberately
left untouched: no concrete result/proof yet (no such study has been run —
flagged for later).

`#one-pager #positioning #two-inputs #dichotomy #docs`

## 2026-06-15 — example-library consistency pass

Made the four examples uniform and self-explanatory, all organised around the
two-input dichotomy above.

- **PowerSearch got a `REQUIREMENTS.md`** (it only had a scattered
  `SIMULATION_PLAN.md` + requirements-flavoured content inside `ARCHITECTURE.md`).
  All four examples now carry the pair `ARCHITECTURE.md` + `REQUIREMENTS.md`.
- **Per-example `README.md` added to all four** — a one-page map: input / model /
  how to run / output / result / **lesson** / files. A matching template lives at
  `skills/simpy-protocol/templates/README.md` and is registered in `SKILL.md`.
- **`## Lesson` section in each README** — the transferable systems insight,
  written standalone (no cross-linking; lessons may repeat, since a new
  example's author writes their own). Each lesson has a precise statement plus an
  *"In plain terms:"* expansion so an outside reader understands. USLmodel:
  servers collapse past saturation + survivorship bias. USLDBmodel: resource
  ceilings don't compose; bottleneck from interaction. FaxRx: judge a design by
  *where* it fails; admission control is a feature. PowerSearch: provision for
  the burst peak, not the mean.
- **FaxRx plot closed** — added `plot_sweep.py` (reads the committed
  `sweep_results.json`; the 7200 s × 33 sweep is too slow to re-run) and
  generated `sweep.png` (success / PSTN block / p95 eff vs burst, one curve per
  architecture). Stale "no plot" notes removed from `SIM_REPORT.md`, the README,
  and `CLAUDE.md`.
- **PowerSearch `SIM_REPORT.md` translated** RU → EN, so all four reports share
  one language.
- **Root `README.md` updated** — the two-input dichotomy added to "How it works";
  per-example README named as the entry point; "Approach" now reads "architecture
  and requirements documents".

`#examples #readme #lessons #requirements #faxrx-plot #consistency #docs`

## 2026-06-15 — one-pager English translation; RU becomes secondary

Translated the one-pager to English. The English version takes the canonical
name `docs/twotakt-one-pager.md` (so existing links resolve to it); the Russian
original was renamed to `docs/twotakt-one-pager-rus.md` via `git mv` to preserve
history. Content is unchanged — same two-input dichotomy
(architecture → model, requirements → testbench), hardware-verification analogy,
audit-first framing, and the two-document offer. The still-open gap (no concrete
proof/result line) carries over to both versions.

## 2026-06-16 — takts↔phases map; verification-harness pilot; article candidate #4

Three things this session: a docs fix, a working harness pilot, and a large
conceptual thread captured as a new article candidate.

**Takts ↔ phases (docs).** Wrote a `WORKFLOW.md` mapping the README's two takts to
the skill's 10 phases, then **dropped the separate file** — a third copy of the same
truth is a third source of drift, and pilots read the README, not a standalone doc.
Folded it into `README.md` as a "Takts ↔ phases" section (per-phase artifact in/out +
human-gate table). `TODO.md` item closed as "added as README section".

**Verification-harness pilot (code).** Built the skeleton top-down and confirmed it
runs green:
- `harness/` package — `run_summary.py` (the `RunSummary` contract: a balanced ledger
  `offered + generated == completed + dropped + in_flight`, with `generated` defaulting
  to 0 so a future generating system fills it in without new logic); `invariants.py`
  (Tier-1 conservation laws, human-authored, model-independent); `runner.py` (runs all
  checks for one example, catches failures so one break doesn't hide the rest, prints a
  summary, returns an exit code). No repo-wide runner yet — examples are independent;
  we play at the example level.
- `examples/USLmodel/verify.py` — adapter (native dict → `RunSummary`) + 6 checks,
  6/6 green: Tier-1 ×3 (conservation / no-drops-without-congestion / non-negative),
  Tier-2 ×3 (linear regime / metamorphic degradation-toggle / decline). Each check
  negative-tested (deliberately broken → goes red).

**Two engineering findings worth keeping.** (1) A test "doesn't bite" if it stays green
on a *broken* model — so a negative test (inject the bug, confirm red) is mandatory, not
optional. (2) The first Tier-2 discriminator used a magic number (`peak < 0.7 × ceiling`)
and turned out not to bite anyway — a rise→fall curve does not prove USL, because
SLA-timeout collapse mimics it even with degradation off (verified). Replaced it with a
**metamorphic toggle**: `peak(degradation ON) < peak(degradation OFF)` — no magic number,
only the direction taken from MODEL.md.

**Article candidate #4 (concept).** The long conceptual thread — invariant / intent-
consistency verification for LLM-generated simulations — lives in full in
`docs/article_candidate_4_vv.md` (NOT duplicated here, to avoid drift). Highlights worked out
this session: spec = goal not invariant; three tiers by authorship (generator must not
author its own trust floor); emergence boundary; mechanism-toggle metamorphic relations
(with an honest triviality note); a third **scope axis** (component / edge / system) with
the **non-composition thesis** (component correctness does not compose into system
correctness — USLDBmodel); the **proportionality razor** (don't fill the cube; automate
verification, keep validation light; the human audit is the real validator); and
**structural ↔ functional** models deciding which technique is even available
(component/unit needs seams; metamorphic needs only boundary + a knob). Flagged as lead
candidate in `TODO.md`, ahead of audit-first.

**Not done:** tile the harness onto USLDBmodel / FaxRx (the `plain_/ocr_` metrics will
stress the contract); mark P1 verification-harness progress in `TODO.md`; the prior-art
check on the term "intent verification".

`#harness #verification #invariants #metamorphic #non-composition #article-4 #workflow #docs`

## 2026-06-16 — harness replicated to USLDBmodel (2nd example)

Small increment: `examples/USLDBmodel/verify.py`, 7/7 green.

- **Contract transfers.** The adapter is identical to USLmodel (same `run()` dict
  keys), and the Tier-1 conservation laws are reused from `harness/` unchanged. Second
  model held by the same `RunSummary` contract — first confirmation it generalizes.
- **New check — pool-exhaustion metamorphic relation (the interaction bottleneck).**
  Shrinking `db_pool_size` must lower throughput where the pool binds. Caught a fresh
  instance of the operating-point lesson: the pool does **not** change the peak (CPU/USL
  binds at the knee, where even pool=1 keeps up) — it binds in **overload**. So the
  toggle is taken at rate=8, not at the peak. Probed: at rate 8, pool=1 → 0.29 vs pool=8
  → 0.89; peaks are equal (~4.07) across pool ∈ {1, 8, 100}. Negative-tested: a
  non-binding pool (8 vs 100, both 0.89) correctly does *not* pass — the relation keys on
  real binding, not noise. This is the USLDBmodel "component ceilings don't compose"
  finding, now demonstrated by an executable check (article candidate #2 material).
- **Duplication flagged, not yet extracted.** The USL shape checks (linear /
  degradation-MR / decline) + the sweep helper are now near-identical in USLmodel and
  USLDBmodel. Kept self-contained (examples are independent). These two are the only USL
  models; extracting `harness/shapes.py` is warranted if a third consumer appears — FaxRx
  is Erlang B, not USL, so it likely won't trigger it.

Next: FaxRx — the real contract stress (plain/ocr classes → multiple `RunSummary` per
run; Erlang B, not USL). P1 verification-harness: 2 of 4 examples done.

`#harness #verification #usldbmodel #metamorphic #pool #non-composition #increment`

## 2026-06-17 — harness on FaxRx (3rd example) + contract refactor; cross-model trend analysis

FaxRx is a different class (Erlang-B blocking + multi-class, not USL), and it bent the
contract — which is the point of a third example.

**Contract refactor (touched all examples, backward compatible).**
- `RunSummary.dropped` split into **`rejected`** (admission / blocking loss, by design —
  503 on a thread cap, Erlang-B busy) and **`dropped_overload`** (congestion loss — SLA
  timeout under load), with `dropped` kept as a derived property. Driven by FaxRx:
  Erlang-B blocks ~by design even at low load, so the lumped "no drops below saturation"
  law falsely reds a *healthy* blocking system (demonstrated: blocked+timeout=12 → old
  strict==0 fails; new overload-only with tolerance passes).
- `assert_no_drops_without_congestion` → **`assert_no_overload_loss`** (forbids only
  congestion loss below saturation; rejection allowed). Tolerance instead of strict 0
  (a healthy run with an SLA has the occasional timeout).
- Dropped the "completed ≈ offered" continuity sub-check from `work_conservation` — it
  assumed in_flight ≈ 0, false for FaxRx's long-lived requests (~3% in flight at sim
  end). The universal core is now just the **ledger balance**.
- USLmodel (6/6) and USLDBmodel (7/7) re-run green after the refactor; adapters updated
  to map dropped_buffer→rejected, dropped_timeout→dropped_overload.

**FaxRx `verify.py` — 6/6 green.**
- Tier-1 ×3 reused (ledger / no-overload / non-negative).
- **Multi-class via several RunSummary** — system + per-class (plain, ocr) summaries,
  with a partition check (plain+ocr == system for completions and timeouts). First use
  of the `label` field; contract bent to multi-class without new machinery.
- Tier-2: **channel metamorphic relation** (adding SIP channels removes PSTN blocking:
  block_rate(270)=0.39 vs block_rate(2565)=0.00 under high load → Erlang-B is wired) +
  **structural OCR-vs-plain** (OCR path strictly slower). No USL checks — USL is off by
  default here; the law is Erlang-B blocking, confirming Tier-2 laws don't transfer.
- Spec slightly too strong: MODEL.md's "OCR ≥ plain + ocr_time_mean" doesn't hold at p50
  on the healthy model (19.1 < 20; holds at p95). Encoded the robust strict-slower form
  and flagged the discrepancy in-code rather than red a healthy model.

**Cross-model trend analysis (the lessons, not just the extension).** Recorded in full in
`docs/article_candidate_4_vv.md` (NOT duplicated here). One line: across USL→USLDB→FaxRx
there are two convergences and one non-convergence — the *universal* laws shrink toward
bare continuity (each model strips a hidden assumption), the *ledger* grows toward a
complete taxonomy of work-fates (each term names a discipline), and the *laws* don't
converge at all (the reusable asset is the metamorphic method, not the laws). Extrapolated
endpoint: `verify.py` becomes a declarative mechanism manifest = the generator↔harness
contract for the Build agent. PowerSearch is queued as a *test of predictions* (cost on
topology not components; ledger bending on composition → per-pipeline + edge conservation).

State: 3 of 4 examples done. Files: `harness/run_summary.py`, `harness/invariants.py`,
`examples/USLmodel/verify.py`, `examples/USLDBmodel/verify.py` modified; new
`examples/FaxRx/verify.py`; analysis added to `docs/article_candidate_4_vv.md`.

`#harness #verification #faxrx #erlang-b #contract-refactor #multi-class #trend #increment`

## 2026-06-17 — harness on PowerSearch (4th example) — predictions tested & refuted

PowerSearch is two submodels (ingestion, queries), each its own `server_sim.py` + `run()`.
Both done: `model1_ingestion/verify.py` (5/5), `model2_queries/verify.py` (5/5), green.
All four examples / five models now covered.

- **Contract transferred unchanged.** Same `run()` vocabulary as the USL family; Tier-1
  reused, no refactor. PowerSearch is NOT a new class — it is two independent instances of
  the cascaded-M/M/c family (ingestion = workers→ES, like USLDBmodel's CPU→DB). Cheap, like
  USLDBmodel.
- **Ingestion Tier-2:** two metamorphic relations for the series cascade (undersize the
  worker pool → it binds; undersize the ES pool → it binds) — bottleneck migration.
- **Queries Tier-2:** baseline latency under SLA (healthy verification) + the PowerSearch
  signature, **survivorship bias** (under overload eff_p95 0.461 > raw_p95 0.412 — surviving
  requests are a biased sample). Article #3 material.

**Predictions (from §9b) mostly refuted — the useful kind.** This was framed as a test of
the cross-model trend; recorded in full in `docs/article_candidate_4_vv.md` §9b "Outcome".
Short version: the contract bends only on a genuinely new *class* (FaxRx), not per model;
PowerSearch was low-novelty so cheap. The "edge conservation between pipelines" prediction
was wrong — the pipelines are modelled independently (shared ES out of scope), and the real
coupling would be **fan-in** (ingest→ES←queries), not series. Two refinements forced:
(1) two composition topologies — series (edge `out_A==in_B`) vs fan-in (demand superposition
+ interference); (2) conservation at edges/shared resources is near-tautological — the value
of composition lives in the **metamorphic** relations (interference, bottleneck migration),
not the conservation identities; (3) the harness sees only couplings the model represents
(a decoupled model exposes none — a Phase-3 choice).

State: 4 of 4 examples done (5 models, all green). New files:
`examples/PowerSearch/model1_ingestion/verify.py`, `examples/PowerSearch/model2_queries/verify.py`;
`docs/article_candidate_4_vv.md` §9b extended with the outcome. Remaining for P1: decide on
a repo-wide aggregator (or keep example-level).

`#harness #verification #powersearch #cascade #survivorship #predictions-refuted #fan-in #increment`

## 2026-06-17 — methodological note: sequential vs holistic analysis (NOT for the article)

A reflection, not a build step, and deliberately kept out of `article_candidate_4_vv.md`
(it is about *how* the conclusions were reached, not a result to publish). Prompted by:
"you analysed the four models in sequence — what if you'd been given all four at once?"

**Core duality.** Sequential analysis produced a **narrative** (trend, evolution,
convergence, tested predictions). Holistic analysis (all four at once) would produce a
**taxonomy** (a static product-space). They are duals: the trend is the time-projection
of the taxonomy; the taxonomy is the time-collapse of the trend.

**What would dissolve (artifacts of sequence):**
- "Universal shrinks / ledger grows / convergence" → holistically just a fixed set of
  dimensions; the universal core is their *intersection* (conservation). No drama of erosion.
- "FaxRx forced the rejected/overload split / a hidden assumption was discovered" →
  holistically all four already carry both loss categories; the split would be *designed
  once* from the union, no refactor. (Nuance kept: FaxRx is still special — its admission
  loss, Erlang-B blocking, is structural/non-optional, so it is correctly the model that
  makes the split non-ignorable. Holism = design upfront; sequence = patch when it breaks;
  same contract.)
- "Predictions" don't exist holistically (nothing to predict from 1..N).

**Robust either way:** the three tiers; "conservation is the weak floor, value is in the
metamorphic relations"; the two composition topologies (series / fan-in); the contract content.

**New conclusions only holism gives:**
1. The split is *inherent*, not discovered → design the contract once from the union.
2. A **portfolio-level gap invisible per-model**: seeing ingestion writes ES and queries
   read ES simultaneously, the obvious question is "is ES shared?" — the unmodelled
   shared-Elasticsearch interference is the most interesting untested coupling, and only
   the cross-model view surfaces it.
3. A clean product-space — *law* (USL / Erlang-B / M/M/c-cascade) × *topology* (single /
   series / fan-in-blocking) × *loss type* (congestion / admission / blocking) × *request
   lifetime* (short→in_flight≈0 / long) × *class count* — which yields the declarative
   contract directly, by classification rather than extrapolation, and more solidly.

**What only sequence gives (holism would lose):**
- The "doesn't bite" / negative-test-first lesson — learned through repeated first-try
  failures (the pain is the teacher).
- *Tested* predictions are epistemically stronger than mere observation (a refuted
  prediction is a real test).
- "Universality is made, not born" — you only know an assumption was hidden by watching
  it break.

**Synthesis.** Complementary epistemics: sequence gives tested / earned / robust knowledge;
holism gives complete / economical / structural knowledge. Current conclusions are biased
toward an "evolution/discovery" framing because of order; holism would re-frame them as
static structure and would have caught (a) the inherent split and (b) the shared-ES gap
sooner. Practical pointer it surfaces: the **shared-Elasticsearch interference** is the one
coupling no model covers.

`#methodology #sequential-vs-holistic #taxonomy #epistemics #not-for-article #reflection`

## 2026-06-17 — Model #5 RadioMonitoring: independent build → verify loop

A bonus 5th model (radio-spectrum surveillance), and the first built *fresh* through the
full protocol rather than retrofitted. Deliberately split across sessions for
**independence** (the §4 principle): a separate session ran the audit + build (Requirements
→ Architecture → MODEL.md → server_sim.py); this session verified it cold, having authored
none of it. The contract is the file boundary — verifier reads MODEL.md + code only.

**Round 1 — verifier caught a real bug.** Two failures, separated:
- *My baseline config was wrong* (mine to fix): baseline made PC generous but left pools at
  the default 2/4. With an 8 s voice record, the lower pool offers ~2.67 Erlang to 2 SDRs —
  saturated at *any* load → voice POI 67%, not ~100%. Fixed: generous pools in the baseline.
- *Model bug* (escalated to the architect): **digital POI ≈ 0.6% even with infinite
  resources at λ×0.1**, contradicting MODEL.md ("digital POI high but < voice"). Root cause
  localized: `t_class=0.5 s` (classification gated recording) equalled the digital block
  duration (0.5 s) → the block ended *during* classification → bucket B. The builder had
  even flagged the "classify gates record" reading in a code comment.

**Architect reworked the model** (interpretation (a) = bug): classification now runs
**concurrently** and does not gate recording (`t_class=0.2`); and a **stage 2 decode
pipeline** was added — a bounded queue + decode workers, with a new loss bucket **G**
(queue overflow). So the model grew from one stage to a record→decode series.

**Round 2 — re-verify, harness extended, all green.**
- Digital record stage now healthy (concurrent classify).
- The model had grown a stage my harness didn't cover — verifying only stage 1 would be
  green-but-blind on a broken decode. **Extended** verify.py to a second per-category
  RunSummary for the decode stage (offered=intercepted, completed=decoded, overload=G,
  in_flight=queue backlog). Result: **19/19 green** (record + decode × voice/digital + Tier-2).
- Balanced-provisioning lesson (user's note): a healthy baseline needs *every* stage
  generous AND matched — decode workers scaled to the receiver count (you cannot record
  faster than you decode; an 8.5 s voice decode on 2 workers saturates at any load). My two
  wrong baselines (PC-only, then pools-but-not-decode) = two "first formulation wrong" hits.

**What this established.** The methodology loop closed end-to-end: independent verifier
flagged a real bug → architect refined → re-verify green (a literal "return to audit on
mismatch"). The contract held a 5th time, and for the first time across a **real async
series edge** (record→decode handoff with its own queue/drops — less tautological than
PowerSearch's within-request cascades; `no_overload(G)` + residual-small genuinely bite).
Strong §8 evidence (independent build, independent verify, real bug caught) — to fold into
the article during the "conclusions" step, not yet.

State: `examples/RadioMonitoring/` (REQUIREMENTS, ARCHITECTURE, MODEL, MODEL.ru, server_sim,
verify) — verify.py 19/19 green; whole folder untracked.

`#harness #verification #radiomonitoring #model-5 #independent-verify #two-stage #audit-loop #increment`

## 2026-06-17 — validation harness folded into the skill (process made coherent)

Closed the gap flagged earlier: build sessions were verifying "by prose", because the
harness was a separate practice the skill knew nothing about. Now it is prescribed.

- **Naming:** the thing is the **validation harness** (`harness/` package), distinct from
  the **sweep harness** (`sweep.py`, which explores behaviour). "Harness" alone is ambiguous
  in this repo — use "validation harness".
- **`harness/README.md`** — user-facing scope: what a green run does and does NOT mean.
  Anchor line: *green ⇒ the model conserves work and its mechanisms behave directionally as
  the spec says, at the tested points; green does NOT ⇒ the model is right about the world
  (that's the audit) or meets its SLA (that's the sweep).*
- **`SKILL.md` Phase 7 rewritten** to prescribe the executable harness instead of prose:
  Verification → Tier-1 conservation reused from `harness/invariants.py` (the fixed,
  independent trust floor — not rewritten per project); Validation → Tier-2 per-model (curve
  shape + metamorphic toggles, direction from MODEL.md, at the binding point); negative-test
  every check; prefer running V&V in a *separate session/agent* (correlated blind spots);
  proportionality razor. `templates/verify.py` added + registered; a "Validation harness"
  section points at `harness/` + README.
- **Sign-off / gate defined and mirrored** in both SKILL.md and the README WORKFLOW table.
  Phase 7 → 8 gate = green certifies *correctness* automatically ("ships only green", the
  executable check replaces a human eyeballing the smoke test) **+** a human **sign-off**
  before sweeps (consent/cost — green means safe to proceed, the human authorizes the spend).
  Autonomous "green-auto, no human in the middle" noted as a future relaxation. README and
  skill now say the same thing.
- **Shared-lib location resolved: keep repo-root `harness/`.** twotakt IS the workspace
  (users model their own system inside `examples/`), so there is no cross-repo need; vendoring
  only matters if the skill is ever packaged for global install (folded into the existing
  "rebuild the `.skill` package" P2 item).

Net: "work on the model → verify (executable harness) → sign-off → sweeps → accept report"
is now ONE process with explicit gates, and the skill prescribes it. No code changed — the
`harness/` package and the examples' imports are untouched; edits are docs + one template.

`#harness #validation-harness #skill #phase-7 #sign-off #process #docs`

`#one-pager #translation #english #docs`

## 2026-07-06 — release-prep pass: skill rename, vocabulary lock, README schema, history cleanup

A naming-and-consistency session ahead of release. No model or harness code changed;
this is identity, vocabulary, docs, and repo hygiene. Several decisions were reached by
working the reasoning out loud, so the *why* is recorded here, not just the *what*.

- **Skill renamed `simpy-protocol` → `simstudy-protocol`** (commit 29d28b8). The argument:
  SimPy is a *swappable engine*, not the methodology — the protocol would survive replacing
  SimPy with another DES simulator, so the name must not encode the implementation. Rejected
  `twotakt-protocol` (couples a portable skill to the container; adds a third naming scheme)
  and `simulation-*`/`gated-*` variants. Landed on `simstudy` = "simulation study" (the full
  cycle: model spec → verification → execution → report) + `-protocol` as the entry-point
  marker. **audit-first stays in the description's first line, not the name** — name says
  *what it is*, description says *what makes it different*. The two sibling skills correctly
  carry `<topic>-<author>` (queueing-lazowska, modeling-jain) because they wrap *borrowed*
  methods; simstudy-protocol is the project's *own* method, so it is named by its principle.

- **Code artifact renamed `server_sim.py` → `executable_model.py`** repo-wide (7 files,
  commit d6a2a3a). Same logic as the skill rename: `server_sim` encoded a "server" assumption
  too narrow for the method (RadioMonitoring, FaxRx are not servers). This forced settling the
  **vocabulary**, which had been conflated: `MODEL.md` = **the model** (spec, human-verified) ·
  `executable_model` = **the code** (machine-verified *against* the model) · `simulation` =
  **the run** (a *process*, not an artifact — never name a file "the simulation"). Rule: bare
  "model" always = MODEL.md; the code is always `executable_model`. User's call: use the
  underscore token because this is "almost a spec — must be unambiguous". Fixed a real
  conflation in README/one-pagers (an executable model was described as *recorded in MODEL.md*)
  and sharpened the trust sentence to "two verifications, two verifiers: you certify the intent,
  the machine certifies the code honours it." "SimPy model" left as descriptive prose where it
  names an actual SimPy example (not a conflation).

- **README rebuilt from the one-pager** (1dad4c9) + a **methodology schema** added
  (`docs/methodology.svg`, self-contained, phase-numbered; d9147b0/8ea8f0c). The diagram
  encodes six aspects the user asked for — steps, takts, inputs, outputs, **human** gates
  (approve MODEL.md; sign off the spend) vs the **automatic** gate (verify = harness green) —
  and collapses the skill's 10 phases into 6 visual steps with per-step phase-number badges
  (Audit 1–3, executable_model 4–6, verify 7, simulation 8, iterate-loop 9, report 10).

- **Git history rewritten to a single author identity** (`gserdyuk@gmail.com`) with
  git-filter-repo; three work emails (refinitive/epam) removed from all 46 commits; tag v2.0
  re-pushed; stale merged branches pruned. Repo-local git config set — **not** global (this is
  a work machine; global gmail would misattribute work repos). Note: old commits remain
  reachable only via GitHub `refs/pull/*` (support-only cleanup).

- **Repo hygiene:** deleted the stale root `perf-simulation.skill` (6153515) — a build
  artifact from the very first skill name, two renames behind and missing the whole V&V/harness
  layer; skills are read from disk, not installed from it. **TODO reconciled** with reality
  (RadioMonitoring Phase 8 is actually done; listing examples in README is deferred by policy,
  not a gap).

- **Policy decisions (locked, do-not-relitigate):** example folder names are **deliberately
  free** (contributors' choice; the *internal* file layout is the convention, per the skill's
  "The library"); in-progress examples stay in-repo but **out of README/one-pagers until ready**
  (RadioMonitoring is the current case). Brand is **TwoTakt** (display) / `twotakt` (repo/paths).

Net: the release-facing surface now speaks one vocabulary and one identity — `simstudy-protocol`
+ `MODEL.md`/`executable_model`/`simulation`, a single-author history, a visual methodology
schema, and a TODO that matches the repo. No simulation or harness code touched.

`#release-prep #rename #simstudy-protocol #executable_model #vocabulary #readme #schema #git-history #hygiene #policy #docs`

## 2026-07-06 — P2 hygiene batch + methodology dedup

Small release-hygiene pass, four items:

- **`PowerSearch/Whiteboarding…txt` re-encoded** — was Windows-1252 with CRLF (broke UTF-8);
  recovered to clean ASCII/UTF-8, LF.
- **ТЗ glossed** for non-Slavic readers — CLAUDE.md now says "REQUIREMENTS (ТЗ — tech spec)";
  SKILL.md already defined it at first use.
- **One-pager proof line** (both en + rus) — a captured lesson as a concrete result: the
  USLDBmodel interaction-bottleneck (pool=1 collapses at ~6 rps despite a ~20 ceiling) — the
  class of failure a spreadsheet misses.
- **Methodology de-duplicated** — `examples/METHODOLOGY.md` was a *byte-identical* copy (same
  SHA256) of `skills/simstudy-protocol/references/methodology.md`; deleted the examples copy,
  repointed the docs (architecture, concept, architecture-llm-layers, critique) to the skill
  copy, which is now the single source.

Finding worth flagging (new TODO item): the surviving `methodology.md` is itself **stale** —
the old 12-step "server degradation" version, predating the current 10-phase SKILL.md (no
audit gate as Phase 1, no MODEL.md/executable_model/simulation vocabulary, no V&V harness). The
dedup removed a *copy*, not the *staleness*; a rewrite-or-retire decision is queued.

`#hygiene #encoding #glossary #one-pager #methodology #dedup #stale #docs`

## 2026-07-06 — methodology retired; RATIONALE started; "ТЗ" eliminated

Three linked moves.

- **methodology.md retired (not rewritten).** The surviving `references/methodology.md` was
  the old 12-step "server degradation" doc, far behind the 10-phase SKILL.md. We deleted it.
  The *reason it rotted* is the interesting part: we had (implicitly) tried to run the
  project's own "spec is primary" principle one level up — a prose **methodology** as the
  source spec, the **skill** as its compilation. That inverted: the skill evolved with every
  project, the methodology doc didn't, and it became the stale one. **Lesson:** spec-first
  holds for *the model* (a per-project artifact a human re-approves each run) but **not** for
  *the method itself* (nobody re-approves the method each run, so the "source" gets ignored
  and the "compiled" skill becomes the truth). SKILL.md is now the single source of the
  protocol; docs repointed to it.

- **RATIONALE.md started** — `skills/simstudy-protocol/RATIONALE.md`, the human "why"
  companion to SKILL.md. Not a parallel protocol (that's what rotted); it explains, phase by
  phase, *what failure each gate prevents* and the judgement behind it — content that does not
  belong in terse agent instructions. Co-located with SKILL.md (location answers "which skill",
  and reduces drift). DRAFT; the author is adding their own reasons iteratively. Planned:
  mirror to the other two skills (shorter — they wrap external methods).

- **"ТЗ" eliminated from English** — the Russism was replaced by **Requirements** repo-wide
  (SKILL.md, audit-protocol, examples, article, CLAUDE.md). Deliberately **not** "Spec":
  that word is reserved for `MODEL.md` (the model spec), so "Spec" for the requirements doc
  would re-introduce a conflation. This reverses the earlier same-day "gloss ТЗ" fix — glossing
  → eliminating. RU one-pager keeps ТЗ (native there). Rule recorded in CLAUDE.md.

`#methodology #retire #rationale #skill #vocabulary #requirements #anti-russism #docs`


## 2026-07-08 — architecture framing: performance is a 42010 concern, not the whole map

Methodological decision on how the project positions itself in architecture terms,
prompted by the author asking how to state precisely "what is being modeled" without
sounding like a dilettante in front of architects.

**Decision.** The project speaks the vocabulary of **ISO/IEC 42010** (architecture
description), because it is a metamodel the other schools reduce to:
- **Concern** = performance / scalability (throughput, latency, behavior under load) —
  a quality attribute owned by specific stakeholders, *not* a "view".
- **Viewpoint** = the convention (questions, notation) that addresses that concern — a
  type, exists before any system.
- **Model kind** = discrete-event simulation (SimPy) + queueing analysis (Lazowska,
  M/M/c, USL) + statistics (Jain). This is *how* the model inside the viewpoint is built.
- **View** = the concrete model of a concrete system under a concrete load profile — an
  instance of the viewpoint.

One-line framing for external use: *"performance view of the system: concern =
performance under load; model kind = discrete-event simulation + queueing analysis."*

**Framework caveat (kept on purpose).** Whether performance is a *viewpoint* or a
*perspective* is school-dependent: Rozanski & Woods treat it as a **perspective**
(cross-cutting quality applied over structural views), pure 42010 as a **concern** served
by a viewpoint, Kruchten 4+1 has no dedicated view for it at all. We deliberately talk in
42010 so we are not pinned to one school. Knowing this landscape is the difference between
sounding expert and sounding like one textbook.

**Direction (planned, not yet built).** Performance is the *first* of a family of
**operational perspectives** reachable on the same structural base (server / queue /
workers): availability & resilience (fault-tree, Markov), capacity & cost (queueing —
already nearly in reach). Security is explicitly **out of perimeter** — it lives in a
different plane (threat model, attack trees), not operational. The three skills
(simstudy / lazowska / jain) cluster in the operational plane, which is why extension to
availability/cost is natural and to security is not.

Not yet propagated to the pitch or README — author will fold it in later.

`#architecture #42010 #viewpoint #perspective #performance #methodology #direction`

## 2026-07-09 — docs/verifiability.md: map + doctrine draft ("verifiability by construction")

Distilled a multi-day design conversation into a new theory doc, `docs/verifiability.md`
(DRAFT). Named for the answer, not the map: the taxonomy turned out to be textbook
material once stress-tested, while the load-bearing element is the doctrine — since AI
made model *construction* cheap and *justification* stayed expensive (Wei's asymmetry of
verification, Karpathy's verification gap, Prediction Machines lineage — all checked,
none of it ours), the response is to make verifiability a **property of the model
itself**: unit-simulatable components, assume/guarantee certificates, built-in degeneracy
to analytic oracles, instrumented invariants, declared calibration paths, metamorphic
properties, runtime frame monitors. One-liner: *a model must carry its own verifiers;
a model without its certificate is unfinished.*

Notable moves recorded in the doc:

- **Rebuilt on standard foundations after self-critique.** The conversation's first
  constructions (gates A/B/C, simulation-as-solver, concern-as-relevance-criterion)
  turned out to be re-derivations of Sargent/ASME V&V, Zeigler's frame/model/simulator,
  and GQM. Kept the standard names — citable beats homegrown, and independent
  re-derivation is evidence the structure is right, not a novelty claim.
- **Composition:** layer B composes (DEVS closure under coupling), layer A does not;
  assume-guarantee certificates as the joint discipline; fix pattern = promote hidden
  coupling to explicit component (shared CPU as Resource ~ parasitic capacitor).
- **Isolation buys compositionality at the price of utilization** (FPGA pipelines,
  network calculus); "design for modelability" as the architectural twin of the doctrine.
- **Per-run verdict:** applicability domain is earned by validation, AI is registrar and
  patrol (not authority); verdicts must be localized and directional. Planned home:
  frame-compliance section in SIM_REPORT.md (prototype before legislating).
- **Complication discipline:** model size is now bounded by the justification budget,
  not construction labor; predicted failure-mode sign flip (too-simple -> baroque).

Deliberately cross-referenced with `article_candidate_4_vv.md` (the harness machinery is
its worked instance) instead of duplicating it — discovered mid-write that the article
already holds the tiers/metamorphic/non-composition layer.

The meta-observation worth keeping: during the source conversation, every aesthetically
pleasing closure the AI produced (skills mapped onto the taxonomy, concern->cell as a
function, simulation as a model kind) was retracted under the author's pushback within a
turn — the author's skepticism operated as gate A at the discourse level. Most direct
confirmation of the project's central thesis so far, obtained about theorizing rather
than about SimPy code.

Pitch/README propagation deliberately deferred until the draft settles.

`#docs #verifiability #doctrine #vv #composition #methodology #draft`

## 2026-07-09 — concern paragraph propagated to README + both one-pagers

Closed the deferred item from the 2026-07-08 architecture-framing entry: README and both
one-pagers now carry a short paragraph naming the concern (ISO/IEC 42010 terms) —
performance & scalability, served by DES + queueing analysis; availability and cost named
as planned operational siblings on the same structural base; security explicitly out of
scope. Placed right after the audience line in the one-pagers and after the opening
question in README — the spot where "performance modeling, capacity planning" was listed
without a frame. RU one-pager worded natively; EN kept to one paragraph per the "short"
requirement.

`#docs #42010 #concern #readme #one-pager`
## 2026-07-09 — scope paragraphs removed from README + both one-pagers (concern → attribute → deletion)

## 2026-07-10 — V&V extracted into its own skill: skills/verification-validation/

Phase 7 detail, metric-checklist.md, templates/verify.py, and the harness pointer
moved out of simstudy-protocol; Phase 7 stays as a thin gate that invokes the new
skill. Why: V&V techniques will keep accumulating (verification levels,
compositional verification) — modularity says no skill grows unbounded; the gate
belongs to the protocol, the technique to its own skill (same split as statistics
into modeling-jain). Name is descriptive, not <topic>-<author>: the author scheme
fits skills wrapping one published method — here the method is in-house and growing,
Sargent is a source, not the owner. Backlog stays project-wide in TODO.md
(per-skill backlogs = the third-source-of-truth drift, learned twice); skills carry
only CHANGELOGs.

`#skills #vv #modularity #verification-validation`

## 2026-07-10 — RadioMonitoring declared a DRAFT project (parked, will be reworked)

Whole-example status instead of per-item debts: draft banners in the example's
README.md and MODEL.md, TODO section collapsed; SIM_REPORT / MODEL.ru cleanups are
moot until the rework.

## 2026-07-10 — stale docs resolved by archiving; concept.md rewritten vision-only; RATIONALE follows the V&V split

Third occurrence of the lesson "current-state descriptions lose the race with
SKILL.md + README" — so this time: archive, don't refresh. architecture.md ->
docs/archive/architecture-v2.md (kept for the v1->v2 decision record: why MCP/DSL
were dropped); architecture-llm-layers.md -> archive (its #1 priority — externalize
validation — was since implemented as the harness; unharvested ideas -> TODO P3:
RAG textbook corpus, deterministic style checkers / spec-drift linter). concept.md
rewritten as a vision-only doc (problem / differentiator / landscape / calibration
direction; phase numbers removed — the phase layout is owned by the skill): vision
rots slowly, cheap to keep. critique.md untouched — it is a dated record, not a
current-state description. RATIONALE: technique-why moved to
skills/verification-validation/RATIONALE.md; simstudy Phase 7 rationale keeps only
the gate-why; the open trust-chain NOTE stays with the author.

`#docs #archive #concept #vision #rationale #verification-validation`


## 2026-07-10 — research-project reframing: corpus/surface split, findings.md + INDEX.md

The recurring cost of documentation was diagnosed at the root: the project was run as an
*engineering* project (all docs must be currently true and synchronized) while it is in
fact a *research* project (truth accumulates through dated records, findings, and
publications). The whack-a-mole contradiction hunts were the price of applying product
discipline to a research corpus.

**Decisions:**

- **Corpus vs surface split** (CLAUDE.md Key constraints): the research corpus (dev-log,
  findings.md, theory docs, article drafts, critique) *accumulates* — append-only, dated,
  contradictions are history; the product surface (README, one-pagers, CLAUDE.md,
  SKILL.MDs, TODO) stays small, current, contradiction-free. Only the surface is ever
  synchronized. Generalizes the thrice-learned "archive, don't refresh" lesson (F25).
- **findings.md created** — the register of what the project knows: F-numbered claims,
  one screen max, append-only (refinements reference back), each pointing to its long
  form. Retrospectively seeded with F1–F26 from article #4, verifiability.md, and the
  dev-log. Highest preservation form remains *compilation into practice* (a finding that
  became a harness check cannot be lost) — marked with `compiled:`.
- **INDEX.md created** — the catalog: one pointer line per thing worth finding again
  (files, key decisions, findings clusters). Pointers + hooks, never content — a copy is
  a future contradiction. Curated, not exhaustive (dev-log stays greppable by #tags).
- **Compaction rhythm** (the video-codec analogy that seeded the design: append deltas =
  P-frames, periodic review produces a new keyframe): when the findings tail stops
  reading clean or before an external showing — review, merge, resolve, rewrite as vN,
  archive vN-1; mature clusters graduate into theory docs / articles / skills.
- **Granularity rule**: a big discussion yields 3–7 findings + possibly a long-form doc,
  never a 4-page findings entry. Precedent was already in-repo: article #4 is "the long
  form; the one-line version lives in TODO".

`#process #research #findings #index #corpus #compaction`

## 2026-07-10 — reproducibility session: the whole example library re-run, bit-exact

Question: do the committed examples reproduce their recorded behavior on the current
environment (Python 3.14.6, simpy 4.1.2)? Answer: yes, exactly.

- **Tier A (V&V regression):** all six verify.py green with the recorded counts —
  USLmodel 6/6, USLDBmodel 7/7, FaxRx 6/6, PowerSearch ingestion 5/5 + queries 5/5,
  RadioMonitoring 19/19 (parked as DRAFT, but the regression still holds). 48/48.
- **Tier B (numeric reproduction against committed sweep_results.json):** PowerSearch
  ingestion and queries — 3 points each across regimes (overload / knee / healthy),
  seeds [42,43]: bit-exact, worst relative diff 0.0. FaxRx — the FULL sweep re-run
  (33 points x 20 metrics = 660 comparisons): zero mismatches. The "slow" FaxRx sweep
  is ~0.6 s/point on this machine (~20 s total) — the slowness note is stale.
- Direct measured backing for the REPRODUCIBILITY position (TODO P2): below MODEL.md
  everything is deterministic — now demonstrated, not asserted.

Gaps noted, not yet acted on: USLmodel/USLDBmodel have no committed sweep baseline
(nothing to regress against); PowerSearch committed JSON predates the config-per-row
format of the current sweep.py (physics matches bit-exact, format would diff on a full
regeneration).

`#testing #reproducibility #regression #harness #seeds`
## 2026-07-13 — article candidates #1-#3 get their own short-form files

Only candidate #4 had a long form on disk; #1 (audit-first), #2 (interaction
bottleneck) and #3 (fail-fast/slow) lived as TODO one-liners plus scattered dev-log /
example material. Wrote a small corpus file per candidate — thesis + pointers to the
evidence, not new content — so each candidate has a citable home before any of them
grows:

- `docs/article_candidate_1_audit_first.md` — spec is primary, "when they diverge,
  the code is the bug"; survivorship-bias exhibit (PowerSearch); F12/F24.
- `docs/article_candidate_2_interaction_bottleneck.md` — component ceilings don't
  compose (USLDBmodel, F10); binding-region and metamorphic-relation sharpenings
  (F9/F11) from the harness work.
- `docs/article_candidate_3_fail_fast_slow.md` — same success rate, opposite failure
  UX (FaxRx); admission loss vs congestion loss as the metric-level root (F7).

Numbering fixed as the order of appearance: TODO already called audit-first "Article
#1" and the 2026-06-16 entry called the pool-MR "article candidate #2 material", so
fail-fast/slow is #3. Publication order is a separate question — article #4 §9 still
argues #4 leads. TODO bullets now carry the numbers + file pointers; INDEX gained the
three lines.

`#articles #corpus #candidates #index`

## 2026-07-13 — publication warm-up: LinkedIn series decided, post #3 drafted

Decision (author): start public visibility with the methodologically *lighter*
candidates as a warm-up series on LinkedIn, each post linking into the repo. Order
#3 (fail-fast/slow) -> #2 (interaction bottleneck) -> #1 (audit-first): concrete
war-stories first, the manifesto after credibility. #4 stays reserved for a long-form
venue (talk/paper) — a feed post would burn its novelty. Rationale: #2/#3 are "weak"
only methodologically; as feed content (one lesson, one chart, a punchline) they are
the strongest of the four.

Post #3 drafted and approved: `docs/linkedin_post_3_fail_fast_slow.md` (text + format
decisions: native post ~2.5k chars, sweep.png as the image, link in first comment,
written for a reader slightly outside the field — no Erlang-B/p95 jargon, each
architecture a mini-story with a user in it). One deliberate simplification: only the
1-hour SLA is mentioned, the 10-minute normal-case SLA dropped from the story.

`#articles #linkedin #visibility #faxrx #publication`

## 2026-07-13 — post #3 grew a second image and a personal frame; DOU chosen for the long form

Post #3 (LinkedIn) revised after review: a second image (one-off architecture diagram,
`docs/linkedin_post_3_architecture.png` — pipeline with the two failure points
accented) and a personal-history frame (the author really built a PSTN fax-reception
service; the frame opens the post and closes the lesson). ~2.9k chars, still under the
3k limit.

Language/platform decision for the second-language version: NOT a Russian-language
duplicate on LinkedIn (marginal reach — RU-speaking LinkedIn reads English, built-in
auto-translate exists) and NOT Habr (rejected by the author). The Ukrainian-language
long form goes to **DOU.ua**, 1-2 weeks after the LinkedIn post. Draft written:
`docs/dou_article_3_fail_fast_slow.md` (~12k chars) — restores everything the feed post
cut (both SLAs, Erlang B sizing math, effective-latency/survivorship sidebar, full
results table, no-redial limitation pre-empting the obvious commenter objection) and
adds a bridge section mapping the lesson to modern systems (429/503, backpressure,
load shedding). One material per candidate, two venues: feed post = hook, longread =
the full story; both link into `examples/FaxRx`.

`#articles #linkedin #dou #publication #faxrx`

## 2026-07-13 — post #3 is live on LinkedIn

Published by the author (title line + personal frame + two images + repo link in the
first comment: github.com/gserdyuk/twotakt/tree/main/examples/FaxRx). ~100 impressions
in the first hour. One glitch: the attached architecture diagram is the pre-fix
version (overlapping "admitted" label) — the corrected PNG is in the repo; replace via
post edit. Draft file marked posted; DOU longread window opens ~2026-07-20.

`#articles #linkedin #published #faxrx`

## 2026-07-13 — second article series born: "AI Influence on the Architectural Landscape"

Grew out of the author's walk-idea (TCO model comparing architectures under business
scenarios) and his "hod 5": the collapse of code-construction cost reprices the
architectural landscape itself. Two conversation moves sharpened it: (1) microservices
decompose into modularity (boundaries for change) + distribution (boundaries for
runtime) — AI removes the change justification and leaves only runtime, which is
exactly what simulation computes; (2) the author's testing-cost "offspring" turned out
to be the center: regeneration is cheap, re-verification is not, so the unit of
architecture becomes the unit of re-verification — making candidate #4 the
*precondition* of the landscape shift, not a neighbor.

Registered: candidates #5 (S1, landscape) and #6 (S2, re-verification surface) as
short forms; S3 (TCO layer over sweep_results.json — break-even framing, rework as
schedule not amount, pilot on FaxRx A/B/C) and S4 (Monte Carlo over growth
trajectories, architecture as options portfolio) live in TODO and need building —
the series deliberately drives the roadmap.

Series name is the author's. Publication pipeline codified in TODO: LinkedIn EN note →
engagement gate (notes are cheap, DOU longreads cost author-written text per DOU's
no-AI-text rule, so the note's engagement selects which topics earn the longread;
comments are harvested as the objection list) → DOU UA longread + same-day UA teaser
post + optional dev.to EN. Series #1 (warm-up: #2, #1) and series #2 interleave.

`#articles #series #ai-landscape #tco #microservices #verification #pipeline`

## 2026-07-13 — candidate #7 born from Karpathy's LLM-wiki gist thread; two publication drafts

The author surfaced Karpathy's "LLM Wiki" gist (5k+ stars) mid-session: twotakt's
corpus system turns out to have converged on the pattern independently (INDEX=index,
dev-log=log, CLAUDE.md=schema, findings=synthesis, compaction=lint). Read the full
thread (107 comments loaded): ~70% self-promo/astroturf, but the substantive core
converges on one pain — staleness/drift/provenance — and every proposed fix is
tooling. Best voices: a-a-k (lossy compression; "not engineering until validators/
source-hashes/regression-tests"), jazzonenl (update cascades, referential integrity,
temporal blindness), nowissan (Identity/Level/Relationship failure modes from a month
of use; claim-first fixes Level — which is findings.md's design), blurman-ai's
measured boundary (pages pay only when compressing scattered facts; mirrors of
greppable files are negative value — validates our no-concept-pages-for-code choice).

Registered candidate #7 (standalone meta-topic): twotakt's answer is discipline, not
tooling — passports (currency ambiguity resolved at read time), corpus/surface split
(staleness solved by NOT promising currency; F25 generalized), claims-before-concepts
(graduation rule). Drafts written and approved: gist field-report comment (restrained
tone as the differentiator in an ad-flooded thread) + LinkedIn EN note (post-#3 house
style). Queue call: gist comment ASAP, note jumps ahead of S1 — the thread is hot,
S1 keeps.

`#articles #candidate7 #llm-wiki #karpathy #corpus-surface #passports #findings-discipline`

## 2026-07-13 — gist field-report comment is live

Posted by the author to Karpathy's llm-wiki thread (user gserdyuk). Renders clean,
@-mentions resolved; one glitch: the passport template's angle-bracket placeholders
(<regime>, <date>) were eaten as HTML — backticks around the line fix it via comment
edit. Noted in the thread right above ours: a commenter independently argues "grade
the trust and make it travel — every page carries status + provenance, so a stale or
disputed page degrades honestly instead of silently" — closest thinking to passports
in the whole thread; possible conversation partner. LinkedIn note (#7) queued next,
ahead of S1.

`#published #candidate7 #karpathy #gist`

## 2026-07-13 — candidate #7 fully published: gist comment + LinkedIn note, same day

The LinkedIn note went live hours after the gist comment (author used the
unicode-bold trick for the title line and section leads; links in the first comment).
Campaign #7 is the fastest candidate to date: born, drafted, and published within one
session — the corpus discipline it describes is also what made that speed possible
(the thesis was already compiled in CLAUDE.md constraints + F25, nothing had to be
invented, only framed). Day total across publications: post #3 (fail-fast/slow,
14h, edited), gist field report, note #7. Queue next: DOU longread #3 (author's text,
window ~07-20..27), then S1 (microservices landscape) EN note.

`#published #candidate7 #linkedin #campaign`

## 2026-07-13 — note #7: first objection and the answer that names the mechanism

Note #7 outpaces post #3 (~550 impressions in hour one vs ~100). First real
objection (S. Osypchuk): "do you expect humans to read automatically maintained
wikis?" The published answer produced a formulation worth keeping for the #7/#4
long forms: the corpus's primary reader is the LLM (context transfer), humans are
the second audience; and the human reads at *write* time — every claim is born in a
reviewed conversation, so the wiki records what a human already judged. "Machine-
drafted, human-gated. The reading you're skeptical about already happened — once,
when it counted." This is the audit-first gate restated for knowledge instead of
code — one discipline, two artifact kinds.

`#candidate7 #linkedin #objections #audit-first`

## 2026-07-14 — lifecycle economics day: F29–F33, candidate #8 born

The author walked the classic lifecycle cost split (Boehm/Glass baselines, two
loops: primary development + modification) through AI-era coefficients. Why-notes
worth keeping:

- The author's structural move: recompute the shares on the *shrunken* base — "the
  economics redistributed, but on a completely different number: 28% instead of
  100%". That observation, formalized, became the Amdahl-over-the-lifecycle claim
  (F29): the human residue (analysis + oracle) holds the asymptote.
- The one genuinely contested coefficient: testing. Author: ×5 like codegen ("ask
  the AI to click through the app"); pushback: only *execution* is ×5, the *oracle*
  barely moves and is correlated with the generator's own misreadings. Not settled —
  deliberately left as an explicit parameter (oracle/execution split), the single
  number the whole shape of the primary loop hangs on.
- Author's field data drove the maintenance-loop inversion (F30): multi-x speedup
  on foreign code (mid-size, 5-dev project, 200k-window models a year ago)
  vs METR's slowdown-on-own-repo. Reconciliation: gain ∝ 1/context-in-head;
  comprehension (~50% of a modification) is AI's best mode.
- Author's corrections that shaped F31/F32: modularity ≠ microservices, monolith ≠
  spaghetti ("you need SERVICES, not MICROservices — code must fit the context");
  batch changes by module, not one-by-one (prompt caching literalizes this); blast
  radius is the real anti-monolith argument — answered by unbundling verification
  from deployment (four glued boundaries, F32).
- Registration caught a naming collision: TODO's S3 is *infrastructure* TCO of the
  modeled system (COCOMO-class dev-cost estimation explicitly out of scope there).
  Today's material is dev-cost economics — registered as standalone candidate #8,
  series-adjacent, with the disambiguation written into both the doc and INDEX.
- Decision: the executable price model (person-hours + tokens as two cost carriers,
  currency = rate table) will likely live in a separate project — author: "не
  хочется смешивать". Sketch recorded in candidate #8 §6 until the home is decided.

`#findings #candidate8 #architecture-economics #lifecycle #amdahl #price-model`

## 2026-07-15 - README onboarding: the "open it in Claude Code" step unpacked

GitHub traffic showed 38 unique cloners on July 7 - and the Getting started
section assumed the reader already lives in Claude Code. The likely failure mode:
a newcomer clones, launches the Claude Code GUI, but the session is not rooted in
the repo - CLAUDE.md never loads, the skills are invisible, and the project looks
like a plain folder of markdown. Nothing tells the user this happened.

Changes to README Option B:

- a one-line prerequisites note (Python 3.10+, Claude Code) - removes the "what
  do I even need" question;
- step 1 expanded: separate CLI vs desktop-app instructions, naming the trap
  explicitly (the working folder is chosen at session start and cannot be changed
  mid-session);
- a sanity check: ask Claude "What is this project?" - a one-question probe that
  tells the newcomer whether the methodology actually loaded, cheaper than any
  documentation;
- Option A gained the AI-native path: instead of running the smoke test by hand,
  ask Claude to run the USLmodel example and explain it - which is also the
  fastest demonstration of the project's value.

Why it matters beyond this fix: the methodology's entry point is environmental
(a correctly-rooted session), not textual - no document can load itself. Any
onboarding text must therefore verify the environment, not just describe the
steps; the sanity-check question is that verification.

`#readme #onboarding #getting-started`

## 2026-07-17 — articles/: EN long-form home on GitHub Pages (canonical layer)

Publication-venue review (run in the 3A8 session; venue analysis recorded in
3A8/publish_platforms.md, journal-mode) found the coverage hole: long form existed
only in Ukrainian (DOU pipeline), LinkedIn is short, the repo is corpus. Author's
architecture decision: no standalone author site ("a shop in the desert — people
shop in malls"); distribution stays in the malls (LinkedIn, DOU, HN), canonical
texts live next to the projects, and a personal publications list (GitHub profile
README + LinkedIn Publications) points at the homes.

Implemented: `articles/` at repo root — index + two EN long forms written clean
from the corpus sources (#3 fail-fast/fail-slow from the DOU draft skeleton; #7
staleness from the candidate file + the "machine-drafted, human-gated" answer born
in the note's comments). Frozen-copy images in `articles/img/` (records freeze
their exhibits). `_config.yml` added: GitHub Pages can only build from root or
/docs, so Pages is configured from root with the corpus (docs/, logs, registers,
skills, harness, examples) excluded — the surface (README + articles) is served,
the corpus stays repo-only. Pending (author actions): enable Pages in repo
settings (root), review both articles, then add Pages links to the first comments
of the two LinkedIn posts.

`#articles #pages #publication #canonical #corpus-surface`

## 2026-07-20 — week-one check of the three publications; the gist thread converges on tiered trust

Status: LinkedIn #7 — 3 comments, no new ones; LinkedIn AI-titled the page "Solving
Staleness in LLM Knowledge Bases with Discipline" (the algorithm parsed the thesis
correctly). LinkedIn #3 — 3 reactions, 1 comment, quiet evergreen tail. Profile
crossed 1,004 followers (990 pre-campaign). Gist comment: live, edited (both fixes
applied: backticked passport line, expanded Level explanation); no direct replies yet.

Material finding: the gist thread independently converges on twotakt's trust
structure. pradocabreroalejandro (production ERP wiki): "grade the trust and make it
travel" — per-page status + extraction provenance, two authorship tiers where only
the human-annotated tier counts as verified provenance (= F3's generator-never-
authors-its-own-trust-floor, rediscovered in production; write-up promised).
bluejaeha (Korean audit accountant): quarantined unverified AI content that cannot
be cited by other pages until checked against primary sources — "unverified citing
unverified is exactly the circular evidence auditors are trained to reject" (an
auditor's phrasing of the #4 tier logic). theafh: "the power of this idea lies in
simplicity" — discipline-over-tooling from another angle. Long forms #7 and #4 are
accumulating third-party evidence without our participation.

`#candidate7 #candidate4 #karpathy #trust-tiers #status-check`

## 2026-07-23 — DOU article #3: channel layer reworded to T1/E1

In the article the channel layer now reads «лінії T1/E1» instead of SIP/T.38.
`examples/FaxRx` (ARCHITECTURE/MODEL/README, `sip_channels`) left as is — the
divergence is deliberate, not an error: same resource contract (N concurrent
channels, no queue), same numbers.

`#candidate3 #dou #faxrx`

## 2026-07-24 — DOU article #3 review pass: success rate is an on-time rate, and FaxRx has two cascaded bottlenecks

Working the DOU longread with the author surfaced two things the FaxRx lesson had
compressed away.

(1) **Under overload, "success rate" is not a delivery rate but an on-time rate**
(SLA attainment). The model drops a fax on SLA-timeout and frees its worker; a real
service delivers it late (the model's queue is unbounded → nothing is truly lost) or
loses it only to a finite-queue overflow. Both simplifications — freeing the worker
and dropping-on-timeout — flatter the accept-everything architectures B and C, i.e.
cut *against* the article's own fail-slow thesis, so the bias is conservative. Named
as an explicit convention in the text rather than hidden.

(2) **The failure is two cascaded bottlenecks, not "OCR."** Processing (20 workers →
4 faxes/s, all faxes, tight 600 s SLA) collapses the *success rate*: plain-path
timeouts dominate at every burst (3x: 228 vs 0 on the OCR path; 10x: 11 852 vs 1 817).
OCR (1.75 faxes/s, half the faxes, loose 3600 s SLA) governs only the *p95 tail*
(-> 3 600 ceiling). Arch C scales only OCR (35 -> 175): OCR timeouts go to zero, p95
falls 3 600 -> 1 402, yet success stays 0.68 because processing is untouched.
ARCHITECTURE.md already names "two cascaded bottlenecks"; the article had flattened it
to one and now restores it.

The article was corrected accordingly: channel layer SIP/T.38 -> T1/E1 (what we
actually bought; termination tech we never knew), the metric reframing above, the
bottleneck attribution, and the title -> the success-rate-paradox line ("Однаковий
success rate - протилежний досвід..."). Also produced: social copy (UA/EN) and a UA
author bio.

Example code and specs left as-is by decision. Register note for later: the SIP/T.38
vs T1/E1 divergence (article vs ARCHITECTURE.md/MODEL.md) and the ARCHITECTURE.md
"overnight baseline" wording (contradicts the day-average the sweep actually
multiplies) are both parked -- not bugs to fix now, recorded so they read as
intentional, not forgotten.

`#candidate3 #dou #faxrx #on-time-rate #two-bottlenecks #metric-hygiene`

## 2026-07-28 — DOU article #3 published (fail-fast/fail-slow, FaxRx)

The FaxRx longread went live on DOU: "Однаковий success rate — протилежний досвід
(де насправді ламається система під навантаженням)"
— https://dou.ua/forums/topic/60921/ . This is the publication the whole #candidate3
line was building toward: the success-rate paradox (same success rate, opposite
behaviour under overload) carried by the two-cascaded-bottlenecks FaxRx model.

Start-of-week metrics (first days): 191 views, 2 likes, 1 favourite, 0 comments; a
colleague acknowledged it. Read as a working organic start for a technical
methodology piece, not a hot-take — views accrue over weeks and comment silence is
normal for the genre (the 1 favourite is the save-not-argue signal). Not acting on the
numbers yet; noting them as the baseline to watch the curve against over 1-2 weeks.

`#candidate3 #dou #faxrx #published`

## 2026-07-28 — LinkedIn announcement of the DOU article posted

Follow-up feed post to the 2026-07-13 warm-up post (#3), now that the full DOU
longread is live: framed as "the full write-up is out" rather than a re-tell — a
compressed hook (same success rate, opposite failures; undersized front door = admission
control) driving to the article, DOU link in the first comment (LinkedIn down-ranks
posts with in-body links, same mechanic as the July post).
Post: https://www.linkedin.com/feed/update/urn:li:activity:7487631871560814592/
Article: https://dou.ua/forums/topic/60921/ . The author's live copy adds "(in
Ukrainian)" so international readers know the target language before clicking; trimmed
the two-cascaded-bottlenecks line for announcement brevity.

`#candidate3 #dou #faxrx #linkedin #published`

## 2026-07-29 — blog surface wired: README -> articles, DOU cross-linked

Publication-plumbing pass, no new content -- three decisions, all following
corpus/surface:
(1) EN long-forms are the GitHub Pages blog (`articles/`, served by `_config.yml`);
the DOU/LinkedIn forms are cross-linked *into* the matching article entry, not added
as new entries -- one story = one entry. Added the Ukrainian DOU longread
(dou.ua/forums/topic/60921) to the fail-fast entry in `articles/index.md`, marked
"Ukrainian long form".
(2) README now points to the articles index (`articles/index.md`, relative) so a repo
reader clicks through to the blog. Deliberately NOT a `gserdyuk.github.io` link: Pages
renders README *as* the site home, so that would be a self-link -- the github.io URL
belongs in external profiles (LinkedIn/DOU/dev.to), and only once Pages is enabled. The
relative link targets the *file* `index.md`, not the folder, because github.com
auto-renders only `README.md` inside a directory.
(3) Notes stay corpus (dev-log); the blog is finished articles only. Open next steps:
publish the EN fail-fast article on dev.to; enable GitHub Pages (commit `_config.yml`,
Settings -> Pages).

`#blog #articles #dou #surface #pages`

## 2026-07-29 — GitHub Pages live

Pages enabled (Settings, source main / root); first build green from 0712cca. Site is
up: gserdyuk.github.io/twotakt (home = README), the `/articles/` index and the fail-fast
article both return 200, the DOU cross-link is visible on the live index. Closes the
"enable Pages" step from the entry above. Jekyll serves articles as `.html`
(`index.md -> index.html`). The now-live Pages article URL becomes the canonical target
for any external re-post (dev.to). Only open publication step left: EN fail-fast on
dev.to.

`#blog #pages #surface #live`

## 2026-07-29 — EN fail-fast mirrored on dev.to

The English long form is now also on dev.to
(dev.to/serdyuk/fail-fast-or-fail-slow-where-should-your-system-break-under-load-7ii),
with `rel=canonical` pointing at the live Pages copy -- verified in the page head, so the
Pages article stays the SEO first-source and the dev.to copy is a non-penalised mirror.
Same EN text as the repo/Pages article, links back to `examples/FaxRx`. Closes the last
open publication step from the entries above. Publication map now: Pages (EN, canonical)
/ dev.to (EN mirror) / DOU (UK, standalone) / LinkedIn (EN distribution). Left to the
author in the dev.to editor (not blocking): add a DOU cross-link in the footer, widen
tags (`#python`, `#simulation`).

`#blog #devto #faxrx #published #surface`

## 2026-07-29 — USLDBmodel re-verified; article #2 reframed (F36-F38)

Preparing article #2 forced a re-verification of its exhibit, and the exhibit died:
SIM_REPORT's "0.27 vs 1.00" at rate 6 is a one-seed artifact — the knee is bimodal
across seeds (F36). Digging into theory instead: a USL fixed-point ceiling in closed
form gives X* ~= 7.2 (not the naive 10), and the pool at default db_query=0.05 moves
it by 0.04 rps — the default-parameter bottleneck is USL-CPU, the pool is innocent
(F37). The pool binds only past a computable crossover db_query > c/X_cpu* ~= 0.14 s;
at 0.3 s the interaction is clean and seed-robust, and the formula's four ceilings
(7.18/7.22/3.21/6.88) match the simulated collapse points, with stochastic onset ~1 rps
below each (F38). Article #2 direction settled with the author: not "interaction
bottleneck" as originally framed, but "the bottleneck is a regime, not a component" —
the narrative follows the actual investigation (paper 10/20 -> falls at 6 -> pool
suspected, acquitted -> USL formula -> crossover). RU master draft first, then UK/EN.
Rejected framings for the record: the knee/metastability story (too subtle — author),
the confession-genre meta piece (weak reception precedent, #7).

`#candidate2 #usldbmodel #verification #negative-finding #findings`

## 2026-07-31 — LinkedIn warm-up post for #2 published

Second post of the warm-up series (#3 -> #2 -> #1) is live:
https://www.linkedin.com/feed/update/urn:li:activity:7488714946508288000/ . Hook is the
broken formula "min(10, 20) = 6"; repo link in the first comment, as with #3. Two
edits made against the platform rather than the argument: markdown emphasis stripped
(LinkedIn renders it literally) and the `X*` notation replaced by numbers (0.14 s
threshold, 0.05 vs 0.3 s regimes) since the symbol is introduced in the article but
not in a feed post. Companion image is a LinkedIn-specific 1080x1350 4:5 render
(`docs/linkedin_post_2_sweep.png`) with the hook burned into the canvas — the article's
own 2.4:1 figure shrinks to unreadable in the feed. Figures for the article itself
(`articles/img/usldbmodel-architecture.png`, `-sweep.png`) were stripped of prose after
review: the diagram carries only the path, the N bracket and the USL loop.
Remaining for #2: author proofread, EN long form to `articles/` (fix image paths to
`img/...`), Pages canonical, dev.to mirror, UA rewrite for DOU.

`#candidate2 #linkedin #published #figures`
