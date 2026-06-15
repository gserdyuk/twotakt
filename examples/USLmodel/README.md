# USLmodel — server degradation under load

The baseline exhibit of the methodology: a single CPU-bound server whose
throughput **rises, peaks, then declines** as load grows — the curve real
servers show and a pure M/M/1 model cannot reproduce.

## Input — what you give

| Document | Role |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | How the system is built (thread-per-request server, single CPU, CPU/IO phases). **→ defines the model.** |
| [`REQUIREMENTS.md`](REQUIREMENTS.md) | Questions, required behaviour, SLA, sweep range. **→ defines the testbench and acceptance criteria.** |

## Model — what gets simulated

CPU is a `Resource(capacity=1)`; each request holds it during bursts, releases
it during I/O. Burst time is inflated by the USL factor `1 + α(N−1) + β·N(N−1)`
at the current in-flight count N. Full spec in [`MODEL.md`](MODEL.md).

## How to run

```sh
pip install -r requirements.txt
python server_sim.py    # smoke test — should report success_rate ≈ 1.0
python sweep.py         # sweeps arrival rate 1→20 rps → sweep_results.json
python plot_sweep.py    # → sweep.png (throughput / success rate / latency)
```

## Output

- `sweep.png` — three panels: throughput vs ideal, success rate, effective vs ok-only latency.
- [`SIM_REPORT.md`](SIM_REPORT.md) — full results, interpretation, recommendations.

## Result — what it shows

Three regimes appear, as theory demands: **linear scaling** (≤ 5 rps), a
**saturation knee** (peak ≈ 5.3 rps), then **thrashing collapse** past 6 rps —
throughput *falls* rather than plateaus (the USL β term). Safe operating point
is ≤ 4 rps; beyond the knee a system like this needs admission control. The
report also shows why ok-only latency lies under overload (survivorship bias)
and why effective latency is the decision-grade metric.

## Lesson

Real servers don't plateau at saturation — they can *collapse* past it (the USL
coherency cost), so the safe operating point sits well below peak throughput.
And under overload, latency-of-successful-requests is a biased, misleading
metric: track effective latency and success rate together, or a dashboard will
report a healthy system while goodput has already gone over the cliff.

*In plain terms:* as you send a server more requests per second, the work it
completes rises until it saturates — and you'd expect it to then hold flat at
that peak. It doesn't: past that point throughput can actually *fall*, because
every extra request in flight slows down all the others (they fight over locks,
caches, and the CPU). So run well below the peak, not at it. The second trap is
in the metrics: under overload, if you look only at the response time of the
requests that *succeeded*, the number looks fine — the slow ones timed out and
dropped out of the sample, so you're measuring only the survivors. Watch the
fraction that completed and a latency that counts the timed-out ones, or your
dashboard will look green while almost nothing useful is getting through.

## Files

| File | What it is |
|---|---|
| `ARCHITECTURE.md`, `REQUIREMENTS.md` | inputs (see above) |
| `MODEL.md` | the audited model spec — source of truth |
| `server_sim.py` | SimPy model + `Config` |
| `sweep.py` | parameter sweep → `sweep_results.json` |
| `plot_sweep.py` | plotting → `sweep.png` |
| `SIM_REPORT.md` | results and conclusions |
