# simstudy-protocol — Rationale (why the protocol is shaped this way)

This is the **rationale** companion to `SKILL.md` (its sibling in this folder).

- `SKILL.md` says **what to do** — the phases, the gates, the order.
- This document says **why** — what each phase is *for*, which failure mode it
  prevents, and the judgement calls behind it.

It is **not** the protocol. If the two ever disagree about the steps, `SKILL.md`
is right and this file is stale — fix it. Read `SKILL.md` for the mechanics; read
this to understand *why the mechanics are worth following*.

> Comments left as `> NOTE:` are open — reasons we have not written down yet, or
> where the author's own reason belongs. Fill them in while they are fresh.

---

## The core bet: specification is primary

**Why it exists.** The natural failure mode of these projects is: write code first,
get a curve, ship it. At that point the model encodes whatever degradation the
*implementation accidentally produced* — a wrong default, a mis-sized pool, an
off-by-one in the service draw — not what the modeller intended. The curve looks
convincing and the conclusion is wrong. This is the worst kind of error: **invisible**.
The simulation "works", the plots are clean, the verdict is false.

So the bet is: **`MODEL.md` (the model, the spec) is the source of truth; the
`executable_model` (the code) is its implementation.** When they disagree, the code
is the bug. Every phase either writes the spec, writes code in service of the spec,
or checks that the code still honours it.

---

## Inputs: why two documents, Requirements + Architecture

**Why two, not one.** They answer different questions and have different authors:

- **Architecture** (how the system is built) → produces **the model**. It is the
  *what* — structural decisions already made by an architect.
- **Requirements** (load, SLA, questions) → produces **the testbench and the
  acceptance criteria**. It is the *why* — motivation and success criteria.

This is the same split as hardware verification: architecture is the design,
requirements are the testbench. Keeping them separate stops the two from
contaminating each other — you cannot quietly relax an SLA to make a model pass, or
quietly add a component to hit a target.

**Why the skill refuses to derive architecture from requirements.** That step is
non-trivial *design* work — the architect's job. If the skill did it, it would be
inventing structure and then grading its own invention. So: no architecture → stop,
engage an architect. Incomplete architecture → the audit surfaces the gaps, filled
jointly, not unilaterally.

---

## Phase 1 — Architecture audit (blocking)

**What it prevents.** Writing code before understanding the system. The audit is a
structured interrogation of the architecture (by a fixed checklist) whose *output*
is the draft `MODEL.md`. It is not a formality — it is what forces the reasons for a
model's shape to be *stated* rather than smuggled in as code.

**Why it is a hard gate.** If code can be written before the spec is approved,
`MODEL.md` becomes a description written *after* the fact — documentation, not a
specification. Then "the code is the bug" has nothing to compare against. The gate is
the whole value; skipping it defeats the point.

**Why a checklist, not free conversation.** Left to improvise, the AI would generate a
plausible spec from what is *obvious* in the doc and sail past the hidden assumptions
(which pool saturates first? what happens when the queue is full? are there timeouts?).
The checklist walks the places bugs hide.

> Evidence: the Little's-Law pool-ceiling rule was born here — an Elasticsearch pool
> of 50 would have saturated before the workers at Year-5 load. Nothing in the
> architecture doc said so; it surfaced only because the checklist made us compute the
> ceiling of every pool.

---

## Phase 2 — Structural decomposition

**Why map before you model.** Decomposition is pure observation: entities (what
processes/holds/routes requests), signal flow (how requests move), control flow
(admission, timeouts, retries, backpressure). No modelling choices yet — that
separation keeps you from picking a fancy model before you even know the parts.

**Why control flow gets its own line.** It is usually invisible in architecture docs
and decisive under overload. "What happens when entity X is saturated?" is the
question that most often has no written answer — so we ask it explicitly.

---

## Phase 3 — Choose model per entity

**Why per-entity, with justification.** Each entity maps to a SimPy primitive and a
mathematical model (M/M/c, M/M/1, USL, bounded queue…). The rule: justify what a model
captures that a simpler one does not — if the answer is "nothing", pick the simpler
one. This is the razor that keeps models honest and small.

**Why the CV check sits here.** `expovariate` is the lazy default, and it is wrong when
service-time variability is high: CV > 1.5 → exponential underestimates p99 by 2–10×.
Checking CV = σ/μ *before* accepting the default is cheap insurance against a tail that
lies. If no samples exist, note the assumption and sweep it as a stress case.

---

## Phase 4 — Build the executable_model

**Why resist features.** The single instruction is: implement only what Phases 1–3
demanded — no priorities, no preemption, no retries, no graceful-degradation logic
unless the audit's control flow listed them. Every un-audited feature is an assumption
you did not declare and cannot see in the report.

**Why `simpy.Resource` count = Phase 2 answer count.** Adding a phantom pool, or
collapsing two distinct scarce resources into one "for convenience", silently changes
where the system binds. Resources are determined by the decomposition, not by the
template.

---

## Phase 5 — Document parameter sources

**Why every number needs a source.** Three valid ones: **measurement** (from real
monitoring), **design decision** (architect/SLA), **assumption** (a guess). A parameter
with no recorded source is a *hidden assumption* — it silently shapes the result and is
invisible in the report. Assumptions get flagged for the sensitivity sweep, so the ones
that matter get stress-tested rather than trusted.

---

## Phase 6 — Build the test bench

**Why the bench is separate from the model.** The bench (arrival process, sweep range,
SLA thresholds) comes from the **requirements**, not the architecture. It *drives* the
model; it does not *change* it. Mixing them lets the experiment quietly edit the thing
it is supposed to be testing. If defining the bench reveals a model gap ("what happens
when the queue is full?"), that goes back to Phase 2/3 — you do not patch it in the bench.

---

## Phase 7 — Verification & Validation

**Two questions, one gate.** Verification: "are we building the model right?" (does the
code implement `MODEL.md`?). Validation: "are we building the right model?" (does it
show the behaviour the chosen law predicts?).

The *technique* — why executable not prose, why negative-test, why an independent
session — moved with the technique itself to
`skills/verification-validation/RATIONALE.md` (extracted 2026-07-10). What stays here
is the gate, because the gate is the protocol's:

**Why two gates here, not one.** Green certifies *correctness* automatically ("ships only
green") — the machine replaces a human eyeballing a smoke test. Then a **human sign-off**
before sweeps: green means it is *safe* to proceed; the human authorizes the *spend*
(sweeps can be expensive). Machine answers "is it right", human answers "do we spend".

> NOTE: the trust chain is the heart of the pitch — you verify the *model* (the spec),
> the machine verifies the *executable_model* honours it. Two verifications, two verifiers.

---

## Phase 8 — Behavioral analysis

**Why the question drives the plots, not a fixed rule.** The goal is to *understand
behaviour*, not to produce charts. Number of panels follows the question from the Requirements:
where is the knee? which entity saturates first? does it meet the SLA?

**Why the three-panel minimum when there is a failure mode.** A throughput chart alone
hides how the system fails. Throughput, success rate and latency are only legible
*together* — see the metric rule below.

---

## Phase 9 — Iterate

**Why a mini-audit before any change.** Before touching `Config`, `Server`, or `_serve`:
which entities, resources, signal-flow phases does this change touch? The audit scope is
proportional — a parameter tweak is light, a new entity is a full Phase 2/3 pass. This
keeps iteration from quietly re-introducing un-audited structure.

**Why `MODEL.md` sync in the same step.** The "spec is primary" principle collapses the
moment the spec drifts from the code. Sync on every intent change, not "later".

**Why sweeps need CI, not 3 seeds.** `mean ± std` over 3 seeds is wrong three ways
(wrong distribution, no warm-up removal, wrong denominator). Report `ȳ ± t·s/√r` over
r ≥ 10 (≥ 20 for p95). A result with a ±30% half-width is not a result.

---

## Phase 10 — Report (optional)

**Why optional.** Sometimes plots and console output are enough; sometimes a stand-alone
document is the actual deliverable. Ask, don't assume.

**Why it must stand alone.** A reader who has not seen the code or the audit must be able
to understand the conclusions *and their limits* — every number with its source, every
verdict against a requirement, and which assumptions, if wrong by 2×, flip a verdict.

---

## The metric rule that cuts across everything

**Latency-of-successful-requests is not safe beyond saturation.** Past the knee, the
requests that *succeed* are a biased sample — the ones that happened to hit a lull while
their neighbours timed out. Trust that number and you will conclude an overloaded system
is healthy. Always track **effective latency** (timeouts counted as SLA seconds) and
**success rate** alongside it. This one survivorship-bias trap motivates the three-panel
plot, the effective-latency metric, and half of Phase 7.

---

## The anti-patterns, and the phase that guards each

| Anti-pattern | Guarded by |
|---|---|
| Code before the audit is done | Phase 1 gate |
| Features the audit did not list | Phase 4 |
| Trusting latency-of-successes under overload | Phase 7 + the metric rule |
| Phantom / merged `simpy.Resource` objects | Phase 2 → 4 |
| Hard-coded numbers in function bodies | Phase 5 (`Config`) |
| Single-curve plots when there is a failure mode | Phase 8 |
| `MODEL.md` drifting from the code | Phase 9 sync |
