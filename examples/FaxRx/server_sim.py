"""
SimPy simulation: FaxRx virtual fax reception pipeline.

Model
-----
* SIP channel pool (Erlang B): bounded concurrent fax calls.
  When all channels are busy, incoming calls are rejected immediately
  (busy signal to sender) — no queue at the PSTN layer.
* Processing worker pool (M/M/c): converts received fax image to TIFF/PDF.
  I/O-bound; no USL degradation (alpha=beta=0).
* OCR worker pool (M/M/c + USL): CPU-bound OCR of fax image to PDF/DOCX.
  Applies to ocr_fraction of faxes (default 50%). USL degradation applies.
* Email delivery: fast uncontended phase (exponential, mean ~2 s).

Two independent SLA clocks:
  - Non-OCR path: sla_delivery_seconds (default 600 s = 10 min)
  - OCR path:     sla_ocr_seconds      (default 3600 s = 1 hour)
  Both clocks start at fax call arrival — call duration (~90 s) consumes
  part of the SLA budget.

Burst pattern
-------------
Exponential-decay spike: rate jumps to burst_multiplier × base at the start
of each burst episode, then decays exponentially back to base over
burst_ramp_duration seconds. Two episodes per burst_interval (12 h) model
EU and NA morning peaks.

Metrics
-------
Separate ok/timeout counts and effective-latency percentiles for the OCR
and non-OCR paths. Effective latency counts timed-out requests at their
SLA value to avoid survivorship bias under overload.

Run
---
    pip install simpy
    python server_sim.py
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Optional

import simpy


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class Config:
    # Load
    arrival_rate: float = 2.78          # base faxes/second (100 000 / 10 h day)
    sim_time: float = 3600.0            # simulated seconds (1 h for smoke test)
    seed: int = 42

    # PSTN layer (Erlang B)
    sip_channels: int = 270             # concurrent SIP channels; Erlang B cap
    call_duration_mean: float = 90.0    # mean fax call duration, seconds

    # Processing workers (I/O-bound, pure M/M/c)
    num_processing_workers: int = 20
    processing_time_mean: float = 5.0   # mean demodulate + convert, seconds

    # OCR workers (CPU-bound, M/M/c + USL)
    ocr_fraction: float = 0.5           # fraction of faxes routed to OCR
    num_ocr_workers: int = 35
    ocr_time_mean: float = 20.0         # mean OCR time per fax, seconds
    alpha: float = 0.0                  # USL linear contention (0 = independent workers)
    beta: float = 0.0                   # USL quadratic coherency (0 = independent workers)

    # Email delivery (uncontended)
    email_delivery_mean: float = 2.0    # mean SMTP delivery, seconds

    # SLA (clock starts at call arrival)
    sla_delivery_seconds: float = 600.0     # 10 min — non-OCR path
    sla_ocr_seconds: float = 3600.0         # 1 hour — OCR path

    # Burst: exponential-decay spike
    # rate(t) = base + (peak - base) * exp(-k * phase)  while phase < ramp_duration
    burst_multiplier: float = 1.0           # 1.0 = no burst; 10.0 = 10× spike
    burst_ramp_duration: float = 3600.0     # seconds for spike to decay to base
    burst_interval: float = 43200.0         # seconds between spike starts (12 h)


# ---------------------------------------------------------------------------
# Per-request bookkeeping
# ---------------------------------------------------------------------------

@dataclass
class RequestRecord:
    rid: int
    arrival: float
    ocr: bool = False
    start: Optional[float] = None       # when processing worker acquired
    finish: Optional[float] = None
    outcome: str = "pending"            # ok | blocked_pstn | dropped_timeout

    @property
    def latency(self) -> Optional[float]:
        return None if self.finish is None else self.finish - self.arrival


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

class Server:
    def __init__(self, env: simpy.Environment, cfg: Config):
        self.env = env
        self.cfg = cfg
        self.sip_pool = simpy.Resource(env, capacity=cfg.sip_channels)
        self.processing_workers = simpy.Resource(env, capacity=cfg.num_processing_workers)
        self.ocr_workers = simpy.Resource(env, capacity=cfg.num_ocr_workers)
        self.ocr_active = 0             # OCR jobs currently running (for USL)
        self.records: list[RequestRecord] = []

    def _ocr_multiplier(self) -> float:
        a, b = self.cfg.alpha, self.cfg.beta
        n = max(self.ocr_active, 1)
        return 1.0 + a * (n - 1) + b * n * (n - 1)

    def handle_request(self, rid: int):
        cfg = self.cfg
        rec = RequestRecord(
            rid=rid,
            arrival=self.env.now,
            ocr=random.random() < cfg.ocr_fraction,
        )
        self.records.append(rec)

        # Erlang B: immediate rejection when all SIP channels are busy
        if self.sip_pool.count >= self.sip_pool.capacity:
            rec.outcome = "blocked_pstn"
            rec.finish = self.env.now
            return                          # no yield — synchronous rejection

        sla = cfg.sla_ocr_seconds if rec.ocr else cfg.sla_delivery_seconds
        inner = self.env.process(self._serve(rec))
        deadline = self.env.timeout(sla)
        result = yield inner | deadline
        if inner not in result:
            inner.interrupt()
            rec.outcome = "dropped_timeout"
            rec.finish = self.env.now

    def _serve(self, rec: RequestRecord):
        cfg = self.cfg
        try:
            # --- Phase 1: SIP channel — hold for fax call duration ---
            with self.sip_pool.request() as req:
                yield req
                yield self.env.timeout(
                    random.expovariate(1.0 / cfg.call_duration_mean)
                )
            # channel released — fax image received

            # --- Phase 2: processing worker (I/O-bound, no USL) ---
            with self.processing_workers.request() as req:
                yield req
                if rec.start is None:
                    rec.start = self.env.now
                yield self.env.timeout(
                    random.expovariate(1.0 / cfg.processing_time_mean)
                )

            # --- Phase 3: OCR worker (CPU-bound, USL) — 50% of faxes ---
            if rec.ocr:
                with self.ocr_workers.request() as req:
                    yield req
                    self.ocr_active += 1
                    try:
                        yield self.env.timeout(
                            random.expovariate(1.0 / cfg.ocr_time_mean)
                            * self._ocr_multiplier()
                        )
                    finally:
                        self.ocr_active -= 1

            # --- Phase 4: email delivery (uncontended) ---
            yield self.env.timeout(
                random.expovariate(1.0 / cfg.email_delivery_mean)
            )

            rec.outcome = "ok"
            rec.finish = self.env.now

        except simpy.Interrupt:
            # SLA timeout fired; handle_request already wrote outcome/finish.
            return


# ---------------------------------------------------------------------------
# Workload generator
# ---------------------------------------------------------------------------

def _burst_rate(t: float, cfg: Config) -> float:
    """Exponential-decay spike: jump to peak at burst start, decay to base."""
    phase = t % cfg.burst_interval
    if cfg.burst_multiplier > 1.0 and phase < cfg.burst_ramp_duration:
        peak = cfg.arrival_rate * cfg.burst_multiplier
        k = 5.0 / cfg.burst_ramp_duration      # 5 time constants → ≈ base at end
        return cfg.arrival_rate + (peak - cfg.arrival_rate) * math.exp(-k * phase)
    return cfg.arrival_rate


def arrival_process(env: simpy.Environment, server: Server):
    cfg = server.cfg
    rid = 0
    while True:
        rate = _burst_rate(env.now, cfg)
        yield env.timeout(random.expovariate(rate))
        env.process(server.handle_request(rid))
        rid += 1


# ---------------------------------------------------------------------------
# Driver and metrics
# ---------------------------------------------------------------------------

def run(cfg: Config) -> dict:
    random.seed(cfg.seed)
    env = simpy.Environment()
    server = Server(env, cfg)
    env.process(arrival_process(env, server))
    env.run(until=cfg.sim_time)
    return summarize(server, cfg)


def _pct(xs: list, p: float):
    if not xs:
        return None
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round((p / 100.0) * (len(xs) - 1)))))
    return xs[k]


def summarize(server: Server, cfg: Config) -> dict:
    recs = server.records

    blocked   = [r for r in recs if r.outcome == "blocked_pstn"]
    timed_out = [r for r in recs if r.outcome == "dropped_timeout"]
    ok        = [r for r in recs if r.outcome == "ok"]

    ok_plain  = [r for r in ok        if not r.ocr]
    ok_ocr    = [r for r in ok        if r.ocr]
    to_plain  = [r for r in timed_out if not r.ocr]
    to_ocr    = [r for r in timed_out if r.ocr]

    lat_plain = [r.latency for r in ok_plain]
    lat_ocr   = [r.latency for r in ok_ocr]

    # Effective latency: timed-out requests counted at their SLA ceiling
    eff_plain = lat_plain + [cfg.sla_delivery_seconds] * len(to_plain)
    eff_ocr   = lat_ocr   + [cfg.sla_ocr_seconds]      * len(to_ocr)
    eff_all   = eff_plain + eff_ocr

    n = len(recs)
    return {
        "config":            cfg.__dict__,
        "total_arrivals":    n,
        "blocked_pstn":      len(blocked),
        "dropped_timeout":   len(timed_out),
        "completed_ok":      len(ok),
        "success_rate":      len(ok) / n if n else None,
        "pstn_block_rate":   len(blocked) / n if n else None,
        "throughput_fps":    len(ok) / cfg.sim_time,

        "plain_ok":          len(ok_plain),
        "plain_timeout":     len(to_plain),
        "plain_eff_p50":     _pct(eff_plain, 50),
        "plain_eff_p95":     _pct(eff_plain, 95),
        "plain_eff_p99":     _pct(eff_plain, 99),

        "ocr_ok":            len(ok_ocr),
        "ocr_timeout":       len(to_ocr),
        "ocr_eff_p50":       _pct(eff_ocr, 50),
        "ocr_eff_p95":       _pct(eff_ocr, 95),
        "ocr_eff_p99":       _pct(eff_ocr, 99),

        "eff_all_p50":       _pct(eff_all, 50),
        "eff_all_p95":       _pct(eff_all, 95),
        "eff_all_p99":       _pct(eff_all, 99),
    }


def print_result(r: dict, header: str = ""):
    if header:
        print(header)
    for k, v in r.items():
        if k == "config":
            continue
        if isinstance(v, float):
            print(f"  {k:22s} {v:.4f}")
        else:
            print(f"  {k:22s} {v}")


# ---------------------------------------------------------------------------
# CLI — smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Smoke test: 1 hour, no burst, defaults
    cfg = Config(sim_time=3600.0, burst_multiplier=1.0)
    print_result(run(cfg), header="=== FaxRx smoke test (1 h, no burst) ===")
