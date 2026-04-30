# {ModelName} — what this model represents

> Template. Replace `{...}` placeholders during the audit (Phase 1).
> The intent of this document is to capture *modelling intent* in
> human prose, so a reader does not have to reconstruct it from the
> code. If the description below and the code disagree, the
> description is the specification and the code is the bug.

## What real system is being modelled

{One paragraph describing the actual system in real-world terms — not
SimPy primitives, not the math. From audit Q1.}

## What is scarce / shared in this system

{The list of contended resources from audit Q2, with capacities. Each
item here corresponds to one `simpy.Resource` in `server_sim.py`.}

## What a request looks like

{The lifecycle of a single request from audit Q3. The phases, their
order, what each phase does, average durations. Include the
distribution shape (exponential by default) and any branching.}

## Workload

{From audit Q4: arrival process (Poisson by default), arrival rate
range, sweep range, simulation duration.}

## How the system degrades under load

{The theoretical framework chosen in Phase 2 and why. Cite the
relevant entry from references/theory-glossary.md. State the formula
and the meaning of each coefficient. List the mechanisms from Phase 3
that this law is meant to encode.}

## Backpressure and safety

{From audit Q6. SLA timeout if any, in-flight cap if any, retry
policy if any. State default values.}

## Lifecycle of a single request

{Numbered step-by-step description of what happens to a request from
arrival to completion or failure. This is the prose version of
`_serve` and `handle_request` together.}

## What the operator can dial

{The full list of `Config` parameters with their meaning, in plain
language. One-line each. Group by topic (workload / work mix /
degradation / backpressure).}

## What this model deliberately does not include

{From audit Q7. The omissions are as important as the inclusions —
they tell the reader the limits of what conclusions this model
supports. Be specific.}

## What success looks like when running this model

{From audit Q8. The smoke-test outcome and the validation-sweep
outcome. The shape of the curve that proves the model is doing what
it was built to do. This becomes the Phase 7 acceptance test.}
