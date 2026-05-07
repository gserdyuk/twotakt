"""
Перебор параметров — Ingestion Pipeline (Модель 1).

Что делает этот скрипт:
  Запускает симуляцию для каждой комбинации (num_resellers, num_workers) и
  собирает ключевые метрики в таблицу. Результаты сохраняются в CSV и JSON
  для дальнейшей визуализации в plot_sweep.py.

Зачем перебирать оба параметра:
  num_resellers — прокси для нагрузки: чем больше ресейлеров, тем выше
  поток Kafka-событий (arrival_rate = num_resellers × update_rate_per_reseller).
  num_workers — основная "ручка настройки": сколько воркеров нужно купить,
  чтобы система выдерживала нагрузку конкретного года роста.

  Пересечение двух кривых на графике (где success_rate начинает падать)
  показывает минимальное num_workers для данного числа ресейлеров.

Зачем несколько seeds:
  p95 задержки — нестабильная метрика: при малой выборке она "прыгает".
  Усреднение по SEEDS=[42, 43] даёт более стабильный результат.
  Для production-анализа лучше брать 5–10 seeds, но 2 уже убирают грубый шум.

Формат вывода:
  Каждая строка = одна (num_resellers, num_workers) пара.
  Столбцы: arrival_rate, success_rate, throughput_rps,
           eff_latency_p95 (честная), latency_p95 (только успешные),
           dropped_timeout (число просроченных запросов).
"""

import csv
import json

from server_sim import Config, run

# ---------------------------------------------------------------------------
# Сетка параметров для перебора.
# ---------------------------------------------------------------------------

# Рост числа ресейлеров: от 15 (Year 1) до 130 (за Year 5).
# Шаг ~15 даёт 9 точек — достаточно, чтобы увидеть колено кривой.
RESELLERS = [15, 30, 45, 60, 75, 90, 105, 115, 130]

# Варианты числа воркеров: от явно недостаточного (5) до заведомо избыточного (80).
# Именно между этими крайностями находится оптимальная точка.
WORKERS   = [5, 10, 20, 30, 40, 60, 80]

# Два фиксированных seed для усреднения p95 (убирает случайный шум).
SEEDS     = [42, 43]


def main():
    results = []
    # Общее число симуляций = len(RESELLERS) × len(WORKERS) × len(SEEDS).
    # Нужно для отображения прогресса.
    total = len(RESELLERS) * len(WORKERS) * len(SEEDS)
    done = 0

    for num_resellers in RESELLERS:
        for num_workers in WORKERS:
            # Запускаем симуляцию для каждого seed и собираем результаты.
            runs = []
            for seed in SEEDS:
                cfg = Config(
                    num_resellers=num_resellers,
                    num_workers=num_workers,
                    seed=seed,
                )
                runs.append(run(cfg))
            done += len(SEEDS)

            # avg(key) — среднее значение метрики по всем seed-прогонам.
            # Пропускаем None (такое бывает, если ни один запрос не завершился успешно).
            def avg(key):
                vals = [r[key] for r in runs if r[key] is not None]
                return sum(vals) / len(vals) if vals else None

            # Одна строка результатов = одна точка на будущем графике.
            row = {
                "num_resellers":   num_resellers,
                "num_workers":     num_workers,
                # arrival_rate одинаков для всех seed при одинаковых num_resellers,
                # берём из первого прогона.
                "arrival_rate":    runs[0]["arrival_rate"],
                "success_rate":    avg("success_rate"),
                "throughput_rps":  avg("throughput_rps"),
                # eff_latency_p95 — честная метрика: дропы считаются как sla_seconds.
                # Именно её нужно сравнивать с бизнес-SLA 10 с.
                "eff_latency_p95": avg("eff_latency_p95"),
                # latency_p95 — только успешные (нужна для диагностики survivorship bias).
                "latency_p95":     avg("latency_p95"),
                "dropped_timeout": avg("dropped_timeout"),
            }
            results.append(row)

            # Прогресс-строка в консоль: [%] resellers=X  workers=Y  success=Z  eff_p95=W
            # success < 1.0 и eff_p95 растущий — сигналы о насыщении системы.
            pct = 100 * done / total
            sr  = row["success_rate"]    or 0
            ep95 = row["eff_latency_p95"] or 0
            print(
                f"  [{pct:5.1f}%] resellers={num_resellers:3d}  workers={num_workers:2d}"
                f"  success={sr:.3f}  eff_p95={ep95:.3f}s",
                flush=True,
            )

    # --- Сохраняем результаты в два формата ---
    # CSV удобен для просмотра в Excel / pandas.
    fieldnames = list(results[0].keys())
    with open("sweep_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # JSON читает plot_sweep.py — структурированный формат проще парсить.
    with open("sweep_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved sweep_results.csv and sweep_results.json ({len(results)} rows)")


if __name__ == "__main__":
    main()
