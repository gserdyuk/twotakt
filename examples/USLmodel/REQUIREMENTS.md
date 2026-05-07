# USLmodel — Educational Requirements

This is an educational example. The "requirements" below define what questions
the model is meant to answer and what behaviour must be observable in the results.

## System under study

An HTTP server with thread-per-request architecture, single CPU, no external
dependencies. Representative of any CPU-bound service where in-flight requests
compete for a shared compute resource.

## Questions this model must answer

1. At what arrival rate does the server saturate?
2. Does throughput decline past saturation (USL thrashing), or merely plateau?
3. How do α (linear contention) and β (quadratic coherency interference) affect
   the saturation point and the depth of post-saturation decline?

## Required behaviour

| Load regime | Expected throughput | Expected latency |
|---|---|---|
| Low (< 50% of saturation) | throughput ≈ arrival rate | p50 ≈ sum of CPU + I/O phase means |
| At saturation | throughput plateaus at peak | p99 rising, some SLA timeouts |
| Overload | throughput falls (USL effect) | SLA timeouts dominant |

All three regimes must be visible in a sweep over arrival rate. If any regime
is missing, the model is mis-tuned.

## SLA

p99 < 10 seconds at load ≤ 50% of the saturation point.

## Sweep

Arrival rate from 1 to 20 rps. Secondary parameter: α and β values to show
the contrast between pure M/M/1 (α=β=0) and USL degradation (α>0 or β>0).
