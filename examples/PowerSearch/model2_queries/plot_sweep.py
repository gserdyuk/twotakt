"""
График перебора параметров — User Query Pipeline (Модель 2).

Три панели на одном рисунке (общая ось X = базовая нагрузка в req/s):

  Панель 1 — Пропускная способность (req/s).
    Идеальная пунктирная линия y = x: при здоровой системе throughput
    равен arrival rate. Отклонение вниз означает дропы — часть пользователей
    не получила ответ.

  Панель 2 — Success rate (доля запросов, получивших ответ).
    Оранжевая линия = 99% — минимальный приемлемый уровень.
    При снижении ниже этой отметки система явно деградирует.

  Панель 3 — Время ответа p95 в секундах (логарифмическая шкала по Y).
    Красная пунктирная линия = SLA = 500 мс.
    Сплошные линии = effective p95 (честная: тайм-ауты считаются как 0.5 с).
    Пунктирные линии = raw p95 только успешных (диагностика survivorship bias).

    Survivorship bias на этом графике:
      Когда система перегружена, медленные запросы дропаются по таймауту.
      В выборке успешных остаются только быстрые. Raw p95 (пунктир) выглядит
      нормально, а eff p95 (сплошная) показывает реальную картину.
      Расхождение сплошной и пунктирной линий = "зона bias".

    Почему log-шкала:
      Latency при перегрузке растёт на порядки; линейная шкала "сплющивает"
      здоровую зону. На log-шкале все три фазы visible одновременно:
      healthy (низкая плоская часть), knee (перегиб у SLA), degraded (плато = SLA).

  Burst-нагрузка учтена в самой симуляции (sweep.py), поэтому все метрики
  уже включают эффект всплесков. Графики отражают средневзвешенное поведение
  за всё 600-секундное окно, включая 5 burst-эпизодов.

Предварительно запустите sweep.py для генерации sweep_results.json.
"""

import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# SLA для этой модели — p95 должен быть меньше 500 мс.
SLA_SECONDS = 0.5
INPUT_FILE  = "sweep_results.json"
OUTPUT_FILE = "sweep_plot.png"


def load(path: str = INPUT_FILE) -> list:
    """Загружает результаты sweep из JSON-файла."""
    with open(path) as f:
        return json.load(f)


def main():
    data = load()

    # Группируем строки по num_search_workers: каждая группа — одна кривая.
    by_workers: dict[int, list] = defaultdict(list)
    for row in sorted(data, key=lambda r: (r["num_search_workers"], r["base_arrival_rate"])):
        by_workers[row["num_search_workers"]].append(row)

    worker_counts = sorted(by_workers.keys())

    # Цветовая шкала plasma: от фиолетового (мало воркеров) до жёлтого (много).
    # linspace(0.1, 0.9) обрезает почти-белые края палитры.
    colors = plt.cm.plasma(np.linspace(0.1, 0.9, len(worker_counts)))

    # Три субграфика в колонку; sharex=True = общая ось X для всех панелей.
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    fig.suptitle(
        "PowerSearch — User Query Pipeline Capacity Sweep\n"
        "Two cascaded M/M/c queues: search workers -> ES query pool  |  5x bursts 30 s/120 s",
        fontsize=12,
    )
    ax_thr, ax_sr, ax_lat = axes

    for workers, color in zip(worker_counts, colors):
        rows    = by_workers[workers]
        # Точки по оси X — базовая нагрузка (burst = base * 5 внутри симуляции).
        xs      = [r["base_arrival_rate"]  for r in rows]
        thr     = [r["throughput_rps"]     for r in rows]
        sr      = [r["success_rate"]       for r in rows]
        eff_p95 = [r["eff_latency_p95"]    for r in rows]
        # raw_p95 может быть None при тотальном дропе — заменяем 0.
        raw_p95 = [r["latency_p95"] or 0   for r in rows]

        lbl = f"{workers} workers"
        ax_thr.plot(xs, thr,     marker="o", ms=4, color=color, label=lbl)
        ax_sr.plot( xs, sr,      marker="o", ms=4, color=color)
        # Сплошная — effective p95 (правильная для сравнения с SLA).
        # Пунктир  — raw p95 (видна разница = survivorship bias).
        ax_lat.plot(xs, eff_p95, marker="o", ms=4, color=color, label=f"{workers}w eff")
        ax_lat.plot(xs, raw_p95, marker="x", ms=3, color=color, ls="--", alpha=0.45,
                    label=f"{workers}w raw")

    # --- Идеальная пропускная способность: y = arrival_rate ---
    # При здоровой системе throughput = arrival rate (все запросы обработаны).
    # Реальные кривые отклоняются вниз при насыщении.
    all_rates = sorted(set(r["base_arrival_rate"] for r in data))
    ax_thr.plot(all_rates, all_rates, "k--", lw=1, alpha=0.45, label="ideal  y = x")

    # --- Красная линия SLA = 0.5 с на панели задержки ---
    ax_lat.axhline(SLA_SECONDS, color="red", lw=1.5, ls=":", label=f"SLA = {SLA_SECONDS} s")

    # --- Форматирование панелей ---
    ax_thr.set_ylabel("Throughput (req/s)")
    ax_thr.legend(fontsize=8, loc="upper left")
    ax_thr.grid(True, alpha=0.3)

    ax_sr.set_ylabel("Success rate")
    ax_sr.set_ylim(-0.05, 1.05)
    # Оранжевая линия = минимальный приемлемый success_rate (99%).
    ax_sr.axhline(0.99, color="orange", lw=1, ls=":", alpha=0.7)
    ax_sr.grid(True, alpha=0.3)
    ax_sr.legend(
        [f"{w}w" for w in worker_counts], fontsize=8, loc="lower left", title="workers"
    )

    ax_lat.set_ylabel("p95 response time (s)")
    # Логарифмическая шкала: одновременно видны миллисекунды и 0.5-секундный SLA.
    ax_lat.set_yscale("log")
    ax_lat.legend(fontsize=7, loc="upper left", ncol=2)
    # which="both" добавляет сетку и на основных, и на вспомогательных делениях.
    ax_lat.grid(True, alpha=0.3, which="both")

    axes[-1].set_xlabel("Base arrival rate (req/s)")

    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches="tight")
    print(f"Saved {OUTPUT_FILE}")
    plt.show()


if __name__ == "__main__":
    main()
