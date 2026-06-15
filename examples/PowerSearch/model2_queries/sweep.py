"""
Перебор параметров — User Query Pipeline (Модель 2).

Что делает этот скрипт:
  Запускает симуляцию для каждой комбинации (base_arrival_rate, num_search_workers)
  и собирает ключевые метрики. Результаты сохраняются в CSV и JSON
  для дальнейшей визуализации в plot_sweep.py.

Главный вопрос, на который отвечает sweep:
  При каком числе воркеров система удерживает effective p95 < 500 мс
  не только в спокойное время, но и во время 5-кратных всплесков нагрузки?

Зачем перебирать оба параметра:
  base_arrival_rate — нагрузка: от лёгкой (10 req/s) до тяжёлой (300 req/s).
  num_search_workers — ресурс: сколько слотов воркеров выделено.

  Три фазы, которые должны появиться на графике:
    1. Healthy:  eff_p95 << 500 мс, success_rate ≈ 1.0
    2. Knee:     eff_p95 приближается к 500 мс, появляются первые дропы
    3. Degraded: success_rate падает, eff_p95 >= 500 мс

Зачем несколько seeds:
  p95 — нестабильная метрика при малой выборке (особенно при burst-нагрузке).
  Усреднение по SEEDS=[42, 43] сглаживает случайный шум. При production-анализе
  лучше использовать 5–10 seeds.

Survivorship bias в результатах:
  При перегрузке raw latency_p95 (только успешных) выглядит нормально,
  хотя часть пользователей уже получает ошибку по таймауту.
  Поэтому в выводе присутствуют оба значения: eff_latency_p95 и latency_p95.
  Для принятия решений используйте только eff_latency_p95.
"""

import csv
import json

from server_sim import Config, run

# ---------------------------------------------------------------------------
# Сетка параметров для перебора.
# ---------------------------------------------------------------------------

# Диапазон базовой нагрузки: от 10 req/s (лёгкая) до 300 req/s (тяжёлая).
# Burst-нагрузка = base * 5, т.е. при base=300 система видит 1500 req/s во всплеске.
ARRIVAL_RATES  = [10, 25, 50, 75, 100, 125, 150, 175, 200, 250, 300]

# Варианты числа воркеров: от явно недостаточного (10) до избыточного (100).
# При base=100 и burst=5x нужно минимум ~50 воркеров, чтобы абсорбировать 500 req/s.
WORKER_COUNTS  = [10, 20, 30, 50, 75, 100]

# Два seed для усреднения p95 (убирает случайный шум).
SEEDS          = [42, 43]


def main():
    results = []
    # Общее число симуляций для отображения прогресса.
    total = len(ARRIVAL_RATES) * len(WORKER_COUNTS) * len(SEEDS)
    done  = 0

    for base_rate in ARRIVAL_RATES:
        for workers in WORKER_COUNTS:
            # Запускаем симуляцию для каждого seed.
            runs = []
            for seed in SEEDS:
                cfg = Config(
                    base_arrival_rate=float(base_rate),
                    num_search_workers=workers,
                    seed=seed,
                )
                runs.append(run(cfg))
            done += len(SEEDS)

            # avg(key) — среднее значение метрики по всем seed-прогонам.
            # None пропускается (бывает, если вообще нет успешных запросов).
            def avg(key):
                vals = [r[key] for r in runs if r[key] is not None]
                return sum(vals) / len(vals) if vals else None

            # Одна строка = одна точка на будущем графике.
            # config из первого прогона (seeds одинаковы по всем параметрам кроме seed).
            base_config = {**runs[0]["config"], "seeds": SEEDS}
            row = {
                "config":             base_config,
                "base_arrival_rate":  base_rate,
                "num_search_workers": workers,
                "success_rate":       avg("success_rate"),
                "throughput_rps":     avg("throughput_rps"),
                # eff_latency_p95 — честная метрика: тайм-ауты считаются как 0.5 с.
                # Именно она показывает реальный опыт пользователей.
                "eff_latency_p95":    avg("eff_latency_p95"),
                # latency_p95 — только успешные (нужна для наглядности survivorship bias).
                "latency_p95":        avg("latency_p95"),
                "dropped_timeout":    avg("dropped_timeout"),
            }
            results.append(row)

            # Прогресс в консоль: при насыщении success падает и eff_p95 растёт.
            pct  = 100 * done / total
            sr   = row["success_rate"]    or 0
            ep95 = row["eff_latency_p95"] or 0
            print(
                f"  [{pct:5.1f}%] rate={base_rate:4d}/s  workers={workers:3d}"
                f"  success={sr:.3f}  eff_p95={ep95:.4f}s",
                flush=True,
            )

    # --- Сохраняем результаты ---
    # CSV — для просмотра в Excel / pandas.
    fieldnames = list(results[0].keys())
    with open("sweep_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # JSON — читается plot_sweep.py.
    with open("sweep_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved sweep_results.csv and sweep_results.json ({len(results)} rows)")


if __name__ == "__main__":
    main()
