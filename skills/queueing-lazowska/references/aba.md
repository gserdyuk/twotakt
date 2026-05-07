# Asymptotic Bound Analysis (ABA)

Source: Lazowska et al., "Quantitative System Performance", Chapter 5.

ABA gives tight **bounds** on throughput and response time without running
MVA. It answers "where is the knee?" in under a minute, analytically.

---

## Inputs

- D_k — service demand at each device k (from laws.md)
- Z — mean think time (0 for batch/open systems)
- N — population range to explore (or a target N)

## Key quantities

    D_sum = Σ_k D_k          # total service demand (minimum response time)
    D_max = max_k(D_k)        # bottleneck demand
    N*    = (D_sum + Z) / D_max   # saturation point

N* is the number of users at which the bottleneck device reaches 100%
utilization. Below N*: system scales linearly. Above N*: bottleneck is
saturated and response time grows linearly with N.

---

## Bounds — closed system (N users, think time Z)

**Throughput:**

    X(N) ≤ min( N / (D_sum + Z) ,  1 / D_max )

- Left term: the "light load" bound — throughput grows linearly with N
  when the system is underloaded (no device saturated).
- Right term: the "heavy load" bound — no device can exceed 100% utilization,
  so throughput is capped at 1/D_max.
- The binding (smaller) value gives the tighter bound at each N.

**Response time:**

    R(N) ≥ max( D_sum ,  N · D_max − Z )

- Left term: the minimum possible response time (zero queuing, pure service).
- Right term: the heavy-load response time growing linearly with N.
- The binding (larger) value gives the tighter bound at each N.

---

## Bounds — open system (arrival rate λ, no N)

For open systems (no fixed population, no think time):

    U_k = λ · D_k                       # utilization at each device
    R_k = D_k / (1 − U_k)              # M/M/1 response time per device
    R   = Σ_k R_k                       # system response time
    X_max = 1 / D_max                   # throughput ceiling (U_k < 1 required)

The open system model is exact under FCFS + exponential assumptions.
It blows up as λ → 1/D_max (saturation).

---

## Bottleneck identification

1. Compute D_k for all devices.
2. The device with largest D_k is the **primary bottleneck** — it saturates first.
3. The second-largest D_k is the secondary bottleneck — it binds after
   the primary is relieved (e.g. by adding capacity).

When you provision more of the bottleneck resource, the knee shifts right
but a new bottleneck emerges. ABA lets you trace this:
- New N* after doubling bottleneck capacity = (D_sum + Z) / (D_max / 2)

---

## Worked example

System: 3 devices — CPU, disk, network.

| Device | D_k (s/job) |
|---|---|
| CPU | 0.050 |
| Disk | 0.150 |  ← bottleneck
| Network | 0.020 |

Think time Z = 5.0 s.

    D_sum = 0.050 + 0.150 + 0.020 = 0.220 s
    D_max = 0.150 s  (disk)
    N*    = (0.220 + 5.0) / 0.150 = 34.8  ≈ 35 users

Throughput bounds at N = 20 and N = 60:

    N=20: X ≤ min(20/5.22, 1/0.15) = min(3.83, 6.67) = 3.83 jobs/s
    N=60: X ≤ min(60/5.22, 1/0.15) = min(11.49, 6.67) = 6.67 jobs/s

Response time bounds:

    N=20: R ≥ max(0.22, 20·0.15 − 5.0) = max(0.22, −2.0) = 0.22 s  (light load)
    N=60: R ≥ max(0.22, 60·0.15 − 5.0) = max(0.22, 4.0) = 4.0 s   (saturated)

Conclusion: provision for ≤ 35 users to stay in the linear region.
At 60 users, response time is at least 4 seconds — the disk is the culprit.
To improve: reduce disk demand (cache, faster disk) or add disk spindles.

---

## What ABA cannot tell you

- The **exact** throughput and response time curve (use MVA for that).
- Behaviour under non-FCFS scheduling.
- Effects of USL-style inter-thread degradation.
- Response time distribution or percentiles (only means).

ABA is a planning tool, not a validation tool. Use MVA or simulation for
precise numbers; use ABA to understand the structure of the problem first.
