# Phase 11 — Extension Audit

When the user wants to add a new component to an existing model
(database, cache, replica, scheduler, downstream service), this is a
**new audit**, not a code change. It is shorter than the Phase 1 audit
because the parent model has already established the system, scarcity
landscape, request lifecycle, and degradation framework — the
extension only has to describe what is being added on top.

Like the Phase 1 audit, this is a **gate**. Do not start coding the
extension until the user has approved the extension audit.

## Structural rules (non-negotiable)

1. **Copy the parent example folder; do not edit in place.** The
   extended model lives in a new sibling folder (e.g. `USLDBmodel`
   from `USLmodel`). Each example must remain a clean exhibit of one
   idea.
2. **The new MODEL.md describes only the diff.** It opens with a
   reference to the parent ("This model is a strict extension of
   X. Read X/MODEL.md first.") and then describes only what is added
   or changed. Do not duplicate the parent's content.
3. **The code change is surgical.** New `Config` fields, new
   `Resource` on `Server`, new acquire–hold–release block in
   `_serve`. If the change requires modifying the existing code more
   broadly than that, the extension is doing too much — split it.

## The questions

### EQ1 — What is being added, in real-world terms?

A connection pool, a cache, a replica, a scheduler, an external
service. One paragraph describing the real component.

### EQ2 — What models of this component are in scope?

For most components there are several modelling traditions, each
emphasising a different failure mode. For a database the menu is:

- **Connection pool** (model #1) — bounded concurrency, FIFO queue.
- **USL on the database** (model #2) — concurrent queries slow each
  other down.
- **Cache hit / miss** (model #3) — bimodal query duration.
- **Read / write split** (model #4) — different concurrency for
  reads vs writes.
- **Disk I/O queue** (model #5) — bounded IOPS.
- **WAL fsync bottleneck** (model #6) — single serializing path for
  writes.

For caches, schedulers, replicas there are analogous menus. Always
present the menu and let the user pick the **simplest** model that
captures the failure mode they care about. They can always extend
later via another extension audit.

Write the chosen model and rejected alternatives into the new
MODEL.md.

### EQ3 — Where in the request lifecycle does the new component sit?

Before the CPU phases? After? Wrapping I/O? Replacing a phase? Each
placement has different dynamics. For a database, "at the end" (commit
after work) and "in the middle" (read-then-render) give different
queueing behaviour. The user must choose explicitly.

### EQ4 — What new parameters does this component introduce?

New `Config` fields, with defaults. Same rule as Phase 5: every
magic number lives on `Config`.

### EQ5 — What is the theoretical throughput ceiling of the new component?

Compute it explicitly. For a connection pool:
`pool_size / mean_query_time` queries/sec. Compare it to the
parent model's ceiling (typically the CPU's). The interesting
configurations are the ones where the new component's ceiling is
**comparable to or below** the parent's — those are the ones where
the new component actually changes the dynamics.

If the new component's ceiling is far above the parent's, default
parameters will leave the parent's bottleneck dominant and the
extension will look invisible in the sweep. Either pick parameters
that make the new component bind, or run a parameter sweep over the
new component's defining parameter (Phase 12) so the binding regime
becomes visible.

### EQ6 — What new failure modes appear?

The parent model had one or more bottlenecks. The extension typically
adds another. Articulate explicitly: "The system can now fail
because of CPU saturation OR pool exhaustion OR cache miss storm,
in this order of likelihood under default parameters."

### EQ7 — What new metrics or plot panels are needed?

If the extension introduces a new failure mode (e.g. "rejected
because pool was full"), it needs its own outcome category and its
own appearance in the plot. Update the metric-checklist application
in Phase 8 accordingly.

## After the extension audit

Write the new `MODEL.md` (referencing the parent), then proceed to
Phase 4 — but with the constraint that the code change is a surgical
diff against the parent, not a fresh build.
