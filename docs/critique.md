# twotakt — Critique (v2)

This document is an adversarial review of the project as it stands.
It is intentionally harsh. Strengths are listed first so they are not
discarded by overcorrection; everything after the strengths is to be
treated as a problem until proven otherwise. Concerns are sorted by
severity. The closing tables capture the competitive landscape and
the highest-impact concerns as a single action list.

## Strengths to preserve through any response

These are real and should not be lost in any pivot prompted by the
critique below.

- The audit-first principle is genuinely uncommon and addresses a
  real failure mode in performance modelling. Few competitors do this.
- The "spec is primary, code is downstream" framing is correct and
  rare. It is the methodologically right answer.
- The metric critique (survivorship bias, effective latency, success
  rate) is technically sharp and will catch real mistakes that
  ad-hoc simulations miss.
- The compositional extension model (`USLDBmodel = USLmodel + DB`)
  is clean and demonstrably reusable.
- The library-as-examples approach is honest about the maturity
  level and avoids premature abstraction.
- The dev-log discipline gives the project a navigable narrative,
  not a pile of files.

What follows is what could damage the project.

---

## Tier 1 — risks that can kill adoption outright

> Reviewed in discussion. Each item below carries a **Response** block
> summarising what we decided to do (accept / defer / counter) and the
> concrete action where one was identified.

### 1.1 The methodology is heavy where users want lightness

The audit is eight blocking questions before any code. For a working
engineer under deadline who just wants to know "is four cores
enough?", this is bureaucracy. They will close the tab and go back
to a spreadsheet, intuition, or asking GPT for a quick simulation
script directly.

There is **no fast path**. There is no "give me a hello-world
simulation in 30 seconds and I will look at the methodology
later" mode. Everything begins with the audit gate. This is correct
in principle and lethal in practice for first impressions.

**Mechanism of damage:** users never reach the second example.
Adoption capped at engineers who already believe in methodology.

**Response (reviewed):** accepted with concrete fix. The examples
library doubles as the fast path: a new user is offered the option
to pick the closest existing example as a starter, get a working
sweep immediately, and only enter the full audit when customising.
Requires a minimal discoverability artefact — a one-paragraph
"when to use this" summary per example (either in `MODEL.md` or as
an `examples/INDEX.md`). Trivial at two examples; necessary at five
or six.

### 1.2 Direct AI + DIY SimPy obviates the skill for the casual user

Anyone can paste "write me a SimPy simulation of an API server with
a database" into Claude or ChatGPT and get a working script in
seconds, no audit, no methodology, no `MODEL.md`. The result will
encode all the failure modes our methodology was built to prevent
(survivorship bias, no validation, magic constants, single-curve
plots) — but the user will not know that until much later, and
maybe never.

We are competing not with other simulation tools but with the
**default LLM behaviour without methodology**. The default is fast,
free, and feels good. Our value lands only on users sophisticated
enough to know they want the discipline before they need it.

**Mechanism of damage:** the methodology is invisible IP. A user
who got "good enough" output without us has no reason to come back.

**Response (reviewed):** accepted as a real and unmitigated risk.
We do not have a defence against this for the casual user — by
positioning we explicitly target users who want methodology before
they need it, and accept losing the rest. The mitigation we have is
relative: against *DIY SimPy* (the path serious modellers would
otherwise take) our methodology is the lighter option and provides
demonstrable value. Long-term, if we can build measured evidence
that no-methodology baselines fail in specific named ways
(survivorship bias in latency reports, etc.), this becomes a
defensible argument rather than a stylistic preference.

### 1.3 No calibration → every model is a "trust me"

Without reverse simulation in place, every output is "the LLM and
the modeller believe this is how your system behaves". Engineers
who have been burned by AI mistakes are increasingly sceptical of
unverified outputs. The single most important credibility lever
(matching real observations) is roadmap, not product.

The concept document promises calibration. The architecture
documents Layer 5. Neither is built. Until it is, the project's
credibility ceiling is determined by the user's prior trust in the
modeller's intuition — which is exactly the thing capacity-planning
tools are supposed to replace.

**Mechanism of damage:** sceptical users (the most valuable kind,
typically) reject the output and the methodology with it.

**Response (reviewed):** accepted; calibration goes into the next
iteration. Until it is built and demonstrated end-to-end, the
project's positioning must be honest: *framework today, calibration
in development* rather than *calibrated simulation tool*. The MVP
path is one data source (application logs or Prometheus, not both)
applied to one existing example, end-to-end, before broadening to
other sources or examples.

### 1.4 Skill is Cowork-only

The architecture admits this as a structural out-of-scope, but it
is a serious adoption barrier. Most engineers do not use Cowork.
They use Cursor, VS Code with Copilot, Claude Code, ChatGPT in a
browser, terminal Claude. The skill mechanism does not port.

The methodology itself is portable as text — anyone can read
`METHODOLOGY.md` — but the *enforcement* (gates, automatic critique,
template generation) is Cowork-bound. Users in other environments
get a much weaker product.

**Mechanism of damage:** the addressable user base is the subset of
performance-modelling-curious engineers who are also willing to
adopt Cowork. That is a small set today.

**Response (reviewed):** accepted; addressed via two parallel
tracks that fix different aspects.

*Portability track.* Publish the methodology as a portable bundle
(Markdown methodology + reference documents + prompt fragments +
templates) that copies into any LLM client — Claude Code, Cursor,
Claude Desktop, ChatGPT. Audit will not be automatically blocking
outside Cowork, but the textual content will be identical and an
agent can be instructed to follow it. Cheapest first step. As a
later evolution: an MCP server that exposes the methodology as
tools (`start_audit`, `validate_curve_shape`, `apply_metric_checklist`)
and resources (the reference documents). Available to any
MCP-compatible client, not just Cowork. This is a different MCP
than v1 — v1 exposed simulation and hid SimPy; this exposes
*methodology* and keeps SimPy visible. We deliberately do NOT
build a CLI host that wraps an LLM directly — that would compete
with Claude Code on agentic UX, which we would lose.

*Credibility track.* Strengthen the audit protocol by grounding it
explicitly in established systems-engineering and capacity-planning
literature: ATAM, ARID, C4, the USE method, Gunther's USL writings,
Menasce/Almeida's workload characterisation. This converts the
methodology from "our invention" to "our adaptation of existing
practice", which raises standalone credibility independently of
where it runs. Separate concern from portability — does not solve
Cowork-binding but makes the textual product stronger anywhere it
is used.

### 1.5 No success stories beyond what we built ourselves

Two examples authored by the methodology authors do not constitute
evidence the methodology is useful to anyone else. Every claim in
`concept.md` and `README.md` is currently aspirational. There is no
external user, no case study, no report of "we used twotakt and it
saved us a wrong decision". A prospective user has only the
authors' word that this works.

**Mechanism of damage:** initial users have no signal that they
are not the first to try this. Many will not be.

**Response (reviewed):** ongoing. No specific action captured here
beyond continuing to seek external use cases.

### 1.6 USL parameter selection is voodoo

The single most important modelling decision in the existing
examples is the choice of α and β. Neither has a physical
interpretation the user can derive from their specific system. The
theory glossary explains *what* α and β are; nothing tells the
user *how to pick the right values for them*. In practice, both
are tuned by hand until the curve "looks right" — exactly the kind
of unprincipled fitting the methodology was built to prevent.

This converts a sharp piece of theory (USL) into a magic-number
exercise.

**Mechanism of damage:** any sufficiently honest user notices this
and concludes the methodology is more rigorous in its packaging
than in its substance.

**Response (reviewed):** counter-objection accepted; concrete
multi-part fix.

1. **Remove USL as the default in templates.** The default
   `server_sim.py` becomes M/M/c — `Resource(capacity=N)` without a
   degradation multiplier. Parameters N (capacity), service rate,
   arrival rate are all directly observable from production data.
   No voodoo at the default level.
2. **Reclassify USL in `theory-glossary.md`.** Currently presented
   as the realistic choice; will be re-presented as an *advanced
   option* whose α and β parameters require fitting against
   observed throughput data, with this constraint stated up front.
3. **Keep `USLmodel` and `USLDBmodel` as advanced demos.** They
   still demonstrate the thrashing zone, which M/M/c by
   construction cannot reproduce. They become specialised
   examples, not the canonical baseline.
4. **Build a USL fitting routine.** A small utility that takes an
   observed throughput-vs-load curve and returns α, β. This turns
   USL parameters from hand-tuned to data-fitted. The routine
   doubles as the first concrete piece of calibration (1.3) —
   fitting model parameters from observation is the elementary
   calibration operation.

The four together remove the "magic numbers" experience from the
default path while preserving USL as a deliberate, documented,
data-grounded choice for users who need its expressiveness.

---

## Tier 2 — risks that significantly limit value

> Reviewed in discussion. Each item below carries a **Response** block
> summarising what we decided to do.

### 2.1 The audit assumes the user already knows the answers

Audit Q5 ("what kinds of degradation do you want the model to
encode?") and Q6 ("what backpressure mechanisms exist?") require
the user to already have the categories straight in their head. If
they do not, the audit becomes Claude teaching them queueing theory
in real time. That is fine when it works, but it changes the
character of the audit from "extract intent" to "create intent".
The methodology does not name this distinction.

**Response (reviewed):** accepted with concrete fix — the two paths
("user has clarity" vs "user is figuring it out") are made explicit
at the start of the audit. A new Q0: *"Do you have a specific view
of the model, or shall we start from the simplest one and refine
along the way?"* Two sub-paths — *Extract intent* (full eight
questions as today) or *Walk-through with the simplest model* (agent
proposes a baseline, explains its consequences, user iterates). The
methodology does not pick for the user; it explains the consequences
of each path and lets the user choose.

### 2.2 No protocol for choosing the right theoretical law

We list M/M/1, M/M/c, USL, cache-hit/miss in `theory-glossary.md`
and tell the user to "pick the simplest one that fits". There is no
guidance on how to *test* whether the chosen law actually fits the
system in question. The choice is made before any data exists.

This is a particularly cruel inversion: we make the user commit to
the law in Phase 2, then validate against the law's predictions in
Phase 7. If the law was wrong, the validation succeeds anyway
(against the wrong law).

**Response (reviewed):** accepted; bundled with 2.3 below — the same
fix viewed from two angles. The narrowing of candidate laws based
on the mechanisms identified in Phase 3 becomes part of the
methodology rather than a free choice. A sufficiently complete
Phase 3 leaves only a small set of laws applicable; the user picks
from that set, not from the full menu.

### 2.3 The "smoke test calibration by adjusting defaults" is question-begging

Phase 6 says: if the smoke test reveals an unhealthy baseline,
recalibrate the defaults until it is healthy. But the unhealthy
baseline might be a real signal that the model has a problem. We
have no rule for distinguishing "defaults are wrong" from "model is
wrong". Adjusting until things look good is exactly the failure
mode the rest of the methodology rejects.

**Response (reviewed):** accepted. Reframing: parameters are either
**fitted against observed data** (when calibration data is
available) or **explicitly assumed from theory** (and documented as
such in `MODEL.md`). The current Phase 6 ("recalibrate defaults
until the smoke test looks healthy") is removed as a step. It is
replaced by — when calibration arrives (1.3) — the proper fitting
procedure. Until then, defaults are stated as theoretical
assumptions, not as tuned values. The new Phase 6 and the planned
Phase 7.5 are the same operation.

### 2.4 Spec-code drift has no enforcement

`MODEL.md` and `server_sim.py` are kept in sync by social pressure
and the agent's discipline. There is no automated check, no test
that they describe the same model, no schema linking them. In
practice they will drift. We have already drifted once during this
project's own construction.

**Response (reviewed):** rejected variant A (regex-driven CI check).
Reason: it would impose a structured format on `MODEL.md`, breaking
the principle "no description language other than natural language".
Adopted instead **variant E — periodic LLM-driven audit**.

Approximate shape: each example tracks (in a small file) the commit
at which spec and code were last reconciled. A simple freshness
check counts relevant changes since then; once activity passes some
threshold, a reminder is raised. The audit itself is performed by
the LLM (or human) reading `MODEL.md` and `server_sim.py` together
and reporting any inconsistencies in natural language — exactly the
kind of work the LLM does well and that a regex parser cannot do.
After reconciliation the tracking file is updated.

This is a **reminder, not an enforcement**. Drift can still occur
between audits; the value is bounding how long it accumulates,
without sacrificing the natural-language discipline.

### 2.5 Examples are all IT

The use-cases section claims fleet management, healthcare, logistics,
warehouse throughput. Zero examples target any of these. A user
arriving from healthcare modelling sees an API server example and
has to translate concepts they may not share. The breadth claim is
unsupported.

**Response (reviewed):** accepted. Concrete first action: add a
patient-flow example (clinic) as the canonical non-IT case. Bus
schedule, charging-station, warehouse-pick examples can follow.
Patient flow chosen as the most relatable for a wide audience.
Once at least one non-IT example exists, the breadth claim moves
from unsupported to demonstrated.

### 2.6 No multi-seed discipline

The templates use a single random seed. Stochastic simulation
results are noisy, especially in the thrashing zone where few
requests complete. Single-run conclusions in that zone are
unreliable. The methodology mentions multi-seed as a critique rule
(Rule 7) but the templates do not implement it and the workflow
does not enforce it.

**Response (reviewed):** reframed. Choice of single-seed vs
multi-seed is **not a methodological enforcement**; it is a property
of the *source model* the user has chosen. Single-seed answers
"what does the system do in *this* scenario?"; multi-seed answers
"what does the system do across an ensemble of stochastic
realisations?". Both are legitimate; both answer different questions.

Source-model decisions therefore include three coordinated choices
made together in the audit: arrival pattern (constant / Poisson /
diurnal / bursty / MMPP / fitted), service-time distribution
(exponential / log-normal / deterministic / fitted), and seed
strategy (single specific scenario / ensemble of N seeds with
mean ± std). Templates support both seed strategies. The metric
checklist's Rule 7 is reframed from "one run is not a measurement"
to "if you used a single seed, your numbers describe one realisation,
not the system — say so explicitly". The user makes the choice; the
methodology educates about the consequences.

### 2.7 Service-time and arrival-time defaults are unrealistic

Exponential service times underestimate tail latency variance —
real services are usually log-normal or heavier-tailed. Poisson
arrivals miss bursty / diurnal / driven workloads, which are most
real workloads. Models built on these defaults will look healthier
than reality.

**Response (reviewed):** accepted as part of the same source-model
framing as 2.6. Distribution choice is the user's decision and an
explicit audit topic. The methodology educates about consequences:
exponential service times underestimate p99 tail; Poisson arrivals
miss bursts and diurnality. `MODEL.md` per example must state the
distributions used and acknowledge them as assumptions when not
fitted to data. When calibration is available, the empirical
distribution from observation replaces the assumed one.

### 2.8 No team workflow

The methodology assumes a single modeller. There is no description
of who reviews the audit answers, who signs off on `MODEL.md`, what
happens when two engineers disagree about the model, how reviews
plug into git workflow. Real engineering organisations work in
teams; the methodology silent here.

**Response (reviewed):** accepted as a real gap; not addressed in
this iteration. The methodology is currently for a single modeller.
Team workflow (audit ownership, MODEL.md review, disagreement
resolution, integration with git PR review) is documented as an
acknowledged limitation; designing it is deferred to a later
revision.

### 2.9 AI capability advancement is an existential risk to the methodology

If a future model can produce a correct, well-validated SimPy model
from a one-paragraph description without any audit, the methodology
becomes packaging without product. This is not a hypothetical: each
model release brings the threshold closer.

The methodology's defensible value (prevent specific failure modes)
holds only as long as the models without methodology actually exhibit
those failure modes.

**Response (reviewed):** accepted with a refinement. Rising AI
capability cuts both ways: it lowers the friction of *applying* the
methodology (audit becomes natural, fitting routines run faster,
explanations sharper), and it lowers the apparent need for the
methodology in the first place (less-disciplined approaches produce
less obviously broken outputs). The defence is to position the
methodology as a *way of thinking* about modelling — analogous to
ATAM surviving improvements in CASE tools — rather than as a
compensation for any specific LLM weakness. Cannot be solved
finally; monitored on every major model release.

---

## Tier 3 — friction that compounds over time

> Pending review. Items below have been raised but not yet
> discussed. Responses will be added in a later session.

### 3.1 Cognitive load on a new user is high

A new reader confronting the project must absorb: README, concept,
architecture, methodology, two MODEL.md files, dev-log, SKILL.md,
five reference documents. This is roughly 2000 lines of prose
before producing the first example. The investment-to-value ratio
is poor for a casual visitor.

### 3.2 Vocabulary expansion

The project introduces named concepts faster than it explains them
in context: Resource, Process, Phase, Audit, Sweep, Critique,
Effective Latency, Survivorship Bias, USL coefficients, Phase 7.5,
Layer 5, Rule of Three. Each is justified individually; cumulatively
they tax the reader.

### 3.3 Three-panel plot is opinionated

`plot_sweep.py` produces exactly three panels, in a specific order,
with specific styling. Useful as default, restrictive as the only
option. A user who wants a heatmap, a single curve for a quick check,
or a comparison overlay must hand-roll matplotlib. Templates do not
support these modes.

### 3.4 The skill bundles its own templates, separately versioned

When the methodology evolves and the templates evolve, the skill
bundle must be re-packaged and re-distributed. There is no in-place
update mechanism. Iteration cost is real.

### 3.5 Anti-patterns list is descriptive, not enforceable

"Don't write code before audit" is good advice. Nothing in the
tooling actually prevents it. The agent can be talked out of the
audit by a sufficiently insistent user.

### 3.6 Hard-coded examples library path

The skill references `twotakt/examples/` as the default. Users who
locate their workspace differently (and most will) hit a small but
annoying friction point. Trivial to fix, but emblematic.

### 3.7 No discoverability tooling

To answer "where in our examples do we use a connection pool" the
user reads files. To answer "which examples have an SLA configured"
the user reads files. There is no CLI, no index, no search. As the
library grows from two to twenty examples, this gets painful.

---

## Tier 4 — minor or monitor-only

> Pending review. Items below have been raised but not yet
> discussed. Responses will be added in a later session.

- The `.skill` bundle is built but not eval-tested. We packaged a
  v1 with no measured effectiveness.
- Dev-log discipline relies on humans remembering. No enforcement.
- Phase numbering (Phase 1–12 with a planned Phase 7.5) is a minor
  cosmetic awkwardness.
- The methodology does not mention warmup periods. Smoke tests
  measure from t=0 with an empty system. Real load tests discard
  warmup.
- `requirements.txt` per example is a duplication that will need
  consolidation eventually.
- The two existing examples both use `capacity=1`. Multi-core /
  multi-instance is not exercised at all.
- "Cooperation with Claude" is implicit in everything but not
  explicit anywhere. The methodology does not say what to do if
  the user is working without an LLM.

---

## Competitive landscape — honestly assessed

> Pending review. Table contents and our defensive position
> against each entry will be discussed in a later session.

The v1 concept's competitive table named four competitors:
load-testers, enterprise simulation tools, APM, architecture
diagrams. The picture is wider and less favourable than that
suggested.

| Competitor                                         | What it actually does                                                        | Why it hurts us                                                                                  |
|----------------------------------------------------|------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| Direct LLM use (no methodology)                    | "Write me a SimPy simulation of X" — instant answer                          | Free, instant, requires no audit. Catches the casual user who never returns to learn discipline. |
| DIY SimPy from a textbook or tutorial              | The same thing, with the user controlling the code                           | Free, well-documented, full power, no methodology overhead.                                       |
| Closed-form queueing formulas in a spreadsheet     | M/M/1, Little's Law, Erlang formulas — calculator-level analysis             | For many practical questions, faster than simulation and more rigorous.                          |
| AnyLogic / Simio                                   | Full DES IDEs with visual modelling, calibration tools, validation           | Commercial product with maturity, support, training. Loses to us only on cost and friction.       |
| OMNeT++ / NS-3 / SimPy alternatives (PyPy, Salabim)| Other DES libraries                                                          | Free, open-source, niche but established communities.                                             |
| TLA+, formal methods                               | Verify correctness rather than simulate behaviour                            | For some questions, more powerful than any simulation. Different category but adjacent.           |
| Locust, k6, JMeter                                 | Load test the real system                                                    | If you have the system, this is more credible than any model.                                     |
| APM (Datadog, NewRelic, Honeycomb)                 | Observe what is happening                                                    | Many engineering orgs decided "we'll observe instead of model".                                   |
| Production traffic shadowing                       | Replay live traffic against staging                                          | For mature shadow-traffic setups, this is essentially calibration without modelling.              |
| Cloud capacity-planning tools                      | AWS Compute Optimizer, Azure Advisor, GCP Recommender                       | Vendor-tied, but answer "do I have enough capacity" with zero modelling effort.                  |
| Doing nothing (intuition + experience)             | The default in industry                                                      | Free, immediate, socially accepted. The hardest competitor to beat because it has zero friction.  |

The honest summary is that most actual capacity decisions today are
made by combining intuition with APM data. Any tool — including
this one — has to compete with that practice, which is invisible
and free.

---

## Top concerns as a single action list

If only a handful of these can be addressed, address these. Tier 1
and Tier 2 rows have been reviewed; the Status column reflects the
agreed disposition. Tier 3 and Tier 4 items are not in this table
yet — they will be added once their responses are recorded. The
competitive-landscape section above is also pending review.

| # | Concern                                                                | Tier | Status                | Action                                                                                                       |
|---|------------------------------------------------------------------------|------|-----------------------|--------------------------------------------------------------------------------------------------------------|
| 1 | No fast path / methodology feels heavy on first contact                | 1    | Accepted              | Use examples library as fast path; add `examples/INDEX.md` or per-example "when to use this" summary.        |
| 2 | Direct LLM use without methodology gives "good enough" output instantly | 1    | Accepted              | Position explicitly to users who want methodology; build measured eval of no-methodology failure modes long-term.|
| 3 | No calibration; every model is "trust me"                              | 1    | Deferred              | Next iteration. MVP: one source (logs or Prometheus) + one example, end-to-end. Reposition as "framework today, calibration in development" until built. |
| 4 | Skill is Cowork-only, methodology is not portable                      | 1    | Counter-action        | Two tracks: (a) portable Markdown bundle now, MCP server later; (b) ground audit in established literature (ATAM/ARID/C4/USE/Gunther/Menasce). |
| 5 | No external success stories                                            | 1    | Ongoing               | Continue seeking external use cases.                                                                          |
| 6 | USL α / β are magic numbers                                            | 1    | Counter-action        | Make M/M/c the template default; reclassify USL as advanced; keep USLmodel as advanced demo; build USL fitter (also seeds calibration MVP). |
| 7 | Theoretical-law choice is unvalidated                                  | 2    | Counter-action        | Narrow candidate laws by Phase 3 mechanisms; user picks from constrained set. Bundled with #8.                |
| 8 | Smoke-test "calibration" by tuning defaults can hide real bugs         | 2    | Counter-action        | Remove "tune defaults until healthy" step; defaults are either fitted (when calibration exists) or assumed-from-theory and labelled as such. |
| 9 | Spec-code drift has no enforcement                                     | 2    | Counter-action        | Variant E adopted: periodic LLM-driven audit triggered by activity since last verified commit. No structured-format imposition. |
| 10 | All examples are IT; non-IT use cases unsupported                     | 2    | Accepted              | Build a clinic patient-flow example as first non-IT case.                                                     |
| 11 | Audit assumes user already knows the answers                          | 2    | Accepted              | Two explicit audit paths at start: extract intent (knowledgeable user) or walk-through with simplest model (figuring out). User chooses. |
| 12 | No multi-seed discipline                                              | 2    | Reframed              | Seed strategy is a property of the source model, not a methodological rule. Audit makes it an explicit choice alongside arrival pattern and service distribution. |
| 13 | Service-time and arrival defaults are unrealistic                     | 2    | Counter-action        | Distribution choice is an explicit audit topic; methodology educates about consequences; calibration replaces assumed distributions with empirical ones when available. |
| 14 | No team workflow                                                       | 2    | Deferred              | Acknowledged limitation; designing team workflow deferred to a later revision.                                |
| 15 | AI capability advancement is an existential risk                       | 2    | Accepted              | Position methodology as way-of-thinking; monitor on each major model release; cannot be solved finally.       |

---

## Closing note

This critique is the starting p