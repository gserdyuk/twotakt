# twotakt — Concept & Direction

> Vision-level document: the problem, the bet, the differentiator, and the
> calibration direction. The **current state** (structure, phases, skills) is
> deliberately not described here — it is owned by `README.md` and
> `skills/*/SKILL.md`. (Rewritten 2026-07-10 from the v2 concept;
> current-state sections dropped, they had rotted twice.)

## Vision

**A disciplined way to build discrete-event simulations of systems under load.**
*Simulate before you build. Understand before you scale. Calibrate before you trust.*

twotakt is a methodology, a set of Claude skills, and a growing library of
worked examples for building simulations of systems that degrade under
concurrent load. It enables architects and engineers to validate capacity
assumptions, identify bottlenecks, and answer "what if" questions — grounded
in discipline, not assumptions.

## The Problem

Architects make capacity decisions based on intuition and experience.
Load testing validates decisions too late — after the system is built.
Existing simulation tools are too complex and too expensive for everyday
architectural decisions. And ad-hoc simulation done without methodology
produces models that encode whatever degradation the implementation
accidentally produced — confidently misleading.

## The Insight

A simulation model that is (a) built through a disciplined audit-first
protocol, and (b) calibrated against real metrics where they exist, can be
trusted. Once trusted, it can be used to explore futures that don't exist yet.

Discipline catches the modelling mistakes (mis-chosen scaling laws,
survivorship-biased metrics, magic numbers in code). Calibration catches the
parameter mistakes (assumed numbers that don't match reality). Together they
turn a simulation from "interesting toy" into "decision-grade evidence".

## Key Differentiator

**Reverse simulation.** Instead of building a model from assumptions, twotakt
builds it from real observations of an existing system, then uses the
calibrated model to extrapolate.

This breaks the adoption barrier: trust comes first, exploration follows.
See *Reverse Simulation* below for the planned calibration mechanism.

## Competitive Landscape

| Tool | What it does | Gap |
|------|-------------|-----|
| Gatling, k6, JMeter | Load test existing systems | Requires built system |
| AnyLogic, Simio | Enterprise simulation | Complex, expensive, not LLM-native |
| APM (Datadog, Prometheus) | Observe what happens | No "what if" capability |
| Architecture diagrams | Model structure | No behavioral simulation |

**The gap:** nothing exists between "architect draws a diagram" and "system
under load". twotakt lives there.

## Why Now

- Modern LLMs make working with SimPy directly tractable for users without
  deep prior knowledge of the library, removing the need for a heavy
  abstraction layer.
- Methodology compiled into a skill becomes a reproducible protocol rather
  than tribal knowledge.
- Discrete-event simulation has been mature for decades — what was missing
  was a low-friction way to apply it correctly.
- The observability stack of a typical modern system (Prometheus, CloudWatch,
  OpenTelemetry, APM) is rich enough to drive calibration automatically.

## Positioning

Not a load tester — those test what exists.
Not an APM — those observe what happens.
Not a generic simulation IDE — those hide the model behind abstractions.

twotakt simulates what hasn't happened yet — and (with calibration) does so
credibly.

---

## Reverse Simulation — the calibration direction

The strongest objection to any simulation is "yes, but does it match
reality?" Reverse simulation answers this objection by inverting the
workflow: instead of asserting a model and hoping it's right, we observe
reality and fit the model to reproduce it. Once the model demonstrably
reproduces *what is*, extrapolations to *what could be* carry the same
credibility.

This is what makes the difference between a simulation that informs a
discussion and a simulation that supports a decision.

### Calibration data sources we plan to support

Different systems expose different telemetry. The plan is to support the
calibration sources already present in most production environments, roughly
in this order of priority:

1. **Application logs.** The lowest common denominator. Per-request
   timestamps and durations are enough to derive the arrival distribution,
   end-to-end latency distribution, and (with enough volume) the
   service-time distribution.
2. **Prometheus / Grafana / OpenMetrics.** Standard for self-hosted
   infrastructure. Provides RPS, latency percentiles, CPU and memory
   utilization, queue depths over time. The richest commonly-available
   calibration source.
3. **AWS CloudWatch and cloud-native analytics.** For managed services where
   Prometheus is not available. Similar shape of data, different ingestion path.
4. **APM (Datadog, New Relic, Honeycomb).** Transaction traces with span
   timings and service dependencies. Particularly useful for calibrating
   multi-component models where the request lifecycle spans several services.
5. **Probes.** Synthetic load runs aimed specifically at gathering
   calibration data when production observability is insufficient.
   Essentially short load tests whose output feeds the model rather than
   producing a verdict directly.

### How calibration integrates with the methodology

Calibration extends the audit-first protocol in three places (stated here by
role, not by phase number — the phase layout is owned by the skill):

- **In the audit** — a new question: *"Do you have observed metrics from a
  similar production system that the model should reproduce?"* If yes, the
  data source becomes part of the spec and the calibration scenario is
  documented in `MODEL.md`. If no, the model is documented as uncalibrated
  and that limitation is stated explicitly, so downstream conclusions carry
  the appropriate caveat.

- **In V&V** — if calibration data exists, the model must reproduce the
  calibration scenario within a stated tolerance before any extrapolation
  result is trusted. The deviation between simulated and observed becomes a
  first-class metric, plotted alongside throughput and latency.

- **As its own gate** — a calibration step between verification and
  behavioral analysis: run the model on the observed scenario, report the
  per-metric deviation, iterate on `Config` parameters until the deviation
  falls within tolerance. Only then does extrapolation begin.

### Roadmap

- **Now.** Forward simulation only. Parameters chosen from measurement,
  design decisions, or documented assumptions (per the parameter-sources
  discipline in the skill).
- **Next.** Prometheus-based calibration. Pull historical metrics for a
  defined window, derive arrival rate and latency distributions, fit the
  corresponding `Config` parameters, report deviation. Prometheus first
  because it covers the largest share of self-hosted production environments.
- **Later.** Application-log calibration, which removes the
  observability-stack prerequisite. Followed by APM-trace calibration for
  multi-component models.
- **Later still.** CloudWatch and managed-service analytics for cloud-native
  deployments. Probes as a fallback when observability data is missing or
  insufficient.
- **Eventually.** Continuous calibration — the model stays in sync with
  production by re-fitting periodically: the **living model**. This is what
  makes capacity-planning dashboards trustworthy as the underlying system
  evolves.

Each of these steps is itself an extension audit of the methodology —
a worked example of the protocol applied to twotakt's own evolution.
