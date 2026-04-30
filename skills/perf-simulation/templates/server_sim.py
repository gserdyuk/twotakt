"""
SimPy server simulation — TEMPLATE.

Fill in the TODOs based on the audit (references/audit-protocol.md).
The file structure is fixed by the perf-simulation skill so that
sibling examples remain copy-compatible. Do not rename Config / Server
/ run / summarize / arrival_process — downstream tooling depends on
these names.

After filling in, the file should:
  - Encode the entities identified in the audit (Q2) as Resources.
  - Encode the request lifecycle (Q3) as the _serve method.
  - Apply the chosen degradation law (Phase 2) inside _serve.
  - Expose every parameter (Q4–Q6) on Config.
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass, field
from typing import Optional

import simpy


# ---------------------------------------------------------------------------
# Configuration — every magic number must live here (Phase 5)
# ---------------------------------------------------------------------------

@dataclass
class Config:
    # Workload (audit Q4)
    arrival_rate: float = 4.0          # requests/sec (Poisson, lambda)
    sim_time: float = 600.0            # simulated seconds
    seed: int = 42

    # Per-request work (audit Q3)
    # TODO: replace with the actual phases identified in the audit
    n_phases: int = 2
    cpu_burst_mean: float = 0.05
    io_wait_mean: float = 0.10

    # Degradation (Phase 2 + theory-glossary.md)
    # TODO: pick the right law and coefficients
    alpha: float = 0.02                # USL linear contention
    beta: float = 0.001                # USL quadratic coherency

    # Backpressure / SLO (audit Q6)
    max_threads: Optional[int] = None
    sla_seconds: Optional[float] = None


# ---------------------------------------------------------------------------
# Per-request bookkeeping
# ---------------------------------------------------------------------------

@dataclass
class RequestRecord:
    rid: int
    arrival: float
    start: Optional[float] = None
    finish: Optional[float] = None
    outcome: str = "pending"           # ok | dropped_buffer | dropped_timeout

    @property
    def wait(self) -> Optional[float]:
        return None if self.start is None else self.start - self.arrival

    @property
    def latency(self) -> Optional[float]:
        return None if self.finish is None else self.finish - self.arrival


# ---------------------------------------------------------------------------
# Server — one Resource per scarce shared thing identified in audit Q2
# ---------------------------------------------------------------------------

class Server:
    def __init__(self, env: simpy.Environment, cfg: Config):
        self.env = env
        self.cfg = cfg
        self.cpu = simpy.Resource(env, capacity=1)
        # TODO: add other Resources here (db pool, disk, etc.) as audit demands
        self.active = 0
        self.records: list[RequestRecord] = []

    # ---- degradation multiplier (Phase 2) ---------------------------------

    def degradation_multiplier(self, n_active: int) -> float:
        a, b = self.cfg.alpha, self.cfg.beta
        n = max(n_active, 1)
        return 1.0 + a * (n - 1) + b * n * (n - 1)

    # ---- top-level request handler ---------------------------------------

    def handle_request(self, rid: int):
        rec = RequestRecord(rid=rid, arrival=self.env.now)
        self.records.append(rec)

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
                    inner.interrupt()
                    rec.outcome = "dropped_timeout"
                    rec.finish = self.env.now
        finally:
            self.active -= 1

    # ---- the actual work — the heart of the model ------------------------
    # Phase 4: encode the request lifecycle from audit Q3 here.

    def _serve(self, rec: RequestRecord):
        cfg = self.cfg
        try:
            for _ in range(cfg.n_phases):
                base = random.expovariate(1.0 / cfg.cpu_burst_mean)
                with self.cpu.request() as req:
                    yield req
                    if rec.start is None:
                        rec.start = self.env.now
                    mult = self.degradation_multiplier(self.active)
                    yield self.env.timeout(base * mult)
                if cfg.io_wait_mean > 0:
                    yield self.env.timeout(
                        random.expovariate(1.0 / cfg.io_wait_mean)
                    )
            # TODO: add downstream phases (DB, cache, etc.) here on extension
            rec.outcome = "ok"
            rec.finish = self.env.now
        except simpy.Interrupt:
            return


# ---------------------------------------------------------------------------
# Workload generator — Poisson by default
# ---------------------------------------------------------------------------

def arrival_process(env: simpy.Environment, server: Server):
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
    """Aggregate per-request records.

    Includes effective latency (timeouts as SLA seconds) and success rate
    by default — these are required by the metric checklist (Phase 8).
    Do not remove them.
    """
    recs = server.records
    ok = [r for r in recs if r.outcome == "ok"]
    dropped_buf = sum(1 for r in recs if r.outcome == "dropped_buffer")
    dropped_to = sum(1 for r in recs if r.outcome == "dropped_timeout")

    latencies = [r.latency for r in ok]
    waits = [r.wait for r in ok]

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


if __name__ == "__main__":
    print_result(run(Config()), header="=== Single run (defaults) ===")
