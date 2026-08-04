> **Type: reasoning** — corpus: prior-art bibliography, append/compact, not synced · born 2026-08-01

# Prior art — "AI Influence on the Architectural Landscape" (series S)

Annotated, two-sided bibliography feeding the analysis articles. Unit = a **record**:
source -> what it actually claims (verified) -> stance vs our thesis -> where we'd cite it.

**Method.** Every entry confirmed by fetch/search, not from memory. `read:` marks what was
actually read (full / abstract / primary / secondary). Home is temporarily this repo; the
landscape series is economics -> likely migrates to **3A8** (see dev-log 2026-08-01). Built
out over clusters A-E (the phase-3 collapse and its four spokes).

**Legend.**
- *Type:* peer-reviewed · preprint (arXiv) · book · practitioner · primary-eng-blog · survey/data
- *Stance:* **SUPPORTS** (our conclusion) · **REFINES** (mechanism we'd adopt) ·
  **TEMPERS** (limits our claim) · **CONTRADICTS** · **BOUNDARY** (it-depends / mainstream)
- *Clusters:* **A** phase-3 collapse (the hub) · **B** microservices · **C** re-verification ·
  **D** options · **E** lifecycle economics. `[K#]` = classical anchor, shared across clusters.

---

## Cluster A — the collapse of phase 3 (code production), and its unevenness

*The economic engine of the whole series (F12). Claim: AI collapsed the cost of writing
code — but unevenly (accidental, not essential), and the collapse does not reach delivery.*

### Supporting — the price drop is real

**[A-S1] Peng, Kalliamvakou, Cihon, Demirer (GitHub/Microsoft), "The Impact of AI on Developer Productivity: Evidence from GitHub Copilot"** — preprint (arXiv 2302.06590), 2023. `read:secondary`.
- *Claim:* controlled experiment, HTTP-server-in-JS task; Copilot group **55.8% faster** (1h11 vs 2h41), P=.0017, CI [21%, 89%]. Less-experienced/older/higher-volume devs gained most.
- *Stance:* **SUPPORTS** — cleanest quantified proof construction got cheaper. Honest caveat to state: greenfield toy task, not mature-codebase change (contrast [A-C1]).

**[A-S2] "AI Made Code Free" (practitioner framing, dev.to/krlz)** — practitioner, 2025-26. `read:secondary`.
- *Claim:* "AI collapsed the cost of writing software to near zero. However, it did not collapse the cost of distribution, trust, support, or being liable when it breaks — and those are ~80% of what a software business actually is."
- *Stance:* **SUPPORTS / REFINES** — our thesis in the wild; the "other 80%" names exactly the phases the collapse does *not* touch. Wave-tier source, but a clean statement.

### Tempering / contradicting — the drop is uneven and stops short of delivery

**[A-C1] METR, "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity"** — preprint (arXiv 2507.09089) + metr.org, 2025-07. `read:primary`.
- *Claim:* RCT, 16 experienced devs, 246 real issues on mature repos they'd maintained for years (22k+ stars, 1M+ LOC), Cursor Pro + Claude 3.5/3.7. Result: **19% slower** with AI — while devs *believed* they were ~20% faster.
- *Stance:* **CONTRADICTS** — for experienced work on mature code the price *rose*. The perception-reality inversion is itself a citable warning against self-reported productivity.

**[A-C2] GitClear, "AI Copilot Code Quality" (2024/2025 reports)** — survey/data, 211M changed lines 2020-2024. `read:secondary`.
- *Claim:* refactoring ("moved" lines) fell 24.1% (2020) -> 9.5% (2024); copy-paste rose 8.3% -> 12.3%; code revised within 2 weeks (churn) 3.1% -> 5.7%; duplicated blocks up ~8x.
- *Stance:* **TEMPERS** — cheap production buys maintainability debt. "Cheap regeneration is clean" is false; the accidental-complexity win is partly repaid downstream.

**[A-C3] Addy Osmani, "The 70% problem" (later "The 80% problem")** — practitioner, addyo.substack, 2024. `read:secondary`.
- *Claim:* AI produces ~70% (scaffolding, obvious patterns) fast; the last 30% — edge cases, security, production integration — "as time consuming as ever."
- *Stance:* **REFINES** — Brooks [K1] in field data: accidental collapses, essential remains. The 30% is the essence; maps onto our "phases 1-2 and verification stay expensive."

**[A-C4] DORA 2025 report** — industry research, dora.dev, 2025. `read:primary`.
- *Claim:* AI is an **"amplifier"** — magnifies strong orgs, magnifies dysfunction in weak ones. Loosely-coupled + strong platform/tests -> AI helps; fragile/tightly-coupled -> AI accelerates tech debt. Higher adoption raises **both** delivery throughput **and** instability; 30% distrust AI code.
- *Stance:* **REFINES (bridges A<->B)** — the price drop is not uniform: architecture decides whether it materializes. An empirical hook straight into the microservices argument.

**[A-C5] The productivity paradox (philippdubach; ShiftMag; Faros AI)** — survey/data, 2025-26. `read:secondary`.
- *Claim:* ~93% adoption, ~27% of production code AI-authored, yet aggregate productivity ~10% and flat >1 year; +21% tasks and +98% PRs merged, but **PR review time +91%** — the bottleneck moved downstream to review/governance.
- *Stance:* **TEMPERS (sets up cluster C)** — faster typing, flat delivery: the collapse doesn't reach the outcome because a *different* phase (verification) is now binding.

### Classical anchor

**[K1] Fred Brooks, "No Silver Bullet — Essence and Accident in Software Engineering"** — 1986. `read:secondary`.
- *Claim:* accidental complexity (languages, tools, coding) vs essential complexity (the problem: requirements, design). Shrinking accidental to zero yields no order-of-magnitude win, because essential remains.
- *Stance:* **REFINES (the spine of the whole series)** — AI is the long-awaited attack on *accidental* complexity (phase 3). Our "phases 1-2 stay expensive, phase 3 collapses" is Brooks restated for the AI era; everything in A-C1..C5 is Brooks playing out.

### Synthesis — cluster A

The price of *typing* code fell hard on greenfield tasks ([A-S1], +56%), and practitioners
feel it as "code is free" ([A-S2]). But three independent lines show the fall is uneven and
does not reach delivery: quality/maintainability erodes ([A-C2]), experienced work on mature
code actually slows ([A-C1]), and aggregate delivery stays flat because the choke moved
downstream ([A-C5]). Brooks ([K1]) explains *why* — only accidental complexity was attacked —
and Osmani's residual 30% ([A-C3]) is the essence made visible. The claim our series needs
survives, but must be stated precisely: what collapsed is **construction of the accidental**,
not "software got cheap." DORA ([A-C4]) sharpens it into architecture's court — the collapse
materializes only for loosely-coupled systems — which is itself the microservices argument
(B), and the flat-delivery choke is the re-verification argument (C). A is the hub; B and C
are its two spokes.

---

## Cluster B — microservices: modularity + distribution (Phase 0 calibration cluster)

*Claim: microservices glue two decisions — modularity (boundaries for change) and
distribution (boundaries for runtime). AI removes the change-cost justification and leaves
runtime untouched; distribution must re-earn its keep.*

### Supporting stream — monolith / modular-monolith / AI-favors-locality

**[B-S1] Amazon Prime Video (Marcin Kolny), "Scaling up ... and reducing costs by 90%"** — primary-eng-blog, Prime Video Tech, Mar 2023. `read:secondary` (corroborated by [B-C1]).
- *Claim:* a distributed serverless design (Step Functions + Lambda, chatty transitions) hit account limits; repacking into a single process cut infra cost **>90%**. Author caveat: "case-by-case."
- *Stance:* **SUPPORTS** — the poster-child that distribution can be net-negative for a workload. **But** read [B-C1] before leaning on it.

**[B-S2] Martin Fowler, "MonolithFirst"** — practitioner, martinfowler.com, 2015-06-03. `read:secondary`.
- *Claim:* start as a modular monolith; split to microservices only when it becomes the problem. Successful microservice teams started from a monolith; greenfield-microservice teams struggled.
- *Stance:* **SUPPORTS / REFINES** — pre-AI, but gives "modular monolith as default" a decade-old authority. Our AI argument = a new *reason* for a boundary Fowler already recommended.

**[B-S3] DHH, "The Majestic Monolith"** — practitioner, Signal v. Noise, 2016-02-29. `read:secondary`.
- *Claim:* the distribution patterns that fit Amazon/Google are often the opposite of what a small org needs; an integrated monolith removes needless abstraction.
- *Stance:* **SUPPORTS** — the org-size argument; also a bridge to "what survives" (Conway [K2]): the split reason is org, not change-cost.

**[B-S4] Shopify Eng ("Deconstructing the Monolith" / Packwerk)** — primary-eng-blog, 2019-2020. `read:secondary`.
- *Claim:* one of the largest Rails monoliths in production, made *modular* via enforced package boundaries (Packwerk: explicit public interfaces, dependency checks) instead of physical service split.
- *Stance:* **SUPPORTS** — existence proof that modularity is separable from distribution at scale. Our two-glued-decisions thesis, in production.

**[B-S5] Vishal Mysore, "Do AI Coding Agents Reason Better in Modular Monoliths Than Microservices?"** — practitioner, Medium, 2026-05-14. `read:full`.
- *Claim:* "Architectural distribution increases reasoning complexity for AI coding agents"; agents do better with co-located logic (finite context, weak long-term memory). Introduces *ModulithBench* — "measurements still in progress."
- *Stance:* **SUPPORTS (weak evidence)** — closest to our thesis; the honest "not-yet-proven" status is itself citable: the field feels this but hasn't measured it.

### Contradicting / tempering

**[B-C1] Adrian Cockcroft, "So many bad takes — ... the Prime Video microservices to monolith story"** — practitioner, Medium, 2023. `read:secondary` (quotes verified across 3 outlets).
- *Claim:* [B-S1] is **not** microservices->monolith; it is "Step Functions->microservices" — a serverless-first prototype refactored to scale. "This definitely isn't a microservices-to-monolith story."
- *Stance:* **CONTRADICTS (the framing, not us)** — the wave's favourite proof point is misread. Citing this *strengthens* our credibility: we don't lean on the bad take.

**[B-C2] Adnan, Esposito, Taibi, Vaidhyanathan, "Can AI Agents Generate Microservices? How Far are We?"** — preprint (arXiv 2603.09004), 2026. `read:abstract`.
- *Claim:* 144 generated microservices; incremental gen 50-76% unit-test pass, clean-state 81-98% integration pass, lower complexity than human baselines, 6-16 min/service. "Fully autonomous microservice generation is not yet achievable" — needs oversight.
- *Stance:* **TEMPERS (both ways)** — AI does *not* trivialize distribution (oversight needed), yet generates distributed services competently — so "AI can't do microservices" is too strong.

**[B-C3] Stefan Tilkov, "Don't start with a monolith"** — practitioner, martinfowler.com, 2015. `read:secondary`.
- *Claim:* direct counter to [B-S2]: it is very hard to keep monolith modules as isolated as microservices demand; starting distributed *forces* clean decoupling.
- *Stance:* **CONTRADICTS** — the strongest principled objection to "modular monolith by default": boundaries erode without the physical wall. Our answer must address enforcement (cf. Packwerk [B-S4], Parnas [K4]).

**[B-C4] Nuthalapati, "Balancing Microservices and Monolithic Architectures"** — preprint (arXiv 2607.03898), 2026. `read:abstract`.
- *Claim:* neither wins; choose by system size, business need, operational maturity, maintainability. No AI angle at all.
- *Stance:* **BOUNDARY** — the mainstream "it depends" that a 2026 survey still holds *without* invoking AI. Useful foil: our contribution is precisely the AI term this paper omits.

**[B-W] The hype wave (states the conclusion, skips the mechanism)** — Lacerda "The Death of Microservices…" (Medium); logiciel.io (vendor). `read:secondary`.
- *Stance:* **SUPPORTS conclusion / weak** — cite as *the wave we differentiate from*: they assert "AI kills microservices"; we supply the why (two glued decisions; only change-cost collapsed) and a computable boundary. Context, not evidence.

### Classical anchors

**[K2] Melvin Conway, "How Do Committees Invent?" (Conway's Law)** — Datamation, 1968. `read:secondary`.
- *Claim:* organizations produce designs that copy their communication structures.
- *Stance:* **BOUNDARY (our honesty clause)** — anchors "what AI does NOT change": org boundaries still force splits regardless of code cost. Keeps the article from over-claiming the monolith's return.

**[K3] Baldwin & Clark, "Design Rules, Vol. 1: The Power of Modularity"** — MIT Press, 2000. `read:secondary`.
- *Claim:* modularity creates **real options** (swap a hidden module's early solution for a later, better one), valuable under uncertainty and pricable by finance theory.
- *Stance:* **REFINES (double duty)** — (a) academic root of "modularity = boundaries for change," separable from distribution; (b) theoretical spine of cluster D / S4 "architecture as an options portfolio."

### Synthesis — cluster B

Consensus in the room: the pendulum has swung toward the **modular monolith**, but the
serious voices refuse the slogan — the mainstream position ([B-C4]) is still "it depends,"
and the wave's best evidence ([B-S1]) is a misread refactor ([B-C1]). Our differentiator is
neither the conclusion (the wave [B-W] has it) nor the "it depends" (the survey [B-C4] has
it), but the **mechanism**: two glued decisions, only change-cost collapsed ([K1] restated),
modularity-as-options separable from distribution ([K3], [B-S4]) — plus a computable boundary
where others opine. Honest edges to keep: enforcement ([B-C3], [K4]), Conway's residue ([K2]),
and that AI neither trivializes nor fails at distribution ([B-C2]).

---

## Cluster C — the re-verification surface (production <-> verification; article #6)

*Claim: regeneration is cheap, re-verification is not; the boundary that now matters is the
one that bounds what you must re-prove. "Unit of architecture = unit of re-verification."*

### Supporting — verification is the new bottleneck

**[C-S1] "The Bottleneck Isn't Coding Anymore. It's Verification"** — practitioner, DevOps.com, 2025. `read:secondary`.
- *Claim:* "Code generation is now cheap; verification is expensive. The bottleneck has moved" — from writing code to deciding whether it is safe to merge.
- *Stance:* **SUPPORTS** — our #6 headline, stated flat by the industry press.

**[C-S2] Review-queue data (ShiftMag "review queues longer"; Faros AI; MetaCTO)** — survey/data, 2025-26. `read:secondary`.
- *Claim:* AI adoption raises task completion +21% and PRs +98%, but **PR review time +91%**; "reviewing and validating AI-generated code" now ranked the #1 skill for the AI era.
- *Stance:* **SUPPORTS** — quantifies that cost relocated to re-verification; the surface, not the writing, is where time goes.

**[C-S3] Trust data (Stack Overflow 2025; "State of Code" surveys; DORA)** — survey, 2025. `read:secondary`.
- *Claim:* trust in AI accuracy ~29% (SO 2025); reports of "96% don't fully trust functional accuracy"; DORA 30% little/no trust.
- *Stance:* **SUPPORTS** — the re-verification burden is structural: you cannot skip re-proving what you do not trust, so it becomes the binding cost.

**[C-S4] Contract testing / bounded-context / blast-radius practice (SoftwareMill; Curiosity; TotalShiftLeft)** — practitioner, 2024-26. `read:secondary`.
- *Claim:* decoupled components behind explicit interfaces let teams "use component tests targeting just the functionality impacted by a change"; "focus contract testing on the integrations with the highest blast radius." Contract tests verify a boundary without running both sides.
- *Stance:* **REFINES (the mechanism)** — the pre-AI practice our slogan generalizes: a service boundary *is* a re-verification boundary. The novelty is only that AI makes re-verification, not rewriting, the reason to draw it.

**[C-S5] "The bottleneck moved to review — understand intent" (CodeRabbit; vietanh.dev; theflock)** — practitioner, 2026. `read:secondary`.
- *Claim:* review is shifting from line-by-line to "does this advance our goals / architectural coherence" — intent-level rather than token-level checking.
- *Stance:* **REFINES (bridge to twotakt #4)** — verification-by-intent is exactly the intent/consistency trust-machinery (series B / #4). Industry is converging on it independently.

### Tempering

**[C-C1] Adnan et al. (arXiv 2603.09004)** — cross-ref [B-C2]. `read:abstract`.
- *Claim:* AI clean-state microservice generation reached **81-98% integration-test pass** — strong API-contract adherence.
- *Stance:* **TEMPERS** — if AI honors contracts well, the re-verification surface at boundaries may be cheaper than pessimists assume; "distributed re-verification is a nightmare" is not absolute.

### Classical anchors

**[K4] David Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules"** — CACM 15(12):1053-1058, 1972. `read:secondary`.
- *Claim:* decompose by **information hiding** — each module hides a likely-to-change decision — so that "if one module changes its internal representation, other modules need not change."
- *Stance:* **REFINES (the deep root)** — Parnas already made "a change is contained within a boundary" the point of modularization. Our re-verification surface is Parnas's containment re-priced: the boundary now bounds *re-proving*, not just *editing*.

**[K5] Edsger Dijkstra, "testing shows the presence, not the absence of bugs"** — Notes on Structured Programming (EWD249), 1970 (earliest 1969, NATO). `read:secondary`.
- *Claim:* testing can demonstrate defects but never prove their absence (except by exhausting finite input).
- *Stance:* **BOUNDARY (why re-verification is fundamentally costly)** — verification is inherently incomplete, so re-verifying a regenerated blob is never "just run the tests." The hard floor under twotakt #4's "coverage, not guarantee."

### Synthesis — cluster C

Best-attested of all: the industry states our #6 thesis almost verbatim — "code is cheap,
verification is expensive, the bottleneck moved" ([C-S1]), with numbers (+91% review time
[C-S2]) and a trust deficit that makes re-proving unavoidable ([C-S3]). The mechanism we
claim — boundaries bound the re-verification surface — is not new; it is Parnas's information
hiding ([K4]) and everyday contract-testing practice ([C-S4]), and Dijkstra ([K5]) explains
why the surface never shrinks to zero. Two moves keep our contribution non-obvious rather
than a restatement: (1) the *reason* to draw a boundary flipped from cost-of-rewrite to
cost-of-re-prove (the F12 -> re-verification pivot), and (2) the answer is intent-level checking
([C-S5]), where the industry and twotakt #4 meet. Honest temper: AI's contract adherence is
already decent ([C-C1]) — the boundary is an optimization, not a rescue.

---

## Cluster D — architecture as options (modularity/oversizing as purchased optionality; S4)

*Claim: modularity and spare runtime capacity are real options — the right, not the
obligation, to change or scale later; priceable under uncertainty. The theoretical spine of
"architecture as an options portfolio."*

### Supporting

**[D-S1] Gregor Hohpe, "Architecture: Selling Options" / The Software Architect Elevator** — practitioner/book, architectelevator.com + O'Reilly 2020. `read:secondary`.
- *Claim:* "I sell options." Architecture's economic value is deferring decisions at a known cost (horizontal scalability defers the server-size decision; separation of concerns localizes change). Explicit tradeoff: more options <-> more complexity — don't buy all options always.
- *Stance:* **SUPPORTS (the practitioner articulation)** — names our S4 framing directly, including the cost side (optionality isn't free), which guards against "just oversize everything."

**[D-S2] Real-options-in-architecture literature (Bahsoon & Emmerich, UCL; "Valuing Modularity as a Real Option," Mgmt Science; ASCE real-options surveys)** — peer-reviewed, 2000s-2020s. `read:abstract`.
- *Claim:* real-options analysis values architectural flexibility under uncertainty; investment = upfront + increments contingent on likely requirement changes; frameworks value both structural (maintainability) and behavioral (throughput) qualities.
- *Stance:* **SUPPORTS (academic rigor)** — a peer-reviewed program already prices architecture as options, including *behavioral* qualities like throughput — the exact seam where twotakt's runtime numbers become the option's payoff distribution.

### Classical anchor

**[K3 Baldwin & Clark]** (defined in cluster B) — the origin: "Design Rules" formalizes modular
design as generating real options, valued by finance theory. Cluster D is the direct
descendant; S4's "portfolio" is Baldwin-Clark applied to one system's architecture variants.

### Synthesis — cluster D

The most academically settled and least AI-specific cluster — which is a feature: S4 doesn't
have to invent its economics, only supply the missing input. Baldwin & Clark ([K3]) established
modularity-as-options in 2000; Hohpe ([D-S1]) turned it into the working architect's mantra
("I sell options") with the discipline that options cost complexity; the real-options program
([D-S2]) already prices flexibility under uncertainty, explicitly over *behavioral* qualities
like throughput. The gap we fill is the payoff distribution: prior work assumes or hand-waves
the runtime/business outcomes; twotakt computes them (constraint), 3A8 runs the Monte Carlo
over growth trajectories (optimization). So D's prior art is strong enough that our contribution
is narrow and defensible — not "architecture is options" (owned), but "here is the computed
distribution that makes the option pricing real for a specific system."

---

## Cluster E — lifecycle economics: where the money actually is (article #8)

*Claim: the lifecycle cost structure (maintenance dominates; defects cheap early, dear late)
is stable and well-measured — and AI's collapse of phase 3 reshapes the pie without erasing
the structure.*

### Classical anchors (this cluster is anchored in the classics; recent work updates them)

**[K6] Lientz & Swanson, "Software Maintenance Management"** — book/survey (487 orgs), 1980. `read:secondary`.
- *Claim:* maintenance/evolution consumes the majority of lifecycle cost (surveys since range 50-90%); within it ~60% is *perfective* (enhancement), not corrective. Proportions have held stable across decades.
- *Stance:* **REFINES (the foundation of #8)** — "the money is in the second loop." The maintenance loop dominates TCO because it repeats — the fact AI economics must reprice, not ignore.

**[K7] Barry Boehm, "Software Engineering Economics" — the cost-of-change curve** — book (TRW/IBM/GTE/Bell data), 1981. `read:secondary`.
- *Claim:* a defect's fix cost rises across phases — a requirements error caught late can cost ~100x (the "1-10-100" heuristic; ~5x for small systems). Boehm & Basili (2001) report a *flatter* slope for agile/CI-CD.
- *Stance:* **REFINES / BOUNDARY** — anchors "phases 1-2 are cheap to get right *only if* caught early." The flattening under CI/CD is a self-check: the curve is context-dependent, not a law — don't overclaim.

### Supporting (AI-era)

**[E-S1] "AI made code free … distribution, trust, support, liability are ~80% of a software business"** — cross-ref [A-S2].
- *Stance:* **SUPPORTS** — the AI-era restatement of Lientz-Swanson: the dominant costs sit outside code construction, so collapsing construction reshapes a minority slice of TCO.

**[E-S2] DORA 2025 (cross-ref [A-C4]) + productivity paradox (cross-ref [A-C5])**
- *Stance:* **SUPPORTS** — empirical confirmation that speeding phase 3 leaves delivery flat when the dominant costs (integration, review, ops) are untouched — Amdahl's law over the lifecycle.

### Synthesis — cluster E

Where the classics do the heavy lifting and the AI-era sources merely confirm. Lientz-Swanson
([K6]) and Boehm ([K7]) fixed, decades ago, the two facts #8 rests on: maintenance dominates
TCO (the second loop), and value is made or lost early (the cost-of-change curve). AI's
collapse of phase 3 attacks a *minority* slice of that pie ([E-S1]) — which is exactly why
individual coding speed doesn't move delivery ([E-S2]): an Amdahl bound over the lifecycle. The
honest edge is Boehm-Basili's flattening under CI/CD ([K7]) — the curve is context-dependent, so
#8 must argue in relative deltas, not absolute 100x claims. This is the cluster where our
differentiator is weakest as *novelty* (the economics is old) and strongest as *synthesis*:
naming which lifecycle slice AI actually cheapens, and refusing the "AI made software cheap"
overclaim by pointing at the pie.

---

## Cross-cluster synthesis

Five clusters, one argument with a hub. **A** is the engine: AI collapsed the *accidental*
half of phase 3 (Brooks [K1]), unevenly and without reaching delivery. The rest are spokes:
- **B** (microservices): the collapse removes the *change-cost* justification for distribution; modularity (Baldwin-Clark [K3], Parnas [K4]) survives, distribution must re-earn its keep at runtime.
- **C** (re-verification): the collapse relocates the binding cost to *re-proving* (Parnas containment [K4], Dijkstra incompleteness [K5]); boundaries are now drawn to bound the re-verification surface.
- **D** (options): modularity and spare capacity were always real options (Baldwin-Clark [K3], Hohpe [D-S1]); AI changes which options are cheap to hold.
- **E** (lifecycle): the collapse reshapes a minority slice of TCO (Lientz-Swanson [K6], Boehm [K7]); delivery stays flat by Amdahl.

*With* the stream: the conclusions are broadly shared and the classics are firmly on our side.
*Against* the stream: we refuse both the slogan ("AI killed microservices") and the shrug
("it depends"), and — the real differentiator — we compute. The prior art itself confirms the
project boundary: the economics/optimization (B-choice, D-pricing, E-pie) is **3A8**; the
runtime feasibility that feeds it as a *constraint* is **twotakt**. The one place they touch —
[D-S2] real options over *behavioral* qualities like throughput — is exactly the
constraint <-> optimization seam.

## Leads to verify (carried forward — not yet admitted)

- Fortune-50 "AI teams shipped ~10x more security findings alongside ~4x velocity" (Sep 2025, secondary only) — would temper "cheap regeneration is clean" and *raise* the value of distribution's blast-radius isolation. Find the primary.
- A named source **defending microservices post-AI on distribution grounds** — cluster B's contradicting side lacks a principled pro-distribution AI-era voice (only [B-C3] Tilkov, pre-AI, and [B-C4] neutral).
- Stronger single primary for the "+91% review time" and "93%/10%" figures (currently multi-secondary).
- METR full paper (arXiv 2507.09089) beyond blog/abstract, for the task-mix caveats.
