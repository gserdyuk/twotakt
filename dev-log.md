# twotakt — development log

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

`#one-pager #translation #english #docs`
