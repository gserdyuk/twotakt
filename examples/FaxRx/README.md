# FaxRx — where should a system fail under burst?

A worldwide fax-reception service: PSTN/SIP channels → processing workers →
optional OCR (50 % of faxes) → email delivery. The exhibit of failure *mode* over
failure *rate* — sizing the system not only for how much it carries, but for
**where it breaks** when a burst exceeds capacity.

## Input — what you give

| Document | Role |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Topology (regional PoPs, SIP/T.38), components, channel sizing, signal flow. **→ defines the model.** |
| [`REQUIREMENTS.md`](REQUIREMENTS.md) | Target scale, the two SLAs (10 min / 1 hour), questions, sweep. **→ defines the testbench and acceptance criteria.** |

## Model — what gets simulated

SIP channels are an **Erlang B** resource — a call arriving when all channels are
busy is rejected immediately (busy signal), no queue. Processing workers are I/O-bound
M/M/c; OCR workers are CPU-bound M/M/c with USL degradation. Full spec in [`MODEL.md`](MODEL.md).

## How to run

```sh
pip install -r requirements.txt
python server_sim.py    # smoke test — should report success_rate ≈ 1.0
python sweep.py         # 3 architectures × 11 burst levels → sweep_results.json
python plot_sweep.py    # reads sweep_results.json → sweep.png
```

## Output

- `sweep_results.json` — 33 runs (3 architectures × 11 burst levels).
- `sweep.png` — three panels (success rate / PSTN block rate / p95 eff latency vs burst), one curve per architecture.
- [`SIM_REPORT.md`](SIM_REPORT.md) — full results table, interpretation, recommendations.

## Result — what it shows

Three architectures under rising burst expose **two failure modes**:

- **A — small front door** (`sip=270`): Erlang B rejects more calls as burst grows
  (0.8 % → 45 %), but everything admitted is served on time (p95 flat ≈ 285 s). It
  fails *fast and honestly* — a busy signal. The undersized door **is** admission control.
- **B — open front door** (`sip=2565`): blocking vanishes, but the backlog drowns OCR;
  p95 climbs to the 1-hour SLA ceiling and failures become silent timeouts. At 10× burst
  its success (0.52) is *no better than A's* (0.54) — the fax was accepted, then died an
  hour later. **Admitting work you cannot finish converts fast, honest failures into slow,
  hidden ones without improving success rate.**
- **C — scale OCR 5×**: helps mid-range, but at 10× still 5× worse latency than A.
  Capacity scaling delays the slow-failure mode; it does not change its nature.

## Lesson

Evaluate an architecture by *where* it fails, not only by how much it carries.
Two designs with the same success rate can deliver opposite user experiences —
a fast, honest busy signal versus a fax silently dropped an hour later. A
bounded front door is admission control, not a deficiency: admitting work you
cannot finish converts fast, honest failures into slow, hidden ones without
improving the success rate.

*In plain terms:* when demand spikes past capacity, a system has to turn work
away somewhere. A small "front door" (few phone lines) rejects extra callers
instantly with a busy signal — they know at once and can redial. A wide-open
front door accepts every call, but the backlog then overwhelms the processing
stage, and faxes are silently dropped an hour later, after the sender already
believed they'd gone through. At a 10× burst both designs deliver the same
fraction of faxes — but one fails fast and visibly, the other slowly and
invisibly, which is far worse for the user. So judge a design by *where* it
breaks, not only by how much it carries; a deliberately limited entry point is a
feature, because accepting work you can't finish only hides the failure.

## Files

| File | What it is |
|---|---|
| `ARCHITECTURE.md`, `REQUIREMENTS.md` | inputs (see above) |
| `MODEL.md` | the audited model spec — source of truth |
| `server_sim.py` | SimPy model + `Config` (Erlang B + M/M/c + USL OCR) |
| `sweep.py` | parameter sweep → `sweep_results.json` |
| `plot_sweep.py` | plotting (reads `sweep_results.json`) → `sweep.png` |
| `SIM_REPORT.md` | results and conclusions |
