"""
Sweep arrival rate against the server simulation and print the
throughput / latency curve. Demonstrates the USL "throughput rises,
peaks, then declines" behavior.

Usage:
    pip install -r requirements.txt
    python sweep.py
"""

from server_sim import Config, run


RATES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20]


def main():
    print(f"{'rate':>5} {'thr':>7} {'p50':>8} {'p95':>8} {'p99':>8} "
          f"{'wait':>8} {'drop_to':>8}")
    for rate in RATES:
        r = run(Config(
            arrival_rate=rate,
            sim_time=300.0,
            sla_seconds=10.0,
            max_threads=500,
        ))
        print(f"{rate:5.1f} "
              f"{r['throughput_rps']:7.2f} "
              f"{(r['latency_p50'] or 0):8.3f} "
              f"{(r['latency_p95'] or 0):8.3f} "
              f"{(r['latency_p99'] or 0):8.3f} "
              f"{(r['wait_mean'] or 0):8.3f} "
              f"{r['dropped_timeout']:8d}")


if __name__ == "__main__":
    main()
