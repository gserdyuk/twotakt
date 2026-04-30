# twotakt — Concept

## Vision

**Natural language bridge to discrete-event simulation.**
*Simulate before you build. Understand before you scale.*

twotakt connects real system metrics to discrete-event simulation models, enabling architects and engineers to validate capacity assumptions, identify bottlenecks, and answer "what if" questions — grounded in reality, not assumptions.

---

## The Problem

Architects make capacity decisions based on intuition and experience. Load testing validates decisions too late — after the system is built. Existing simulation tools are too complex and too expensive for everyday architectural decisions.

---

## The Insight

A simulation model calibrated against real metrics can be trusted. Once trusted — it can be used to explore futures that don't exist yet.

---

## Key Differentiator

**Reverse simulation** — instead of building a model from assumptions, twotakt builds it from real observations.

1. Feed real metrics (latency, throughput, CPU) from existing system
2. twotakt constructs a SimPy model that reproduces those numbers
3. Model is verified against reality — architect trusts it
4. Now ask: *"What happens at 10x load?"* — and believe the answer

This breaks the adoption barrier: trust comes first, exploration follows.

---

## Competitive Landscape

| Tool | What it does | Gap |
|------|-------------|-----|
| Gatling, k6, JMeter | Load test existing systems | Requires built system |
| AnyLogic, Simio | Enterprise simulation | Complex, expensive, not Claude-native |
| APM (Datadog, Prometheus) | Observe what happens | No "what if" capability |
| Architecture diagrams | Model structure | No behavioral simulation |

**The gap:** nothing exists between "architect draws a diagram" and "system under load." twotakt lives there.

---

## Architecture

```
twotakt-probe
L-- connects to Prometheus, Datadog, CloudWatch, OpenTelemetry
L-- collects latency, throughput, resource utilization

twotakt-core
L-- builds discrete-event SimPy model from metrics
L-- validates model against real observations
L-- exposes model for querying

twotakt-mcp
L-- MCP server for Claude Code
L-- natural language interface to the model
L-- answers "what if" questions
L-- iterates on scenarios
```

---

## User Journey

1. Architect runs `twotakt-probe` against existing system
2. twotakt builds and validates a SimPy model
3. Architect asks Claude: *"What happens at 10x load?"*
4. twotakt simulates, explains, recommends

---

## Why Now

- LLMs can translate domain descriptions to simulation models
- OpenTelemetry standardizes metric collection
- MCP enables Claude to use tools natively
- SimPy is mature, lightweight, Python-native

---

## Positioning

Not a load tester — those test what exists.
Not an APM — those observe what happens.
twotakt simulates what hasn't happened yet.
