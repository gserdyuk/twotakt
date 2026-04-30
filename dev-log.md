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
