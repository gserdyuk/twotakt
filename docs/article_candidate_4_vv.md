# Article candidate #4 — Invariant-based acceptance testing for LLM-generated simulations

*Status: candidate (captured 2026-06-15). Target form: conference talk / short paper.*
*Origin: design conversation while scoping the P1 verification harness.*

*Working title is "invariant-based..."; a later turn reframed the whole thing as
**intent / consistency verification** (§4) — that framing may belong in the title.
Pending a prior-art check on the term (§10).*

This file is the long form — the reasoning chain in full, so the details are not
lost. The one-line version lives in `TODO.md` under "Article / pitch material".

---

## 1. How this came up (provenance)

It surfaced while scoping the **P1 verification harness** ("one command that runs
Phase 7 V&V for every example"). Tracing *why* that item exists revealed it has two
lineages that had quietly merged:

- **Line 1 — narrow, from the skill.** Phase 7 already prescribes V&V for every run.
  The harness just automates an existing phase across the examples → regression-tested
  exhibits. Motive: examples must not silently break.
- **Line 2 — broad, from archived chats** (`dev-log.md`, 2026-06-12, `#v2`): a
  *hybrid validator* — deterministic checkers + LLM-as-judge behind one contract,
  tied to the future Build agent's "ships only green" exit criterion.

The harness we will actually build is **the deterministic half of Line 2 = the whole
of Line 1**. The LLM-judge half stays in v2. Keeping these apart is the guard against
scope creep — and noticing the structure is what produced the article idea.

## 2. The correction that made the idea sharp

First wrong turn (recorded so we don't repeat it): "write the asserts from the spec's
V&V criteria." **Wrong** — the spec / ТЗ is the **goal**, not an invariant. We build
the model precisely to test whether the goal is *achievable* in this architecture.
Asserting the goal asserts the very thing under investigation: a correct model that
shows "this architecture fails the SLA at 10 rps" is a **correct result**, yet a
goal-assert would "fail" on it. Absurd.

> **spec = goal, not invariant.** The requirements verdict (met / not-met) is the
> *output* of the study, never an assertion.

This is the same trap, restated, that appears later with emergent systems (§5).

## 3. What is actually assertable — three layers

| Layer | Question | Assertable? |
|-------|----------|-------------|
| **Requirements / ТЗ** (goal) | does the architecture meet the SLA? | **No** — this is the output (SIM_REPORT verdict) |
| **Verification** ("building the model right") | does the code conserve work? | **Yes** — conservation laws |
| **Validation** ("building the right model") | does the curve have the law's shape? | **Yes** — law-shape, with caveats |

Verification invariants hold for *any* correct implementation, independent of whether
the architecture is any good. Examples at a **deliberately healthy (sub-saturation)
operating point**:
- work conservation: `throughput == arrival_rate`
- no drops without congestion
- `latency == Σ service times` when there is no queueing (no phantom / missing delays)
- success rate 100%

(The skill already requires the verification baseline to be *healthy, not a stress
test* — that is exactly so these invariants don't entangle with goal-achievement.)

> **Don't confuse the two "threes."** This section's *three layers* are Sargent's V&V
> vocabulary (requirements / verification / validation — *what kind of claim*). §4's
> *three tiers* are an orthogonal axis — *who authors the check, how independent*. They
> map: Verification ≈ Tier 1; Validation ≈ Tiers 2–3; Requirements = not assertable.

## 4. The core idea — invariant-based / metamorphic testing

There is **no oracle**: nobody knows whether "throughput = 3.98" is correct. But we
*do* know **relationships that must hold regardless of the answer** ("below saturation,
in = out"). Checking those catches **logical / coding bugs** without an oracle.

Two established techniques attack this oracle problem, and we use **both** (don't conflate
them — see Appendix A):
- **Property-based** — a property of a *single* run that must hold over many inputs
  ("`throughput ≤ arrival_rate` always"). Our Tier-1-at-a-point checks are this.
- **Metamorphic** — a relation *between several* runs ("double the capacity → throughput
  must not decrease"; "scale arrival rate below saturation → throughput scales linearly").
  The multi-generation experiment is metamorphic in spirit.

Both sit on the conservation-law / V&V validation tradition (Sargent).

### Mechanism-toggle metamorphic relations (and an honest note on triviality)

A practical Tier-2 technique that fell out of building the harness. To check that a
declared mechanism (degradation, SLA timeout, retry, …) is actually wired and has its
intended effect, **toggle it and assert a directional relation** between the two runs —
no magic-number threshold.

Worked example (USLmodel). First attempt was a tuned threshold: "peak throughput
< 0.7 × undegraded ceiling". Brittle — the 0.7 is coupled to the specific α, β. It also
turned out a rise→fall curve does **not** prove USL: SLA-timeout collapse mimics it even
with degradation off (verified empirically). The metamorphic replacement:

> `peak(degradation ON) < peak(degradation OFF)`

Degradation can only reduce throughput (multiplier ≥ 1), so disabling it must *raise* the
peak. If degradation is dead, toggling changes nothing → the peaks coincide → the strict
relation fails → bug caught. No tuned constant; the only input is the **sign** of the
effect (off ≥ on), taken qualitatively from MODEL.md. (Measured: peak 4.05 on vs 7.98 off
→ holds; a dead coefficient gives 7.98 vs 7.98 → fails.)

**Precondition — monotonic, isolable sign.** The technique needs the mechanism's effect on
the metric to have a known, monotonic direction. Clean: degradation and SLA timeout each
only ever reduce throughput / completions. Not clean: admission control (`max_threads`) is
non-monotonic — it *raises* throughput under overload by curbing thrashing but *lowers* it
if set too small. And signs can entangle: isolating the SLA relation requires turning
degradation off first, or both collapse together at overload. So: a recipe with boundaries,
not a universal switch.

**Honest note on triviality.** The mechanic is trivial — toggle a flag, compare two runs,
assert an inequality; it is metamorphic / differential / ablation testing, long known. Its
weight here is not the trick but: (a) it dissolves the magic-number brittleness that the
threshold version had; (b) "sign from the spec, qualitative not quantitative" plus the
monotonicity/isolation precondition turns a one-liner into a bounded recipe (enumerate a
model's mechanisms → one relation each); (c) value accrues only *inside* the tiered
no-oracle methodology and the LLM-generated-code context. It is a tool in the kit, never a
standalone headline — claimed as such, a reviewer closes it in seconds.

### Three tiers of invariants (by authorship / independence)

- **Tier 1 — universal (conservation laws).** True for any discrete-event system,
  architecture-independent: work conservation, no-drops-without-congestion, Little's
  law (`L = λ·W`), non-negativity, flow balance (in = out + Δstock). **Human-authored,
  fixed**, lives in the skill **once** as a shared checker. Catches: lost requests,
  phantom/missing delays, wrong Resource capacity.
- **Tier 2 — model-specific law shape.** From the Phase-3 modeling choice: USL → three
  regimes (a region where throughput *falls*); M/M/c → plateau at `capacity/service_time`;
  M/M/1 → hyperbolic latency rise. The **check** is generated per model, but the
  **expectation (which law)** comes from the human-approved MODEL.md, not from the
  generator. Catches: dead degradation coefficient, unwired mechanism.
- **Tier 3 — generator-authored, model-specific bounds.** Properties the generator
  derives from *this* model that are neither universal nor law-shape: "pool = N → concurrent
  DB ops ≤ N", "retries k → a request is served ≤ k+1 times", "admission cap = max_threads
  → queue length ≤ max_threads", inter-component relations. The generator, having just built
  the model, is best placed to state these; a human would not pre-write them.

### Who authors what — and why it matters

| Tier | Author | Independent of generator? | Role |
|------|--------|---------------------------|------|
| **1** conservation | human, fixed library | **yes** | trust floor |
| **2** law shape | check generated; *expectation* from MODEL.md (human-approved) | yes (on the expectation) | trust floor |
| **3** model-specific bounds | generator | **no** (correlated) | extra coverage + catches self-contradiction |

**Tier 1 must not be authored by the code generator.** If the LLM that wrote the model
also writes its safety net, they share blind spots (dev-log: *correlated blind spots*) —
a generator that forgot work-conservation will equally fail to *check* for it. The value
of Tier 1 is precisely its **independence**; generating it per-model with the same model
destroys that. This independence is load-bearing for the whole trust claim (and is a
strong point for the paper). The generator's only Tier-1 obligation is **conforming to a
fixed output contract** (uniform `run(Config()) -> dict` with standard keys —
`throughput`, `arrival_rate`, `success_rate`…) so the fixed checker can bind mechanically.
(Practical note: the examples currently expose `throughput_rps` vs `throughput_fps` vs
`plain_/ocr_` — standardizing this interface is part of the harness work.)

### Tier 3 is coverage, not guarantee — contradiction vs silent agreement

Adding generator-authored checks is **purely additive**: it can only catch more, never
weaken the independent net. The rule that keeps it honest: **certify "green" on Tier 1 + 2
only** (independent); Tier 3 is a bonus net.

Even with correlated blind spots, Tier 3 has real power — it catches the generator's
**self-contradiction**. A failure occurs two ways: code and invariant **silently agree
and are both wrong** (the blind spot — Tier 3 misses this) — *or* they **disagree**, i.e.
the generator built a model and then stated a property the model violates. Disagreement is
high signal: either the code or the stated property is wrong, so there is a real bug or a
real spec ambiguity. Tier 3 cannot *guarantee* generator correctness (silent agreement);
it reliably catches generator *inconsistency* (disagreement). Different things; the second
is valuable.

### Promotion loop (rule of three)

A Tier-3 invariant that recurs across models graduates — by the skill's existing **rule of
three** — to Tier 1: a human vets it and adds it to the fixed library. The generator
becomes a *proposer of candidate universal laws*; humans canonicalize over time.
Bottom-up proposal → top-down canonicalization.

### Critical subtlety — validity region
An invariant carries the operating point where it must hold. `throughput == arrival_rate`
is true **only below saturation**; in overload `throughput < arrival_rate` is **correct,
not a bug**. Every assert must declare its valid range.

### The deeper framing — intent / consistency verification

With no oracle (no golden reference), the legitimate move is **not** to compare against
truth but to **check mutual consistency among several independent expressions of the same
intent**. The tiers are exactly that — independent statements of intent about the system,
cross-checked:

| Expression of intent | Whose | Authority |
|----------------------|-------|-----------|
| Tier 1 — conservation | a universal law ("any correct system must…") | high, near-absolute |
| Tier 2 — law shape | the modeller's, from MODEL.md (human-approved) | high |
| Tier 3 — specific bounds | the generator's, about this model | low, but contradiction is high-signal |
| the code | the implementation | — |

Two independent expressions of one intent **disagree → contradiction → bug**. This is
*consistency verification*, not *oracle verification*.

Spectrum caveat (don't over-generalize): not all tiers are pure consistency. Tier 1 is
closer to an **absolute law** (a truth about reality, not merely a stated intent) →
law-checking. The consistency framing bites hardest on **Tier 3** (generator
self-contradiction) and partly Tier 2. The axis is *whose intent, and how independent*.

This also explains §2 cleanly: a **goal/spec is a desired outcome, not an intent about
mechanism.** Consistency verification checks agreement among statements of *how the system
is built*, not *what we wish it achieved* — so the requirements verdict is structurally
outside the net, by a different reason than "it would beg the question."

Lineage: capturing *design intent* as properties/assertions and checking the
implementation for consistency is long-standing practice in **formal / hardware
verification** (SVA, property checking) and requirements engineering. The project already
leans on this metaphor (README: "same split as hardware verification — architecture =
design, requirements = testbench"), so the framing extends a chosen lineage rather than
importing a foreign one.

### Three orthogonal axes — and why you don't fill the cube

A check has three independent coordinates:
1. **Authorship / independence** — Tier 1 / 2 / 3 (who wrote it, how independent of the generator).
2. **V&V layer** (Sargent) — verification / validation / requirements (what kind of claim).
3. **Scope** — component / edge / system (at what granularity).

The cube of axis1 × axis2 × axis3 is a *map of the possible*, not a checklist. Most cells
are empty or redundant; the map's job is to choose a few high-value checks deliberately and
to know what is left unchecked.

**Proportionality razor** — the same razor simpy-protocol Phase 3 applies to model choices
("what does this capture that a simpler one does not? if nothing, drop it"), applied to
checks: add a check only against a *named risk*, and only if it catches a bug the cheaper
checks miss. Default = system-level Tier-1 conservation (cheap, universal, ~80% of the
value); everything else is added on demand.

**Rebalance V vs V.** Verification (conservation, deterministic) automates well — invest
here. Validation (law-shape, and especially "is the model right about reality") is fuzzy,
expensive, and ultimately settled by the **human audit**, which has no automated oracle —
keep it light. Piling on automated validation hits diminishing returns and risks false
confidence.

**Operational constraint.** The harness is the Build agent's "ships only green" gate, which
must be fast and non-flaky. Minimalism is not aesthetics — a bloated, slow, flaky suite
defeats the gate.

### Component (unit) tests and the non-composition thesis

The scope axis: invariants apply not only to the whole system but to its parts — exactly
the entities the Phase-2 decomposition already names (each Resource, each stage, each
routing edge). The tiers recur per component: Tier-1 (this Resource conserves: acquired ==
released + held; utilization ≤ 1; local throughput ≤ its M/M/c ceiling), Tier-2 (this pool
behaves like its chosen model), metamorphic toggles per component.

Conservation **composes hierarchically** — the continuity equation at every node and edge:
- per node: `in_i = out_i + Δstock_i`
- per edge: `out_A routed to B == in_B` (nothing lost in the wiring)
- system conservation = composition of node + edge balances.

So component + edge checks *decompose* the system invariant and *localize* faults: a system
imbalance with all components green points at the wiring (an edge). System tests say
"something leaks"; component tests say "where."

But both levels are necessary because **component correctness does not compose into system
correctness.** Canonical demonstration — USLDBmodel: each component is individually correct
(would pass its unit invariants) yet the system collapses at 6 rps because a pool=1 binds,
despite a 20 rps paper ceiling. Component ceilings don't compose. The gap between "all parts
OK" and "system fails" is exactly where the interesting findings — and emergent behavior —
live, and component tests provably cannot reach it.

Cost: a component test needs the part observable at its boundary — free in a structural
model, invasive in a monolithic one (see next).

### Component vs metamorphic: orthogonal, complementary, gated by model type

Not competitors — different axes (scope vs technique). They partially overlap in *coverage*
(both fire on, e.g., a broken pool limit) but are not redundant:
- **different requirements:** a component test needs internal observability; a metamorphic
  test needs only the boundary metric + a control knob (observability vs controllability);
- **each catches a class the other misses:** component tests see local violations that never
  reach the boundary; metamorphic tests see interaction / relevance, not a single part's
  local property;
- **they answer different questions:** component = "is this part internally correct?";
  metamorphic toggle = "does this part have its intended effect?" A part can be correct yet
  causally irrelevant (USLDBmodel again).

**Key non-redundancy — they disambiguate each other.** A failing metamorphic toggle ("no
effect") is ambiguous: the mechanism is either dead, or alive but not binding at this
operating point (bottleneck elsewhere). The component test resolves which.

**Which technique is even *available* depends on the model:**

| model type | component / unit test | metamorphic |
|------------|----------------------|-------------|
| **structural** (separable parts, has internal seams) | available & cheap → *unit test*; prefer (fast, localizing, uses an existing seam) | available |
| **functional / black-box / lumped** (defined only at its boundary; analytical formula or undecomposed monolith) | **impossible** | the *only* handle on internal mechanisms (reach in via toggles) |

Terminology: the antonym of *structural* is **functional** — a model defined by *what it
does* (its input→output behaviour), not by its parts; sometimes *phenomenological* (when it
is fitted to observed behaviour). Field-specific synonyms: *reduced-form* (econometrics),
*black-box* (systems / ML), *lumped-parameter* (engineering). The real axis is "has internal
seams / decomposable" vs "defined at the boundary" — **not** "simulation vs formula" (a
monolithic simulation is also seamless).

Design hook: how structural a model is, is a Phase-3 choice (model the pool as its own
Resource → unit-testable; fold it into an aggregate service time → not). Structure *buys*
testability — but by the razor, structure must earn its place on modeling grounds;
testability is a bonus, not a license to over-decompose.

## 5. Does it generalize? Stress test across system classes

*(Tier 3 is omitted here — it is per-model regardless of domain, so it is orthogonal to
the cross-domain axis. The generalization question is about the two trust-floor tiers.)*

| Class | Tier 1 (conservation) | Tier 2 (law shape) |
|-------|----------------------|--------------------|
| Queues / IT | strong | strong (USL / M/M/c) |
| Bus fleet | strong | strong (bunching instability) |
| Precision agriculture | **stronger** (physical mass balance) | medium (dose-response) |
| Agent-based economics | strong (money, Walras' law) | **weak / dangerous** (emergence) |

- **Bus fleet** — still queue-like. Passengers conserved, a bus is always somewhere,
  Little holds, capacity bounded. Tier 2: demand growth → bus *bunching* (known
  instability), nonlinear wait past a knee. Clean transfer.
- **Precision agriculture** — spatial/continuous stochastic. Tier 1 gets *stronger*
  because conservation is literal physics: water balance (in = evapotranspiration +
  runoff + Δsoil storage + uptake), nitrogen balance; non-negativity (0 ≤ moisture ≤
  field capacity). Tier 2 becomes a dose-response curve (more water → yield → plateau →
  harm — structurally the same "knee" as USL). New class: spatial invariants. Mass
  balance is the *canonical* validation for ODE models.
- **Agent-based economics** — the boundary case. Tier 1 holds (money conserved in a
  closed economy; emission is an explicit flow, so conservation holds on the augmented
  system — **stock-flow consistency**; Walras' law: Σ excess demands = 0; budget
  constraints; no negative inventory). **Tier 2 collapses — and rightly so:** equilibria
  are emergent, multiple, path-dependent (bubbles). The expected shape is **not known a
  priori — discovering it is the research.**

### The boundary insight (the talk's keystone)
**Tier-2 strength is inversely proportional to emergence.** Asserting emergent
macro-behavior repeats *exactly* the §2 error of asserting the spec/goal: emergent
behavior is the study's **output**, not an invariant. Same prohibition, two faces:
*don't assert the research result.*

### The cross-domain unifier
Tier 1 is one equation wearing different domain clothes:

> work conservation (queues) = mass balance (agronomy) = stock-flow consistency
> (economics) = the **continuity equation**: `inflow = outflow + d(stock)/dt`.

That is the domain-independent core of the method.

### Honest boundary
The **principle** (oracle-free invariant testing) generalizes to all three classes.
The **harness code** does not — SimPy / queueing primitives won't map onto ODE crop
models or ABM economics. And the current skill is intentionally scoped to IT
performance. So: portable idea, non-portable implementation.

## 6. Novelty assessment (what reviewers will say)

**Not new:** invariant / metamorphic testing of simulations; Sargent V&V balance
checks; conservation-law validation in scientific computing; intent/consistency
verification in formal & hardware verification (assertions, property checking) and
requirements engineering; the unit/integration (component/system) testing distinction.
Claiming "test simulations with invariants / check intent consistency" alone invites
"known for decades."

**Actually new — the contribution:** the intersection with **LLM-generated model code**.
The open 2026 question with no good answer:

> How do you trust a simulation model written by a language model, when you have no oracle?

Intent/consistency verification as the **exit criterion of an AI build agent**
("ships only green"), plus the original observations as the core:
1. the **three-tier taxonomy by authorship/independence** (human-fixed conservation,
   spec-driven law shape, generator-authored bounds) — with the explicit rule that the
   generator must not author its own trust floor (correlated blind spots);
2. the **emergence boundary** (Tier-2 strength ∝ 1/emergence; asserting emergence =
   asserting the goal);
3. **self-contradiction vs silent agreement** — generator-authored checks catch the
   generator's inconsistency even though they cannot guarantee its correctness;
4. the **promotion loop** (generator proposes → rule of three → human canonicalizes into
   the fixed library);
5. the **scope axis + non-composition thesis** — two-level (component + system)
   verification where *component correctness does not compose into system correctness*
   (demonstrated on USLDBmodel), and the orthogonal-axes map with a proportionality razor
   that bounds the suite (default system Tier-1; automate verification, keep validation
   light). Arguably the strongest contribution — it is about the tool, not one example.

## 7. One-sentence thesis

> Conservation invariants give a domain-independent, oracle-free acceptance test for
> LLM-generated simulations; law-shape can be asserted only up to the emergence boundary,
> beyond which it degenerates into asserting the research result.

Reframed (consistency view): *with no oracle, trust in an LLM-generated model comes from
checking mutual consistency among independent expressions of intent — human-fixed
conservation laws, the human-approved chosen law, and the generator's own stated bounds —
where the generator may never author its own trust floor.*

## 8. Evidence plan (what turns this from essay into a credible talk)

Minimum: **one demonstration where an invariant catches a real bug in AI-generated code.**
Good news — this is already on the roadmap, so the paper is a *writeup*, not extra work:

- **P1 harness** = the empirical core (Tier-1 checker on the examples). The USLmodel pilot
  already shows the pattern end-to-end: 3 Tier-1 conservation checks + 3 Tier-2 checks
  (shape + a mechanism-toggle metamorphic relation), all green on the healthy model, and
  each negative-tested (deliberately broken → goes red). That "passes when healthy, fails
  when broken" pair is a miniature Figure 1.
- **Multi-generation experiment** (TODO P3): regenerate an example 3–5× from the same
  description, run the invariant checks, show they catch divergences between generations.
  This is literally Figure 1.

Build the harness **with the talk in mind** — i.e., log enough at each run (which
invariant, at which operating point, pass/fail, observed vs bound) that a regeneration
sweep produces publishable evidence directly.

## 9. Positioning among the existing candidates

TODO already lists three article candidates (interaction bottleneck, fail-fast/slow,
audit-first). This is the **fourth, and methodologically the strongest** — it is about
the *trust mechanism for the tool itself*, not a single example. Candidate to lead
**ahead of** audit-first as "article #1".

## 10. Open questions / to decide later

- Venue and format (workshop short paper vs conference talk).
- Do we need a *planted* bug, a *found* bug, or both, for credibility?
- How much of the LLM-judge (Tier-2 semantic) half to even mention — or keep it strictly
  to the deterministic Tier-1 story for a clean claim?
- Whether to include a non-IT worked example (agriculture / economics) or keep them as
  the "generalizes in principle" argument only.
- **Prior-art check on "intent verification."** The term is not one standardized concept —
  it appears in formal verification, requirements engineering, and recently in LLM-code
  contexts (checking generated code against stated intent). Before using it as the paper's
  umbrella term, verify exact prior art so we neither reinvent a named method nor rename
  someone else's. Decide title accordingly (invariant-based vs intent/consistency).
- Title: keep "invariant-based acceptance testing" or move to "intent / consistency
  verification" (depends on the prior-art check above).
- How much per-component instrumentation to require of generated models — the observability
  cost of component/unit tests vs their localization benefit. Where to draw the structural
  vs reduced-form line for the case studies.

---

## Appendix A — Reading & definitions

Background for the terms used above. Read these before writing the paper; several of our
"new" ideas are instances of established techniques, and citing them correctly is what
keeps the novelty claim (the LLM-generated-code angle) defensible.

### Sargent — simulation V&V
**R.G. Sargent, "Verification and Validation of Simulation Models."** Canonical tutorial,
re-published for decades in the **Winter Simulation Conference (WSC)** proceedings; polished
version in **Journal of Simulation, 2013** (the one cited in the skill).

- Splits **conceptual model** vs **computerized model** — our `MODEL.md` vs code.
- Validity framework: conceptual validity, computerized verification, operational validity,
  data validity.
- Catalog of validation techniques — and **several are our invariants under other names**:
  *extreme-condition test* (behaviour at overload / zero load), *degenerate / fixed-value
  test* (set a parameter so the answer is known — e.g. α=β=0 → pure M/M/1), *internal
  validity* (spread across seeds must be sane), *face validity, traces, sensitivity*.
- **Use:** vocabulary + legitimacy. We instantiate Sargent's techniques for LLM-generated
  code; we are not inventing the techniques.
- **Read:** the free WSC tutorial (~15 pp) as entry; JoS-2013 as the citation.

### Metamorphic testing — and how it differs from property-based
Origin: **T.Y. Chen et al., 1998**. Survey: **Chen et al., "Metamorphic Testing: A Review of
Challenges and Opportunities," ACM Computing Surveys, 2018.**

Solves the **oracle problem**: when you cannot tell if a *single* output is correct, check
**metamorphic relations (MRs)** — relations across *multiple* runs that must hold if the
program is correct. E.g. `sin(x) == sin(π − x)`; search `A AND B` returns ≤ results of `A`;
`det(AB) == det(A)·det(B)`.

**Distinguish two oracle-free techniques — we use both:**
| Technique | Scope | Our example |
|-----------|-------|-------------|
| **Property-based** (e.g. QuickCheck) | a property of *one* run, over many inputs | `throughput ≤ arrival_rate` always (Tier-1-at-a-point) |
| **Metamorphic** | a relation *between* runs | "double capacity → throughput non-decreasing"; "scale λ below saturation → throughput scales linearly" |

The multi-generation experiment is metamorphic in spirit (same spec, different generations →
outputs must satisfy the same relations). In the paper, name property-based vs metamorphic
precisely — a reviewer will catch sloppy conflation.

### Emergent behavior — and why it bounds Tier-2
Informally "the appearance of new properties," but precisely: **system-level
properties/patterns arising from component interactions that are not properties of any single
component and are not directly derivable from them.** "The whole behaves as the parts cannot."
Touchstone: **P.W. Anderson, "More is Different," 1972.** Accessible book: **M. Mitchell,
*Complexity: A Guided Tour.***

- Signs: macro-pattern from micro-interactions (bottom-up), nonlinearity, feedback,
  multiple / path-dependent equilibria, phase transitions.
- Examples (increasing): traffic jam from individual cars; bus bunching; market bubbles
  from individual traders. The USL **knee** is *weak* emergence — born from coordination
  overhead but still **analytically predictable**.
- **Weak vs strong** is a philosophy debate we can skip. The operational line that matters:

  > Can you name the expected macro-pattern **before** running?
  > — Yes (M/M/c plateau, USL three regimes) → **Tier-2-assertable.**
  > — No, the run exists to discover it → **not assertable** (= the §2 trap, asserting the
  >   research result).

- The keystone tie-back: **emergence does not violate conservation.** Money is conserved
  inside a bubble; mass inside a chaotic system. So **Tier-1 survives everywhere**, while
  Tier-2 degrades exactly as emergence grows — that is the *emergence boundary* (§5).
