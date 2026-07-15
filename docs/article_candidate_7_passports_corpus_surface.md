# Article candidate #7 — Staleness is solved by not promising currency: passports and the corpus/surface split

> **Type: reasoning** — corpus: append/compact, not synced · born 2026-07-13

*Status: candidate, publication drafts ready (see `linkedin_post_7_llm_wiki_staleness.md`
— LinkedIn note + gist comment). Standalone meta-topic (knowledge transfer between LLM
sessions), outside both series. Origin: reading Karpathy's "LLM Wiki" gist thread
(2026-07-13) and discovering twotakt's corpus system had converged on the pattern —
with two mechanics the thread lacks, aimed at its top-voted pain.*

---

## Thesis

The LLM-wiki community's hard problem is **staleness/drift/provenance** (per the
gist thread's substantive critique cluster: lossy compression, update cascades,
temporal blindness, silent contradictions), and every proposed fix is *tooling* —
validators, freshness states, contradiction detectors. twotakt's convergent answer
is *discipline*:

1. **Document passports** — one immutable header line per corpus document (type,
   regime, birth date) telling any reader, human or LLM, how to treat the file.
   Resolves "is this current?" at *read* time instead of preventing it at write time.
2. **Corpus/surface split** — the corpus accumulates (append-only, dated,
   contradictions are history, compacted not patched); only a deliberately small
   surface promises currency and is synchronized. Staleness is solved by not
   promising currency — except where the promise is affordable (F25 generalized).
3. **Claims before concepts** — claim-first synthesis register (F-numbered, one
   screen, pointer to long form; refinements are new claims, never edits); concept
   docs *graduate* out of recurring claim clusters. Structurally solves the "Level"
   failure mode reported in the thread (nowissan: flat wikis lose importance).

## Supporting material

- Karpathy's gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
  (pattern mapping: INDEX.md=index, dev-log=log, CLAUDE.md=schema, findings=synthesis,
  compaction=lint).
- Thread critique cluster: a-a-k (no validators = not engineering), jazzonenl
  (transactional overhead, referential integrity, temporal blindness), nowissan
  (Identity/Level/Relationship after a month of real use), Jasonleonardvolk
  (deterministic contradiction detection), JeanHuguesRobert (judgment points).
- Measured boundary (blurman-ai's experiment): a wiki page pays only when it
  compresses facts scattered across many sources; mirrors of greppable files are
  negative value — validates findings.md's design and the absence of concept pages
  for code.
- CLAUDE.md "Corpus vs surface" + "Findings discipline" constraints — the mechanics
  themselves; F25 (archive, don't refresh) — the precursor finding.

## Related findings

F25 (current-state descriptions lose the race). Related candidates: #4 (trust
machinery — the thread's "wiki needs verify.py" demand is the same shape); the
series "AI Influence on the Architectural Landscape" (alirezabbasi's comment —
knowledge decay as the real bottleneck — supports its thesis).
