# FaxRx — Performance Simulation Report

**Date:** 2026-06-11
**Models:** SimPy discrete-event simulation; Erlang B (PSTN/SIP layer) + M/M/c (processing) + M/M/c with USL (OCR)
**Data source:** committed `sweep_results.json` (33 runs, sim_time = 7200 s)
**Repository:** `examples/FaxRx/`

## Context

A fax receiving system: PSTN/SIP channels → processing workers → optional OCR (50 % of
faxes) → email delivery. SLA: 10 min for plain faxes, 1 hour for OCR faxes.
The question: **how should the system be sized for traffic bursts — and what is the right
place for it to fail when a burst exceeds capacity?**

## Model summary

SIP channels are an Erlang B resource — a call arriving when all channels are busy is
rejected immediately (busy signal), no queue: lines have no waiting room. Processing
workers are I/O-bound M/M/c; OCR workers are CPU-bound M/M/c with USL degradation.
See `MODEL.md`.

### Parameters

Defaults sized for average load; see `MODEL.md` parameter table. Sweep-relevant:

| Parameter | Values | Justification / source |
|---|---|---|
| sip_channels | 270 / 2565 | average-load sizing vs 10× burst sizing |
| num_ocr_workers | 35 / 175 | default vs 5× scale-out |
| burst_multiplier | 1.0 → 10.0 | burst severity sweep |

## Sweep design

Three architectures × eleven burst levels:
A) `sip=270, ocr=35` — front door sized for average load;
B) `sip=2565, ocr=35` — front door opened 10×, backend unchanged;
C) `sip=2565, ocr=175` — front door opened 10×, OCR scaled 5×.

## Results

| burst | A: succ / block / p95 eff | B: succ / block / p95 eff | C: succ / block / p95 eff |
|---|---|---|---|
| 1× | 0.98 / 0.8 % / 291 s | 0.98 / 0 / 287 s | 0.99 / 0 / 291 s |
| 3× | 0.84 / 14 % / 288 s | 0.98 / 0 / 748 s | 0.98 / 0 / 520 s |
| 5× | 0.72 / 27 % / 284 s | 0.83 / 0 / 1734 s | 0.87 / 0 / 717 s |
| 10× | 0.54 / 45 % / 286 s | 0.52 / 0 / 3600 s | 0.68 / 0 / 1402 s |

## Interpretation

The sweep exposes **two qualitatively different failure modes**:

**Architecture A fails fast at the edge.** As burst grows, Erlang B rejects more calls
(0.8 % → 45 %), but everything admitted is served on time: p95 stays flat at ~285 s across
the entire range, OCR timeouts ≈ 0. The failure is a busy signal — the sender knows
immediately and redials. The small front door acts as admission control protecting
the backend.

**Architecture B fails slowly inside.** Opening the front door 10× eliminates blocking,
but the backlog drowns OCR: p95 climbs to the SLA ceiling (3600 s), and failures become
timeouts. At 10× burst its success rate (0.52) is *no better than A's* (0.54) — but the
user experience is far worse: the fax was accepted, then silently died an hour later.
**Admitting work you cannot finish converts fast, honest failures into slow, hidden ones
— without improving the success rate.**

**Architecture C (scale OCR 5×) helps but does not absolve.** Mid-range bursts improve
markedly (0.87 vs 0.83 at 5×), yet at 10× success is 0.68 with p95 at 1400 s — still 5×
worse latency than A. Capacity scaling delays the slow-failure mode; it does not change
its nature.

## Conclusions & recommendations

- The undersized front door of architecture A is a **feature, not a deficiency**: it is
  the system's admission control. Removing it (B) makes overload strictly worse for users.
- If burst tolerance beyond ~3× is a requirement, combine: moderate SIP expansion +
  OCR scaling + an explicit admission/backpressure policy — not unconditional admission.
- Sizing rule from the data: every architecture choice should be evaluated by **where**
  it fails, not only by how much it carries. "Success rate" alone hides the difference
  between a busy signal and a broken promise.

## Risks & sensitivity

Sensitive to the OCR fraction (0.5 assumed) and OCR service time: a higher OCR share
moves the inside-failure onset to lower bursts. The 1-hour OCR SLA is the ceiling that
defines "timeout" — a tighter SLA shifts all success rates down in B and C, barely in A.

## Limitations

No redial behavior modeled (rejected callers vanish rather than retry — real Erlang
retries would raise effective load on A); single processing stage; no priority lanes.
Most likely next extension: redial loop with exponential backoff, which would quantify
how much of A's advantage survives retry pressure.

## Repo note

This example currently has no `plot_sweep.py` / `sweep.png` — results exist only as JSON.
Recommended before publication: add the standard three-panel plot (success rate, block
rate, p95 eff vs burst, three curves per panel) for visual parity with other examples.
