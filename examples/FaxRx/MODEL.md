# FaxRx — Simulation Model

This document describes the simulation model — how the architecture is
translated into SimPy, which mathematical laws are applied, and what the
model deliberately excludes. Read `ARCHITECTURE.md` first.

If this description and the code disagree, this description is the
specification and the code is the bug.

## From architecture to SimPy

| Architectural element | SimPy primitive | Mathematical model |
|---|---|---|
| SIP channel pool | `simpy.Resource(capacity=sip_channels)` | Erlang B: immediate rejection when all channels busy (no queue) |
| Fax call in progress | SimPy process holding SIP resource | Exponential call duration |
| Processing worker pool | `simpy.Resource(capacity=num_processing_workers)` | M/M/c — I/O-bound, no USL degradation |
| OCR worker pool | `simpy.Resource(capacity=num_ocr_workers)` | M/M/c + USL multiplier — CPU-bound |
| OCR routing decision | `random.random() < ocr_fraction` | Bernoulli(0.5) per fax |
| Email delivery | `simpy.timeout(Exp(email_delivery_mean))` | Fixed fast phase, not a contended resource |
| SLA timeout | `simpy.timeout(sla_seconds)` + `process.interrupt()` | Separate SLA per path (10 min / 1 hour) |

## Mathematical model

### PSTN layer — Erlang B (immediate rejection)

If all SIP channels are occupied when a call arrives, the call is rejected
immediately — no queue, no wait. The sender receives a busy signal and must
redial. Implemented by checking `sip_pool.count >= sip_pool.capacity` before
requesting:

    if sip_pool.count >= sip_pool.capacity:
        rec.outcome = "blocked_pstn"
        return

This is the correct model for PSTN fax: lines do not have a waiting room.

### Processing workers — pure M/M/c

Processing workers are I/O-bound (object storage read/write). No shared
CPU state between workers. USL degradation does not apply:

    effective_processing_time = Exp(processing_time_mean)   # alpha = beta = 0

### OCR workers — M/M/c with USL degradation

OCR is CPU-bound. Multiple OCR jobs competing for CPU cores cause measurable
coherency and context-switch overhead:

    effective_ocr_time = Exp(ocr_time_mean) × (1 + α·(N−1) + β·N·(N−1))

where N is the number of OCR jobs currently active. α captures linear
contention; β captures quadratic cache/lock interference.

### Request lifecycle

```
1. Fax call arrives (Poisson with burst modulation)
2. SIP channel check (Erlang B):
       if sip_pool.count >= capacity → blocked_pstn, done
       else → acquire SIP channel
3. Hold SIP channel for Exp(call_duration_mean) — fax reception
4. Release SIP channel
5. Acquire processing worker (M/M/c queue if all busy)
   rec.start = env.now
6. Exp(processing_time_mean) — demodulate + convert to TIFF/PDF
7. Release processing worker
8. if Bernoulli(ocr_fraction):
       acquire OCR worker (M/M/c queue if all busy)
       Exp(ocr_time_mean) × USL_multiplier(N_ocr_active) — OCR
       release OCR worker
9. Exp(email_delivery_mean) — SMTP delivery (fast, uncontended)
10. rec.outcome = "ok", rec.finish = env.now
```

SLA timer wraps steps 2–10. Two independent SLA clocks:
- Non-OCR path: `sla_delivery_seconds` = 600 s (10 min)
- OCR path: `sla_ocr_seconds` = 3 600 s (1 hour)

The SLA clock starts at call arrival (step 1), so call duration (~90 s)
consumes part of the SLA budget. Under normal load this is not binding;
under burst it reduces the slack available for queue wait.

## Parameter sources

| Parameter | Default | Source |
|---|---|---|
| `sip_channels` | 270 | Erlang B calculation: 250 Erlangs offered at average load, 1% blocking |
| `call_duration_mean` | 90 s | **Assumption** — 1–2 page fax at V.34; standard industry estimate |
| `num_processing_workers` | 20 | **Estimate** — offered load = 2.78 × 5 s = 14 Erlangs; 20 gives headroom |
| `processing_time_mean` | 5 s | **Assumption** — demodulation + TIFF + PDF conversion, fast I/O-bound |
| `ocr_fraction` | 0.5 | Requirements (50% of users enable OCR) |
| `num_ocr_workers` | 35 | **Estimate** — offered load = 1.39 × 20 s = 28 Erlangs; 35 gives headroom |
| `ocr_time_mean` | 20 s | **Assumption** — OCR of 1–2 pages on modern hardware |
| `email_delivery_mean` | 2 s | **Assumption** — SMTP relay, warm connection, small attachment |
| `alpha` | 0.0 | Default: independent OCR workers (separate machines, no shared CPU). Set > 0 to model a single multi-threaded OCR server with contention. |
| `beta` | 0.0 | Default: same as alpha. Sweep alpha/beta together to observe USL degradation curve. |
| `arrival_rate` | 2.78 faxes/s | Requirements: 100 000 faxes / 10 h day |
| `burst_multiplier` | 10.0 | Requirements: 10× burst scenario |
| `burst_ramp_duration` | 3 600 s | Architecture: EU/NA morning ramp ~60 min |
| `burst_interval` | 43 200 s | Architecture: two peaks per 24 h (12 h apart) |
| `sla_delivery_seconds` | 600 s | Requirements: 10 min non-OCR SLA |
| `sla_ocr_seconds` | 3 600 s | Requirements: 1 hour OCR SLA |

All numeric assumptions should be replaced with measurements when the
system is instrumented. Use `modeling-jain/references/workload.md`.

## What this model deliberately does not include

- Outbound fax sending
- Per-region channel pools (single aggregate pool; split by region is
  a one-line change but does not change the essential dynamics)
- Fax retransmission on line errors (modelled as extended call duration)
- Email deliverability failures (SMTP assumed reliable)
- Balance check and fax-hold logic (business rule, not load-path)
- User cabinet and web tier (not in critical processing path)
- OCR quality variation (all pages treated identically)
- Multi-page fax variability in processing time (mean covers 1–2 pages)

## Verification & Validation criteria

**Verification** (smoke test at defaults, average load, alpha=beta=0):
- Throughput ≈ arrival rate × (1 − PSTN blocking) ≈ 2.73 faxes/s
- PSTN blocking rate ≈ 1% (270 channels, 250 Erlangs offered)
- Success rate ≈ 0.98 (PSTN blocking only; queues near empty at this load)
- Non-OCR p95 delivery ≈ call_duration + processing + email ≈ 100–150 s; well under 600 s
- OCR p95 delivery ≈ 120–200 s; well under 3 600 s
- OCR and non-OCR completions ≈ 50/50 split

**Validation** (sweep over burst multiplier 1×→10×):

Three phases must appear on both delivery paths:
1. **Healthy** — both SLAs hold, success rate ≈ 1.0, queues near zero
2. **Knee** — one pool saturates first; p95 climbs toward SLA; small miss rate appears
3. **Degraded** — SLA misses dominate; identify which resource saturated first

Additionally:
- PSTN blocking must appear when `sip_channels` is held at 270 and
  burst multiplier exceeds ~1.1× (offered traffic > channel capacity).
- With `sip_channels` = 2 565, PSTN blocking must be ≈ 0 even at 10× burst.
- OCR path latency must always exceed non-OCR path latency by ≥ `ocr_time_mean`
  at any load level (structural sanity check).
- Setting `alpha = beta = 0` on OCR workers must produce a pure M/M/c plateau
  (no decline) — baseline sanity check for the USL implementation on the OCR pool.
