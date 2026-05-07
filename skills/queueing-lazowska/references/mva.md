# Mean Value Analysis (MVA)

Source: Lazowska et al., "Quantitative System Performance", Chapter 6.
Algorithm: Reiser & Lavenberg (1980).

MVA computes the **exact** throughput, response time, and queue lengths
for a closed, single-class, product-form queueing network. It iterates
from an empty system up to N users, using the arrival theorem at each step.

---

## The Arrival Theorem

A customer arriving at a device in a closed network with N customers
observes the system as if it were in steady state with N−1 customers.
This is the key insight that makes MVA tractable: R_k(N) depends on
Q_k(N−1), which is already known from the previous iteration.

---

## Algorithm (exact, single class)

**Inputs:**
- D_k — service demand at each device k  (k = 1 … K)
- Z — mean think time
- N — population size (or range 1…N_max)

**Initialization:**
    Q_k(0) = 0   for all k     # empty system: no queues

**For n = 1, 2, …, N:**

    # Step 1: Residence time (arrival theorem)
    R_k(n) = D_k × (1 + Q_k(n−1))   for each k

    # Step 2: System throughput (Little's Law at system level)
    X(n) = n / (Z + Σ_k R_k(n))

    # Step 3: Queue length (Little's Law at device level)
    Q_k(n) = X(n) × R_k(n)   for each k

**Outputs at population n:**
- X(n) — system throughput
- R(n) = Σ_k R_k(n) — system response time
- U_k(n) = X(n) × D_k — device utilization
- Q_k(n) — mean queue length at device k

---

## Worked example (same system as aba.md)

Devices: CPU (D=0.05), Disk (D=0.15), Net (D=0.02). Z = 5.0 s.

**n = 1:**
    R_CPU(1) = 0.05 × (1 + 0) = 0.050
    R_Disk(1) = 0.15 × (1 + 0) = 0.150
    R_Net(1)  = 0.02 × (1 + 0) = 0.020
    X(1)      = 1 / (5.0 + 0.22) = 0.190 jobs/s
    Q_CPU(1)  = 0.190 × 0.050 = 0.0095
    Q_Disk(1) = 0.190 × 0.150 = 0.0285
    Q_Net(1)  = 0.190 × 0.020 = 0.0038

**n = 35 (near N*):**
    Disk queue grows large; R_Disk >> D_Disk.
    X(35) ≈ 6.5 jobs/s  (approaching 1/D_max = 6.67)
    R(35) ≈ 0.38 s

MVA gives the complete curve X(N) and R(N), not just bounds.

---

## Complexity and limits

- Single-class: O(N × K) time — fast, can run for N = 10,000 in milliseconds.
- Multi-class: O(N₁ × N₂ × … × Nᵣ × K) — exponential; use AMVA approximation
  (Bard–Schweitzer) for more than 2 classes.
- Assumes: FCFS queues, exponential service times (or BCMP-compatible).
  Does NOT apply when service time depends on queue length (load-dependent),
  but a generalization exists (load-dependent MVA, Chapter 20 of QSP).

---

## When to use MVA vs. ABA

- ABA first: identify bottleneck, estimate N*, decide if the question
  can be answered by bounds alone. Often it can.
- MVA when: you need the exact curve (not just bounds), e.g. to find the
  precise N at which success_rate drops below 99%, or to compare two
  configurations that differ by a small margin near the knee.
- Simulation when: the system violates product-form (USL degradation,
  complex admission control, non-FCFS with priorities, correlated arrivals).

---

## Relationship to simpy-protocol Phase 7

The MVA throughput curve X(N) is the analytical ground truth for
an M/M/c queueing network. Use it to validate a SimPy sweep:

1. Run MVA with the same D_k and Z as the SimPy model.
2. Plot both curves on the same axes.
3. They should agree within simulation variance in the pre-saturation zone.
4. Post-saturation divergence is expected if the SimPy model has SLA
   timeouts (which MVA does not model) — this is a feature, not a bug.
