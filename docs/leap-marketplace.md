# Twotakt → EPAM LEAP AI Assets Marketplace

> **Type: record** — corpus: procedure and decisions, annotated in place with dates · born 2026-09-11

Working note. Written 2026-09-11 after reviewing the LEAP portal
(https://leap.epam.com) and its asset submission guide; updated 2026-09-13 and
2026-10-19.

Decision 2026-09-11: **not submitting yet**, but bring the repository to the
expected layout in advance. Decision 2026-10-19: the layout work is **done** and
the letter is drafted — `docs/leap_submission_2026-10-19.md`. The author sends the
mail; the repository never does.

## 1. To do before submission

Twotakt is the closest to ready: `skills/` is already in the expected shape
(4 skills with `SKILL.md`), and the Apache 2.0 license is in place.

- [x] **Skill frontmatter.** (done 2026-10-19) Add `author: "Gennadiy Serdyuk <gserdyuk@gmail.com>"`
      to `skills/modeling-jain`, `skills/queueing-lazowska`,
      `skills/simstudy-protocol`, `skills/verification-validation`. Today
      they carry only `name` and `description`.
      Email decision: one address per field, never two. Skills are reused
      outside EPAM, so they carry the git identity (gmail). The EPAM address
      goes into `FACTORY.md` `authors` only (see 2.3): that is the file the
      marketplace card is built from. The crawler does not validate the
      domain, and published assets exist with no email at all.
- [x] **Maintainer line in README.** (done 2026-10-19, a `## Maintainer` section
      at the end, carrying the licence and the canonical repository with it) One human-readable line with both
      addresses, e.g. `Maintainer: Gennadiy Serdyuk <gserdyuk@gmail.com>
      (at EPAM: gennadiy_serdyuk@epam.com)`. No parser touches it. If some
      commits are ever made with the EPAM address, add a `.mailmap` so
      `git log` and GitHub show one person.
- [x] **Package as a factory.** (done 2026-10-19 as **`FACTORY.md` in the
      repository root**, not `factories/twotakt/` — see the correction in 2.3)
      Create `FACTORY.md` (template in 2.3). The factory describes the full cycle:
      ARCHITECTURE.md + REQUIREMENTS.md → MODEL.md (audit gate) →
      executable_model (SimPy) → SIM_REPORT.md. List the four skills as its
      components. Use cases:
      - Capacity planning and bottleneck analysis before load tests
      - Comparing architecture options under identical load scenarios
      - Character of degradation at 10x load
- [x] **Worktrees are not in the repository.** `.claude/worktrees/` holds
      full copies with `.venv`, but `.claude/` as a whole is in `.gitignore`
      (line 221), so it will not reach the EPAM GitLab copy. Checked 2026-09-11.
- [x] **Validate YAML** (done 2026-10-19, `tools/check_frontmatter.py` carried
      over from 3A8, run with `PYTHONUTF8=1 py tools/check_frontmatter.py`; 5 files,
      0 failing) of every frontmatter block with `yaml.safe_load()`;
      multi-line `description: >-` is fine, but run the check.
- [x] **Folder names** — letters, digits, `-`, `_` only (checked 2026-10-19).
- [x] **Confirm Apache 2.0 is acceptable** for an internal copy with EPAM
      authorship (see 2.5). Settled 2026-10-19 the same way as on 3A8: the
      copyright line in `LICENSE` is filled (`Copyright 2026 Gennadiy Serdyuk
      <gserdyuk@gmail.com>`) and a `NOTICE` states that the GitLab copy is a
      mirror under the same licence, not a transfer of ownership.

## 2. Getting the project into EPAM GitLab and the LEAP Marketplace

Portal: https://leap.epam.com → HyperFactory → AI Assets Marketplace.
Guide: https://leap.epam.com/sp/ai-marketplace/contribute.

### 2.1. Hosting scheme (precedent: arozumenko/sdlc-skills)

The canonical repository stays on personal GitHub under its own license.
The EPAM GitLab copy exists only for the marketplace crawler. Artem Rozumenko
does exactly this: 4 catalog factories, `install_script` in FACTORY.md points
to `npx github:arozumenko/sdlc-skills`, and the catalog accepts it.

Half of the catalog's factories (19 of 38) live in personal namespaces of the
form `git.epam.com/<name_surname>/<repo>`; no team or practice is required.

### 2.2. EPAM GitLab copy (done 2026-09-13)

Project: https://git.epam.com/gennadiy_serdyuk/twotakt — created by importing
from GitHub. Import is one-off; it keeps no link to the source.

**Chosen sync method: a separate remote `epam`, pushed on demand.**
Pull mirroring (Settings → Repository → Mirroring, direction Pull) is not
available on git.epam.com (no Premium). A second push URL on origin and
GitHub Actions mirroring were rejected as less controllable.

The remote is already in `.git/config` (repeat on another machine):

```bash
git remote add epam https://git.epam.com/gennadiy_serdyuk/twotakt.git
```

Refresh the EPAM copy when the state is ready to be seen:

```bash
git push epam main
```

- `git push` / `git pull` without a remote name still go to GitHub only.
- HTTPS push needs a Personal Access Token (scope `write_repository`); the
  SSO password does not work. Credential Manager remembers it after the
  first use.
- If `main` on GitLab is protected against force-push and history on GitHub
  was rewritten, the push is rejected: relax it in Settings → Repository →
  Protected branches, or do not rewrite `main`.
- Check the project Visibility is **Internal**: the crawler cannot see
  Private.
- The marketplace crawler re-reads the repository after every push.

### 2.3. Crawler layout requirements

- `skills/<name>/SKILL.md` — one skill per folder.
- `agents/<name>/agent.md` (or `<name>.md`, `<name>.agent.md`) — one agent
  per folder.
- `FACTORY.md` — file name strictly uppercase, **in the root of the directory
  the factory occupies**. For a repository that *is* one factory, that is the
  repository root. **Corrected 2026-10-19 from `factories/<name>/FACTORY.md`:**
  on 2026-09-17 the LEAP team (Dima) told 3A8 that their data-processing rules
  require the root placement, and 3A8's file was moved there and `factories/`
  deleted. Twotakt was built with the file in the root from the start, so there
  is nothing to move here.
- Folder name = asset identifier: letters, digits, `-`, `_` only.
- Skill and agent frontmatter: `name`, `description`,
  `author: "Name <email>"`. The guide says email is required; in practice
  assets are published with no email and even with no `author` field at all
  (team-skills, epm-ease/agent-skills). The domain is not checked.
- Keep something out of the catalog: `discoverable: false` in its frontmatter.

FACTORY.md template (as filled in `FACTORY.md` on 2026-10-19). Any value
containing a colon must be quoted, otherwise the YAML breaks silently and the
asset simply never appears:

```yaml
---
name: Twotakt — Architecture Simulation
description: "Audit-first performance modeling: architecture and requirements in, verified MODEL.md, executable SimPy model, bottleneck report out."
owner: Gennadiy Serdyuk
authors:
  - "Gennadiy Serdyuk <gennadiy_serdyuk@epam.com>"
install_script: "git clone https://github.com/gserdyuk/twotakt.git"
install_script_unix: "git clone https://github.com/gserdyuk/twotakt.git"
sdlc_phase: Architecture & Design
support_level: Self-Serve
use_cases:
  - Capacity planning and bottleneck analysis before load tests
  - Comparing architecture options under identical load scenarios
  - Character of degradation at 10x load
---
# Twotakt
<markdown: what it does, how to run, limits, link to README>
```

`support_level` is strictly one of `Self-Serve`, `Best Effort Support`,
`Dedicated Capacity`. `sdlc_phase` is a single value, not a list. Omit
`project_deployments` if there is nothing to put there.

### 2.4. Submitting

Email to SpecialEPM-EASEFeedback@epam.com, one folder URL per asset type
plus the owner:

```
skills:    https://git.epam.com/gennadiy_serdyuk/twotakt/-/tree/main/skills
factories: https://git.epam.com/gennadiy_serdyuk/twotakt/-/blob/main/FACTORY.md
owner:     Gennadiy Serdyuk
```

The factory URL points at the file, not at a `factories/` folder — see the
placement rule in 2.3. The drafted letter, with the pre-send check, is
`docs/leap_submission_2026-10-19.md`.

**What is submitted, decided 2026-10-19:** one factory **and the four skills as
assets in their own right**. This is a deliberate difference from 3A8, where the
skills were entry points of one instrument and the LEAP team was asked to treat
them as parts of the factory. Here `queueing-lazowska` and `modeling-jain` are
self-contained methodology skills — a capacity question that closed-form queueing
theory answers in a minute should not be simulated at all — and
`verification-validation` works against any SimPy model.

Published within a few working days. After that the repository is
re-crawled automatically on every push; no resubmission needed. Check it
appeared at https://leap.epam.com/hyperfactory/ai-assets-marketplace.

### 2.5. Decide before submitting

- Ownership and license: a copy on EPAM GitLab with an EPAM author makes the
  asset an internal corporate one. Apache 2.0 allows it, but make the
  decision consciously.
- `owner`: personal name or EPM-UASP. **Settled 2026-10-19:** personal name, as
  on 3A8.
- "Proven On" (L2/L3) is filled for only 8 of 38 factories; the examples in
  `examples/` without a production case honestly rate L2. **Narrowed 2026-10-19:**
  the letter claims **L1, L2 at most**, and says why — four worked models, one of
  them (FaxRx) built on a real production platform, but none a prediction later
  scored against a measured production result. 3A8 could claim L2 on a sealed
  outcome; twotakt cannot, and the letter says so rather than letting the
  catalogue infer it.
- **Packaging, stated as a limit rather than fixed (2026-10-19).** The skills are
  read from disk by the repository's `CLAUDE.md`, so `install_script` is a
  `git clone` and the method is used by moving into a clone. Plugin packaging stays
  deferred (dev-log 2026-08-04: "probably none, I'm not ready"; the blocker is
  `examples/*/verify.py`'s `sys.path.insert(..., parents[2])`). Both the FACTORY.md
  body and the letter say this out loud, including that `simstudy-protocol`'s
  description still points at `twotakt/examples`.
- The niche is empty: the catalog has no factory about architecture
  performance simulation. The closest is "AI Systems Performance Testing
  docs generator", and that one is about documents, not models.
