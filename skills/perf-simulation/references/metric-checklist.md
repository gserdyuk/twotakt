# Phase 8 — Metric Critique Checklist

After every sweep, walk through this checklist. Each rule is a
specific failure mode that has misled real performance investigations.
Apply the rules whether or not the user asked for them — half the
value of this skill is catching these silently.

## Rule 1 — Never report ok-only latency without success rate

`latency_p99` over completed requests is a **biased sample** under
overload. As load grows, more requests time out; the ones that
survive are precisely the ones that hit a brief lull when the active
count happened to be lower (because several neighbours just timed
out). These survivors get faster service than average. Result:
`latency_p99` of completed requests can *decrease* as offered load
increases past saturation.

**The fix:** always report success rate alongside latency. Better,
plot them on the same chart. Best, also compute the effective latency
(rule 2).

If you find yourself reporting "latency p99 = 5s under heavy load"
without also reporting "success rate = 3%", you are misleading the
reader.

## Rule 2 — Effective latency: count timeouts as SLA seconds

When a request hits an SLA timeout, it actually waited that long
before being killed. It is dishonest to drop it from the latency
distribution. The "effective latency" metric includes timed-out
requests with latency = SLA seconds:

    latencies_eff = latencies_ok + [sla_seconds] * num_timeouts

Plot effective latency (solid) and ok-only latency (dashed) on the
same panel. The gap between them is a direct visual measure of how
much survivorship bias the ok-only metric is hiding.

Buffer drops (immediate 503) are excluded from effective latency
because including them as latency = 0 would falsely *lower* the
percentiles. Track them via success rate instead.

## Rule 3 — Throughput is not a sufficient summary

A single throughput number hides whether the system is in the
healthy region, the saturation knee, or the thrashing zone. Always
compare throughput against the offered load (the diagonal y=x line
on the throughput plot). The gap between the two is the dropped or
delayed work.

## Rule 4 — Multi-modal latency needs more than one percentile

If the request involves cache hits and misses, or fast and slow
phases, the latency distribution is bimodal. p50 and p99 will live
in different modes. Report at least three percentiles (p50, p95,
p99) and look at them together. A p99 spike with a stable p50 is
not the same problem as both rising together.

## Rule 5 — Throughput plateau ≠ healthy ceiling

If the throughput sweep shows a flat plateau instead of the
characteristic USL peak-and-decline, one of two things is true:

- You chose the wrong law (M/M/c instead of USL); the model cannot
  thrash by construction.
- You chose USL but β = 0; without quadratic interaction the model
  degenerates to M/M/c.

Either is a Phase 2 / Phase 4 bug. Fix the model, do not paper over
the curve.

## Rule 6 — Look at the in-flight count, not just throughput

The state variable that drives degradation in USL is N (in-flight
requests), not λ (arrival rate). A useful diagnostic: log the
maximum and mean N during the sweep. If N stays small even at high
load, the model is not actually loaded — typically because of an
admission control that rejects too aggressively.

## Rule 7 — One run is not a measurement

Stochastic simulations with finite duration have run-to-run variance.
Single-run results in the thrashing zone are particularly noisy
(small numbers of completed requests). For any number that goes into
a decision, run multiple seeds and report mean ± std. For
illustration plots a single run is acceptable.

## Rule 8 — Three-panel plot is the minimum

Throughput chart alone hides the failure mode. The minimum useful
plot for any sweep is three stacked panels:

1. **Throughput** vs offered load (with the y=x ideal as a reference
   line).
2. **Success rate** vs offered load (linear 0–1 scale).
3. **Latency percentiles** vs offered load (log-y; effective solid,
   ok-only dashed).

`templates/plot_sweep.py` has this layout pre-built. Use it.

## Rule 9 — Be suspicious of monotone curves where they shouldn't be

If a metric is monotone in a region where it should not be, suspect
a bug. Examples:

- Latency monotonically *decreasing* as load grows past saturation
  → almost certainly survivorship bias (rule 1).
- Throughput monotonically *increasing* without bound → almost
  certainly a missing capacity constraint or a missing degradation
  term.
- Success rate at exactly 100.00% across all load levels → the SLA
  is so loose it never bites; either tighten it or report that the
  SLA is irrelevant for the configured workload.

## Rule 10 — Always say what you measured, not just the result

In the report, state explicitly: which percentile, over which subset
of requests (ok-only? effective?), under which workload (arrival
rate, sim duration, seeds), with which configuration (the Config
fields). A latency number without this provenance is decoration, not
data.
