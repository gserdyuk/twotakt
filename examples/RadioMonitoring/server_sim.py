"""
RadioMonitoring — SimPy model (two-stage).

Implements MODEL.md / MODEL.ru.md. If code and MODEL.md disagree, MODEL.md is the
spec and the code is the bug.

Stage ① INTERCEPT (scarce resource = SDR pool):
  Bank = adversary frequency plan (pre-known at baseline). Observer/recording SDRs
  hop the bank (watch) and RECORD. Record-first: on detecting activity an SDR
  records immediately; classification runs CONCURRENTLY (sets length cap only,
  does not gate). A target "request" = a channel ACTIVITY BLOCK; lost the instant
  the channel goes quiet if no SDR is recording it.
    metric: POI. buckets ✓ / A (hop gap) / C (no free SDR); B,D,E ≈ 0.

Stage ② DECODE (scarce resource = decode workers), DECOUPLED — SDR is free after
  recording, so stage ② does NOT affect POI:
  recording → bounded QUEUE (100 000, drop on overflow = bucket G) → 2 workers
  → (gigabit LAN if workers are remote) → decode (t_proc = overhead + R·L).
    metric: decode-yield (= decoded / intercepted). end-to-end = POI × decode-yield.
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass

import simpy


# ---------------------------------------------------------------------------
# Configuration — every magic number lives here (Phase 5)
# ---------------------------------------------------------------------------

@dataclass
class Config:
    # --- Bench / workload (ТЗ; sweepable) ---
    lambda_mult: float = 1.0
    sim_time: float = 600.0            # short by default (keep runs fast; add seeds, not length)
    warmup: float = 120.0
    seed: int = 42

    # --- Frequency plan (adversary) ---
    plan_voice: int = 64
    plan_digital: int = 10
    plan_drone: int = 5                 # interference, snippet-only
    plan_radar: int = 1                # pure interference
    digital_lower_frac: float = 0.5

    # --- Emitter populations & cadence ---
    n_voice_emitters: int = 200
    voice_key_interval: float = 60.0
    n_digital_emitters: int = 20
    digital_key_interval: float = 20.0

    # --- Stage ① hardware: SDR pools ---
    n_sdr_lower: int = 2
    n_sdr_upper: int = 4
    n_pc_slots: int = 8                 # PC slots for concurrent classification (light)

    # --- Stage ① service times (s) ---
    t_retune: float = 0.0036
    t_class: float = 0.2               # classification, CONCURRENT, sets cap only
    t_snip: float = 3.0
    rec_voice: float = 8.0             # voice record cap (= block, fixed)
    rec_digital: float = 0.5

    # --- Stage ② decode pipeline ---
    decode_queue_cap: int = 100_000    # bounded queue; drop on overflow (bucket G)
    n_decode_workers: int = 2
    decode_colocated: bool = True      # True: on the PC; False: separate machines (use LAN)
    t_proc_overhead: float = 0.5       # decode fixed overhead
    t_proc_rate: float = 1.0           # decode real-time factor R; t_proc = oh + R*L

    # --- Network (gigabit LAN), used only when workers are remote ---
    net_bandwidth_MBps: float = 125.0  # ~1 Gbit/s
    iq_rate_voice_MBps: float = 0.1    # decimated voice IQ
    iq_rate_digital_MBps: float = 4.0  # decimated digital IQ


VOICE, DIGITAL, DRONE, RADAR = "voice", "digital", "drone", "radar"
TARGETS = (VOICE, DIGITAL)
LOWER, UPPER = "lower", "upper"


@dataclass
class Channel:
    cid: int
    category: str
    band: str
    rate: float = 0.0
    active: bool = False
    active_until: float = 0.0
    block_start: float = 0.0
    captured: bool = False
    handling: bool = False
    snippet_done: bool = False


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

class Server:
    def __init__(self, env: simpy.Environment, cfg: Config):
        self.env = env
        self.cfg = cfg

        # Stage ① resources
        self.pc = simpy.Resource(env, capacity=cfg.n_pc_slots)
        self.n_sdr = {LOWER: cfg.n_sdr_lower, UPPER: cfg.n_sdr_upper}
        self.recording = {LOWER: 0, UPPER: 0}

        # Stage ② resources
        self.decode_q = simpy.Store(env)             # unbounded store; cap enforced manually
        self.net = simpy.Resource(env, capacity=1)   # gigabit LAN as a serial link

        # Per-band wake events — let idle SDRs sleep instead of busy-hopping
        # (efficiency only; revisit semantics preserved — see sdr_worker).
        self.wake = {LOWER: env.event(), UPPER: env.event()}

        self.channels: list[Channel] = []
        self._build_plan()
        self.by_band = {
            LOWER: [c for c in self.channels if c.band == LOWER],
            UPPER: [c for c in self.channels if c.band == UPPER],
        }

        # Metrics — stage ①
        self.total = {VOICE: 0, DIGITAL: 0}
        self.bucket = {c: {"ok": 0, "A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
                       for c in TARGETS}
        self.latencies = {VOICE: [], DIGITAL: []}      # on-air → recorded
        # Metrics — stage ②
        self.decoded = {VOICE: 0, DIGITAL: 0}
        self.decode_dropped = {VOICE: 0, DIGITAL: 0}   # queue overflow (bucket G)
        self.decode_lat = {VOICE: [], DIGITAL: []}     # on-air → decoded
        self.queue_hwm = 0

    def _counting(self) -> bool:
        return self.env.now >= self.cfg.warmup

    def _build_plan(self):
        cfg = self.cfg
        cid = 0
        m = cfg.lambda_mult
        v_rate = (cfg.n_voice_emitters / cfg.voice_key_interval) / cfg.plan_voice
        for _ in range(cfg.plan_voice):
            self.channels.append(Channel(cid, VOICE, LOWER, rate=v_rate * m)); cid += 1
        d_rate = (cfg.n_digital_emitters / cfg.digital_key_interval) / cfg.plan_digital
        n_dig_lower = round(cfg.plan_digital * cfg.digital_lower_frac)
        for i in range(cfg.plan_digital):
            band = LOWER if i < n_dig_lower else UPPER
            self.channels.append(Channel(cid, DIGITAL, band, rate=d_rate * m)); cid += 1
        for _ in range(cfg.plan_drone):
            self.channels.append(Channel(cid, DRONE, UPPER)); cid += 1
        for _ in range(cfg.plan_radar):
            self.channels.append(Channel(cid, RADAR, UPPER)); cid += 1
        for c in self.channels:
            if c.category in (DRONE, RADAR):
                c.active = True

    # ---- Stage ①: per-channel traffic (activity blocks) --------------------

    def channel_traffic(self, ch: Channel):
        dur = self.cfg.rec_voice if ch.category == VOICE else self.cfg.rec_digital
        while True:
            yield self.env.timeout(random.expovariate(ch.rate))
            now = self.env.now
            if not ch.active:
                ch.active = True
                ch.active_until = now + dur
                ch.block_start = now
                ch.captured = False
                ch.handling = False
                if self._counting():
                    self.total[ch.category] += 1
                self.env.process(self.block_closer(ch))
                self._signal_band(ch.band)             # wake any sleeping SDRs
            else:
                ch.active_until = max(ch.active_until, now + dur)

    # ---- wake / serviceability helpers (efficiency for idle SDRs) ----------

    def _signal_band(self, band: str):
        ev = self.wake[band]
        if not ev.triggered:
            ev.succeed()
        self.wake[band] = self.env.event()

    def _serviceable(self, ch: Channel) -> bool:
        if not ch.active or ch.captured or ch.handling:
            return False
        if ch.category == RADAR:
            return False
        if ch.category == DRONE:
            return not ch.snippet_done
        return True

    def _band_has_serviceable(self, band: str) -> bool:
        return any(self._serviceable(c) for c in self.by_band[band])

    def block_closer(self, ch: Channel):
        while True:
            delay = ch.active_until - self.env.now
            if delay <= 0:
                break
            yield self.env.timeout(delay)
        if not ch.captured:
            self._record_loss(ch)
        ch.active = False
        ch.handling = False

    def _record_loss(self, ch: Channel):
        if not self._counting():
            return
        bucket = "C" if self.recording[ch.band] >= self.n_sdr[ch.band] else "A"
        self.bucket[ch.category][bucket] += 1

    # ---- Stage ①: SDR worker (hop + record) --------------------------------

    def sdr_worker(self, band: str, start_idx: int):
        # Hop the bank one channel per t_retune (revisit latency = bucket A). When a
        # full cycle finds nothing serviceable, SLEEP until the next block start
        # instead of busy-hopping — observationally equivalent (an empty hop detects
        # nothing) but ~100x fewer events at light load.
        cfg = self.cfg
        chans = self.by_band[band]
        n = len(chans)
        i = start_idx
        while True:
            serviced = False
            for _ in range(n):
                ch = chans[i % n]
                i += 1
                yield self.env.timeout(cfg.t_retune)
                if not ch.active or ch.captured or ch.handling:
                    continue
                cat = ch.category
                if cat == RADAR:
                    continue
                if cat == DRONE:
                    if ch.snippet_done:
                        continue
                    ch.handling = True
                    self.recording[band] += 1
                    yield self.env.timeout(cfg.t_snip)
                    self.recording[band] -= 1
                    ch.snippet_done = True
                    ch.handling = False
                    serviced = True
                    break
                # target: record immediately; classify concurrently
                ch.handling = True
                ch.captured = True
                on_air = ch.block_start
                self.env.process(self.classify())
                rec_dur = cfg.rec_voice if cat == VOICE else cfg.rec_digital
                self.recording[band] += 1
                yield self.env.timeout(rec_dur)
                self.recording[band] -= 1
                ch.handling = False
                if self._counting():
                    self.bucket[cat]["ok"] += 1
                    self.latencies[cat].append(self.env.now - on_air)
                self._enqueue_decode(cat, on_air)
                serviced = True
                break
            if not serviced and not self._band_has_serviceable(band):
                yield self.wake[band]                  # nothing to do — sleep until activity

    def classify(self):
        with self.pc.request() as req:
            yield req
            yield self.env.timeout(self.cfg.t_class)

    # ---- Stage ②: decode pipeline ------------------------------------------

    def _enqueue_decode(self, cat: str, on_air: float):
        cfg = self.cfg
        if len(self.decode_q.items) >= cfg.decode_queue_cap:
            if on_air >= cfg.warmup:
                self.decode_dropped[cat] += 1          # bucket G: queue overflow
            return
        size = (cfg.iq_rate_voice_MBps if cat == VOICE else cfg.iq_rate_digital_MBps)
        size *= (cfg.rec_voice if cat == VOICE else cfg.rec_digital)
        self.decode_q.put({"cat": cat, "size": size, "on_air": on_air})
        self.queue_hwm = max(self.queue_hwm, len(self.decode_q.items))

    def decode_worker(self):
        cfg = self.cfg
        while True:
            msg = yield self.decode_q.get()
            if not cfg.decode_colocated:                # fetch over the gigabit LAN
                with self.net.request() as req:
                    yield req
                    yield self.env.timeout(msg["size"] / cfg.net_bandwidth_MBps)
            L = cfg.rec_voice if msg["cat"] == VOICE else cfg.rec_digital
            yield self.env.timeout(cfg.t_proc_overhead + cfg.t_proc_rate * L)
            if msg["on_air"] >= cfg.warmup:
                self.decoded[msg["cat"]] += 1
                self.decode_lat[msg["cat"]].append(self.env.now - msg["on_air"])


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def run(cfg: Config) -> dict:
    random.seed(cfg.seed)
    env = simpy.Environment()
    server = Server(env, cfg)
    for ch in server.channels:
        if ch.category in TARGETS:
            env.process(server.channel_traffic(ch))
    for band in (LOWER, UPPER):
        for k in range(server.n_sdr[band]):
            env.process(server.sdr_worker(band, start_idx=k * 7))
    for _ in range(cfg.n_decode_workers):
        env.process(server.decode_worker())
    env.run(until=cfg.sim_time)
    return summarize(server, cfg)


def _percentile(xs, p):
    if not xs:
        return None
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round((p / 100.0) * (len(xs) - 1)))))
    return xs[k]


def summarize(server: Server, cfg: Config) -> dict:
    out = {"config": cfg.__dict__, "queue_hwm": server.queue_hwm, "by_category": {}}
    for cat in TARGETS:
        tot = server.total[cat]
        b = server.bucket[cat]
        intercepted = b["ok"]
        accounted = b["ok"] + b["A"] + b["B"] + b["C"] + b["D"] + b["E"]
        dec = server.decoded[cat]
        out["by_category"][cat] = {
            "blocks": tot,
            "intercepted": intercepted,
            "poi": (intercepted / tot) if tot else None,
            "A_hop_gap": b["A"], "B_pc_wait": b["B"], "C_no_sdr": b["C"],
            "D_starved": b["D"], "E_sensitivity": b["E"],
            "conservation_ok": (accounted == tot),
            "rec_lat_p50": _percentile(server.latencies[cat], 50),
            # stage ②
            "decoded": dec,
            "decode_dropped_G": server.decode_dropped[cat],
            "decode_yield": (dec / intercepted) if intercepted else None,
            "e2e_yield": (dec / tot) if tot else None,
            "decode_lat_p50": _percentile(server.decode_lat[cat], 50),
        }
    return out


def print_result(r: dict, header: str = ""):
    if header:
        print(header)
    print(f"  queue high-water = {r['queue_hwm']}")
    for cat, d in r["by_category"].items():
        poi = f"{d['poi']:5.1%}" if d["poi"] is not None else "  n/a"
        dy = f"{d['decode_yield']:5.1%}" if d["decode_yield"] is not None else "  n/a"
        e2e = f"{d['e2e_yield']:5.1%}" if d["e2e_yield"] is not None else "  n/a"
        print(f"  {cat:8s} blocks={d['blocks']:6d}  POI={poi}  "
              f"A={d['A_hop_gap']:5d} C={d['C_no_sdr']:5d} "
              f"cons={'OK' if d['conservation_ok'] else 'FAIL'}  ||  "
              f"decoded={d['decoded']:5d} dropG={d['decode_dropped_G']:6d}  "
              f"dec-yield={dy}  e2e={e2e}")


if __name__ == "__main__":
    # Verification smoke test: HEALTHY config (light load, generous decode) →
    # POI ≈ 100%, decode-yield ≈ 100%, no drops, conservation OK.
    healthy = Config(lambda_mult=0.05, n_decode_workers=16, seed=1)
    print_result(run(healthy), header="=== SMOKE (healthy) ===")

    # Reference architecture (2/4 SDR, 2 decode workers, co-located).
    print_result(run(Config()), header="\n=== REFERENCE (lambda x1, 2/4 SDR, 2 decode) ===")
