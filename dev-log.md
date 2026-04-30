# twotakt — development log

Append-only log of project evolution. Newest entries at the bottom.
Tag entries with `#tag` so the log is greppable later.

Conventions:
- Date in `YYYY-MM-DD` format.
- One header per entry, describing the change in one line.
- Body explains what, why, and where the artifact lives.
- Tags at the end of the body.

---

## 2026-04-30 — examples/USLmodel created

First worked example. Single-CPU thread-per-request server simulated in
SimPy with USL-based degradation (linear α + quadratic β
coefficients applied as a multiplier to CPU bursts). Three-panel plot
(throughput / success rate / latency). Effective latency metric added
after we noticed survivorship bias in ok-only percentiles under
overload.

Lives at `examples/USLmodel/` with `server_sim.py`, `sweep.py`,
`plot_sweep.py`, `requirements.txt`, `MODEL.md`, `sweep.png`.

`#example #model #USL #v1`

## 2026-04-30 — examples/USLDBmodel created

Extension of USLmodel adding a database connection pool (model #1
from the database modelling menu — bounded concurrency, FIFO queue,
fixed query duration). Built by copying USLmodel and surgically
adding `db_pool_size` / `db_query_mean` to Config, a `self.db`
Resource on Server, and a new acquire-hold-release block at the end
of `_serve`. Two sweeps saved (`sweep.png` for default pool=8, and
`sweep_2.png` for pool=1).

Lives at `examples/USLDBmodel/`. `MODEL.md` references its parent
and describes only the diff.

`#example #extension #model #database`

## 2026-04-30 — examples/METHODOLOGY.md written

12-step methodology document capturing the path that produced the
two examples, plus a list of recurring anti-patterns. Intended as a
working protocol for future examples, not a historical record.

`#methodology #docs`

## 2026-04-30 — per-model MODEL.md spec documents

Wrote `MODEL.md` inside both example folders. They describe the
*intent* of each model in human prose so a reader does not need to
read the code to understand modelling choices. Established the rule:
spec is the specification, code is its implementation; if they
disagree, the code is the bug.

`#docs #spec`

## 2026-04-30 — perf-simulation skill v1 packaged

Packaged the methodology + audit protocol + theory glossary + metric
checklist + code templates as a Cowork skill (`perf-simulation`).
Encodes the audit-first protocol as a blocking gate so future
modelling sessions cannot skip the audit before writing code. The
user's `examples/` directory is treated as the working library —
when a pattern recurs three times across examples, candidate for
extraction into a real library module (rule of three).

Skill v1 has draft quality only — no test cases run, no iteration
cycle. Decision: ship as-is, iterate later if needed.

Artifacts:
  - source: `skills/perf-simulation/` (editable folder for future iteration)
  - package: `perf-simulation.skill` (24 KB, installable bundle)

`#skill #release #v1 #methodology`

## 2026-04-30 — pivot from MCP-centric to skill-and-templates approach (v2)

The original vision (`docs/archive/architecture-v1.md`,
`docs/archive/concept-v1.md`) was an MCP server (`twotakt-mcp`) that
exposed simulation through declarative tools (`build_model`,
`run_bench`, `show_model`, etc.) and hid SimPy behind a generic
Resource/Activity/Step abstraction. After building two worked examples
(`USLmodel`, `USLDBmodel`) and packaging the methodology as the
`perf-simulation` skill, we converged on a different position:

- Don't hide SimPy. The user sees the code.
- The skill provides discipline (audit-first, metric checklist,
  templates, theory glossary) so direct SimPy use stays honest.
- Modern LLMs make SimPy tractable for users without deep library
  knowledge, removing the original justification for the MCP fasade.
- First prove the approach on real cases; polishing for non-technical
  users is a later concern.

Cleanup performed:
- `architecture.md` → `docs/archive/architecture-v1.md`
- `concept.md`     → `docs/archive/concept-v1.md`
- `pyproject.toml` stripped of `mcp` dependency and `twotakt-mcp`
  script; bumped to `0.2.0`.
- `.mcp.json` reset to empty `mcpServers` (effectively disabled).
- `README.md` rewritten to describe v2 layout and approach.

Manual cleanup still needed (Windows ACL prevented Linux-side
deletion): remove the `twotakt/` Python package directory (containing
the now-unused `twotakt/mcp/server.py`) and optionally the orphaned
`uv.lock`.

`#pivot #v2 #cleanup #methodology`
