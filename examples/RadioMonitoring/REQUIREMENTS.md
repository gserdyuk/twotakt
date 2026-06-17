# RadioMonitoring — Requirements (ТЗ)

> Status: **ТЗ COMPLETE (step 1 closed).** Workload, timings, SLA, loss-accounting,
> and the strong/weak split (5 %/95 %) are agreed. Architecture (step 2) —
> receiver/channel/worker counts, record & re-detection policy, resource binding —
> is the next step, out of scope of this doc.

## What this system does

A software-defined hardware system for **radio spectrum surveillance**
("радиомониторинг"). It continuously scans the radio spectrum, and for every
signal it finds it must:

1. **Detect** — register the presence of a signal.
2. **Classify** — determine signal type and modulation.
3. **Demodulate + record** — capture the IQ sequence and store a segment
   (fractions of a second for digital bursts, up to tens of seconds for voice).
4. **Process recordings** — review, decrypt, and store the recorded IQ segments.
5. **Analyse** — exploit the stored recordings.

Frequency coverage: **100 MHz – 6 GHz** (set to the Fobos receiver ceiling),
possibly split into 2 sub-bands.

### Pipeline

```
spectrum (100 MHz – 6 GHz)
   │
   ▼
① SCAN — sweep the band, look for energy        ← scarce resource: receiver/tuner
   │  (signal detected)
   ▼
② DETECT — register signal presence
   ▼
③ CLASSIFY — signal type, modulation
   ▼
④ DEMODULATE + RECORD IQ — 0.5 s (digital) … tens of s (voice)  ← holds a channel for the whole record
   ▼
⑤ PROCESS — review, decrypt, store
   ▼
⑥ ANALYSE
```

### The core tension (why we simulate)

Receivers/recording channels are finite. While a channel is **demodulating and
recording** a signal (the longest phase — seconds), it is not scanning and not
available for a new signal. If signals appear faster than the system can service
them, **some signals pass by undetected**. The governing metric is
**POI — probability of intercept** (the fraction of signals successfully
intercepted end-to-end).

This is exactly the survivorship trap the methodology warns about: missed
signals are invisible, and latency-of-successes lies. POI / success-rate is
tracked as a first-class metric.

## Operational scenario

Frontline surveillance. A reasonably sensitive VHF antenna with ≈ **10 km**
reception radius → detection footprint ≈ **π·10² ≈ 314 km²**.

AGC (automatic gain control) with 2 levels: **0 dB / +20 dB**. This controls
sensitivity range and the near-far dynamic-range problem (strong nearby vs weak
distant emitter). → It is a **detection-model** parameter (per-sweep detection
probability, two sensitivity regimes), **not** a workload parameter. Recorded
here so it is not lost; enters the model at the detection phase.

### Strong / weak signal split (geometry-derived)

Emitters are assumed **uniformly distributed by area** over the R = 10 km disk →
P(d < r) = r²/R² (far-weighted; median distance ≈ 7.07 km). Received power ∝
1/dⁿ. The +20 dB AGC step = a range ratio 10^(2/n); with 10 km as the max range
(at +20 dB), the strong/weak boundary is at d_b = 10 / 10^(2/n) km, and the
strong fraction = (d_b/R)² = 10^(−4/n).

| n | strong | weak |
|---|---|---|
| 2 free space | 1 % | 99 % |
| **3 VHF over terrain (chosen)** | **5 %** | **95 %** |
| 4 with obstacles | 10 % | 90 % |

**Agreed: n = 3 → strong 5 %, weak 95 %.** Important: this split is about
**recording** sensitivity, not detection. Detection (scanner, 0 dB energy
detection) is the easy part — it catches in-footprint targets including weak ones.
**Recording** needs high SNR: strong (5 %) record at 0 dB, weak (95 %) need the
SDR to command +20 dB. Since the SDR does command +20 dB, weak targets are
recordable → **bucket E ≈ 0 at baseline**. The split instead drives the SDR's AGC
choice and the **near-far** development variant (strong emitter clipping a +20 dB
weak recording). Sweep n = 2…4 as sensitivity.

## Receiver hardware — Fobos SDR (RigExpert)

| Spec | Value | Model impact |
|---|---|---|
| Tuning range | 100 kHz – **6 GHz** | scan band fixed to 100 MHz–6 GHz = **5.9 GHz** (ТЗ ceiling set to match) |
| Instantaneous bandwidth | **50 MHz** | scan step / record window |
| IQ rate | 50 MSPS, 14-bit | ≈ 200 MB/s per channel over USB 3.0 |
| Band Scan rate | **14 GHz/s** | T_sweep = 5.9/14 ≈ 0.42 s → rounded to **0.5 s** |
| Interface | USB 3.0, double conversion (RFFC5072 + MAX2830, LTC2143 ADC) | one tuner = **scan OR record, not both** |

**Key consequence:** one Fobos is a single USB-3 tuner — it can *either* sweep
*or* demodulate+record, never both at once. While it records a 10 s voice signal
it is blind to the whole spectrum. This makes **number of receivers** the primary
scarce resource (count decided in step 2).

**Detection physics (POI):** a signal is caught only if a sweep visits its
50 MHz slice while it is on-air. Rough model: **P(detect) ≈ min(1, L / T_sweep)**
for emission length L. With T_sweep = 0.5 s: voice (5–15 s) ≈ certain; digital
0.5 s ≈ borderline; 0.1 s burst ≈ 0.2 — signals are lost on scanning alone,
before any channel contention. This is the detection-phase model (with AGC).

## Workload — AGREED

Source emitter population inside the 314 km² footprint, across 100 MHz – 6 GHz.
Ratio anchor (user): per 10 voice nets → 1 datalink; 1 radar; 5 drones present.

| Emitter class | Population | Duty cycle (on-air fraction) | Active at once | Emission length |
|---|---|---|---|---|
| Tactical VHF voice (PTT) | **200** | ~3–5 % | ~8 | **8 s (fixed)** |
| Digital datalinks / relays | **20** (200/10) | bursty ~10 % | ~2 | **0.5 s (fixed)** |
| Drone video / command links | **5** | ~100 % (continuous) | 5 | continuous |
| Radars / continuous emitters | **1** | ~100 % | 1 | continuous |
| **Instantaneous occupancy N_occ** | | | **≈ 16** | |

Continuous emitters occupying capacity: **6** (5 drones + 1 radar).

Two distinct workload quantities the model needs:

| Quantity | Meaning | Role in model |
|---|---|---|
| **Instantaneous occupancy** N_occ ≈ **16** | signals on-air at a moment | how crowded each scan sweep is |
| **Appearance rate** λ ≈ **3.5 new signals/s** | new emissions starting per second | the arrival process driving the model |

Relation: **λ = N_occ / mean_emission_length**.

Derivation of λ (voice-dominated, bursty): 200 voice emitters, each keys
≈ once / 60 s for 8 s → λ_voice ≈ 200/60 ≈ **3.3 emissions/s**, voice occupancy
≈ 3.3 × 8 ≈ 27... but with ~3–5 % duty the simultaneous voice count is ~8;
plus ~2 datalink + 6 continuous → **N_occ ≈ 16**. Continuous emitters (drones,
radars) are modelled as **persistently occupied capacity**, not an event stream.

**Emission/recording durations are FIXED (deterministic, CV = 0):** voice = 8 s,
digital = 0.5 s. No spread modelled at baseline.

**Frequency placement: UNIFORM across 100 MHz – 6 GHz** at baseline. Clustering
(voice in VHF 100–512 MHz, drones at 2.4/5.8 GHz) is a later stress variant.

**Frequency plan (adversary uses a fixed channel plan, tighter than physics):**
voice = **64 channels** (200 emitters reuse them), digital = **10 channels**
(20 emitters), drone ≈ 5, radar 1 → **bank ≈ 80 channels, bounded**. The bank
recovers this plan; recurrence on the same channels is what makes it useful. A
frequency hopper has no fixed channel and defeats the bank (dev variant).

**Reference operating point:** λ ≈ 3.5 new signals/s, N_occ ≈ 16, 6 channels
held by continuous emitters.

## Phase timings *(proposed — to confirm)*

| Phase | Symbol | Proposed value | Source |
|---|---|---|---|
| ① Full band sweep (one Fobos over 5.9 GHz @ 14 GHz/s) | T_sweep | **0.5 s** | Fobos Band Scan spec (0.42 s rounded) |
| ② Detection / fixation | t_detect | *TBD (small, ~ms)* | assumption |
| ③ Classification (type + modulation) | t_class | **500 ms** (compute time) | assumption |
| ④ Demodulate + record (digital) | t_rec_dig | **0.5 s** | given |
| ④ Demodulate + record (voice) | t_rec_voice | **tens of s** | given |
| ⑤ Process / decrypt one recording | t_proc | **t_overhead + R·L_record** (R=1.0, t_overhead=0.5 s) | hypothesis, sweep R |

> **t_class is a duration, not a resource binding.** Whether those 500 ms are
> spent on the receiver (parked on frequency, blind) or on a separate compute
> unit working from already-recorded IQ is an **architecture decision (step 2)**.
> Different architectures → different POI; the model will compare them. ТЗ fixes
> only the duration.

## SLA / targets

| Target | Value | Source |
|---|---|---|
| POI (probability of intercept) | ≥ **50 %** | agreed |
| End-to-end latency (on-air → recording decrypted) | **measured, no hard threshold** | agreed |

> **POI is reported per signal type, not aggregate.** A single aggregate POI is
> misleading here — voice (long emissions) will be near 100 %, short digital
> bursts near 20 % from scan physics alone. Averaging to "50 %" hides that the
> system fails on bursts. Verdict is per-class: voice POI, digital POI, etc.

## Target scope (what counts as a signal to intercept)

| Category | Role | POI counted? | Importance |
|---|---|---|---|
| Voice | target | yes | high |
| Digital / datalink | target | yes | high |
| **Drone** | **interference (baseline)** — mode switch: target = variant | no (baseline) | high if enabled |
| **Radar (RLS)** | **interference only** | no | — (occupies capacity, never a target) |

Two target categories at baseline: **voice / digital**. Radar and drone are both
interference — they consume scanning + classification (PC) capacity but are never
recorded and have no POI. Drone has an operating-mode switch (ignore = baseline,
intercept = development variant). Targets share the POI ≥ 50 % goal; no priority
ordering at baseline.

## Loss accounting — the primary report

**Unit of interception = "channel activity block"** — a continuous period a banked
channel is transmitting (may merge back-to-back sessions). **POI is counted by
channel** (reliable): the fraction of activity blocks captured, per category
(voice / digital). Session-level POI is best-effort only (merged blocks undercount
sessions). Dedup: returning to a still-active channel = same block, leave.

For every target-channel activity block, the model assigns exactly one outcome,
counted **per target category** (voice / digital).
The buckets must sum to 100 % of present signals per category (conservation of
signals — also a verification check).

| Bucket | Outcome | Cause |
|---|---|---|
| ✅ | Intercepted | passed scan → detect → classify → record → process |
| A | Missed — scan gap | no sweep visited its slice while on-air (P ≈ L/T_sweep) |
| B | Ended before record start | detected, but emission ended during classify / channel wait |
| C | No free channel | all receivers/channels busy at detection (blocked) |
| D | Starved by continuous emitters | channels held by radar (and drones if recorded) → no capacity for others |
| E | Below sensitivity (AGC) | weak target the SDR cannot record even at +20 dB — **≈ 0 at baseline** (SDR reaches the 10 km footprint at +20 dB); non-zero only via near-far clipping (dev variant) |

Buckets A–D are core. **E (AGC/sensitivity) ≈ 0 at baseline** — the SDR commands
+20 dB and reaches the whole 10 km footprint; detection at 0 dB catches weak
targets too (detection ≠ recording sensitivity). E becomes non-zero only via the
near-far dev variant. Classifier-rejection and downstream-queue drop are assumed zero at baseline
(perfect classifier, unbounded decrypt queue) and listed in risks.

**Also measured:** end-to-end latency distribution (on-air → decrypted) for the
intercepted signals, per category — reported, no pass/fail threshold.

> Note: re-detection policy, record policy, and which resource each phase binds
> are **model/architecture decisions (step 2 + Phase 1 audit)** — out of scope
> for this ТЗ. The ТЗ fixes only *what we measure*, not *how it is computed*.

## Questions this model must answer

1. As spectrum density grows (λ from 1× to N× the reference), what fraction of
   signals does the system intercept end-to-end (POI)? Where is the knee?
2. Which stage saturates first — scanning (receivers), recording channels, or
   processing/decrypt workers?
3. How many receivers / recording channels / decrypt workers are needed to keep
   POI above target at the reference load and at 2×, 5×, 10×?
4. How much do the always-on emitters (radar interference + drones if recorded)
   cost — they occupy capacity persistently and starve the bursty voice traffic.
5. Does splitting into 2 sub-bands (parallel scan tracks) move the knee?

## Required behaviour

| Load condition | Expected outcome |
|---|---|
| Reference (λ ≈ 3.5/s, N_occ ≈ 16) | POI ≥ target; finite queues |
| 2×–5× density | Identify first saturating stage; quantify POI drop |
| 10× density | POI knee characterised; bottleneck named |

## Sweep

Primary: signal appearance rate λ from 1× to ~10× the reference load.
Secondary: number of receivers, recording channels, decrypt workers.

Simulation duration: TBD (long enough to capture steady-state occupancy and
many emission cycles).

## Development axes / scenario variants

The baseline keeps every dimension at its simplest defensible setting so the first
model is auditable. Each axis below is a deliberate knob for later exploration —
listed so the expansion path is known up front, not retrofitted.

| # | Axis | Baseline | Variant (development) |
|---|---|---|---|
| 1 | **Temporal arrival** | stationary Poisson (Palm–Khintchine: superposition of 200 rare keying nets ≈ Poisson) | **battle-rhythm λ(t)** (quiet→surge); **correlated clusters** (Hawkes/MMPP — synchronous overload, worst case for POI) |
| 2 | **Emission duration** | fixed (CV = 0): voice 8 s, digital 0.5 s | lognormal/exp with CV > 0 (stresses p99 / tail) |
| 3 | **Frequency placement** | uniform across 100 MHz–6 GHz | **clusters** (voice in VHF 100–512 MHz, drone video 2.4/5.8 GHz) |
| 4 | **Strong/weak split** | geometry only, uniform area, n = 3 → 5 %/95 % | **EIRP × distance** (heterogeneous TX power, not distance alone); n = 2…4 by terrain/weather |
| 5 | **Emitter mobility** | static positions | front moves → distances drift → strong/weak fraction changes in time |
| 6 | **Frequency hopping** | none (fixed-frequency emitters) | ⭐ **hopping emitters** — defeat a scanning receiver; changes the detection model fundamentally |
| 7 | **Signal bandwidth** | all fit in the 50 MHz window | wideband (drone video tens of MHz) vs narrowband voice → window fit + record volume |
| 8 | **Drone mode** | **ignored** (interference like radar) | target (intercepted) — reintroduces upper-pool saturation / bucket D |
| 9 | **Category priority** | none (all targets equal) | priority ordering (e.g. voice > datalink) + preemption |
| 10 | **Encryption** | not modelled (decrypt = fixed t_proc) | encrypted fraction; undecryptable share; affects success definition |
| 11 | **Classifier accuracy** | perfect (bucket F = 0) | false alarms / misses consuming resources (bucket F) |
| 12 | **Downstream queue** | unbounded (bucket G = 0) | finite storage / decrypt queue → drops (bucket G) |
| 13 | **Scan strategy** | uniform sweep | adaptive / cognitive dwell on hot sub-bands |
| 14 | **AGC strategy** | per the detection model | global vs per-sub-band vs adaptive level selection |

Highest-impact axes for radio monitoring specifically: **#6 frequency hopping**
and **#1 correlated surges** — both attack POI in ways average load does not.

## Out of scope for simulation

- Step 2 (architecture): receiver count, channelisation, processing topology —
  decided by the architect, audited in Phase 1.
- RF physics: propagation, exact link budgets, antenna patterns (the 10 km
  footprint and AGC levels enter only as a detection-probability abstraction).
- Signal exploitation / intelligence value of recordings (phase ⑥ analysis is
  the consumer, not a contended resource in this model — unless step 2 says so).
- Sub-band RF design details (sub-bands enter only as parallel scan capacity).
