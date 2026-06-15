# USLDBmodel — a second contended resource

A strict extension of [`USLmodel`](../USLmodel/): the same CPU-bound server, now
with a backend **database connection pool**. The exhibit of "extend by
composition" — one new resource, two new `Config` fields, nothing else changed —
and of how two resources interact to produce a bottleneck neither shows alone.

## Input — what you give

| Document | Role |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | The USLmodel server plus a bounded DB pool reached once per request. **→ defines the model.** |
| [`REQUIREMENTS.md`](REQUIREMENTS.md) | Regression + bottleneck-shift questions, required behaviour, SLA, sweep. **→ defines the testbench and acceptance criteria.** |

## Model — what gets simulated

Inherits USLmodel's USL-degraded CPU; adds a DB pool as `Resource(capacity=db_pool_size)`
with query time ~ `Exp(db_query_mean)`, no DB-side degradation (pure M/M/c). Each request
issues exactly one query after its CPU/IO work. Full spec in [`MODEL.md`](MODEL.md).

## How to run

```sh
pip install -r requirements.txt
python server_sim.py    # smoke test — should report success_rate ≈ 1.0
python sweep.py         # arrival-rate sweep, default pool vs starved pool → sweep_results.json
python plot_sweep.py    # → sweep.png (regression) and sweep_2.png (pool comparison)
```

## Output

- `sweep.png` — arrival-rate sweep at the default pool (regression vs USLmodel).
- `sweep_2.png` — pool = 1 vs pool = 8 comparison (bottleneck shift).
- [`SIM_REPORT.md`](SIM_REPORT.md) — full results, interpretation, recommendations.

## Result — what it shows

**Regression:** with a generous pool (≥ 8) the database is invisible — it adds a
constant ~0.05 s to latency and the curve is indistinguishable from USLmodel.

**The non-obvious finding:** a single connection has a theoretical ceiling of
20 rps (1 / 0.05 s), so on paper it is comfortable at 6 rps — yet the simulation
collapses there (success 0.27 vs 1.00 with pool = 8). Near CPU saturation the USL
term inflates the in-flight count, those requests serialize on the one connection,
and the wait burns the SLA budget. **Component ceilings do not compose additively —
the bottleneck emerges from the interaction of two resources at a load where
neither is saturated alone.** Size the pool against in-flight count at the knee,
not against average query rate.

## Lesson

Per-component capacity math is unsafe. When two resources sit in series, the
system can collapse at a load well below either resource's individual ceiling:
pressure on one (the USL term inflating in-flight count) serializes work on the
other (the single connection), and the wait burns the SLA budget. Size shared
pools against the in-flight count at the knee, not against the average request
rate — and when production fails "below every component's limit," suspect a
resource interaction of exactly this kind.

*In plain terms:* it's tempting to size each resource on its own — if one
database connection can serve 20 queries per second, then 6 per second should be
easy. This example shows why that's dangerous when resources sit one behind
another. As the CPU gets busy, the number of requests in flight balloons, and
they all queue behind the single shared connection; the waiting eats the
deadline and requests start failing — at a load far below what either the CPU or
the connection could handle alone. The bottleneck came from the two resources
*interacting*, not from either hitting its own limit. Size shared pools for the
worst-case number of simultaneous requests, not the average rate.

## Files

| File | What it is |
|---|---|
| `ARCHITECTURE.md`, `REQUIREMENTS.md` | inputs (see above) |
| `MODEL.md` | the audited model spec — source of truth |
| `server_sim.py` | SimPy model + `Config` (USLmodel + DB pool) |
| `sweep.py` | parameter sweep → `sweep_results.json` |
| `plot_sweep.py` | plotting → `sweep.png`, `sweep_2.png` |
| `SIM_REPORT.md` | results and conclusions |
