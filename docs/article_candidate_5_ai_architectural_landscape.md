# Article candidate #5 — Microservices after the price drop: the architectural landscape repriced

> **Type: reasoning** — corpus: append/compact, not synced · born 2026-07-13

*Status: candidate. Series: **AI Influence on the Architectural Landscape** (episode S1
of 4). Target form: LinkedIn note (EN) → DOU longread (UA) per the series pipeline in
TODO. Origin: author's idea (2026-07-13, "ход 5" of the TCO conversation) — he was
heading to write this note when the series crystallized around it.*

---

## Thesis

Microservices are two decisions glued together: **modularity** (boundaries for
*change*: modify a little, per team, independently) and **distribution** (boundaries
for *runtime*: independent scaling, fault isolation, blast radius). The old landscape
glued them because cost-of-change dominated — for its sake we paid the distributed
tax (debugging across ten services, network latency, partial failures, eventual
consistency).

AI collapses the cost of writing and rewriting code — and thereby **removes the first
justification without touching the second**. "It will be convenient to change" is no
longer an argument for distribution. What remains is runtime — and runtime properties
are exactly what simulation computes (the twotakt bridge is built into the thesis).

Consequences to argue:

- **Modularity stays, distribution retreats.** The modular monolith becomes the
  default; distribute only for runtime reasons (scale, isolation, failure modes) —
  never for team-convenience-of-change reasons.
- **The AI's own boundary is the context window**: a codebase the model can hold is
  regenerable as a unit; one it cannot — is not. Punchline candidate: "the new module
  boundary is the context window."
- **What survives untouched** (keeps the piece honest, not hype): Conway's law (a
  hundred people cannot release one artifact), stack heterogeneity, independent
  release cadences.

The differentiator vs the existing "AI kills microservices" op-ed wave: the two-glued
-decisions decomposition, plus a computational companion — the TCO layer (S3/S4) can
*draw the boundary* ("monolith cheaper when change rate > X and scale < Y") instead
of opining.

## Supporting material

- F12 (construction cost collapsed; justification did not) — the economic engine of
  the whole argument.
- F20 (cheap construction makes relevance an experiment) — extended here from model
  variants to architecture economics.
- Candidate #6 is the hard half of this argument (re-verification surface); candidate
  #4 is its precondition (regeneration is only viable with automated verification).

## Related findings

F12, F20. Related candidates: #6 (S2, the verification currency), #4 (the trust
machinery), TCO layer items S3/S4 in TODO.
