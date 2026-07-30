# LinkedIn post — article #2 (bottleneck is a regime)

> **Type: reasoning** — corpus: publication draft (EN warm-up post) · born 2026-07-30

*Second post of the warm-up series (#3 → #2 → #1). Standalone story; repo link goes
in the first comment (LinkedIn down-ranks in-body links — same mechanic as the #3
posts). Companion image: `docs/linkedin_post_2_sweep.png` — 1080x1350 (4:5 portrait,
the mobile-friendly ratio), panels stacked and the hook burned into the image, so it
reads while scrolling. The article's own wide version lives in `articles/img/`.*

---

min(10, 20) = 6.

A server sustains 10 requests/s. Its database pool sustains 20. Capacity math says
the system is good for 10.

The simulation dies at 6 — with no component anywhere near its own limit.

We blamed the single DB connection first. Obvious suspect: one connection, requests
serialize, waiting burns the deadline. Wrong — eight connections die at exactly the
same load.

The real mechanism is a feedback loop. Requests in flight make the CPU slower
(contention — USL). A slower CPU keeps more requests in flight (Little's law). The
loop feeds itself, and past a computable ceiling it stops converging: queues grow,
and the system simply stops coping. That ceiling — a closed-form fixed point — is
7.2 rps for this system. Not 10.

And the pool? Whether it is ever the bottleneck at all is a regime switch with a
computable threshold: the pool binds only once a single query takes longer than the
pool size divided by that ceiling — 0.14 s for one connection. Our query took 0.05 s,
so the pool was invisible at any size. Make it 0.3 s and the pool dominates: the same
system now collapses at 3 rps. Same components. Different regime. Different
bottleneck.

A bottleneck is not a property of a component. It is the conditions the system puts
that component in — and the influence runs both ways.

Model, spec and every number are open and reproducible (SimPy, 10 seeds per point) —
link in the first comment.

---

*First comment:* The model, its spec, and all sweeps:
https://github.com/gserdyuk/twotakt/tree/main/examples/USLDBmodel
