# Article candidate #2 — The interaction bottleneck: component ceilings don't compose

> **Type: reasoning** — corpus: append/compact, not synced · born 2026-07-13

*Status: candidate. Target form: practitioner article with a runnable exhibit.*
*Origin: USLDBmodel lesson; the one-line version lives in `TODO.md` under
"Article / pitch material". Dev-log 2026-06-16 already tags the executable
demonstration "article candidate #2 material".*

---

## Thesis

Component correctness does not compose into system correctness. In USLDBmodel every
component is individually correct and individually sufficient on paper (~20 rps
component ceilings), yet the system collapses at **~6 rps** with `db_pool_size=1`.
The bottleneck is not *in* any component — it lives in the **interaction** (holding a
pooled connection across a slow downstream call). Paper capacity math that sums or
mins component ceilings misses this class entirely; only a system-level executable
model exposes it.

Two sharpening points from the harness work:

- **A mechanism binds in its own regime** (F9): the pool does *not* change the peak —
  CPU/USL binds at the knee, where even pool=1 keeps up. The pool binds in
  **overload**: at rate 8, pool=1 gives 0.29 vs pool=8's 0.89, while peaks are equal
  (~4.07) across pool ∈ {1, 8, 100}. An interaction bottleneck can be invisible at the
  operating point where you benchmarked.
- **What detects the class** (F10, F11): component + edge checks *localize* faults;
  only system-level checks *detect* interactions. The value lives in metamorphic
  relations (bottleneck migration, interference), not in conservation identities,
  which trend toward tautology.

## Supporting material

- `examples/USLDBmodel/README.md` ## Lesson — the narrative version.
- `examples/USLDBmodel/verify.py` — the pool-exhaustion metamorphic relation, taken at
  rate=8 (overload), negative-tested against a non-binding pool (8 vs 100).
- dev-log 2026-06-16 ("harness on USLDBmodel") — probed numbers and the
  operating-point lesson.

## Related findings

F9 (binding region), F10 (non-composition), F11 (composition value = metamorphic
relations). Related candidates: #4 provides the trust machinery that made the
executable demonstration credible; #3 is the same "paper metrics mislead" genre on
the failure-mode axis.
