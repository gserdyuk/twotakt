"""
2D parameter sweep — TEMPLATE.

Когда использовать:
  Когда аудит (Q4b) выявил два независимых параметра для перебора.
  Типичный пример: нагрузка (arrival_rate) × ресурс (num_workers).
  Результат: семейство кривых на графике — одна кривая на значение
  второго параметра.

Предупреждение о ресурсоёмкости:
  Число симуляций = |DIM1| × |DIM2| × |SEEDS|.
  Пример: 10 × 7 × 3 = 210 прогонов. Начинай с грубой сетки,
  сужай диапазон только вокруг колена кривой.

Выход:
  sweep_results.csv  — для анализа в Excel / pandas
  sweep_results.json — читается plot_sweep.py

Структура plot_sweep.py при 2D-свипе:
  x-ось = DIM1, одна кривая = одно значение DIM2.
  (Адаптируй plot_sweep.py из templates/ соответственно.)
"""

import csv
import json

from server_sim import Config, run

# ---------------------------------------------------------------------------
# Сетки параметров — определяются задачей (audit Q4b).
# Размер сетки выбирай сознательно: каждое новое значение умножает время.
# ---------------------------------------------------------------------------

# TODO: заменить на реальный первый параметр из аудита (обычно нагрузка)
DIM1 = [10, 25, 50, 75, 100, 150, 200]   # например, arrival_rate (req/s)

# TODO: заменить на реальный второй параметр из аудита (обычно ресурс)
DIM2 = [5, 10, 20, 40, 80]               # например, num_workers

# Минимум 2 seed для стабилизации p95. При высокой дисперсии увеличь до 5.
SEEDS = [42, 43]


def main():
    results = []
    total = len(DIM1) * len(DIM2) * len(SEEDS)
    done  = 0

    for dim1_val in DIM1:
        for dim2_val in DIM2:
            runs = []
            for seed in SEEDS:
                # TODO: подставить dim1_val и dim2_val в правильные поля Config
                cfg = Config(
                    arrival_rate=float(dim1_val),   # TODO: замени имя поля
                    # num_workers=dim2_val,          # TODO: раскомментируй и замени
                    seed=seed,
                )
                runs.append(run(cfg))
            done += len(SEEDS)

            # Усреднение метрик по seeds: убирает случайный шум p95.
            def avg(key):
                vals = [r[key] for r in runs if r[key] is not None]
                return sum(vals) / len(vals) if vals else None

            row = {
                "dim1":            dim1_val,   # TODO: переименуй в реальный параметр
                "dim2":            dim2_val,   # TODO: переименуй в реальный параметр
                "success_rate":    avg("success_rate"),
                "throughput_rps":  avg("throughput_rps"),
                "eff_latency_p95": avg("eff_latency_p95"),   # честная метрика
                "latency_p95":     avg("latency_p95"),        # только успешные (bias)
                "dropped_timeout": avg("dropped_timeout"),
            }
            results.append(row)

            # Прогресс: убывающий success_rate и рост eff_p95 — признак насыщения.
            pct  = 100 * done / total
            sr   = row["success_rate"]    or 0
            ep95 = row["eff_latency_p95"] or 0
            print(
                f"  [{pct:5.1f}%]  dim1={dim1_val}  dim2={dim2_val}"
                f"  success={sr:.3f}  eff_p95={ep95:.4f}s",
                flush=True,
            )

    # --- Сохраняем оба формата ---
    fieldnames = list(results[0].keys())
    with open("sweep_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    with open("sweep_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved sweep_results.csv and sweep_results.json ({len(results)} rows)")


if __name__ == "__main__":
    main()
