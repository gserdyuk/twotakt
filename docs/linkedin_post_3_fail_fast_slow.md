# LinkedIn post — article candidate #3 (fail-fast vs fail-slow)

> **Type: record** — corpus: publication draft, frozen once posted · born 2026-07-13

*Status: **posted 2026-07-13**. The attached architecture image is the pre-fix version
(overlapping "admitted" label); author's call: leave it as is. The corrected
`linkedin_post_3_architecture.png` is in the repo and goes into the DOU article.
Source: `article_candidate_3_fail_fast_slow.md`
long form; `examples/FaxRx` for all numbers. First post of the LinkedIn warm-up series
(#3 → #2 → #1; #4 is reserved for a long-form venue).*

## Format decisions

- Native feed post, **not** a LinkedIn Article (articles get almost no reach).
- 2,726 chars measured (limit 3,000 — fits with margin). First line is a
  title-question ("Fail fast or fail slow — …");
  the fold (~200 chars) still shows the start of the personal-history opener under it.
  LinkedIn has no bold — post the title line as plain text, or use the Unicode
  bold-letters trick only if it renders cleanly.
- **Two images**, attached as images (not link previews); LinkedIn shows them as a grid:
  1. `docs/linkedin_post_3_architecture.png` — pipeline diagram, the two failure points
     accented (front door / OCR); generated one-off for this post, not example canon.
  2. `examples/FaxRx/sweep.png` — the evidence (three panels).
- External link goes in the **first comment** (LinkedIn down-ranks posts with links);
  link to the example folder, not the repo root — the reader arrives inside the story.
- Written for a reader *slightly* outside the field: no Erlang-B, no p95, each
  architecture told as a mini-story with a user in it.
- Personal frame (author's confirmed biography: he built a PSTN fax-reception service
  in the past): opens the post, closes the lesson ("would have loved to have on paper
  back then").
- Only the 1-hour SLA is mentioned; the 10-minute normal-case SLA is dropped as
  unnecessary for the story.

## Post text

**Fail fast or fail slow — where should your system break under load?**

Some years ago I worked on a fax-reception service over PSTN: you buy a number, and
incoming faxes land in your inbox as email. Recently — mostly out of curiosity — I
went back and modeled several variants of its architecture in SimPy. One result is
worth sharing: two designs with the same success rate under a 10× traffic burst, and
one of them is much worse for its users. Interestingly, the success-rate metric just
cannot see it.

The pipeline (first picture): calls arrive over phone/SIP lines, workers convert the
fax, about half of the faxes go through OCR, the result is delivered by email. The
SLA: deliver within an hour, worst case.

The question I wanted the simulation to answer: when a traffic burst exceeds capacity,
**where** exactly does the system break — and what does that failure look like from
the outside?

Three architectures, burst swept from mild to 10× the normal load (second picture):

**A — small front door: 270 phone lines.** A phone line doesn't queue: if all lines
are busy, a new call gets a busy signal immediately. As the burst grows, up to 45% of
calls get rejected this way. Sounds terrible? Look closer: everything that *did* get
through is delivered on time — delivery time stays flat no matter the burst. And the
rejected caller knows it instantly. He just redials.

**B — open the door wide: 2,565 lines.** Busy signals disappear... and the backlog
quietly drowns the OCR stage. Delivery time climbs until it hits the 1-hour SLA
ceiling. At 10× burst, B's success rate is 0.52 vs A's 0.54 — statistically the same.
But the failure could not be more different: the fax was *accepted*, the sender walked
away confident — and the fax died in a queue an hour later. Nobody redials, because
nobody knows.

**C — keep the wide door, scale OCR 5×.** Helps at moderate bursts; at 10× it is
still ~5× slower than A. More capacity postpones the slow-failure mode. It doesn't
change its nature.

The lesson — one I would have loved to have on paper back then: a success-rate number
tells you how much a system carries, not where it breaks. Two architectures with
identical success rates gave users opposite experiences: a fast, honest "busy, try
again" versus a silent loss discovered an hour later. An undersized front door is not a deficiency — it is admission control.
Accepting work you cannot finish converts fast, honest failures into slow, hidden
ones. And it doesn't even improve the success rate.

Full model, spec, and sweep results are open — link in the comments.

(Part of twotakt — an audit-first workflow for building SimPy simulations you can
actually trust.)

#systemdesign #performanceengineering #capacityplanning #simulation

## First comment

Model, spec and the full sweep: https://github.com/gserdyuk/twotakt/tree/main/examples/FaxRx
