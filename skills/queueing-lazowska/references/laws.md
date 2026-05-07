# Operational Laws — Reference Card

Source: Lazowska et al., "Quantitative System Performance", Chapter 3.

These laws are **operational** — they hold for any real system during any
finite observation interval, without assuming any particular statistical
distribution. They are consequences of counting, not probability theory.

---

## Variables

| Symbol | Meaning |
|---|---|
| T | observation interval (seconds) |
| A_k | arrivals to device k during T |
| C_k | completions at device k during T |
| B_k | busy time at device k during T |
| λ_k | arrival rate at device k = A_k / T |
| X_k | throughput at device k = C_k / T |
| X | **system throughput** = C₀ / T (C₀ = completed jobs) |
| U_k | utilization of device k = B_k / T |
| S_k | mean service time per visit = B_k / C_k |
| V_k | visit ratio = C_k / C₀ (visits to k per system job) |
| D_k | **service demand** = V_k × S_k = B_k / C₀ |
| R_k | mean residence time at device k (queue + service) |
| T_k | total residence time per job = V_k × R_k |
| Q_k | mean number of jobs at device k |
| R | system response time = Σ_k T_k |
| N | number of customers (closed system) |
| Z | mean think time (closed system) |

---

## Law 1 — Utilization Law

    U_k = X · D_k

Utilization equals system throughput times service demand.
Also written: U_k = X_k · S_k.

**Use for:** checking if any device is saturated (U_k → 1), or computing
throughput ceiling: X_max = 1 / D_k for each device.

**Measurement form:** D_k = U_k / X — the easiest way to get service demand
from monitoring data (observe CPU%, disk%, throughput simultaneously).

---

## Law 2 — Service Demand Law

    D_k = V_k × S_k

Service demand combines visit ratio and per-visit service time.

**Two ways to measure D_k:**
1. Direct: D_k = U_k / X  (monitoring: utilization + system throughput)
2. Indirect: D_k = V_k × S_k  (profiling: visit counts + service time per visit)

Method 1 is usually more reliable for parameterizing a model of an
existing system. Method 2 is used when building a model of a proposed system.

---

## Law 3 — Little's Law

    Q_k = X · T_k         (at a device)
    N   = X · (R + Z)     (at the system level, closed network)

Queue length equals throughput times residence time.

**System-level form:** rearranges to the Interactive Response Time Law:
    R = N/X − Z

If you measure N (active users), X (throughput), and Z (think time),
you get R without any assumptions about distributions.

---

## Law 4 — Forced Flow Law

    X_k = X · V_k

Device-level throughput equals system throughput times visit ratio.

**Use for:** converting a system-level throughput target into per-device
throughput requirements. Also: X_k × S_k = X · D_k = U_k (round-trips back
to the Utilization Law).

---

## Law 5 — Response Time Law (General)

    R = Σ_k (V_k · R_k) = Σ_k T_k

System response time is the sum of residence times across all devices.
For an **open** system: R_k = D_k / (1 − U_k)  (M/M/1 approximation
per device), so R = Σ_k D_k / (1 − X · D_k).

---

## Summary: what you need and what you get

| Given | Compute |
|---|---|
| U_k and X (monitoring) | D_k = U_k / X |
| D_k | bottleneck: k* = argmax(D_k), ceiling: X_max = 1/D_max |
| D_k, Z, N | ABA bounds (→ aba.md), exact curve via MVA (→ mva.md) |
| N, X, Z (measured) | R = N/X − Z (Interactive Response Time Law) |
