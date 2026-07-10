# verification-validation — Rationale (why the technique is shaped this way)

This is the **rationale** companion to `SKILL.md` (its sibling in this folder).

- `SKILL.md` says **what to do** — the checks, the tiers, the battery.
- This document says **why** — which failure mode each element prevents.

It is **not** the protocol. If the two ever disagree about the steps, `SKILL.md`
is right and this file is stale — fix it.

---

## Why this is a separate skill

The gate belongs to the protocol; the technique belongs here. `simstudy-protocol`
Phase 7 keeps the gate (green + human sign-off before sweeps) and points at this
skill for the how. V&V techniques accumulate (verification levels, compositional
verification are expected next) — modularity says no skill grows unbounded. And
the separation is not only organisational: the checker living apart from the
builder is itself part of the independence argument below.

## Why it is executable, not prose

"Verify by reading" is how accidental semantics survive. `verify.py` runs a small
battery: Tier-1 conservation invariants (work is conserved; no congestion loss at
a healthy baseline) reused unchanged across projects — the fixed trust floor —
plus Tier-2 per-model checks (curve shape, metamorphic toggles: disable a
mechanism, assert the metric moves the right way).

## Why the generator never authors its own trust floor

There is no oracle for a fresh simulation — no one knows the "right" curve in
advance. Trust comes from consistency among *independent* expressions of intent:
the spec, the code, and conservation laws fixed by a human. If the generator
writes the invariants too, one blind spot signs off on itself.

## Why negative-test every check

A check that stays green on a deliberately broken model is worthless. This is
non-negotiable — an assertion you have not seen fail is not evidence. Experience
across the five-model build-out: every check's *first* version was wrong (did not
bite, or bit the healthy model).

## Why prefer an independent session

The generator that missed a bug also fails to check for it (correlated blind
spots). Running V&V in a separate session/agent makes the file boundary the
hand-off, so the checker isn't the author. This was tested for real: the
independent verifier of Model #5 (RadioMonitoring) caught a genuine modelling
bug the builder had missed.

## Why the verdict stops at correctness

Green certifies consistency (code ↔ spec ↔ invariants) — automatically, so the
machine replaces a human eyeballing a smoke test. Whether green is *sufficient
to proceed* is the caller's decision: sign-off is about consent and spend, not
about correctness, so it cannot be delegated to this skill. See
`harness/README.md` for what green does — and does not — mean.
