---
title: "twotakt - articles"
description: "Long-form English write-ups from the twotakt project: performance modeling, discrete-event simulation, and the methodology that makes a model trustworthy."
---

# twotakt — articles

> **Type: register** — publication index: one line per published article · born 2026-07-17

Long-form English versions of the project's published notes. Each article is a
frozen record; the living material (models, sweeps, verification) stays in the
[repository](https://github.com/gserdyuk/twotakt).

- **[Fail fast or fail slow: where should your system break under load?](fail-fast-or-fail-slow.md)**
  — two architectures, the same success rate under a 10× burst, opposite user
  experience; why an undersized front door is admission control, not a defect.
  (2026-07-17; short form: LinkedIn, 2026-07-13; Ukrainian long form:
  [DOU](https://dou.ua/forums/topic/60921/), 2026-07-28; EN mirror:
  [dev.to](https://dev.to/serdyuk/fail-fast-or-fail-slow-where-should-your-system-break-under-load-7ii),
  2026-07-28, canonical -> this page)
- **[min(10, 20) = 6: where is the system's bottleneck?](min-10-20-equals-6.md)**
  — two components rated 10 and 20 requests/s, a system that dies at 6; the
  closed-form ceiling the napkin math misses, and why the bottleneck turns out to be
  a property of the regime rather than of any component.
  (2026-07-31; short form: LinkedIn, 2026-07-31; Ukrainian long form:
  [DOU](https://dou.ua/forums/topic/61089/), 2026-07-31)
- **[Staleness is solved by not promising currency](llm-wiki-staleness.md)**
  — what a research repo's discipline says to the LLM-wiki staleness problem:
  document passports, the corpus/surface split, claims before concepts.
  (2026-07-17; short forms: Karpathy-gist comment + LinkedIn note, 2026-07-13)
