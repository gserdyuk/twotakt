---
name: queueing-lazowska
description: >-
  Analytical performance modeling of computer systems using queueing network
  models — the Lazowska/QSP methodology. Use when the user wants to estimate
  throughput, utilization, response time, or bottleneck without running a
  simulation: capacity planning, "what if N users?", "which device saturates
  first?", "how many servers do I need?". Complements simpy-protocol:
  QSP gives fast closed-form answers; simpy-protocol explores stochastic
  behaviour and non-product-form mechanisms. Source: Lazowska, Zahorjan,
  Graham, Sevcik — "Quantitative System Performance" (1984),
  freely available at homes.cs.washington.edu/~lazowska/qsp/
---

# QSP — Analytical Performance Modeling (Lazowska)

This skill encodes the Lazowska queueing network methodology: operational
laws, asymptotic bound analysis (ABA), and mean value analysis (MVA).

## When to use this skill vs. simpy-protocol

| Question | Use |
|---|---|
| Which device is the bottleneck? | QSP (ABA, instant) |
| What throughput can I sustain at N users? | QSP (MVA, exact) |
| How does latency behave near saturation? | simpy-protocol |
| Does USL thrashing appear past saturation? | simpy-protocol |
| Circuit breaker / retry / admission control? | simpy-protocol |
| Validating a SimPy sweep against theory | **Both** — use QSP ceiling as reference line |

## Core concepts

**Service demand D_k** (seconds per system-level job at device k) is the
single most important parameter. Everything else follows from it.

    D_k = V_k × S_k        (visit ratio × mean service time per visit)
    D_k = U_k / X          (from monitoring: utilization / throughput)

**Saturation point N\*** — the number of users at which the bottleneck
device's utilization reaches 1 and throughput stops growing:

    N* = (D_sum + Z) / D_max
         D_sum = Σ D_k,  D_max = max(D_k),  Z = mean think time

## The protocol

### Step 1 — Identify devices and collect service demands

List every device that is a potential bottleneck (CPU, disk, network,
connection pool). Measure or estimate D_k for each. Read
`references/laws.md` — the Service Demand Law gives two ways to get D_k
from monitoring data.

**Measuring D_k from a real system:** use `modeling-jain/references/workload.md`.
The direct method: `D_k = U_k / X` — device utilization divided by system
throughput, both measured over the same window. Validate: if you have multiple
devices, `Σ_k (X · D_k)` should equal total CPU busy fraction. If it doesn't,
a device is missing from the model.

### Step 2 — Identify bottleneck (5 seconds)

    bottleneck = device with largest D_k

If the bottleneck changes under load (e.g. CPU at low N, DB pool at high N),
note both and the crossover N.

### Step 3 — Asymptotic Bound Analysis (ABA)

Before running MVA, compute the bounding curves: upper bound on throughput,
lower bound on response time. These take 30 seconds to compute by hand and
already answer most capacity planning questions. Read `references/aba.md`.
Use `templates/aba_calc.py`.

### Step 4 — Mean Value Analysis (MVA)

Run MVA if you need the exact curve, not just the bounds. MVA is exact
for product-form (BCMP) networks. Read `references/mva.md`. Use
`templates/mva_calc.py`.

### Step 5 — Interpret results

Plot throughput and response time vs. N (number of users). Look for:
- **Linear region** (N < N*): throughput ∝ N, response time ≈ D_sum
- **Knee** (N ≈ N*): throughput plateaus at 1/D_max, response time turns up
- **Saturation region** (N > N*): response time grows linearly (N·D_max - Z)

The knee is the operating point you want to provision for.

### Step 6 — Sensitivity

Re-run ABA/MVA with ±2× on the key assumption (usually D_max). If the
knee shifts by more than 20%, the conclusion is sensitive to that estimate
and should be flagged.

## Hybrid modeling (FESC)

When a multi-tier system has some tiers that are well-behaved (M/M/c,
product-form) and others that are complex (USL, burst, SLA timeouts):

1. Solve the well-behaved tier analytically with MVA → produce T(k) table.
2. In SimPy, replace that tier's `simpy.Resource` block with a lookup:
   `yield env.timeout(1.0 / T_fesc[k])` — no Resource, no SimPy queuing.
3. The complex tier runs as normal SimPy simulation.

Read `references/fesc.md` for the full algorithm and applicability rules.
Check `references/fesc.md` → "Applicability to our models" table before
deciding which tiers to simulate and which to replace with FESC.

## Relationship to simpy-protocol

Use QSP first (fast), then simpy-protocol (slow but richer):

1. QSP identifies the bottleneck and approximate knee → informs
   the sweep range and validates model choices made in Phase 3
   (choose model per entity) of simpy-protocol.
2. simpy-protocol validates behaviour: USL thrashing, burst spikes,
   SLA timeout effects that QSP cannot model (USL and product-form
   assumptions are incompatible).
3. QSP ceiling (`1/D_max`) becomes the reference line on the SimPy
   throughput plot — used in Phase 7 (V&V, curve shape validation)
   and Phase 8 (behavioral analysis) of simpy-protocol.

## Source of D_k

QSP requires service demand D_k for each device. The source depends
on the project stage — all of the following are valid:

| Source | When |
|---|---|
| Real system measurement | `modeling-jain`: D_k = U_k / X from monitoring |
| Design specification | ТЗ or architecture: "DB query ≤ 50ms", "CPU per request = 10ms" |
| Engineering estimate | System does not exist yet — estimate by analogy |
| Analytical derivation | From physics: bytes / bandwidth, disk seek + transfer formulas |
| Component benchmark | Synthetic benchmark of an isolated component |

Document the source for each D_k the same way as any other parameter
(see Phase 5 of simpy-protocol). Estimates should be flagged for
sensitivity analysis (Step 6).

## Extended integration with simpy-protocol (optional)

Beyond the basic "QSP first, then simulate" pattern, QSP can play
additional roles at Phase 3 (choose model per entity) of simpy-protocol:

| Role | What it provides |
|---|---|
| **Hybrid (FESC)** | Replace a well-behaved SimPy component with an analytical MVA solution — reduces simulation complexity. See `references/fesc.md`. |
| **Model validation** | Verify Phase 3 choices: if M/M/c was chosen, QSP ceiling must agree with simulation within ~5%. Divergence signals a wrong model in Phase 3. |
| **Prioritization** | Bottleneck device (largest D_k) needs the most faithful model; peripheral devices can be simplified. Guides where to invest modeling effort. |
| **V&V reference curve** | Build the expected analytical curve before running SimPy. Phase 7 (V&V) then compares against a specific curve, not just a qualitative shape. |

These are methodological options — use them when the project warrants
the extra rigour. A simple single-bottleneck model may not need all four.

## Assumptions and limitations

Product-form (BCMP theorem) requires:
- FCFS service at load-independent centers (exponential or BCMP-compatible distributions)
- No preemption, no processor sharing with more than one class (with exceptions)

When these fail, use simulation instead (or as a check).

Does NOT model: USL-style degradation, admission control with complex
policies, correlated arrivals, non-FIFO scheduling with priority classes
across devices, or transient behaviour.

## Reference files

- `references/laws.md` — five operational laws, formulas, variable definitions
- `references/aba.md` — asymptotic bound analysis, bottleneck identification
- `references/mva.md` — MVA algorithm (exact, single class)
- `references/fesc.md` — Flow-Equivalent Service Center: hybrid analytical+simulation

## Templates

- `templates/aba_calc.py` — ABA bounds computation and plot
- `templates/mva_calc.py` — exact MVA for single-class closed network
