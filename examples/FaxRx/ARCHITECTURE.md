# FaxRx — Architecture

## What this system does

FaxRx is a worldwide virtual fax reception service. Users purchase a DID
(Direct Inward Dialing) number in a country of their choice, provide an email
address, and receive all incoming faxes as email attachments (TIFF or PDF).
An optional OCR add-on delivers a searchable PDF or DOCX instead of a raw image.

## User base and DID inventory

| Metric | Value |
|---|---|
| Active users (target) | 500 000 |
| DID numbers purchased | 500 000 (one per user) |
| Countries covered | USA, Canada, full Europe |

DIDs are pre-purchased from carriers per country and assigned to users at
signup. DID count affects procurement and billing but has no effect on channel
capacity math or system throughput — it does not appear as a resource in the
simulation model.

## Infrastructure topology

FaxRx operates on-premises servers co-located at PSTN carrier PoPs in three
regions. Each region is an independent stack.

| Region | Coverage |
|---|---|
| NA-East | USA East Coast + Canada |
| NA-West | USA West Coast |
| EU | All European countries |

Each PoP terminates fax calls via **SIP trunks with T.38 fax-over-IP**. The
number of SIP channels purchased at each PoP is the primary capacity decision.

## Channel sizing

| Load scenario | Arrival rate | Offered traffic | SIP channels required (1% blocking) |
|---|---|---|---|
| Average (100 K faxes / 10 h day) | 2.8 faxes/s | 250 Erlangs | ~270 |
| 5× burst | 14 faxes/s | 1 250 Erlangs | ~1 300 |
| 10× burst | 28 faxes/s | 2 500 Erlangs | ~2 565 |

Offered traffic = arrival rate × mean call duration (90 s).
Channel count derived from Erlang B formula at 1% blocking probability.
If all channels are busy, the sender receives a busy signal immediately —
there is no queue at the PSTN layer (Erlang B, not M/M/c).

## Components

| Component | Role | Instances |
|---|---|---|
| SIP termination server | Answers fax calls, runs T.38/T.30, produces raw fax image | 1 pool per PoP; bounded by SIP channel count |
| Reception queue | Decouples call termination from processing (Kafka) | 1 per region |
| Processing worker | Converts raw fax → TIFF + PDF; routes to OCR queue or email queue | Bounded pool |
| OCR worker | Converts TIFF/PDF → searchable PDF or DOCX | Bounded pool; fed by 50% of faxes |
| Email delivery worker | Sends processed attachment via SMTP to user | Fast; not the primary bottleneck |
| Object storage | Stores fax images and processed documents | Not a concurrency bottleneck |
| User database | User records, DID assignments, balance, fax metadata | Not in the critical processing path |
| User cabinet (web) | Fax history, balance, config — accessed by user directly | Not in the critical processing path |

## Signal flow

```
Fax sender dials DID number
    → SIP trunk (PoP)
        [if all channels busy → busy signal to sender, call cleared — Erlang B]
    → T.38 / T.30 handshake, fax image received
    → raw fax image stored to object storage
    → event emitted to reception queue (Kafka)

Reception queue
    → processing worker (bounded pool)
        → demodulate signal → TIFF image
        → convert TIFF → PDF
        → if user has OCR enabled (50% of users):
              emit to OCR queue
          else:
              emit to email delivery queue

OCR queue (50% of faxes)
    → OCR worker (bounded pool)
        → OCR TIFF/PDF → searchable PDF / DOCX
        → emit to email delivery queue

Email delivery queue
    → email delivery worker
        → send SMTP to user email
        → fax delivered ✓
```

## Control flow

- **PSTN blocking (Erlang B):** if all SIP channels at a PoP are occupied, the
  incoming call is rejected immediately. No queue. Sender must redial.
- **SLA timeout (processing):** if a fax event sits in the processing queue too
  long, the 10-minute delivery SLA is missed. Tracked as a pipeline miss.
- **SLA timeout (OCR):** separate 1-hour SLA clock. OCR queue depth is the
  leading indicator.
- **Balance check:** performed at email delivery time. If user balance = 0,
  fax is stored (not delivered) for up to 30 days, then the DID is deactivated.
  This is a business rule, not a load-path component.

## Burst shape

Traffic follows a double-peak daily pattern driven by business-hours
concentration in two time zones:

- **EU morning peak:** ramp-up starting ~07:00 UTC, peak ~09:00–10:00 UTC,
  exponential decay over 2–3 hours.
- **NA morning peak:** ramp-up starting ~13:00 UTC, peak ~14:00–15:00 UTC,
  exponential decay over 2–3 hours.

For simulation: modelled as two independent exponential-ramp burst episodes
per 24-hour period. The 10× burst scenario represents the peak of the EU or
NA morning spike relative to the overnight baseline.

## Two cascaded bottlenecks (post-PSTN)

Once a fax call completes and the image is in the reception queue, the pipeline
reduces to two cascaded M/M/c queues — the same pattern as USLDBmodel:

```
Reception queue → [processing workers, M/M/c] → [OCR workers, M/M/c, 50% path]
                                               → [email delivery, fast]
```

Processing workers are I/O-bound (object storage read/write, no shared CPU
state). OCR workers are CPU-bound. USL degradation applies to OCR workers
(alpha > 0); processing workers use pure M/M/c (alpha = beta = 0).

## What is explicitly out of scope

- Outbound fax sending
- User cabinet, balance management, number provisioning (not in critical path)
- Per-country SIP routing and number porting mechanics
- Email deliverability (SMTP relay treated as reliable with fixed additive latency)
- Carrier-level PSTN routing topology
- Cross-region failover and active-active load balancing
- Fax retransmission on line quality errors (modelled as extended call duration)
