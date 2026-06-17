"""
Behavioral sweep (Phase 8) for the two-stage RadioMonitoring model.

Three sweeps, each averaged over seeds with a 95% CI half-width:
  1. LOAD   — lambda_mult at nominal hardware (2/4 SDR, 2 decode): how POI and
              decode-yield degrade, by category.
  2. SDR    — vary SDR pool size with GENEROUS decode (isolates stage ①):
              how many receivers to reach POI ≥ 50%.
  3. DECODE — vary decode workers with GENEROUS SDR (isolates stage ②):
              how many workers to stop the queue overflowing.

plot_sweep.py imports the ranges and run_avg so text and visual stay aligned.
"""

from statistics import mean, stdev

from server_sim import Config, run

LAMBDA_MULTS = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0]
SDR_SIZES = [1, 2, 4, 8, 16, 24]          # lower = upper = k
DECODE_WORKERS = [1, 2, 4, 8, 16, 32, 48]
SEEDS = list(range(10))

GEN_DECODE = 64                            # "generous" decode to isolate stage ①
GEN_SDR = 20                               # "generous" SDR to isolate stage ②


def _avg(values):
    m = mean(values)
    h = 1.96 * (stdev(values) / len(values) ** 0.5) if len(values) > 1 else 0.0
    return m, h


def run_avg(seeds=SEEDS, **kw):
    """Run across seeds; return {cat: {metric: (mean, ci_half)}} + queue_hwm."""
    acc = {c: {"poi": [], "yield": [], "e2e": [], "A": [], "C": []}
           for c in ("voice", "digital")}
    qhwm, dropped = [], []
    for s in seeds:
        r = run(Config(seed=s, **kw))
        qhwm.append(r["queue_hwm"])
        drop = sum(r["by_category"][c]["decode_dropped_G"] for c in ("voice", "digital"))
        dropped.append(drop)
        for c in ("voice", "digital"):
            d = r["by_category"][c]
            tot = d["blocks"] or 1
            acc[c]["poi"].append(d["poi"] or 0.0)
            acc[c]["yield"].append(d["decode_yield"] or 0.0)
            acc[c]["e2e"].append(d["e2e_yield"] or 0.0)
            acc[c]["A"].append(d["A_hop_gap"] / tot)
            acc[c]["C"].append(d["C_no_sdr"] / tot)
    out = {c: {k: _avg(v) for k, v in acc[c].items()} for c in acc}
    out["queue_hwm"] = _avg(qhwm)
    out["dropped"] = _avg(dropped)
    return out


def _row(label, o):
    return (f"{label:>8} "
            f"{o['voice']['poi'][0]:7.1%} {o['digital']['poi'][0]:7.1%} "
            f"{o['voice']['yield'][0]:7.1%} {o['digital']['yield'][0]:7.1%} "
            f"{o['voice']['e2e'][0]:7.1%} {o['digital']['e2e'][0]:7.1%} "
            f"{o['queue_hwm'][0]:9.0f} {o['dropped'][0]:9.0f}")


def main():
    hdr = (f"{'x':>8} {'POI_v':>7} {'POI_d':>7} {'yld_v':>7} {'yld_d':>7} "
           f"{'e2e_v':>7} {'e2e_d':>7} {'q_hwm':>9} {'dropG':>9}")

    print("== LOAD sweep (nominal 2/4 SDR, 2 decode workers) ==")
    print(hdr)
    for m in LAMBDA_MULTS:
        print(_row(f"x{m:g}", run_avg(lambda_mult=m)))

    print("\n== SDR sizing @ x1, generous decode (isolates stage 1) ==")
    print(hdr)
    for k in SDR_SIZES:
        print(_row(f"sdr{k}", run_avg(n_sdr_lower=k, n_sdr_upper=k,
                                      n_decode_workers=GEN_DECODE)))

    print("\n== DECODE sizing @ x1, generous SDR (isolates stage 2) ==")
    print(hdr)
    for w in DECODE_WORKERS:
        print(_row(f"w{w}", run_avg(n_sdr_lower=GEN_SDR, n_sdr_upper=GEN_SDR,
                                    n_decode_workers=w)))


if __name__ == "__main__":
    main()
