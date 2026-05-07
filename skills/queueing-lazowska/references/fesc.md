# Flow-Equivalent Service Center (FESC)

Source: Lazowska et al., "Quantitative System Performance", Chapter 8.
Also known as: Norton's theorem for queueing networks, Chandy–Herzog–Woo method.

---

## Core idea

A complex subnetwork can be replaced by a single **load-dependent server**
whose service rate at concurrency level k equals the subnetwork's throughput
at that level:

    μ(k) = T(k)     k = 1, 2, …, N

From outside, this single server is indistinguishable from the original
subnetwork. The subnetwork becomes a black box — only its throughput
function T(k) matters to the rest of the system.

Analogy: Norton's theorem in electrical circuits — a complex two-terminal
network is equivalent to a current source + impedance.

---

## Algorithm (3 steps)

### Step 1 — Solve the subnetwork in isolation

Isolate the subnetwork. Treat it as a closed network with k customers,
no think time (Z = 0). Run MVA for k = 0, 1, 2, …, N_max.

    T(0) = 0
    T(k) = MVA throughput of subnetwork with k jobs,  k = 1…N_max

Result: a table or function T(k).

### Step 2 — Construct the FESC

Replace the entire subnetwork with one load-dependent server:
- When k jobs are at this server, its service rate is μ(k) = T(k).
- Equivalently: mean service time when k jobs present = 1 / T(k).

If the subnetwork has a maximum concurrency limit M_max (e.g. a thread pool):

    μ(k) = T(k)          for k ≤ M_max
    μ(k) = T(M_max)      for k > M_max    (saturated — throughput plateaus)

### Step 3 — Solve the higher-level model

Replace the subnetwork with the FESC. Solve the resulting (simpler) system
using load-dependent MVA or discrete-event simulation.

---

## Accuracy

- **Exact** when the subnetwork is product-form (M/M/c, BCMP-compatible,
  no USL degradation, no complex admission control).
- **Approximate but good** for non-product-form subnetworks. Experience
  shows errors typically under 5% for utilizations below 0.9.
- **Breaks down** at the boundary if the subnetwork has strong correlations
  (e.g. burst arrivals, lock convoys that depend on external state).

Hierarchical analysis typically gives an order-of-magnitude reduction in
computation cost compared to full simulation of the combined system.

---

## Hybrid simulation pattern

The most practical application: combine analytical lower level with
simulation upper level.

**Lower level (analytical):** solve subnetwork with MVA → produce T(k) table.

**Upper level (SimPy simulation):** instead of simulating the subnetwork's
internals, the simulation looks up T(k) and uses it as a service rate:

```python
# Instead of: yield env.timeout(random.expovariate(1.0 / S_k))
# Use:
k = count_jobs_in_subnetwork()
yield env.timeout(random.expovariate(T_fesc[k]))
```

The SimPy process for the complex upper tier (USL degradation, burst,
SLA timeouts) runs as normal. The simple lower tier (well-behaved M/M/c
pool) is replaced by the T(k) lookup — no simpy.Resource, no queuing
in SimPy for that tier.

**When to iterate:** if the two levels interact strongly (load at the lower
level depends on the upper level's throughput), run both, extract the
steady-state load, re-solve the lower level with that load, and repeat
until T(k) stabilises. Usually converges in 2–3 iterations.

---

## Applicability to our models

| Component | Fits FESC? | Reason |
|---|---|---|
| ES indexing pool (M/M/c, I/O-bound) | ✅ Yes | Product-form, no USL |
| ES query pool (M/M/c, I/O-bound) | ✅ Yes | Product-form, no USL |
| Kafka consumer pool (M/M/c) | ✅ Yes | Product-form |
| Processing workers (I/O-bound, no burst) | ✅ Yes | Product-form |
| Processing workers (burst + SLA timeout) | ❌ No | Burst violates BCMP |
| Workers with USL degradation (alpha>0) | ❌ No | Non-product-form |

**Practical split for PowerSearch:**
- ES pools → FESC (solve analytically with MVA, produce T(k))
- Worker tier with burst → SimPy simulation, calls T_es(k) as lookup

---

## Integration with simpy-protocol skill

When extending a SimPy model with a new tier that is well-behaved (M/M/c):

1. Run `mva_calc.py` on the new tier alone → get T(k) table.
2. In `server_sim.py`: replace the `simpy.Resource` + `yield timeout` block
   for that tier with a single `yield env.timeout(1.0 / T_fesc[k])`.
3. The FESC tier no longer appears as a `simpy.Resource` — it is invisible
   to SimPy's scheduler, which reduces event count and speeds up the simulation.
4. Update MODEL.md: note which tiers are simulated and which are FESC.
5. Validate: compare full simulation (both tiers as Resources) against
   hybrid (one tier as FESC) — they should agree within ~5% below saturation.

---

## Reference

- Lazowska et al., QSP Chapter 8 (full text: homes.cs.washington.edu/~lazowska/qsp/)
- Chandy, Herzog, Woo (1975) — original paper introducing the method
- arxiv 2401.09292 — "Hierarchical Analyses Applied to Computer System
  Performance: Review and Call for Further Studies" — modern survey with
  hybrid simulation example (Section 5, Example 3)
