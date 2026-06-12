# {ProjectName} — Simulation Report

> Template. Replace `{...}` placeholders. Write this document after sweep
> plots exist and are validated (Phase 10). The report must stand alone —
> a reader who has not seen the code or the audit should be able to
> understand the conclusions and their limits. If a reader opens only one
> file in the project, it should be this one.

---

**Date:** {YYYY-MM-DD}
**Data source:** {committed sweep results / re-run of committed code, date.
For stochastic models state: r = {N} replications per point, warm-up discarded,
values reported as mean ± 95% CI (`modeling-jain/templates/ci_calc.py`).}

## Context

{One paragraph: what real system was modelled, how many models, and —
explicitly — **what question the simulation answers**. A report without a
question is a data dump. Link to MODEL.md files.}

**Models:**
- [{ModelName1}]({path/to/model1/MODEL.md}) — {one-line summary}
- [{ModelName2}]({path/to/model2/MODEL.md}) — {one-line summary}

---

## Parameters and assumptions

> Every number must be justified. Numbers derived from measurement get a
> source. Numbers set by the architect or requirements get "Design decision".
> Numbers that were assumed get an explicit "Assumed:" label and a risk
> statement. (Three valid sources — see simpy-protocol Phase 5.)

| Parameter | Value | Source / Justification |
|---|---|---|
| `{param}` | {value} | {measured from X / design decision: Y / Assumed: rationale} |

**Key risks from assumptions:**
- If `{param}` is {N}× higher in production, {consequence}.
- {One row per assumption whose 2× error would flip a verdict.}

---

## Sweep design

{What was varied, over what range, and why that range answers the question
from Context. One short paragraph or a small table.}

---

## Graph interpretation

### {ModelName1}

![]({path/to/model1/sweep_plot.png})

**Panel 1 — Throughput.**
{What the panel shows. Where curves diverge from ideal. What that means.}

**Panel 2 — Success rate.**
{Where success rate drops below the business threshold. What causes it.}

**Panel 3 — Latency p95 (log scale).**
{Where eff p95 crosses SLA. How large is the gap between solid (eff) and
dashed (raw) lines — survivorship bias made visible.}

> Interpret **mechanisms, not just shapes**: say *why* the curve bends, not
> only where. Call out anything counterintuitive — that is where the model
> earns its keep.

### {ModelName2}

{Same structure as above.}

---

## Requirements

> Three verdicts only: **Feasible**, **Feasible with conditions**, **Not feasible**.
> "Feasible with conditions" requires the condition stated explicitly in the same cell.

| Requirement | SLA | Verdict | Minimum resource | Notes |
|---|---|---|---|---|
| {Requirement} | {SLA} | **Feasible** | {N workers at Year X} | {any caveat} |
| {Requirement} | {SLA} | **Feasible with conditions** | {N workers} | Condition: {state it} |
| {Requirement} | {SLA} | **Not feasible** | — | {what would need to change} |

---

## Sensitivity and risks

> Which assumptions, if wrong by 2×, would flip a Feasible verdict to
> Not feasible?

| Assumption | Current value | 2× scenario | Impact |
|---|---|---|---|
| `{param}` | {value} | {2× value} | {consequence on verdict} |

**Monitoring recommendation:**
{Which production metrics to watch. Which metric crossing which threshold is
the first signal of the system approaching the knee identified in the sweep.}

---

## Limitations

{What the model deliberately excludes — link to the corresponding section of
MODEL.md rather than repeating it. Name the one exclusion most likely to be
the next extension, and what question it would answer.}

---

## Reproduction

```bash
# {ModelName1}
cd {path/to/model1}
pip install -r requirements.txt   # versions pinned
python server_sim.py    # smoke test (fixed seed from Config)
python sweep.py         # generates sweep_results.json (r replications per point, run Config embedded)
python plot_sweep.py    # generates sweep_plot.png
```
