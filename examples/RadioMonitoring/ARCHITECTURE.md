# RadioMonitoring — Architecture (step 2)

> Architect's design (input #2 to the simpy-protocol). Captures *how the system
> is built*. **Revised** after model review: recording starts immediately on
> detection (classification is concurrent, not a gate), and downstream
> analysis/decoding is out of scope. Resolved audit gaps are listed at the end.

## Scope — a TWO-STAGE system

```
STAGE ① INTERCEPT (scarce resource: SDR pool)
  SCAN/DISCOVERY → WATCH (observer hops bank) → DETECT → DOWNCONVERT to IQ
    → RECORD IQ (decimated to signal BW; length cap by concurrent classification)
        │  metric: POI (loss A/C)
        ▼
STAGE ② DECODE (scarce resource: decode workers)
  [QUEUE, bounded 100 000 — drop on overflow] → decode worker pool (2)
    → over LAN (gigabit) if workers are separate machines; local if co-located
    → determine type → call matching decoder → decode (t_proc = 0.5 + R·L)
        │  metric: decode-yield (loss = queue overflow, bucket G)
        ▼
   end-to-end yield = POI × decode-yield   (recorded AND decoded)
```

**Key property:** the SDR is free the instant recording ends — it does **not** wait
for decode. So **stage ② does not affect POI**; it is a decoupled second stage with
its own metric (decode-yield + decode latency). The two stages have independent
scarce resources (SDR pool vs decode workers) and can bottleneck independently.

Downstream intelligence exploitation / correlation (after decode) remains out of scope.

## Key design decisions

1. **Two scan roles.** A **discovery scanner** sweeps the full band to find carriers
   (*new* frequencies) and populate the bank — it recovers the adversary's frequency
   plan. The **observer = recording SDRs hop across the banked channels** (variant a):
   they take each banked frequency, check if anything is there, and if so record it.
   The bank is small (≈ plan size), so hopping it is far faster than sweeping the
   continuous range. Variant (b) — discovery scanner flags activity and directs an
   SDR — is rejected: the full-range scanner's revisit is too slow, short sessions
   die before it returns.
2. **Record-first, classify-concurrent.** When an observer SDR finds activity on a
   banked channel, it downconverts to zero IF (IQ) and **starts recording
   immediately**. Classification (digital vs voice, read from the symbol/sample
   rate) runs **concurrently** and only sets the **recording length cap**:
   digital → cap 0.5 s, voice → cap 8 s, or the signal ends on its own first.
   Classification does **not** gate the start of recording. (For channels already
   in the plan the category — hence the cap — is effectively known.)
3. **Recording SDRs do double duty (watch + record).** The pool is the scarce
   resource for *both* activity detection and recording: a long voice record (8 s)
   removes one hopper for 8 s → the other channels are revisited less often.
   **This pool — not the PC — is the primary bottleneck.**
4. **Two independent band subsystems.** Lower (100–800 MHz) and upper
   (800 MHz–6 GHz) each have their own antenna, discovery scanner, bank, and SDR
   pool. They do not share capacity.
5. **Frequency bank = recovered frequency plan.** Bounded (≈ 80 channels: 64 voice
   + 10 digital + 5 drone + 1 radar). The adversary uses a fixed channel plan, so
   detections recur on the same channels — that recurrence is the bank's value. The
   plan **drifts** (adversary changes it, unknown how), so the discovery scanner
   **continuously re-scans** the full range; a channel unseen for **2 days** ages
   out (TTL). A frequency hopper has no fixed channel and defeats the bank (dev variant).

## Topology

```
┌─ LOWER BAND (100–800 MHz) ────────────────┐   ┌─ UPPER BAND (800 MHz–6 GHz) ──────────────┐
│ Antenna L                                 │   │ Antenna U                                 │
│   → Discovery scanner L (full sweep)      │   │   → Discovery scanner U (full sweep)      │
│   → Frequency Bank L (= plan, classified) │   │   → Frequency Bank U (= plan, classified) │
│   → Observer/Recording pool L: 2 SDR      │   │   → Observer/Recording pool U: 4 SDR      │
│        (hop bank → detect → IQ → record)  │   │        (hop bank → detect → IQ → record)  │
└───────────────────────────────────────────┘   └───────────────────────────────────────────┘
                         │                                          │
                         └──────────────► DECODE QUEUE (≤ 100 000) ◄┘
                                            │  drop on overflow → bucket G
                                            │  (over gigabit LAN if workers remote)
                                            ▼
                                 DECODE WORKER POOL (2)
                                  type → decoder → decode (0.5 + R·L)
                                            ┆
                                            ┆  (out of scope after decode)
                                            ▼
                                   analyse / correlate
```

Central **industrial PC** runs control + concurrent classification (light). The
decode workers may live **on the same PC** (share its compute) **or on separate
machines** (own compute, fed over the gigabit LAN) — a configurable placement, an
analysis axis. With decimated recordings the LAN is non-binding (see below), so
placement is essentially a compute decision.

## Components

| Component | Role | Instances |
|---|---|---|
| Antenna L / Discovery scanner L | Sweep 100–800 MHz, find **new** carriers → bank | 1 |
| Antenna U / Discovery scanner U | Sweep 800 MHz–6 GHz, find **new** carriers → bank | 1 |
| Industrial PC | Control + **concurrent classification** (sets record cap; does not gate record). Decode is out of scope. | 1 (light at baseline) |
| Frequency Bank L / U | Recovered frequency plan per band (≈ 80 ch total), **2-day** TTL | 1 each (shared state) |
| Observer/Recording SDR (lower) | **Hop bank L → detect → IQ → record** | **2** |
| Observer/Recording SDR (upper) | **Hop bank U → detect → IQ → record** | **4** |
| Decode queue | Buffers recordings between record and decode; **bounded 100 000**, drop on overflow (bucket G) | 1 (shared) |
| Gigabit LAN | Carries recordings to remote decode workers; serial link ≈ 125 MB/s | 1 (only used if workers remote) |
| Decode worker pool | Pull from queue → determine type → call decoder → decode (t_proc = 0.5 + R·L) | **2** (co-located on PC **or** separate machines — placement axis) |
| Decoder | Selected by signal type — routing only, **not a limited resource** | — |
| Downstream analysis | Correlate / exploit decoded output | out of scope (after decode) |

## Per-band scan times (derived from Fobos 14 GHz/s)

| Discovery scanner | Span | T_sweep = span / 14 GHz/s | Revisit rate |
|---|---|---|---|
| Lower (100–800 MHz) | 700 MHz | **≈ 0.05 s** | ~20×/s |
| Upper (800 MHz–6 GHz) | 5200 MHz | **≈ 0.37 s** | ~2.7×/s |

These set how fast the discovery scanner finds *new* carriers. Activity detection on
*known* (banked) channels is done by the observer SDRs hopping the bank, not by the
discovery sweep.

## Signal flow

```
Per band (L and U independently):

Discovery scanner (continuous full sweep)
    → finds a carrier at frequency f → f entered into the Frequency Bank
      (classified voice/digital/radar/drone; for known plan channels, cached)

Observer/Recording SDR pool — each SDR hops the bank:
    → tune to next banked f (T_retune), check: is anything there now?
        → nothing  → move to next channel
        → activity → DOWNCONVERT to IQ and START RECORDING immediately
              · concurrently classify (digital/voice) → set cap: 0.5 s / 8 s
              · record until cap reached OR signal ends on its own
              · radar  → interference, skip (not recorded)
              · drone  → one 3 s snippet, then de-dup while continuously on air
        → recorded IQ written to DISK   ▮ done (our scope ends)
```

## Control flow

- **Discovery scanner:** runs forever, full sweep; output is new carriers into the
  bank. Never blocked by recording.
- **Observer/recording pool:** each SDR independently hops the bank; "find activity
  → record immediately → continue hopping". Busy for the record duration.
- **Classification:** concurrent with recording, sets the length cap only — never
  delays record start.
- **Radar = pure interference:** classified, never recorded.
- **Drone = not a POI target, snippet-logged:** one ~T_snip (3 s) snippet on first
  sight, then **de-duplicated** while continuously on air. Minor one-time upper-pool
  footprint. (Drone-as-full-target is a dev variant.)
- **De-dup / once-per-block rule:** a captured channel block is marked done; not
  re-recorded while continuously present; recordable again after it drops and reappears.
- **Frequency bank = recovered plan, 2-day TTL:** discovery scanner keeps it fresh
  against drift; size ≈ plan (~80), bounded. A still-active target missed on one SDR
  hop-cycle stays in the bank and can be caught on a later cycle while still
  transmitting → re-detection exists.
- **Band isolation:** lower and upper pools are independent; no spill-over.
- **SDR retune + check time:** 50 MHz / 14 GHz/s ≈ **3.6 ms** per banked channel
  (tune + energy check). One full bank cycle ≈ N × 3.6 ms (N ≈ 80) — the pool's
  effective revisit latency. A recording SDR drops out of the hop rotation for the
  record duration, lengthening revisit for the rest.
- **AGC:** the recording SDR commands AGC (+20 dB on weak targets); the discovery
  scanner runs at 0 dB. Detection (energy, 0 dB) catches in-footprint targets;
  recording (+20 dB) reaches the weak ones → bucket E ≈ 0 at baseline.

## Workload-to-band mapping

| Category | Band | Notes |
|---|---|---|
| Voice (VHF) | Lower (100–800) | 64 channels; observer revisit drives its POI |
| Digital / datalink | both (lower + upper) | 10 channels, split 50/50 |
| Drone | Upper (2.4/5.8 GHz) | 5 continuous emitters, snippet-only (interference) |
| Radar | Upper | 1, pure interference, not recorded |

## Resolved audit gaps

1. **Classification.** Runs on the PC **concurrently with recording**, setting the
   length cap (0.5 s / 8 s); it does **not** gate record start. For known plan
   channels the cap is effectively known. At baseline (static plan) classification
   load is light → **not** a bottleneck. (Supersedes the earlier "classify-before-
   record on PC" design.)
2. **Drone vs upper pool.** Drone is not a POI target; one 3 s snippet then de-dup.
   Minor one-time upper-pool footprint. Bucket D ≈ 0 at baseline.
3. **Bank lifecycle.** Bank = recovered plan, 2-day TTL; discovery scanner
   continuously re-scans for drift; re-detection exists.
4. **Recording SDR cycling.** De-dup rule: captured block marked done, not
   re-recorded while continuously present.
5. **Decode/analysis.** Modelled as a **decoupled stage ②**: bounded queue
   (100 000, drop on overflow → bucket G) feeding **2 decode workers**, each
   decoding in t_proc = 0.5 + R·L. Workers are **co-located on the PC or on
   separate machines** (placement axis); recordings cross the **gigabit LAN** when
   remote. Decode does **not** affect POI (SDR free after recording) — it sets a
   second metric, **decode-yield**. Likely the tighter stage: 2 workers vs 8.5 s
   voice decode → the queue may overflow (the question to answer).
6. **AGC / sensitivity.** Detection (0 dB) ≠ recording (+20 dB) thresholds; SDR
   commands +20 dB → bucket E ≈ 0 at baseline. Residual near-far clipping = dev variant.
7. **Datalink band assignment.** Datalinks in **both** bands, split 50/50.

## Data sizes & network (gigabit LAN)

Recordings are **decimated to signal bandwidth** (the point of zero-IF downconvert):

| Type | Signal BW | IQ rate | Recording size |
|---|---|---|---|
| Voice | ~25 kHz | ~0.1 MB/s | 8 s → ~1 MB |
| Digital | ~1 MHz | ~4 MB/s | 0.5 s → ~2 MB |

Gigabit ≈ 125 MB/s. All 6 SDRs streaming digital ≈ 24 MB/s ≪ 125 → the LAN is
**non-binding** at baseline; transfer (~10–20 ms) ≪ decode (seconds). The link is
in the model (serial resource) so a future **full-band** variant (50 MHz raw ≈
200 MB/s, busts gigabit) can make it bind. Drone snippets (wideband, ~120 MB) are
not decoded, so they do not load the decode LAN at baseline.

## Loss buckets (two stages)

**Stage ① interception** — each target channel activity block, exactly one outcome
(sum = 100 % per category):
- ✅ **Intercepted (recorded)** — observer detected and recorded it.
- **A — hop gap:** an SDR was free but the hop cycle didn't reach the channel in time.
- **C — no free SDR:** all SDRs busy recording → no observer free.
- **B / D / E ≈ 0** — classify no longer gates (B), drones snippet-only (D), +20 dB
  reaches the footprint (E).

**Stage ② decode** — each intercepted recording:
- ✅ **Decoded** — passed queue + a worker.
- **G — queue overflow drop:** the 100 000 queue was full → recording dropped undecoded.

**Two independent bottlenecks.** Stage ①: the SDR pool (watch + record); long voice
records steal hopping capacity, short digital bursts lost to revisit (A) / saturation
(C). Stage ②: 2 decode workers vs heavy voice decode (8.5 s) — likely the tighter
stage. **End-to-end yield = POI × decode-yield.**

## What is out of scope

- RF design of antennas and the 100–800 / 800–6000 split rationale.
- **Intelligence exploitation / correlation after decode** (the consumer of decoded output).
- Disk capacity / storage retention (baseline: not a bottleneck; the decode queue
  bound of 100 000 is modelled).
