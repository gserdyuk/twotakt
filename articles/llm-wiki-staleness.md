# Staleness is solved by not promising currency

> **Type: record** — publication: frozen once published · born 2026-07-17

*English long form of the campaign published 2026-07-13: a field-report comment in
[Karpathy's "LLM Wiki" gist
thread](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and a
LinkedIn note. Expanded here with the mechanics in full and the first objection
from the comments — which produced the best formulation of the whole idea.*

---

Everyone is building LLM wikis. Karpathy's "LLM Wiki" gist — a pattern for
LLM-maintained knowledge bases (markdown pages, an index, a log, a schema file) —
collected 5,000+ stars and a comment thread full of implementations. Read past the
self-promotion, and the substantive comments converge on one pain: **staleness**.
Summaries drift from their sources. One new document cascades into dozens of stale
pages. Two pages assert conflicting facts and nobody notices.

And every proposed fix in the thread is *tooling*: validators, freshness states,
contradiction detectors, source hashes, regression tests for knowledge.

The funny thing: our simulation-methodology repo
([twotakt](https://github.com/gserdyuk/twotakt)) converged on Karpathy's pattern
independently — same index file, same append-only log, same schema file — but we
arrived from a different direction: research reproducibility, not personal
knowledge management. And from that side, the staleness answer turned out to be
**discipline, not tooling**. Three mechanics.

## 1. Document passports

Every knowledge document opens with one immutable header line:

```
> Type: reasoning | register | journal | record — <regime> · born <date>
```

It tells the reader — human or LLM — how to treat the file before reading a single
content line: is it append-only? may it contradict newer documents? is it
synchronized with anything? A `journal` accumulates dated entries and never
retracts them. A `register` holds pointers, never content. A `reasoning` doc is a
dated snapshot of thinking — free to be superseded. A `record` is frozen at
publication.

The trick is *where* the ambiguity gets resolved. Tooling tries to prevent
staleness at **write** time — keep everything current, detect every drift. A
passport resolves it at **read** time: the page openly declares what kind of truth
it holds and from when. A dated snapshot cannot be stale — it never promised to be
current.

## 2. The corpus/surface split

We stopped fighting staleness for 90% of our documents — deliberately.

The **corpus** (the log, the findings register, reasoning docs, article drafts)
*accumulates*: append-only, dated, internal contradictions are history and are
never "fixed". It is periodically *compacted* — reviewed, merged, rewritten as a
new version with the previous one archived — rather than patched in place.

Only a deliberately small **surface** (README, the schema file, one-pagers)
promises currency — and only the surface is ever synchronized.

We paid for this lesson three times: three current-state documents died of rot —
each written as "the current architecture", each stale within weeks — before we
generalized the rule. **Staleness is solved by not promising currency — except
where you can actually afford the promise.** The whole synchronization budget goes
to a surface small enough to actually keep in sync.

## 3. Claims before concepts

The synthesis layer is a register of numbered one-screen claims (F1, F2, …), each
pointing to its long form. A refinement is a *new* claim referencing the old one
("refines F9", "supersedes F14") — never an edit. Concept-level documents only
*graduate* out of claim clusters that keep recurring.

This structurally dissolves a failure mode reported in the thread after a month of
real use: in a flat wiki, a life-scale theme and a tactical detail sit at the same
level, and importance disappears. Here importance is **measured, not assigned**: a
concept with ten claims under it is heavyweight; one with a single claim is light.
No author decides what matters — the cluster size does.

## The objection, and the answer worth keeping

The first substantive objection to the published note: *"Do you actually expect
humans to read automatically maintained wikis?"*

The answer produced the formulation that now summarizes the whole approach. The
corpus's primary reader is the LLM — its job is context transfer between sessions;
humans are the second audience. And the human reads at **write** time: every claim
is born inside a reviewed conversation, so the wiki records what a human already
judged.

**Machine-drafted, human-gated. The reading you're skeptical about already
happened — once, when it counted.**

This is the same gate we use for generated code (the spec is approved by a human,
the code is verified against it) — one discipline, two kinds of artifact.

## What we do not claim

A measured boundary from the thread deserves repeating: a wiki page pays for
itself only when it *compresses facts scattered across many sources*. Mirrors of
individually greppable files are negative value — a copy is a future
contradiction. That experiment matches our design choice exactly: no concept pages
for things the repo already states once, greppably.

None of this removes the need for verification where verification is affordable —
our own harness exists precisely because "the model computes prettily" is not "the
model computes correctly". The claim is narrower: for a knowledge base, most
staleness machinery becomes unnecessary once each page honestly declares what kind
of truth it holds, and the only pages promising currency are the ones you can
afford to keep current.

---

*The mechanics live in the twotakt repo — CLAUDE.md (the schema and constraints),
INDEX.md (the register), findings.md (the claims), dev-log.md (the journal):
[github.com/gserdyuk/twotakt](https://github.com/gserdyuk/twotakt).*
