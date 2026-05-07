# {ProjectName} — Simulation Report

> Template. Replace `{...}` placeholders. Write this document after
> sweep plots exist and are validated (Phase 13). The report must
> stand alone — a reader who has not seen the code or the audit should
> be able to understand the conclusions and their limits.

---

## Context

{One paragraph: what real system was modelled, how many models, what
capacity-planning questions were asked. Link to MODEL.md files.}

**Models:**
- [{ModelName1}]({path/to/model1/MODEL.md}) — {one-line summary}
- [{ModelName2}]({path/to/model2/MODEL.md}) — {one-line summary}

---

## Parameters and assumptions

> Every number must be justified. Numbers derived from measurement get
> a source. Numbers that were assumed get an explicit "Assumed:" label
> and a risk statement.

| Parameter | Value | Source / Justification |
|---|---|---|
| `{param}` | {value} | {measured from X / Assumed: rationale} |

**Key risks from assumptions:**
- If `{param}` is {N}× higher in production, {consequence}.
- {Add one row per assumption whose 2× error would flip a verdict.}

---

## Graph interpretation

### {ModelName1}

![]({path/to/model1/sweep_plot.png})

**Panel 1 — Throughput.**
{What the panel shows. Where curves diverge from ideal. What that means.}

**Panel 2 — Success rate.**
{Where success rate drops below 99%. What causes it. Which worker count holds.}

**Panel 3 — Latency p95 (log scale).**
{Where eff p95 crosses SLA. How large is the gap between solid (eff) and
dashed (raw) lines — this is survivorship bias made visible.}

### {ModelName2}

![]({path/to/model2/sweep_plot.png})

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
{One paragraph on which metrics to watch in production. Which metric
crossing which threshold is the first signal of the system approaching
the knee identified in the sweep.}

---

## Reproduction

```bash
# {ModelName1}
cd {path/to/model1}
pip install -r requirements.txt
python server_sim.py    # smoke test
python sweep.py         # generates sweep_results.json
python plot_sweep.py    # generates sweep_plot.png

# {ModelName2}
cd {path/to/model2}
# ... same pattern
```
