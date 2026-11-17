# Validation harness

The **validation harness** checks that an executable model is trustworthy *before* you use
it to study behaviour. It is the executable form of the methodology's V&V step (Phase 7).

It is **not** the sweep harness: `sweep.py` / `sweep_2d.py` *explore* behaviour (the
research); this harness *validates* the model so that exploration is worth doing.

Each example has a `verify.py` you run standalone:

```bash
cd examples/USLmodel
python verify.py        # prints a per-check pass/fail summary; exit 0 only if all green
```

`verify.py` adapts the model's own output into a canonical ledger (`RunSummary`) and runs a
small battery of checks. **Green means: the executable model is trustworthy enough to run
sweeps on.**

## What it checks (now)

- **Conservation of work.** Nothing is silently created or lost: everything offered ends up
  completed, rejected (by design), lost to congestion, or still in flight. Catches lost /
  miscounted requests. Universal — the same check applies to every model.
- **Mechanism behaviour, by toggling.** For each declared mechanism (degradation, a pool,
  an admission/blocking front door, a decode stage…), the harness toggles it and asserts the
  metric moves the right way — e.g. *turning degradation off must raise peak throughput*;
  *shrinking the pool must lower throughput where the pool binds*. No magic-number thresholds;
  only the **direction** of the effect, taken from the model's spec (`MODEL.md`). Each such
  check is taken at the operating point where the mechanism actually binds.
- **Curve shape** where a model has a known law (e.g. the three USL regimes: rise → knee →
  decline).
- **Multi-class and multi-stage models** — one ledger per category (e.g. voice / digital)
  and per stage (e.g. record → decode), with partition checks.
- **Every check is negative-tested, on every run** — each example keeps a `mutants.py`:
  named, realistic bugs (a request that vanishes, a pool sized from a constant, a dead
  degradation multiplier, latency in ms against an SLA in s...) planted into the model.
  The mutation suite (`harness/mutation.py`) re-imports `verify.py` on top of each broken
  model in its own subprocess and requires every check the mutant claims to go red.
  A check that no mutant turns red is *unguarded* and fails the suite. A check that
  structurally cannot fail may be declared in `WAIVED` with the reason; waivers are
  printed on every run as a known gap, never as a pass.

## Running everything

```bash
pip install -r requirements-verify.txt      # exact engine pin (simpy)
python -m harness verify-all                # every example: verify.py + mutation suite
python -m harness verify-all --no-mutants   # checks only
cd examples/USLmodel && python verify.py --mutants   # one example's mutation suite
```

CI (`.github/workflows/verify.yml`) runs `verify-all` on every push. `constraints.txt`
holds the exact versions the examples were last verified with.

## What it does NOT do

- **It does not prove the model is "right" about reality.** That is the human audit (the
  `MODEL.md` approval gate). The harness checks that the *code implements the spec* and that
  *mechanisms behave as the spec says* — not that the spec itself is correct.
- **It does not decide whether the architecture meets its requirements** (the SLA verdict).
  That is the *output* of the sweep/analysis, never asserted here. Asserting the goal would
  defeat the purpose of running the study.
- **The behaviour/law checks are per-model, not universal.** Conservation transfers to every
  model; the law-shape and mechanism checks are written per model from its `MODEL.md`
  (USL ≠ Erlang ≠ cascade — the laws don't compose).
- **Not yet:** per-component checks (today: system / per-category / per-stage only);
  generator-authored bounds; statistical confidence intervals in the checks (runs are
  deterministic, fixed-seed); integration into the skill (so build sessions may still
  verify by prose).

## The one line to remember

> **Green ⇒** the executable model conserves work and its mechanisms behave directionally as
> the spec says, at the tested points.
> **Green does *not* ⇒** the model is right about the world (that is the audit) or that the
> architecture meets its SLA (that is the sweep).
