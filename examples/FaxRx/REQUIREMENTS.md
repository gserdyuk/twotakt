# FaxRx — Requirements

## What this system does

FaxRx is a worldwide virtual fax reception service. A user registers, selects
a fax number from an available country/area code (USA, Canada, all of Europe),
and provides an email address. All faxes sent to that number are received by
FaxRx and delivered to the user's email as TIFF or PDF attachments. An optional
OCR add-on converts the fax image to searchable PDF or DOCX before delivery.

Users access a web cabinet to view received faxes, manage settings, and check
subscription balance. If the balance reaches zero, incoming faxes are held for
up to 30 days without delivery; after 30 days the number is deactivated.

## Target scale

| Metric | Value |
|---|---|
| Geographic coverage | USA, Canada, full Europe |
| Fax volume | 100 000 faxes per 10-hour business day |
| Average arrival rate | ≈ 2.8 faxes/second |
| Peak burst scenario | 10× average = 28 faxes/second |
| Fax call duration (typical) | 60–90 seconds (1–2 pages, V.34/V.17) |
| Offered traffic at average load | ≈ 250 Erlangs |
| Offered traffic at 10× burst | ≈ 2 500 Erlangs |

Infrastructure topology: on-premises termination servers co-located at major
PSTN carrier PoPs in USA, Canada, and Europe. Each PoP terminates fax calls
via T.30 over analog/digital PSTN lines.

## SLA

| Delivery type | SLA |
|---|---|
| TIFF / PDF (no OCR) | Fax reaches user email within **10 minutes** of reception |
| OCR (PDF text / DOCX) | Fax reaches user email within **1 hour** of reception |

The SLA clock starts when the PSTN call is answered (fax reception begins),
not when the call is placed by the sender.

## Questions this model must answer

1. How many PSTN channels (concurrent fax lines) are required per region to
   handle average load and 10× burst without blocking incoming calls?
2. How many processing workers (fax demodulation → image conversion) are needed
   to meet the 10-minute delivery SLA at average and burst load?
3. How many OCR workers are needed to meet the 1-hour OCR SLA?
4. Which stage saturates first under 10× burst — PSTN channel capacity,
   processing workers, OCR workers, or email delivery?
5. What does the latency distribution look like at burst: does the 10-minute
   SLA hold, and at what burst level does it break?

## Required behaviour

| Load condition | Expected outcome |
|---|---|
| Average load (2.8 faxes/s) | Delivery p95 well under 10 min; OCR p95 well under 1 hour |
| 5× burst | Delivery SLA holds with provisioned capacity; queue depth finite |
| 10× burst | Identify which resource saturates first; quantify SLA misses |
| OCR disabled | Same pipeline as non-OCR; OCR worker pool idle |

## Sweep

Primary: arrival rate from 1× to 10× average load (2.8 → 28 faxes/second).
Secondary: number of processing workers and number of OCR workers.

Simulation duration: 3 600 s per configuration (captures multiple burst episodes
and steady-state statistics).

## Out of scope for simulation

- User cabinet, balance management, number provisioning (web/API tier — not in
  the fax processing critical path)
- Subscription billing and payment processing
- Fax sending (outbound) — this model covers reception only
- Per-country routing decisions (modelled as a single aggregate arrival stream)
- Carrier-level PSTN routing and number porting
- Email deliverability (SMTP relay is assumed reliable; email delivery time
  is included as a fixed additive latency, not a contended resource)
