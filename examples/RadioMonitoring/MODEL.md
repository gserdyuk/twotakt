# RadioMonitoring — what this model represents

> Audit (Phase 1) output. Source of truth for the SimPy model. If this doc and
> the code disagree, this doc is the spec and the code is the bug.
> **Status: DRAFT — awaiting user approval before any code is written.**

## What real system is being modelled

A frontline radio-spectrum surveillance system. The target is an adversary running
comms on a **frequency plan** (a bounded set of channels). Two full-range
**discovery scanners** (lower 100–800 MHz, upper 800 MHz–6 GHz) find new
frequencies and populate a **frequency bank** — effectively **reconstructing the
adversary's frequency plan**. A pool of **recording SDRs** hops across the banked
channels (watching), and when a channel is active it records the IQ (full emission
for voice/digital; a 3 s snippet for drones), writes to disk, and the PC decodes.
Radar is interference. The question: **what fraction of target-channel activity the
system intercepts (POI), by category, as density grows** — and what binds first,
the SDR pool (watch+record) or PC compute.

## What is scarce / shared in this system

| Resource | SimPy primitive | Capacity | Role |
|---|---|---|---|
| Discovery scanner L | process (cyclic) | 1, full range, cycle ≈ 0.05 s | finds **new** frequencies → bank L |
| Discovery scanner U | process (cyclic) | 1, full range, cycle ≈ 0.37 s | finds **new** frequencies → bank U |
| **SDR pool L** (watch+record) | `simpy.Resource` | **2 SDR** | hop bank L, detect activity **and** record |
| **SDR pool U** | `simpy.Resource` | **4 SDR** | hop bank U, detect **and** record |
| PC compute | `simpy.Resource` | **C slots** (chosen, swept) | classification (500 ms) + decode (t_proc) |
| Frequency bank L / U | shared store | = frequency plan (**bounded**) | known plan channels, **2-day** TTL, dedup flags |

**Key:** the recording SDRs do double duty — **watch and record** — so the pool is
the contended resource for *both* activity detection and recording.

> *Implementation note:* an idle SDR sleeps until the next block start instead of
> busy-hopping every t_retune; revisit latency (bucket A) is preserved. This is an
> efficiency change only — re-verified green (statistical equivalence, not per-seed). The discovery
scanner **continuously re-scans** the full range (the plan drifts — the adversary
changes it, in unknown ways), constantly refreshing the bank. Its load is fixed and
independent of signal density → it never saturates → **not a bottleneck, but not idle.**

## Frequency plan and bank

Emitters are channelised, on the adversary's plan (tighter than channel-grid physics):

| Category | Plan channels | Emitters | Band |
|---|---|---|---|
| Voice | **64** | 200 (reuse channels) | lower |
| Digital / datalink | **10** | 20 | lower & upper (50/50) |
| Drone | ~5 | 5 | upper |
| Radar | 1 | 1 | upper |
| **Bank (total)** | **≈ 80 channels** | | |

The bank is bounded by the plan (~80) and converges to it after warm-up. New keyings
are **repeats** of known channels (the bank's whole point). The plan **drifts** — the
discovery scanner keeps hunting new channels; a channel unseen for 2 days ages out
(TTL). A frequency hopper (dev axis #6) has no fixed channel → defeats the bank.

**SDR bank-hop cycle:** (N_channels / n_sdr) × T_retune. A **recording SDR drops out
of the watch rotation** for the record duration → revisit of the other channels grows.

## Unit of interception and POI

**Unit = "channel activity block"** — a continuous period a channel is transmitting
(may merge back-to-back sessions of different emitters).

- **POI counted by channel** (reliable): fraction of channel activity blocks captured,
  per category (voice / digital).
- **Dedup:** an SDR returning to a still-active channel treats it as the same block and
  leaves (no re-record). Channel goes quiet then active again → new block → recordable.
- **By session** — best-effort only: merging two back-to-back sessions into one block
  undercounts sessions. Accepted; channel-level is the primary metric.

## What a request looks like

A "request" = one **target-channel activity block**.

| Category | Band | Block duration | Recorded? | Record duration |
|---|---|---|---|---|
| Voice | lower | ~8 s (fixed, may merge) | yes (target) | full block |
| Digital / datalink | lower & upper | ~0.5 s (fixed) | yes (target) | full block |
| Drone | upper | continuous | snippet only (not POI) | **3 s (T_snip)**, then dedup |
| Radar | upper | continuous | no (interference) | — |

Lifecycle (target block): channel becomes active → **detection**: an SDR hopping the
bank lands on the channel while active (a brand-new, not-yet-planned channel is first
found by the discovery scanner → classified on PC 500 ms → banked) → **record** (holds
the SDR for the block) → IQ to disk → **decode** on PC (t_proc) → **intercepted ✓**.
Failure at any step → loss bucket.

## Workload

- **Arrival:** Poisson (baseline, Palm–Khintchine). 200 voice emitters spread over
  64 channels; 20 digital over 10 channels.
- **Rate** λ ≈ 3.5 new emissions/s; per voice channel ≈ 0.05 keys/s (channel occupancy
  ≈ 40 %, merges possible).
- **N_occ ≈ 16** simultaneous. **Sweep:** λ × {1,2,5,10}; secondary C, pool sizes.
- **Sim duration:** TBD (Phase 6; warm-up = bank convergence time, discarded).

## How the system degrades under load

Per SDR pool: **multi-server queue with abandonment (Erlang-A, M/M/c+M)** — a block
is lost if no SDR reaches the channel before activity **ends**.

**Clean mechanism:** SDRs do watch+record. A long voice record (8 s) **removes one
hopping SDR for 8 s** → other channels revisited less often → short digital (0.5 s)
ends before revisit → lost. The SDR pool is scarce for detection **and** recording at
once.

**Deadline asymmetry:** voice (8 s) patient → high POI; digital (0.5 s) impatient →
falls first.

Bottleneck candidates (sweep ranks):
1. **SDR pool** — watch+record contend (buckets A and C merge).
2. **PC (C slots)** — classification + decode (bucket B).
3. Discovery scanner — continuously re-scans (plan drift), fixed load, never
   saturates → **not** a steady-state bottleneck (but not idle).

## Loss accounting (the primary output)

Each target-channel activity block → exactly one bucket, counted per category
(voice / digital); buckets sum to 100 % (conservation = verification check):

| Bucket | Meaning | Driven by |
|---|---|---|
| ✅ Intercepted | full pipeline done | — |
| A | SDR pool did not visit the channel while active | bank size, free-SDR count |
| B | ended before record start (classify/PC wait) | PC slots C |
| C | all SDRs busy recording until block ended | pool size, record length |
| D | starved by continuous emitters | ≈ 0 baseline (drone snippet only) |
| E | below recording sensitivity | ≈ 0 baseline (SDR +20 dB reaches footprint) |

**Also measured:** end-to-end latency (on-air → decoded) per category, no threshold.
**SLA target: POI ≥ 50 % per category (by channel).**

## Backpressure and safety

- **Abandonment (reneging):** a block is lost the instant channel activity ends, if not
  yet recording. The only "timeout".
- **Dedup:** return to an active channel → same block, leave. Re-record only after a
  quiet gap then re-activation.
- **Bank TTL:** 2 days (a channel unseen for 48 h drops from the plan). No retries /
  priorities / preemption at baseline.

## What the operator can dial (Config)

**Topology:** `n_sdr_lower=2`, `n_sdr_upper=4`, `n_pc_slots=C` (chosen).
**Scan:** `scan_rate=14 GHz/s`, `window=50 MHz` → `T_sweep_L/U` derived;
`band_lower=(100,800)`, `band_upper=(800,6000)` MHz.
**Plan:** `plan_voice=64`, `plan_digital=10`, `plan_drone=5`, `plan_radar=1`.
**Times:** `t_class=0.5 s`, `t_proc=0.5+1.0·L`, `t_snip=3 s`, `t_retune=0.0036 s`.
**Record durations (fixed):** `rec_voice=8 s`, `rec_digital=0.5 s`.
**Workload:** populations (200/20/5/1), `voice_key_interval=60 s`, `lambda_ref≈3.5/s`,
`datalink_split=0.5`.
**Sensitivity (baseline E≈0):** `strong_frac=0.05`, `path_loss_n=3`.
**Bench:** `lambda_mult` sweep {1,2,5,10}, `sim_time`, `seeds`.

## Parameter sources

| Type | Parameters |
|---|---|
| **Design decision** | pools 2/4, two bands, discovery-scan vs SDR bank-hop (variant a), scan@0dB/record@+20dB, drone=ignore+snippet, bank TTL 2 days, T_snip=3 s |
| **Measurement / spec** | scan 14 GHz/s, window 50 MHz, T_sweep, T_retune (derived) |
| **Assumption** (sweep) | plan voice 64 / digital 10, t_class 500 ms, t_proc R=1.0, populations, λ, 5 %/95 % (n=3), C |

## What this model deliberately does not include

Baseline excludes (dev axes in REQUIREMENTS.md): frequency hopping, correlated/surge
arrivals, mobility, duration spread (CV>0), near-far clipping, encryption, classifier
errors, bounded decrypt queue, adaptive scanning, category priority, drone-as-target,
**session distinction within a channel block**. Also out: RF link budgets, disk
capacity, phase ⑥.

## What success looks like when running this model

**Verification (smoke, low load, generous C and pools):**
- Voice POI ≈ 100 %; digital POI high but < voice.
- Buckets D, E ≈ 0. Conservation: buckets sum to 100 % per category.
- SDR pool and PC mostly idle; latency p50 ≈ sum of phase means.

**Validation (sweep λ 1→10×):**
- POI declines; **voice holds longer, digital falls first** (Erlang-A signature).
- A clear **knee**; bucket mix (A/B/C) names the bottleneck.
- Expect **SDR pool** or **PC (C)**, not the discovery scanner. Sweep confirms.

If voice and digital fall together, or D/E are non-zero, or buckets do not sum to
100 % — the model is wrong; debug before analysis.
