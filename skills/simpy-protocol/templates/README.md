# <Name> — <one-line description of the idea this example exhibits>

<1–2 sentences: what this model demonstrates and why it is interesting —
the single takeaway a reader should leave with.>

## Input — what you give

| Document | Role |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | How the system is built (components, pools, queues, flows). **→ defines the model.** |
| [`REQUIREMENTS.md`](REQUIREMENTS.md) | Questions, required behaviour, SLA, sweep range. **→ defines the testbench and acceptance criteria.** |

## Model — what gets simulated

<Brief prose: the SimPy primitives and the resource structure — e.g. "two
cascaded M/M/c queues", "CPU as Resource(capacity=1) with a USL multiplier".
Full spec in [`MODEL.md`](MODEL.md).>

## How to run

```sh
pip install -r requirements.txt
python server_sim.py    # smoke test — should report success_rate ≈ 1.0
python sweep.py         # runs the sweep → sweep_results.json
python plot_sweep.py    # → sweep.png
```

## Output

- `sweep.png` — <what the panels show>.
- [`SIM_REPORT.md`](SIM_REPORT.md) — full results, interpretation, recommendations.

## Result — what it shows

<The headline finding(s): where the bottleneck is, peak throughput, where the
SLA breaks, the safe operating point. Pull these from SIM_REPORT.md — do not
invent numbers. If the simulation has not been run yet, say so plainly instead
of inventing a result.>

## Lesson

<The one transferable systems insight a reader takes away — 1–2 sentences, stated
precisely (domain terms are fine here).>

*In plain terms:* <the same lesson re-told for an outside reader who has not read
the report — define the jargon, explain the mechanism, say why it matters.>

<Write the lesson standalone: do not assume the reader has seen the other
examples, and do not cross-link them. If your lesson overlaps another example's,
that is fine — state it in full anyway. Omit this section only if the example
genuinely carries no general lesson beyond being a worked case.>

## Files

| File | What it is |
|---|---|
| `ARCHITECTURE.md`, `REQUIREMENTS.md` | inputs (see above) |
| `MODEL.md` | the audited model spec — source of truth |
| `server_sim.py` | SimPy model + `Config` |
| `sweep.py` | parameter sweep → `sweep_results.json` |
| `plot_sweep.py` | plotting → `sweep.png` |
| `SIM_REPORT.md` | results and conclusions |
