# Verifiability by construction — a map and a doctrine for AI-built models

> **Type: reasoning** — corpus: append/compact, not synced · born 2026-07-09

*Status: DRAFT. Distilled from a design conversation; the author is still deciding
what survives.*

*Relation to other docs: [`article_candidate_4_vv.md`](article_candidate_4_vv.md) covers
the **validation-harness machinery** in depth (invariant tiers, authorship/independence,
metamorphic relations, the non-composition evidence). This document is the **floor above
it**: why that machinery exists, what it is a special case of, and the design doctrine
that follows. Where they overlap, this file points there instead of repeating.*

---

## 1. The premise: the asymmetry

AI collapsed the cost of **constructing** models. The cost of **justifying** them did not
move. Everything below is one answer to that single fact.

The asymmetry itself is not ours — it has a genealogy:

- **Economics of complements** — Agrawal/Gans/Goldfarb, *Prediction Machines* (2018):
  when prediction gets cheap, its complements (judgment, data) appreciate. General
  mechanism: Baumol — cost concentrates in what does not automate.
- **Asymmetry of verification / Verifier's Law** — Jason Wei (2025): the ease of training
  AI on a task is proportional to its verifiability. Wei also names the **inverse**
  asymmetry: tasks where verification costs *more* than generation.
- **The verification gap** — Karpathy/Balaji (2025), on AI coding: "prompting scales
  because prompting is just typing; verifying doesn't."
- **Pre-AI wisdom** — simulation V&V always knew that building the model is the easy
  part; making it *credible* is the work (Sargent).

Our position on this map: **models of systems are the worst case of the inverse
asymmetry** — a task with *no oracle*. Code has tests and a runtime; a theorem has a
proof checker; a model's correspondence to its object is checkable only against the
object itself. The rest of this document is an engineering construction for living there.

## 2. The map (on standard foundations, deliberately)

We use established vocabulary throughout — the constructions below were mostly
re-derived independently and then found in the literature, which is evidence they are
right, and citable foundations beat homegrown terms.

**Model kinds.** Static/dynamic x deterministic/stochastic (Law & Kelton's classic
simulation taxonomy; Jain ch. 24 has a longer list). A coarse slice — the
continuous/discrete axis is folded in — and deliberately so: the 2x2 does vocabulary
work, not decision work.

**Model is not solver.** Zeigler's triad (*Theory of Modeling and Simulation*, 1976):
**experimental frame** (the questions and conditions under which the model is valid),
**model** (the formal object), **simulator** (the procedure that extracts answers).
Consequences:

- *Simulation is a solver, not a model kind* — the universal solver of last resort.
  The same queueing network can be solved in closed form (Jackson/BCMP), numerically
  (CTMC linear algebra, MVA), or by simulation. The relation is many-to-many.
- Solvers trade generality against trust cost: closed form (restrictive assumptions,
  free trust) -> numeric (state-space limits) -> simulation (works always; pays with
  warm-up, replications, CIs, seeds).
- Historically models were bent to fit solvers (exponential assumptions exist to buy
  Markov tractability). AI collapsed the cost of the *simulation* solver specifically,
  weakening the pressure to simplify — and with it, the habit of analytic
  cross-checking. That habit must be reinstated as a gate (see 3).

**Gates in three layers** — this is standard V&V vocabulary (Sargent; ASME V&V):

| Layer | Standard name | Who checks | Scope |
|-------|--------------|------------|-------|
| **A** | validation ("right model") | human — no oracle exists | invariant across all model kinds |
| **B** | verification ("model right") | machine | specific to the model kind |
| **C** | solution verification | machine | specific to the solver |

Layer A is the irreducible human gate (the audit gate of simstudy-protocol is its
instance). Layers B and C are machine-checkable and therefore delegable to AI. The
B/C distinction separates "the model is wrong" from "we solved it wrong" — two failures
AI produces with equal fluency.

Per-kind B-gates, sketched (each kind has a characteristic way of being
plausibly-wrong; the gate targets it):

| Model kind | B-gates (about the model) | C-gates (about the solution) |
|---|---|---|
| equation system | existence/uniqueness (rank, n vs m), dimensional consistency, closure/conservation, sign/range, reduction to known limits | conditioning, residual norm |
| optimization | feasibility, boundedness, KKT | solver convergence, duality gap, local vs global |
| Markov / CTMC | rows/generator sum correctly, irreducibility, stationary distribution exists | mixing rate, state-space truncation |
| queueing (analytic) | stability rho<1, Little's law, formula preconditions hold | (nearly empty — closed forms) |
| stochastic process solved by DES | entity conservation, no negative queues, discipline correctness | warm-up, replications/CIs (Jain), run length, seeds |
| anything solved by Monte Carlo | sampled distributions correct, input dependence structure | CI width, N sufficiency, seed |

**Concern -> region, not point.** A concern (ISO/IEC 42010: a stakeholder's interest) is
the model's *relevance criterion* — "what may be omitted" has no answer without one.
Formalizing a concern into metrics and questions is the GQM move (Basili), it is lossy,
and it is human (choosing p99 over the mean is already a stakeholder judgment). The
formalized questions point at a *region* of the map, not a cell — whether time or
variability is essential is partly a modeling decision, not a property of the question.

## 3. The verifier portfolio (living without an oracle)

No single verifier exists; what exists is a portfolio of **partial verifiers with
one-sided error** — each can reject, none can certify (Popper). The portfolio (largely =
Sargent's validation-technique catalog + metamorphic testing (Chen 1998) +
property-based testing):

- **invariants** (conservation, probabilities sum to 1, Little) — kill coding/structure
  error classes cheaply;
- **dimensional consistency**;
- **limiting cases** — reduction to analytically known regimes: a *partial oracle*,
  exact within a subregion of parameter space;
- **cross-solver triangulation** — DES vs closed forms on a simplified variant; the
  strongest C-gate available (errors must correlate to slip through);
- **metamorphic relations** — the answer is unknown but its *response to input
  transformations* is known (add a server -> latency must not rise); the only machine
  gate that reaches *mechanism* errors;
- **extreme conditions**; **sensitivity directions**; **data from the object** (when it
  exists — the only true oracle access, partial and expensive).

What the portfolio buys — three things, in increasing importance:

1. **Shrinks the residue**: each gate deletes a class of wrong models.
2. **Severity (Mayo)**: a check's value is the probability it *would fail* if the model
   were wrong in a given way — so gates are chosen against AI's actual failure
   distribution (plausible-invalid step, dropped case, silent inconsistency), not out of
   general tidiness.
3. **Re-prices the human eye**: with the machine-checkable filtered out, the human stops
   verifying arithmetic and verifies only the **mechanism**. The human eye stops being
   the *only* verifier and becomes the *last* one.

The residue has a name: the **well-formed lie** — a wrong mechanism satisfying every
invariant (FIFO modeled where the real system has priorities: conservation balances,
Little holds, the M/M/1 limit matches — and p99 under load is radically wrong, because
tails are exactly where disciplines differ). This defines precisely what layer A must
examine: not correctness, but mechanism.

One recursion worth naming: gates are code, and code sits on the *verifiable* side of
Wei's asymmetry — so AI can cheaply build its own cage. The correlated-blind-spot rule
from [`article_candidate_4_vv.md`](article_candidate_4_vv.md) applies: the trust floor
(which invariants must hold) is named by the human; AI implements and runs them.

*(For the full machinery — tier taxonomy by authorship/independence, promotion loop,
negative-test-first, binding regions — see article #4. It is the worked-out instance of
this section.)*

## 4. Composition: what composes and what does not

> **Layer B composes. Layer A does not.**

**What composes exactly.** Event-level coupling of discrete-event components — DEVS
*closure under coupling* (Zeigler). Departure-process correlations that break *flow-level
analytic* composition (Burke's theorem holds only for M/M/1; M/G/1 departures are not
Poisson; feedback breaks Poisson everywhere) are propagated *correctly and automatically*
by event-level simulation — that is much of why we simulate at all.

**What breaks anyway** — the two preconditions that circuit theory (the tempting analogy:
Kirchhoff at nodes + component equations => valid model) gets from physics and we do not:

1. **Ports carry all interaction** (the lumped assumption). Circuits get it guaranteed
   with a known validity criterion (dimensions << wavelength); systems must earn it per
   assembly — real components share CPU, memory, GC, pools. These are our parasitics and
   crosstalk, except first-order and without a "when can I ignore it" law.
2. **Component equations are context-free.** v = iR is a law across all waveforms;
   "service ~ Exp(mu), FIFO" is a hypothesis validated inside a tested frame. Exact
   composition will faithfully drag a component *outside* the frame it was validated in
   (bursty input, rho -> 1) and faithfully propagate its unvalidated extrapolation.
   Worse, the parameter may not be intrinsic at all (service time depends on a
   colocated neighbor's load — the resistor heated by the circuit).

**The discipline that makes composition sound — assume-guarantee.** Each component
carries a certificate: *assume* (input frame: "Poisson, lambda < mu, C_a^2 <= 2") /
*guarantee* (output law). A joint is valid iff upstream guarantees discharge downstream
assumptions — machine-checkable. Interfaces must carry *enough of the law*, not just
flow balance: conservation preserves rates, but queueing responds to variability
(Kingman: W ~ (C_a^2 + C_s^2)/2), which is why Whitt's QNA propagates (lambda, C_a^2)
through nodes rather than lambda alone.

**Integration gate checklist** (all of layer A that composition adds):

1. Are messages the *only* real coupling? (enumerate shared resources)
2. Is each component, *in situ in the assembly*, inside its certified frame?
   (machine-checkable: log actual input characteristics per component per run, compare
   to certificate — see 7)
3. Are component parameters actually intrinsic, or neighbor-dependent?

**The fix pattern is shared with electronics:** promote the hidden coupling to an
explicit element. The engineer draws a parasitic capacitor or a thermal node; we add
the shared CPU as an explicit Resource the components contend for. The coupling returns
to the ports; the port-completeness assumption becomes true again.

*(Empirical anchor: the non-composition thesis is demonstrated on USLDBmodel in
article #4 — every component individually correct, system collapses at 6 rps on a
pool=1. Component ceilings do not compose.)*

## 5. The architecture lever: isolation buys compositionality

The direction can be inverted: instead of "the model must account for the couplings the
architecture has," choose an architecture whose couplings are *enumerable* — then the
lumped assumption is true by construction. FPGA spatial pipelines are the pure case
(each stage owns its silicon: no time-sharing, no contention, deterministic stage
latency — which is why static timing analysis composes). Same principle under other
names: time-triggered architecture (Kopetz), ARINC 653 partitioning, core pinning,
shared-nothing, bulkheads; circuit vs packet switching is the same axis.

The price is explicit:

> **Isolation buys compositionality and predictability at the price of utilization.
> Sharing buys utilization at the price of modeling complexity.**
> (Queueing theory is, in this sense, the tax paid on statistical-multiplexing gains.)

Isolation also *moves the model across the map*: an isolated deterministic pipeline
leaves the dynamic/stochastic cell for near-deterministic algebra (throughput = min over
stages; latency = sum), stochasticity concentrates at the ingress boundary, and a
compositional formalism with hard bounds exists — **network calculus** (Cruz, Le
Boudec), used to certify AFDX in avionics. Even in an FPGA the shared points do not
vanish (DDR controller, PCIe, thermal) — the workable requirement is not zero couplings
but *named, counted* couplings.

The general principle — the architectural twin of this document's methodological one:

> **Design for modelability.** As chips spend silicon on testability (design-for-test),
> systems can spend utilization on analyzability: isolate flows, reduce couplings to
> enumerable ports, declare frames per level. Then validity is assembled, not
> re-discovered at every level.

Closest existing program: SEI's **Predictability by Construction** (the PACC
initiative — Predictable Assembly from Certifiable Components): predictable assemblies
from certified components, i.e. section 4's certificates aimed at one perspective.
Ours generalizes: modelability includes the observational half (calibratability,
below), and the driver is the AI asymmetry.

Modelability has two halves, and a system can have either without the other:

- **Structural** — isolated flows, enumerable couplings, explicit ports. Buys
  *composable* models: section 4's preconditions hold by construction.
- **Observational** — the system is measurable: metrics, tracing, extraction points at
  component boundaries. Buys *calibratable* models — it is what makes "every parameter
  declares its calibration path" (section 6, item 5) satisfiable at all. Industry calls
  this half observability and motivates it by debugging; the modeling motive is
  different — without it, model parameters are orphans.

A pure pipeline without metrics is composable but not calibratable; a monolith with
perfect tracing is calibratable but not composable.

The diagnostic corollary — the same inversion software went through with testability
("hard to test" is a design defect, not a tester's failing): **"hard to model" is a
diagnosis of the architecture, not of the modeler.** Every place the modeling process
stumbles — a hidden coupling that had to be promoted to a component, a parameter with
no calibration path, a frame nothing can check — is a *finding about the architecture*,
of the same rank as a bottleneck. Collecting these costs nothing (the stumbles happen
anyway) and suggests a second deliverable: a **"modelability findings"** section in the
report — the tool answers about performance and, in passing, measures how analyzable
the architecture is.

Hierarchical version: a level is trustworthy when **its semantics and frame are
explicit** — "exact" means "we know precisely what it claims and when," not "accurate in
every sense." Levels stack by vertical assume-guarantee (the hardware flow
RTL -> gate -> timing, with equivalence checking between levels, is the industrial
existence proof).

## 6. The doctrine: verifiability by construction

Since construction is cheap and justification is the bottleneck, the answer is to make
**verifiability a property of the model itself** — the same move as correctness-by-
construction (Dijkstra), design-by-contract (Meyer), **design for verification**
(software/hardware: build the artifact so it is easier to verify), design-for-test, and
software's discovery that "testable code" and "good code" converge. One distinction
against the parent rhyme: correctness-by-construction promises *correctness* (through
verified refinement); we promise only *checkability* — a weaker claim about a different
object (the model, not the program).

One distinction first: **isolation is a property of the system; verifiability is a
property of the model.** The first is available only when you control the architecture.
The second is available always — even a model of a tightly-coupled dirty system can be
built verifiable, if its structure *exposes* couplings, frames, and parameters instead
of burying them.

| | Verifiability by construction | Design for modelability |
|---|---|---|
| property of | the **model** (the artifact) | the **system** (the object) |
| who acts | the modeler | the system's architect |
| pays with | modeling discipline | utilization, hardware, sometimes simplicity |
| available | always — even for someone else's dirty system | only when you design the system |
| buys | checkable claims about the model | cheap, faithful models of the system — all future ones |
| lineage | correctness-by-construction, design-by-contract | design-for-test, observability |

A model is verifiable by construction when:

1. **Each component runs alone** against its own oracle (unit-simulatable) — built to be
   extracted, like DI in testable code.
2. **Each component carries a certificate**: assume (input frame) / guarantee (output
   law) / gates passed. Joints check mechanically: guarantee covers assume.
3. **Degeneracy is built in**: special parameter values collapse the model onto an
   analytically known case (exponential service + Poisson arrivals -> M/M/1). The
   partial oracle is mounted, not hunted for later.
4. **Invariants are instrumented**: conservation counters, balances, Little's law are
   computed by the model *on every run*, not by a separate script on holidays.
5. **Every parameter declares its calibration path** — "measured thus," or honestly
   "unmeasurable -> scenario variable; output is a fan, not a point." No orphan
   parameters.
6. **Symmetries are declared**: metamorphic relations recorded as properties of the
   model and checkable by runs.
7. **Frame monitors run at runtime** (see 7).

Compressed to one line:

> **A model must carry its own verifiers** — as code carries tests. The artifact is
> Requirements + the model spec + the executable model + the certificate (frames,
> oracles, gates passed) + a per-run verdict. A model without its certificate is not
> under-verified; it is **unfinished**.

The caution that keeps the doctrine honest: **verifiability is not validity.** A
perfectly verifiable model — degradable, instrumented, certified — can still model the
wrong mechanism (the FIFO/priority lie passes all seven points). Layer A does not
disappear; it *concentrates*: one question ("is this the mechanism?"), asked over an
artifact where everything else is already machine-answered. That is the whole deal:
verifiability-by-construction does not remove the incompressible core — it scrapes off
everything compressible around it.

## 7. The per-run verdict: runtime frame monitoring

The applicability domain of a model is **earned, not decreed**: it is the union of
regimes in which the model was actually checked against oracles. AI's legitimate role is
**registrar and patrol**, not authority — it bookkeeps the earned frame and polices it:

- **Input-frame monitors per component**: each run logs actual input characteristics
  (rate, C_a^2, autocorrelation, burstiness) at every component and compares them to
  the certificate's assume-part. "Queue #2 certified for C_a^2 <= 2, saw 4.2" is a line
  of code, not philosophy.
- **Regime monitors**: per-component rho, saturation proximity (the error-amplification
  zone), stationarity, run-length sufficiency.
- **Parameter geometry**: config point inside the convex hull of validated points =
  interpolation; outside = extrapolation. A geometric flag, no judgment involved.

The verdict is **graded, localized, and directional** — not a binary and not a vague
"trust with caution":

1. *where* violated (component, assumption, magnitude);
2. *which outputs are contaminated* (a C_a^2 violation hits latency tails; mean
   throughput may stand) — sensitivity knowledge routes the suspicion;
3. *which direction the bias points*, when known (Kingman: higher C_a^2 -> longer
   waits -> "our p99 is **optimistic**"). A directional qualification beats a shrug.

Precedents — the idea is not speculative, it is scar tissue: **runtime verification**
(monitors compiled from specs), **ODD** in autonomous driving (the system knows its
envelope and flags exits), and **NASA-STD-7009** — written after Columbia, where the
Crater model was applied far outside its calibration domain and the result was read
without the "with caution" qualifier.

Two honesty clauses: the monitor guards only *declared* assumptions (the green verdict
reads "no violations of the declared frame," never "valid"); and flags must stay rare,
localized, and directional, or alarm fatigue turns the patrol into ritual.

Home in this repo: a **frame-compliance section in `SIM_REPORT.md`**, generated per run.
The model does not just carry its verifiers — it **signs every result it produces**.

## 8. The complication discipline

"Model every coupling — construction is cheap now" has a known asymptote (the 1:1 map;
Bonini's paradox: a model as rich as the object is as opaque as the object; digital
twins' actual pain is calibration and drift, not construction). The reason it fails is
the asymmetry itself: each promoted coupling brings **parameters that must be earned**
(measured, calibrated — layer A, not cheapened), a frame to police, and state space to
burn. An accounted-for coupling with an invented parameter is worse than an
unaccounted-for one: a known blind spot becomes **false precision**. Complication
without calibration is degradation dressed as progress.

> Model size used to be bounded by the labor of construction. It is now bounded by the
> **budget of justification**. A model must not be larger than you can validate.

Predicted sign flip (testable): pre-AI models erred *simple* (couplings too expensive to
include); AI-era models will err *baroque* (unvalidatable richness with invented
parameters). A methodology that used to push modelers to include more must now prune.

What cheap construction actually buys here: **relevance becomes an experiment**. Build
both variants (with and without the coupling), sweep, compare — overnight. The
inclusion discipline, per candidate coupling:

| | parameter measurable | parameter unmeasurable |
|---|---|---|
| **output sensitive** | include, calibrate | danger zone: model honest only as a scenario fan ("if contention = X..."), never as a prediction |
| **output insensitive** | drop | drop with relief |

Sensitivity is checked by AI runs (cheap); measurability is a question to the object and
the human (expensive). The matrix sorts details by *cost of trust*, not cost of
construction — the same inversion as everything above.

On emergence: an emergent surprise (retry storm, metastability) is the *purpose* of
simulating, not a defect of composition — but it has no verifier of its own, by
definition. Its credibility is entirely inherited from the gates beneath it:

> **A surprise is worth exactly what the gates under it are worth.**

(The emergence boundary — what may and may not be asserted — is worked out in
article #4: asserting emergent macro-behavior repeats the error of asserting the goal.)

## 9. What is imported and what is ours

**Imported (deliberately):** Zeigler's frame/model/simulator; V&V layering (validation /
verification / solution verification — Sargent, ASME); GQM (Basili); ISO/IEC 42010
concerns; Sargent's validation-technique catalog; metamorphic testing (Chen);
property-based testing; assume-guarantee reasoning; Burke/Jackson/Kingman/QNA; DEVS
closure under coupling; network calculus; correctness-by-construction lineage;
NASA-STD-7009. Using the standard names is itself a decision: they are citable, and the
constructions were verified by fifty years of other people.

**Ours (the actual claims):**

1. **Standard V&V repurposed as the control loop for AI-built models** in the no-oracle
   regime: the machine-certifiable layers (B, C) are delegated to the AI that also
   builds the model *plus* an independent trust floor; the human keeps validation (A)
   and concern-formalization (A'). The gates stop being a project phase and become the
   human-AI interface.
2. **The doctrine** (section 6): verifiability as a constructed property of the model;
   the artifact includes its certificate and signs its runs.
3. **Testable predictions**: (i) transferring the methodology to a new model kind is
   cheap — layer A carries over unchanged, only the B/C tables are rewritten (if a real
   attempt at, say, equation systems finds nothing transfers, the map is wrong); (ii)
   the characteristic failure of AI-era modeling flips from too-simple to
   unvalidatably-rich.

## 10. Open threads

- **Stress-test the map** on a static/stochastic case (direction-finder accuracy: error
  budget, CRLB, Monte Carlo — a different region of the map than everything built so
  far).
- **Frame-compliance section**: prototype it in one example's `SIM_REPORT.md` before
  legislating it in the skill.
- **Modelability findings**: decide whether `SIM_REPORT.md` gains a "modelability
  findings" section (modeling stumbles reported as architectural diagnostics); collect
  real instances during the next example before legislating.
- **Propagation** to the pitch / README — deferred on purpose; this draft settles first.
