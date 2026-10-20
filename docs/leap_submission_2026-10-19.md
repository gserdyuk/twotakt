# Submission of Twotakt to the LEAP AI Assets Marketplace — the letter and the pre-send check

> **Type: record** — corpus: the letter as drafted, frozen once sent · born 2026-10-19

> **Superseded in its mechanism on 2026-10-20, one day after it was written: the letter is
> not how you submit any more.** The mailbox route was replaced by a merge request against
> `epm-ease/factory-registry` — see `docs/leap-marketplace.md` §3, and the section at the
> end of this file. The letter below is kept as written: its content did not become wrong,
> only its envelope, and the "what it is / proven on / limits" paragraphs are the raw
> material for the merge request description.

Prepared 2026-10-19, after bringing the repository to the layout the crawler expects (`FACTORY.md` in the
root, `author` in every skill, `NOTICE`, maintainer line, validator). The author sends the mail; nothing
here is sent by the repository or its tools. Procedure and layout rules: `docs/leap-marketplace.md` §2.

Precedent followed throughout: 3A8, submitted 2026-09-16 (`../../3A8/docs/leap_submission_2026-09-16.md`
in the author's workspace — not part of this repository). One deliberate difference: there, the four
skills were entry points of a single instrument and the LEAP team was asked to treat them as parts of
the factory. Here the four skills are submitted **as assets in their own right as well** —
`queueing-lazowska` and `modeling-jain` are self-contained methodology skills that are useful without
ever running a simulation, and `verification-validation` is usable against any SimPy model.

## Pre-send check

- [x] `git push epam main` done and `git rev-parse epam/main` equals `origin/main` (both at the commit
      that carries this file). Done 2026-10-19: both remotes at `07277df`. One local fix was needed —
      twotakt's `.git/config` resets `credential.helper` to empty before adding gh's helper, which also
      drops the system-wide Git Credential Manager, so git.epam.com had no helper at all; fixed with
      `git config --local credential."https://git.epam.com".helper manager`. 3A8 needs nothing: it has
      no local credential block and inherits GCM.
- [x] https://git.epam.com/gennadiy_serdyuk/twotakt → Settings → General → Visibility is **Internal**
      (the crawler cannot read Private). Confirmed by the author 2026-10-20.
- [x] `PYTHONUTF8=1 py tools/check_frontmatter.py` passes (4 skills + `FACTORY.md`). Run 2026-10-19:
      5 files, 0 failing.
- [ ] The two folder URLs below open in a browser while signed in to git.epam.com.
- [x] `FACTORY.md` is in the repository root, not under `factories/` (the LEAP team's rule, learned on
      3A8 on 2026-09-17). Built that way from the start.

## The letter

**To:** SpecialEPM-EASEFeedback@epam.com
**Subject:** AI Assets Marketplace submission — Twotakt, an architecture performance simulation factory and four modeling skills

Hello,

I would like to submit one factory and four skills to the AI Assets Marketplace.

```
factories: https://git.epam.com/gennadiy_serdyuk/twotakt/-/blob/main/FACTORY.md
skills:    https://git.epam.com/gennadiy_serdyuk/twotakt/-/tree/main/skills
owner:     Gennadiy Serdyuk
```

**What it is.** Twotakt is a kit for building a discrete-event performance model of an IT architecture
with an AI assistant. Two documents go in — the architecture and the requirements — and what comes out is
a `MODEL.md` the architect has read and approved, a SimPy program machine-checked against that model, and
a report on where the system breaks under load: throughput, latency, queues, the order in which
bottlenecks appear, the character of degradation at 10x load. It is not a load-testing tool and it does
not hide the simulator: the SimPy code is meant to be read.

**What makes it a method rather than a code generator.** No simulation code is written before the human
has approved `MODEL.md`. An assistant with that gate removed still produces a model, a curve and a
report — they just stop meaning anything, because what is then being trusted is code nobody specified.
So there are two verifications with two different verifiers: the architect certifies the *intent*
(`MODEL.md` is the spec; when code and model disagree, the code is the bug), and an executable verifier
plus the shared harness certify that the code *honours* it — conservation invariants, law-shape and
metamorphic checks, and negative tests that must fail on a deliberately broken model. Green means the
code implements the model; it never means the model is right about the world.

**The four skills** (submitted as assets in their own right, and also the components of the factory):
`simstudy-protocol` — the audit-first ten-phase protocol, the entry point; `verification-validation` —
the executable trust check between building a model and paying for sweeps; `queueing-lazowska` —
analytical queueing answers without simulation (M/M/c, MVA, operational laws, "how many servers do I
need"); `modeling-jain` — statistical rigour on the way in and out (distribution choice, confidence
intervals, an audit for common measurement mistakes). The last two are useful without ever running a
simulation, which is why I am not asking that they be folded into the factory: a capacity question that
closed-form queueing theory answers in a minute should not be simulated at all.

**Support level:** Self-Serve. **SDLC phase:** Architecture & Design.

**Proven On.** I claim no production outcome. There are four worked models in `examples/` — a server
with USL degradation, the same with a database connection pool (cascaded bottlenecks), a search
aggregator with two pipelines, and worldwide fax reception with Erlang B plus OCR built on a real
production platform — but none of them is a prediction that was later scored against a measured
production result. The fax case produced a published result (the success-rate paradox: fail fast or fail
slow, DOU 2026-07-28, https://dou.ua/forums/topic/60921/). I would rate this L1, L2 at most; please set
the level as your criteria prescribe.

**One limit worth stating up front.** Today the skills are read from disk by the repository's
`CLAUDE.md`, so the method is used by cloning the repository and working inside it, not from inside an
existing project. Packaging it as a Claude Code plugin is a known next step that I have deliberately
deferred; `install_script` is therefore a `git clone`.

**Licence and hosting.** Apache 2.0, copyright Gennadiy Serdyuk. The canonical repository is
https://github.com/gserdyuk/twotakt; the git.epam.com project is a mirror refreshed on demand for the
crawler.

As far as I can see the catalogue has no factory on architecture performance simulation today — the
nearest is an "AI Systems Performance Testing docs generator", which produces documents rather than
models.

Thank you,
Gennadiy Serdyuk
gennadiy_serdyuk@epam.com

## After it is published

- Check the card at https://leap.epam.com/hyperfactory/ai-assets-marketplace; the repository is
  re-crawled on every `git push epam main`, no resubmission needed.
- Record the publication date and the assigned Proven On level in `docs/leap-marketplace.md` §2.5.
- If the LEAP team asks whether the four skills belong to the factory rather than standing on their own
  (they asked exactly that on 3A8), the answer is in the letter: `simstudy-protocol` and
  `verification-validation` are the factory's own surface, `queueing-lazowska` and `modeling-jain` stand
  on their own. Their call either way; nothing in the repository has to move.


## What replaces the letter — 2026-10-20

The official guide (https://leap.epam.com/sp/ai-marketplace/contribute, LEAP v.0.48.0.4)
now describes a registry merge request. Full reading of the deltas:
`docs/leap-marketplace.md` §3. The short form for twotakt:

1. Confirm write access to https://git.epam.com/epm-ease/factory-registry (`registry` →
   **+** → **New file**). A fork offer means no access — ask the LEAP team for it.
2. Add `registry/gennadiy-serdyuk-twotakt.yaml`:

   ```yaml
   repo_url: https://git.epam.com/gennadiy_serdyuk/twotakt
   repo_path: ./
   contacts:
   - gennadiy_serdyuk@epam.com
   owner: Gennadiy Serdyuk
   is_factory: true
   ```

   Identical in shape to the author's existing `registry/gennadiy-serdyuk-3a8.yaml`.
3. Commit to a new branch, open the merge request with the **registry-entry** template,
   complete its checklist, wait for `validate:registry`, `validate:targets` and
   `scan:security` to go green, then a maintainer reviews and merges.
4. In the merge request description, say what the letter says: what the factory is, that
   no production outcome is claimed (L1, L2 at most), and that the four skills are meant to
   stand on their own — and ask whether a second entry with `repo_path: skills` and
   `is_factory: false` is acceptable given that `./` already covers that folder. Measured
   on 3A8, a `./` factory entry publishes the factory card only: its catalogue page shows
   Factories 1, Agents 0, Skills 0.

The pre-send check above still applies as a pre-**merge-request** check: visibility
Internal, mirror pushed, frontmatter validator green, `FACTORY.md` in the factory root.
