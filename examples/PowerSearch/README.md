# PowerSearch — capacity planning for two pipelines

A clothes price aggregator with two independent load paths, each modelled
separately: **ingestion** (crawler → Kafka → processing workers → Elasticsearch)
and **user queries** (search → workers → Elasticsearch). The exhibit of
capacity planning — "how many workers do we need at Year 5?" — across two cascaded
M/M/c pipelines, including a burst-provisioning lesson on the query side.

## Input — what you give

| Document | Role |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Two subsystems, components, regional topology, the simplified-model derivation. **→ defines the models.** |
| [`REQUIREMENTS.md`](REQUIREMENTS.md) | Target scale (Year 1→5), the two SLAs, questions, sweep ranges. **→ defines the testbench and acceptance criteria.** |

## Models — what gets simulated

Both pipelines reduce to **two cascaded M/M/c queues** (worker pool → ES pool),
pure queueing, no USL (I/O-bound workers, `alpha = beta = 0`). Each lives in its
own folder with its own `MODEL.md`:

- [`model1_ingestion/`](model1_ingestion/) — SLA: price change queryable within 10 s.
- [`model2_queries/`](model2_queries/) — SLA: p95 response < 500 ms, with 5× burst episodes.

## How to run

Run each pipeline from its own folder:

```sh
# Ingestion
cd model1_ingestion
pip install -r requirements.txt
python server_sim.py    # smoke test
python sweep.py         # ~2 min → sweep_results.json
python plot_sweep.py    # → sweep_plot.png

# User queries
cd ../model2_queries
pip install -r requirements.txt
python server_sim.py    # smoke test + survivorship-bias check
python sweep.py         # ~3 min → sweep_results.json
python plot_sweep.py    # → sweep_plot.png
```

## Output

- `model1_ingestion/sweep_plot.png`, `model2_queries/sweep_plot.png` — three-panel plots.
- [`SIM_REPORT.md`](SIM_REPORT.md) — full results, per-year worker recommendations, interpretation.

## Result — what it shows

**Ingestion:** the 10 s SLA holds across the whole Year 1→5 horizon. Required
workers grow roughly linearly — **~0.65 worker per added reseller**, reaching
60–80 workers at Year 5. The ES pool (200 connections) is never the bottleneck;
the worker pool always saturates first.

**Queries:** p95 < 500 ms is achievable (≈ 50 workers at base 100 req/s), **but
provisioning must target the 5× burst peak, not the average** — the worker count
needed to survive bursts is 2–3× the steady-state requirement.

**Both pipelines** show the survivorship-bias effect: under overload, raw
latency-of-successes stays low while effective latency pegs at the SLA. Monitor
`success_rate` and `eff_latency_p95`, never raw p95 alone.

## Lesson

For bursty workloads, provision against the burst peak, not the average — the
worker count needed to hold the SLA through a 5× burst is 2–3× the steady-state
requirement, so capacity sized for the mean will miss the SLA exactly when load
matters most. And under overload, raw latency-of-successes looks healthy while
real users time out: watch `success_rate` and effective p95, not raw p95.

*In plain terms:* real traffic often arrives in short, sharp bursts — a sale, an
evening peak — several times the normal rate. If you size capacity for the
average, you'll hit your response-time target almost always and miss it exactly
during the bursts, when it matters most; here, surviving a 5× burst needs 2–3×
the workers the normal load alone would require. The example also re-shows a
measurement trap: during overload the response time of the requests that
*succeeded* still looks fine, because the ones that timed out vanish from the
average. Track the fraction of requests that completed and a latency that
includes the timeouts, not the latency of the survivors.

## Files

| File | What it is |
|---|---|
| `ARCHITECTURE.md`, `REQUIREMENTS.md` | inputs (see above) |
| `model1_ingestion/`, `model2_queries/` | the two models — each has `MODEL.md`, `server_sim.py`, `sweep.py`, `plot_sweep.py`, `sweep_plot.png` |
| `SIMULATION_PLAN.md` | audit answers + MODEL drafts + build sequence (downstream planning artifact) |
| `SIM_REPORT.md` | results and conclusions for both pipelines |
