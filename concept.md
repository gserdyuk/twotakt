# twotakt / Concept

## Vision

Natural language bridge to discrete-event simulation.
Simulate before you build. Understand before you scale.

twotakt connects real system metrics to discrete-event simulation models, enabling architects and engineers to validate capacity assumptions, identify bottlenecks, and answer "what if" questions � grounded in reality, not assumptions.

## The Problem

Architects make capacity decisions based on intuition and experience. Load testing validates decisions too late � after the system is built. Existing simulation tools are too complex and too expensive for everyday architectural decisions.

## The Insight

A simulation model calibrated against real metrics can be trusted. Once trusted � it can be used to explore futures that don't exist yet.

## Architecture

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

## User Journey

Architect runs twotakt-probe against existing system
twotakt builds and validates a SimPy model
Architect asks Claude: "What happens at 10x load?"
twotakt simulates, explains, recommends

## Why Now

LLMs can translate domain descriptions to simulation models
OpenTelemetry standardizes metric collection
MCP enables Claude to use tools natively
SimPy is mature, lightweight, Python-native

## Positioning

Not a load tester � those test what exists.
Not an APM � those observe what happens.
twotakt simulates what hasn't happened yet.