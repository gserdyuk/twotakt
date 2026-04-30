"""
SimPy simulation: thread-per-request server with USL-style degradation.

Model
-----
* One CPU, modeled as simpy.Resource(capacity=1).
* Each incoming request becomes its own process (== a thread).
* A request is a sequence of N phases: each phase = (CPU burst, IO wait).
  - During CPU burst: process holds the CPU resource (contended).
  - During IO wait: CPU is released (parallel I/O).
* Per-burst CPU time is scaled by a USL-like degradation multiplier:
        mult(N_active) = 1 + alpha*(N-1) + beta*N*(N-1)
  - alpha: linear contention (Amdahl-like serialization)
  - beta : quadratic coherency penalty (cache, locks, GC, ...)
  This is what makes the server's effective CPU work *more* with more in-flight
  threads — the realistic part beyond pure M/M/1 queueing.
* Optional backpressure:
  - max_threads: hard cap on in-flight requests; overflow returns "503".
  - sla_seconds: per-request deadline; misses are recorded as timeouts.

Metrics
-------
For every arriving request we record arrival/start/finish times and an outcome
(ok | dropped_buffer | dropped_timeout). summarize() returns aggregate stats:
throughput, mean/p50/p95/p99 latency, mean wait, drop counts.

Run
---
    pip install simpy
    python server_sim.py

Tweak Config(...) at the bottom or call run(Config(...)) from a sweep harness.
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass, field
from typing import Optional

import simpy


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class Config:
    # Load
    # Defaults give base CPU demand = n_phases * cpu_burst_mean = 0.1 s/req,
    # so utilization at arrival_rate=4 is ~0.4 — comfortably below saturation.
    arrival_rate: float = 4.0          # requests/sec (Poisson, lambda)
    sim_time: float = 600.0            # simulated seconds
    seed: int = 42

    # Per-request work mix
    n_phases: int = 2                  # number of (CPU, IO) phases per request
    cpu_burst_mean: float = 0.05       # mean CPU seconds per burst (base, undegraded)
    io_wait_mean: float = 0.10         # mean IO seconds per phase

    # Degradation (Universal Scalability Law style)
    alpha: float = 0.02                # contention coefficient (linear)
    beta: float = 0.001                # coherency coefficient  (quadratic)

    # Backpressure / SLO
    max_threads: Optional[int] = None       # None = unlimited; else 503 on overflow
    sla_seconds: Optional[float] = None     # None = no deadline; else drop on miss

    # Database (model #1: connection pool)
    db_pool_size: int = 8                   # number of DB connections in the pool
    db_query_mean: float = 0.05             # mean DB query time, seconds (exponential)


# ---------------------------------------------------------------------------
# Per-request bookkeeping
# ---------------------------------------------------------------------------

@dataclass
class RequestRecord:
    rid: int
    arrival: float
    start: Optional[float] = None      # first moment CPU is acquired
    finish: Optional[float] = None
    outcome: str = "pending"           # ok | dropped_buffer | dropped_timeout

    @property
    def wait(self) -> Optional[float]:
        return None if self.start is None else self.start - self.arrival

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
        self.cpu = simpy.Resource(env, capacity=1)
        self.db = simpy.Resource(env, capacity=cfg.db_pool_size)
        self.active = 0                       # in-flight (admitted) requests
        self.records: list[RequestRecord] = []

    # ---- degradation -------------------------------------------------------

    def degradation_multiplier(self, n_active: int) -> float:
        a, b = self.cfg.alpha, self.cfg.beta
        n = max(n_active, 1)
        return 1.0 + a * (n - 1) + b * n * (n - 1)

    # ---- top-level request handler ----------------------------------------

    def handle_request(self, rid: int):
        rec = RequestRecord(rid=rid, arrival=self.env.now)
        self.records.append(rec)

        # Backpressure: refuse if over the thread cap
        cap = self.cfg.max_threads
        if cap is not None and self.active >= cap:
            rec.outcome = "dropped_buffer"
            rec.finish = self.env.now
            return

        self.active += 1
        try:
            sla = self.cfg.sla_seconds
            if sla is None:
                yield self.env.process(self._serve(rec))
            else:
                inner = self.env.process(self._serve(rec))
                deadline = self.env.timeout(sla)
                result = yield inner | deadline
                if inner not in result:
                    # SLA missed: cancel the inner process cleanly
                    inner.interrupt()
                    rec.outcome = "dropped_timeout"
                    rec.finish = self.env.now
        finally:
            self.active -= 1

    # ---- the actual work ---------------------------------------------------

    def _serve(self, rec: RequestRecord):
        cfg = self.cfg
        try:
            for _ in range(cfg.n_phases):
                # ----- CPU burst (contended) -----
                base = random.expovariate(1.0 / cfg.cpu_burst_mean)
                with self.cpu.request() as req:
                    yield req
                    if rec.start is None:
                        rec.start = self.env.now
                    mult = self.degradation_multiplier(self.active)
                    yield self.env.timeout(base * mult)

                # ----- IO wait (CPU released, runs in parallel) -----
                if cfg.io_wait_mean > 0:
                    yield self.env.timeout(
                        random.expovariate(1.0 / cfg.io_wait_mean)
                    )

            # ----- DB query: hold a pooled connection for query_time -----
            # Pool is bounded — under high concurrency this becomes a queue.
            with self.db.request() as conn:
                yield conn
                yield self.env.timeout(
                    random.expovariate(1.0 / cfg.db_query_mean)
                )

            rec.outcome = "ok"
            rec.finish = self.env.now

        except simpy.Interrupt:
            # SLA cancelled us. The `with` blocks above released the CPU
            # automatically. The outer handler already wrote outcome/finish.
            return


# ---------------------------------------------------------------------------
# Workload generator
# ---------------------------------------------------------------------------

def arrival_process(env: simpy.Environment, server: Server):
    """Poisson arrivals at rate cfg.arrival_rate."""
    rid = 0
    rate = server.cfg.arrival_rate
    while True:
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


def _percentile(xs, p):
    if not xs:
        return None
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round((p / 100.0) * (len(xs) - 1)))))
    return xs[k]


def summarize(server: Server, cfg: Config) -> dict:
    recs = server.records
    ok = [r for r in recs if r.outcome == "ok"]
    dropped_buf = sum(1 for r in recs if r.outcome == "dropped_buffer")
    dropped_to = sum(1 for r in recs if r.outcome == "dropped_timeout")

    latencies = [r.latency for r in ok]
    waits = [r.wait for r in ok]

    # "Effective" latency: include timed-out requests as latency = SLA seconds
    # (they actually waited that long before being killed). Without this, the
    # ok-only percentiles suffer survivorship bias under overload.
    # Buffer drops are excluded — those fail instantly, so counting them as 0
    # would falsely *lower* the percentiles. Track them via success_rate instead.
    sla = cfg.sla_seconds
    if sla is not None and (latencies or dropped_to):
        latencies_eff = latencies + [sla] * dropped_to
    else:
        latencies_eff = latencies

    return {
        "config": cfg.__dict__,
        "total_arrivals": len(recs),
        "completed_ok": len(ok),
        "dropped_buffer": dropped_buf,
        "dropped_timeout": dropped_to,
        "success_rate": len(ok) / len(recs) if recs else None,
        "throughput_rps": len(ok) / cfg.sim_time if cfg.sim_time else 0.0,
        "latency_mean": statistics.mean(latencies) if latencies else None,
        "latency_p50": _percentile(latencies, 50),
        "latency_p95": _percentile(latencies, 95),
        "latency_p99": _percentile(latencies, 99),
        "eff_latency_p50": _percentile(latencies_eff, 50),
        "eff_latency_p95": _percentile(latencies_eff, 95),
        "eff_latency_p99": _percentile(latencies_eff, 99),
        "wait_mean": statistics.mean(waits) if waits else None,
    }


def print_result(r: dict, header: str = ""):
    if header:
        print(header)
    for k, v in r.items():
        if k == "config":
            continue
        if isinstance(v, float):
            print(f"  {k:18s} {v:.4f}")
        else:
            print(f"  {k:18s} {v}")


# ---------------------------------------------------------------------------
# CLI: single run + (commented) sweep example
# -------------------------------