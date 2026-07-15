# LinkedIn post + gist comment — article candidate #7 (LLM-wiki staleness)

> **Type: record** — corpus: publication draft, frozen once posted · born 2026-07-13

*Status: **both posted 2026-07-13** — gist comment (github.com user gserdyuk) and the
LinkedIn note. Known nits, fixable via edit: gist — passport template's
`<regime>`/`<date>` swallowed as HTML (backtick the line); LinkedIn — missing space
"measured*by" in point 3. Source: `article_candidate_7_passports_corpus_surface.md`.
Two artifacts, one campaign: (1) field-report comment in Karpathy's gist thread,
(2) LinkedIn EN note. Queue: gist comment ASAP (live thread sinks under ad spam
daily); LinkedIn note jumps ahead of S1 (hot topic; S1 keeps).*

## Format decisions

- Gist comment: restrained field-report tone — on a thread flooded with self-promo,
  restraint IS the differentiator. References actual thread voices (@a-a-k, nowissan).
  Repo link at the end, no pitch.
- LinkedIn note: same skeleton as post #3 (bold title-question, story, numbered
  mechanics, closing rule) — deliberate house style. ~2,400 chars. Links in first
  comment (gist + repo).
- Author posts both himself (GitHub login for the gist; publishing is the author's
  action).

## 1. Gist comment text

Field report from a different starting point: a research repo (simulation-methodology
project, twotakt) that converged on this pattern *before* reading the gist — same
mechanics: INDEX.md as the catalog (one pointer line + a one-line hook, never
content), an append-only dated log with greppable tags, CLAUDE.md as the schema file,
a findings register as the synthesis layer. Coming from research reproducibility
rather than PKM, we ended up with two mechanics I haven't seen in the thread, both
aimed at the staleness/drift problem @a-a-k and others raise:

**1. Document passports.** Every corpus document opens with a one-line immutable
header: `> Type: reasoning|register|journal|record — <regime> · born <date>`. It
tells the reader — human or LLM — how to treat the file: is it append-only, may it
contradict newer documents, is it synchronized. Cheap, and it resolves the "is this
page current?" ambiguity at *read* time instead of trying to prevent it at write time.

**2. Corpus/surface split.** We stopped fighting staleness for most documents. The
corpus (log, findings, reasoning docs) *accumulates*: dated, append-only, internal
contradictions are history and never "fixed"; it gets periodically compacted
(reviewed, rewritten as vN, previous version archived) rather than patched in place.
Only a deliberately small "surface" (README, the schema file) promises currency and
is synchronized. We had three current-state documents die of rot before generalizing
the rule: staleness is solved by not promising currency — except where you can
actually afford the promise.

Also +1 to nowissan's "Level" problem: our synthesis layer is claim-first (numbered
one-screen claims, each pointing to its long form; refinements are new claims —
"refines/supersedes #N" — never edits), and concept-level docs only *graduate* out of
claim clusters that recur. Level falls out structurally.

*(Posted 2026-07-13. Suggested comment edits, apply via ⋯ → Edit: (a) backtick the
passport template line — `<regime>`/`<date>` got eaten as HTML; (b) expand the last
sentence: "Level falls out structurally: a concept with ten claims under it is
heavyweight, one with a single claim is light — importance is *measured* by the size
of the cluster, not assigned by an author.")*

The mechanics live in CLAUDE.md / INDEX.md / findings.md / dev-log.md here:
https://github.com/gserdyuk/twotakt

## 2. LinkedIn note text

**Everyone is building LLM wikis. The hard problem isn't the wiki — it's the promise
of being current.**

Karpathy's "LLM Wiki" gist — a pattern for LLM-maintained knowledge bases (markdown
pages, an index, a log, a schema file) — collected 5,000+ stars and a comment thread
full of implementations. Read past the ads, and the substantive comments converge on
one pain: **staleness**. Summaries drift from sources. One new document cascades into
dozens of stale pages. Two pages assert conflicting facts and nobody notices. And all
the proposed fixes are tooling: validators, freshness states, contradiction detectors.

Funny thing: our simulation-methodology repo (twotakt) converged on Karpathy's
pattern independently — same index file, same append-only log, same schema file — but
coming from research reproducibility, not personal knowledge management. From that
side, the staleness answer turned out to be discipline, not tooling:

**1. Document passports.** Every knowledge document opens with one immutable line:
its type (journal / register / reasoning / record), how to treat it, and its birth
date. The reader — human or LLM — knows from line 1 whether this file promises
currency or is a dated snapshot.

**2. The corpus/surface split.** We stopped fighting staleness for 90% of documents.
The research corpus accumulates: append-only, dated, contradictions are history —
never "fixed". Only a deliberately small surface (README, the schema file) promises
to be current, and only that gets synchronized. Three of our documents died of
current-state rot before we learned this.

**3. Claims before concepts.** The synthesis layer is a register of numbered
one-screen claims, each pointing to its long form. A refinement is a new claim
referencing the old one, never an edit. Concept pages only graduate out of claim
clusters that keep recurring — and that's the trick: a concept with ten claims under
it is heavyweight, one with a single claim is light. In a flat wiki, a life-scale
theme and a tactical detail sit at the same level and importance disappears; here
importance is *measured* by the size of the cluster, not assigned by an author.

The rule underneath: **staleness is solved by not promising currency — except where
you can actually afford the promise.** A knowledge base that marks what kind of truth
each page holds needs far less machinery to stay trustworthy.

Gist and our repo — in the comments.

## First comment (LinkedIn)

Karpathy's gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
Our repo (mechanics in CLAUDE.md, INDEX.md, findings.md, dev-log.md):
https://github.com/gserdyuk/twotakt
