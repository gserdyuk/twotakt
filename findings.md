# twotakt — findings

> **Type: register** — corpus: append-only, compacted to vN · born 2026-07-10

The register of what the project *knows*: one F-numbered entry per claim. The long
form (the *why*) lives elsewhere — every entry points to it.

Rules:
- **Append-only.** A refinement or reversal is a new entry referencing the old one
  ("refines F7", "supersedes F3"), never an edit.
- **One screen max per entry.** If it doesn't fit, it is a document pretending to be
  an entry: give the reasoning its own file, register each distinct claim here.
- **Born here, same day.** A finding leaves the chat the session it appears in.
- **Compaction.** When the tail stops reading clean (or before an external showing):
  review, merge, resolve refinements, rewrite as vN; previous version goes to
  `docs/archive/findings-vN-1.md`. Mature clusters may *graduate* into a theory doc,
  an article, or — the highest form — a skill/harness rule that executes itself.
- `compiled:` marks findings already turned into practice (they can no longer be lost).

---

## Verification & trust (mostly 2026-06, harness build-out)

**F1 (2026-06-15). Spec = goal, not invariant.** The requirements verdict (SLA met /
not met) is the *output* of the study; asserting it asserts the thing under
investigation. A correct model showing "this architecture fails" is a correct result.
→ `docs/article_candidate_4_vv.md` §2. compiled: V&V skill (healthy-baseline rule).

**F2 (2026-06-15). Three layers of assertability.** Requirements — not assertable
(output); verification ("built right") — assertable via conservation; validation
("right model") — assertable via law-shape, only up to the emergence boundary (F5).
→ article #4 §3.

**F3 (2026-06-15). No-oracle trust = consistency among independent expressions of
intent.** With no golden reference, trust comes from cross-checking independent
statements of the same intent (human-fixed conservation, spec-driven law shape,
generator-authored bounds). The generator must never author its own trust floor —
correlated blind spots. → article #4 §4. compiled: harness Tier structure.

**F4 (2026-06-15). Generator-authored checks catch self-contradiction, not silent
agreement.** Tier 3 cannot certify correctness (code and check can be wrong together)
but reliably catches the generator disagreeing with itself — high-signal either way.
→ article #4 §4.

**F5 (2026-06-15). Law-shape assertability is inversely proportional to emergence.**
If the macro-pattern can be named before the run, it is assertable; if the run exists
to discover it, asserting it repeats F1's error. Conservation survives everywhere —
emergence does not violate continuity. → article #4 §5, Appendix A.

**F6 (2026-06-15). Tier-1 is one law in domain clothes.** Work conservation (queues)
= mass balance (agronomy) = stock-flow consistency (economics) = the continuity
equation. The domain-independent core of oracle-free acceptance testing.
→ article #4 §5.

**F7 (2026-06). Replication strips assumptions: the universal core shrinks, the
ledger grows, laws don't transfer.** Each new system class peels a hidden assumption
off a "universal" invariant (no-loss assumed queueing; completed≈offered assumed
short requests); the work-fate ledger converges to a small complete schema; Tier-2
laws never transfer between classes — the *metamorphic method* does.
→ article #4 §9b–9c.

**F8 (2026-06). Negative-test-first: every check's first version is wrong.** It
either doesn't bite or bites the healthy model. The negative test (deliberately break
→ must go red) is the real unit of verification work. → article #4 §9c.
compiled: V&V skill.

**F9 (2026-06). A mechanism check is valid only where the mechanism binds.**
Degradation at the peak, pool in overload, blocking at high offered load. Every
metamorphic relation carries a binding region; tested elsewhere it is vacuous or
wrong. → article #4 §9c. compiled: V&V skill.

**F10 (2026-05..06). Component correctness does not compose into system
correctness.** USLDBmodel: every component individually correct, system collapses at
~6 rps on pool=1 despite ~20 rps component ceilings. Component + edge checks
*localize* faults; only system-level checks *detect* the interaction class.
→ article #4 §4 (scope axis), examples/USLDBmodel README ## Lesson.

**F11 (2026-06). Composition value lives in metamorphic relations, not conservation
identities.** Edge/shared-resource conservation trends toward tautology (demand
summation); what bites is bottleneck-migration and interference relations. Two
distinct composition topologies: series (A→B: edge balance) vs fan-in (A→R←B:
superposition + interference). → article #4 §9b (PowerSearch outcome).

## Theory: the map and the doctrine (2026-07-08..09)

**F12 (2026-07-08). AI collapsed model construction cost; justification cost did not
move.** Everything downstream is one answer to this asymmetry. Not ours (Prediction
Machines 2018; Wei's Verifier's Law and its inverse; Karpathy's verification gap) —
our position: models of systems are the worst case, a task with *no oracle*.
→ `docs/verifiability.md` §1.

**F13 (2026-07-09). Simulation is a solver, not a model kind.** Zeigler's triad
(frame / model / simulator). Layer C (solution verification) belongs to the solver,
not the model — separating "the model is wrong" from "we solved it wrong", two
failures AI produces with equal fluency. → verifiability.md §2.

**F14 (2026-07-09). The gates are standard V&V, deliberately.** A = validation
(human, invariant across model kinds — no oracle exists), B = verification (machine,
per model kind), C = solution verification (machine, per solver). A concern (42010)
selects a *region* of the model-kind map, not a point; the remaining choice is human.
→ verifiability.md §2. compiled: the audit gate + verify.py were already its instance.

**F15 (2026-07-09). The residue after all machine gates is the well-formed lie.**
A wrong mechanism satisfying every invariant (FIFO modeled where reality has
priorities: conservation balances, Little holds, M/M/1 limit matches — p99 lies).
Defines exactly what the human gate must examine: the mechanism, not correctness.
→ verifiability.md §3.

**F16 (2026-07-09). Layer B composes; layer A does not.** Event-level coupling is
exact (DEVS closure under coupling) — flow-level analytic composition breaks (Burke
only for M/M/1) but simulation propagates the law automatically. What still breaks:
frames at joints, hidden couplings, amplification near saturation. Sound composition
= assume-guarantee discharge at every joint; interfaces must carry enough of the law
(Kingman: variability, not just rate — QNA propagates (lambda, Ca^2)).
→ verifiability.md §4.

**F17 (2026-07-09). Fix pattern: promote the hidden coupling to an explicit
component.** The electronics move (draw the parasitic capacitor, add the thermal
node) = add the shared CPU as an explicit Resource. The coupling returns to the
ports; port-completeness becomes true again. → verifiability.md §4.

**F18 (2026-07-09). Isolation buys compositionality at the price of utilization.**
Sharing buys utilization at the price of modeling complexity — queueing theory is the
tax on statistical multiplexing. Design for modelability has two halves: structural
(composability) and observational (calibratability); a system can have either without
the other. Closest prior program: SEI's Predictability by Construction / PACC.
→ verifiability.md §5.

**F19 (2026-07-09). "Hard to model" is a diagnosis of the architecture, not of the
modeler.** Same inversion software made with testability. Every modeling stumble
(hidden coupling, orphan parameter, uncheckable frame) is an architectural finding of
the same rank as a bottleneck — collectable for free ("modelability findings" section
candidate). → verifiability.md §5.

**F20 (2026-07-09). Model size is now bounded by the justification budget, not
construction labor.** Complication without calibration is degradation dressed as
progress (invented parameters = false precision). Predicted sign flip: AI-era models
err baroque, not simple. The sensitivity x measurability matrix sorts candidate
couplings; cheap construction makes *relevance an experiment* (build both, sweep,
compare). → verifiability.md §8.

**F21 (2026-07-09). A surprise is worth exactly what the gates under it are worth.**
Emergent findings (retry storms, metastability) are the purpose of simulating, but
have no verifier of their own by definition — their credibility is entirely inherited
from the boring gates beneath. → verifiability.md §8; boundary formalized in
article #4 §5 (emergence boundary).

**F22 (2026-07-09). The applicability domain is earned, not decreed.** It is the
union of regimes actually checked against oracles. AI's legitimate role is registrar
and patrol (frame monitors at runtime), not authority. Verdicts must be graded,
localized, and *directional* ("p99 optimistic"), or alarm fatigue turns the patrol
into ritual. Scar-tissue precedent: NASA-STD-7009 after Columbia/Crater.
→ verifiability.md §7.

**F23 (2026-07-09). Verifiability by construction: a model must carry its own
verifiers.** Artifact = Requirements + model spec + executable model + certificate
(frames, oracles, gates passed) + per-run verdict; a model without its certificate is
unfinished. Verifiability ≠ validity: layer A concentrates onto one question ("is
this the mechanism?"), it never disappears. → verifiability.md §6.

## Process & method (2026-06..07)

**F24 (2026-07-06). Spec-first holds for the model, not for the method.** A
per-project artifact a human re-approves each run can be the source of truth; a prose
methodology nobody re-approves rots while its "compilation" (the skill) evolves.
methodology.md died of this; SKILL.md is the protocol's single source.
→ dev-log 2026-07-06..08. compiled: the skill.

**F25 (2026-07-10). Current-state descriptions lose the race — archive, don't
refresh.** Third occurrence of the same rot (methodology.md, WORKFLOW.md,
architecture docs). Generalized 2026-07-10 into the corpus/surface split: the
research corpus accumulates (dated, contradictions are history), only the small
product surface is synchronized. → dev-log 2026-07-10; CLAUDE.md Key constraints.

**F26 (2026-07-09). The author's skepticism is gate A at the discourse level.**
During theory-building, every aesthetically pleasing closure the AI produced (skills
mapped onto the taxonomy, concern→cell as a function, simulation as a model kind) was
retracted under the author's pushback within a turn. The AI could not distinguish its
substantive constructions from symmetry-driven filler *from the inside* — the most
direct confirmation of F12's consequence so far, obtained about theorizing itself.
→ dev-log 2026-07-09 (verifiability entry).

## Architecture economics (2026-07-13, series "AI Influence on the Architectural Landscape")

**F27 (2026-07-13). Microservices are two decisions glued: modularity (change
boundaries) + distribution (runtime boundaries). AI unglues them.** The collapse of
code-construction cost removes the cheap-localized-change justification and leaves
only runtime reasons (scale, isolation, failure modes) — which are exactly what
simulation computes. Modular monolith becomes the default; distribute only for
runtime. → `docs/article_candidate_5_ai_architectural_landscape.md`.

**F28 (2026-07-13). The unit of architecture is the unit of re-verification.**
Regeneration is cheap; re-proving is not (F12 applied to the loop). A monolith's
re-verification surface is "everything"; contracts bound it per service. Boundaries
migrate from cost-of-rewriting to cost-of-re-proving; automated verification (the
candidate-#4 machinery, F23) is the *precondition* of any "just regenerate it"
strategy. → `docs/article_candidate_6_reverification_surface.md`.

**F29 (2026-07-14). AI compresses lifecycle phases unevenly; the residue is Amdahl's
law over the lifecycle.** Codegen ×5, test *execution* ×5, analysis ×1, test *oracle*
≤×1.5 → the primary-development total shrinks to ~30% of its old self and testing
becomes its largest line (~43%); analysis grows 10%→~30% by denominator collapse
alone. The unaccelerated human fraction (analysis + oracle) bounds total speedup from
above, regardless of further codegen progress.
→ `docs/article_candidate_8_lifecycle_economics.md`.

**F30 (2026-07-14). AI gain is inversely proportional to the context already in the
maintainer's head.** Comprehension (~50% of modification effort, the Lientz–Swanson-
era constant) is AI's strongest mode → in the maintenance loop development falls
*more* than in greenfield; reconciles METR's slowdown-on-own-repo with the observed
multi-x speedup on foreign code. → candidate #8.

**F31 (2026-07-14). Architecture enters the financial model as a multiplier on the
AI coefficients, not as a cost line.** Two mechanisms: context locality (does the
change-relevant slice fit the window) and blast radius. One-context rule replaces the
two-pizza rule. Refines F27: modularity ≠ microservices, monolith ≠ spaghetti —
partitioning suffices, *provided* boundaries are machine-enforced (AI erodes
convention-held boundaries at generation speed). → candidate #8, candidate #5.

**F32 (2026-07-14). Microservices glued four boundaries: comprehension, verification,
deployment, team.** AI economics is sensitive only to the first two, and both are
achievable inside a monolith (partitioning + contracts/specs); deployment bounds only
the operational radius (process, memory, scaling) — the honest residual case for
services. Refines F27/F28. → candidate #8.

**F33 (2026-07-14). The spec is a context-compression format (~100:1), invariant to
window size.** A neighbor enters the context as its MODEL.md, not its implementation;
window growth and sparse attention shift the constant, not the gradient (sparsity
prunes exactly the long-range pairs spaghetti needs). The spec also makes the
re-verification radius *definable* — without it the rational radius is "everything".
Ties audit-first to both economies. Refines F28. → candidate #8.
