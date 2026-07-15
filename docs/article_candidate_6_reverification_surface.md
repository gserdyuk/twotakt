# Article candidate #6 — The new currency of architecture: the re-verification surface

> **Type: reasoning** — corpus: append/compact, not synced · born 2026-07-13

*Status: candidate. Series: **AI Influence on the Architectural Landscape** (episode S2
of 4). Target form: LinkedIn note (EN) → DOU longread (UA) per the series pipeline in
TODO. Origin: sharpening of candidate #5 during the same conversation — the author's
"offspring" question (what happens to testing cost?) turned out to be the center, not
a side effect.*

---

## Thesis

Regenerating a monolith is cheap; **re-verifying it is not** (F12 applied to the
regeneration loop). The blast radius of a change in a monolith is "everything" — so
the re-verification surface is "everything" too. Microservices, having lost their old
justification (cheap localized change — see #5), acquire a new one nobody designed
them for: **they bound the re-verification surface** (contract at the boundary →
re-verify one service plus its contract tests).

So the currency changed: boundaries used to be drawn by the cost of *rewriting*;
now they are drawn by the cost of *re-proving*. Slogan form: **the unit of
architecture is the unit of re-verification.**

Corollaries:

- "Just regenerate the whole thing" is a viable strategy **only** with automated
  verification machinery — invariant harnesses, models that carry their own verifiers
  (F23). Cheap regeneration without cheap re-verification is just fast production of
  untested code.
- Candidate #4 (invariant/intent verification) is therefore not a neighboring topic
  but the **precondition** of the landscape shift in #5 — the series makes this
  dependency explicit.
- Design-for-verifiability becomes an architectural selection criterion on par with
  scalability (continues F19's "hard to model is a diagnosis of the architecture").

## Supporting material

- F12 (the asymmetry), F23 (verifiability by construction: artifact carries its
  verifiers), F19 (modelability as architectural diagnosis).
- The repo's own harness (`harness/`, per-example `verify.py`) is the working exhibit:
  what "cheap re-verification" concretely looks like.

## Related findings

F12, F19, F23. Related candidates: #5 (S1 — the landscape claim this hardens),
#4 (the trust machinery this depends on).
