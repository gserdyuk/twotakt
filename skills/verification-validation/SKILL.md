---
name: verification-validation
description: >-
  Verification & Validation (V&V) protocol for simulation models — the
  executable trust check between building an executable_model and spending
  on sweeps. Verification asks "are we building the model right" (does the
  code implement MODEL.md); validation asks "are we building the right
  model" (does it exhibit the law the spec chose). Use whenever an
  executable_model must be checked against its MODEL.md: writing or
  reviewing a verify.py, running the validation harness, Tier-1
  conservation invariants, Tier-2 law-shape checks and metamorphic
  toggles, negative-testing checks, or answering "can this generated code
  be trusted". Invoked by simstudy-protocol at Phase 7; also standalone
  for re-verifying an existing example after a change. Triggers: verify,
  validation, V&V, verify.py, harness, smoke test, invariant, metamorphic
  test, negative test, верификация, валидация, проверка модели.
---

# Verification & Validation of simulation models

*Ref: Sargent, R.G. "Verification and Validation of Simulation Models",
Journal of Simulation, 2013.*

LLM-generated simulation code has no oracle: no one knows the "right"
curve in advance — that is why the simulation is being run. Trust
therefore comes from checking mutual consistency among independent
expressions of intent: the spec (`MODEL.md`), the code
(`executable_model`), and fixed conservation laws no generator may
touch. This skill encodes that check as an executable protocol.

**This skill is the technique. The calling protocol owns the gate.**
When invoked from `simstudy-protocol` (Phase 7), the pass/fail verdict
feeds that protocol's gate (green + human sign-off before sweeps).
Standalone, the verdict stands alone.

## When to invoke this skill

- From `simstudy-protocol` Phase 7 — the primary caller.
- Standalone: the user asks to verify an existing `executable_model`
  against its `MODEL.md`, to re-verify after a change, or asks whether
  generated simulation code can be trusted.

## Input signature

- **`MODEL.md`** — the approved spec: entities, signal flow, the law
  chosen per entity, parameter sources.
- **`executable_model`** — the code under test (plus its bench if the
  validation run needs a load range).

**Output:** a green `verify.py` — an executable, negative-tested check
battery. Not prose, not a hand-eyeballed smoke test.

**Independence:** prefer running V&V in a *separate* session/agent from
the one that built the code. Correlated blind spots are the failure
mode: a generator that missed a bug also fails to check for it. The
file boundary (`MODEL.md` + code in, `verify.py` verdict out) is the
hand-off. This skill living apart from the build protocol is itself
part of that separation.

## The two questions

**Verification — "are we building the model right?"** Does the code
correctly implement `MODEL.md`? Run once with default parameters.
Expected outcome: healthy baseline — throughput equal to arrival rate,
latency p50 close to the sum of phase means, no drops, success rate
100%. If the baseline is already pathological, the defaults are wrong
(not the model) — adjust arrival rate until a healthy point exists.
The defaults should demonstrate the model works, not stress-test it.

**Validation — "are we building the right model?"** Does the simulation
exhibit the behavior predicted by the law chosen in the spec? Run over
a load range and inspect the curve shape:

- USL: three regimes — linear scaling → knee → declining throughput
- M/M/1: hyperbolic latency rise toward saturation
- M/M/c: throughput plateau within ~5% of the analytical ceiling
  `capacity / service_time_mean`

If the curve does not match: debug the model — a degradation
coefficient is zero, a Resource has wrong capacity, or the
service-time draw is wrong.

## The executable form: verify.py on the shared harness

Write `verify.py` using the shared harness (repo-root `harness/`, see
`harness/README.md`; skeleton at `templates/verify.py`). It adapts the
model's output into the `RunSummary` ledger and runs a small battery:

- **Verification → Tier-1 conservation** — universal invariants reused
  from `harness/invariants.py` (work is conserved; no congestion loss
  at a healthy baseline; non-negative ledger). Do not rewrite these per
  project — they are the fixed, independent trust floor. The generator
  of the model must never author its own trust floor.
- **Validation → Tier-2, per model** — the curve shape for the chosen
  law, and **metamorphic toggles**: disable a mechanism and assert the
  metric moves the right way (e.g. degradation off → peak rises; shrink
  a pool → throughput drops where it binds). Use the *direction* from
  `MODEL.md`, not magic-number thresholds, and take each toggle at the
  operating point where the mechanism **binds**.
- **Negative-test every check** — confirm it goes red on a deliberately
  broken model. A check that stays green on a broken model is
  worthless; this is non-negotiable. Experience says every check's
  *first* version is wrong (does not bite, or bites the healthy model).
- **Proportionality razor** — keep it small: system-level Tier-1 by
  default; add a Tier-2 check only against a named risk.

## Metric lens

Apply `references/metric-checklist.md` as a mandatory lens on both
checks. Critical rule: latency-of-successful-requests is not safe
beyond saturation — surviving requests are a biased sample. Always
track **effective latency** (timeouts counted as SLA seconds) and
**success rate** alongside latency. If the user has not asked for
these, add them and explain why.

## What the verdict means

Green certifies *correctness* automatically — the code is consistent
with the spec and with the fixed invariants. Green does **not** certify
that the model reflects reality, that the parameters are right, or
that results beyond the validated region can be trusted — see
`harness/README.md` for the full list of what green does and does not
mean. Read it before trusting a run. Whether green is *sufficient to
proceed* (sign-off, spend authorization) is the calling protocol's
decision, not this skill's.

## Reference files

- `references/metric-checklist.md` — the metric lens: survivorship
  bias, effective latency, success rate, pool ceilings.

## Templates

- `templates/verify.py` — per-example V&V skeleton; the executable
  form of this protocol.

## Validation harness (shared, repo root)

The fixed machinery lives in the repo-root `harness/` package:

- `harness/run_summary.py` — the `RunSummary` ledger (the contract each
  model adapts into).
- `harness/invariants.py` — Tier-1 universal conservation invariants
  (do not edit per project).
- `harness/runner.py` — runs one example's checks and reports
  pass/fail.
- `harness/README.md` — **what green does and does NOT mean**.

Distinct from the *sweep* harness (`sweep.py` / `sweep_2d.py`), which
explores behaviour; this one certifies consistency.

## Maintaining this skill

Same convention as `simstudy-protocol`: during a project, note gaps in
memory as pending skill updates; at project end, review with the user
and record agreed changes in this skill's `CHANGELOG.md` with the
source project. V&V techniques are expected to accumulate here
(verification levels, compositional verification) — that growth is why
this skill is separate.
