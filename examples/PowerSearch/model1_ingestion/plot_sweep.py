"""
График перебора параметров — Ingestion Pipeline (Модель 1).

Три панели на одном рисунке (общая ось X = число ресейлеров):

  Панель 1 — Пропускная способность (events/s).
    Показывает, сколько событий система реально успевает обработать.
    Идеальная пунктирная линия y = arrival_rate: при здоровой системе
    все кривые «прижаты» к ней. Как только кривая отходит вниз — воркеров
    не хватает и часть событий дропается по таймауту.

  Панель 2 — Success rate (доля успешно обработанных запросов).
    Главный бизнес-показатель. Горизонтальная оранжевая линия = 99%.
    При success_rate < 0.99 система не выдерживает SLA.

  Панель 3 — Задержка p95 в секундах (логарифмическая шкала по Y).
    Красная пунктирная линия = SLA 10 с.
    Сплошные линии = effective p95 (честная метрика: дропы считаются как 10 с).
    Пунктирные линии = raw p95 только успешных (диагностика bias).

    Почему log-шкала:
      При перегрузке latency растёт экспоненциально; линейная шкала
      "сплющивает" здоровую зону и не позволяет видеть детали у SLA-линии.
      На log-шкале все три фазы (healthy / knee / degraded) видны одновременно.

    Survivorship bias хорошо виден на панели 3: при насыщении сплошная линия
    (eff p95) поднимается к SLA, а пунктирная (raw p95) остаётся ниже —
    медленные запросы вылетают по таймауту и не попадают в raw-выборку.

Предварительно запустите sweep.py для генерации sweep_results.json.
"""

import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# SLA для этой модели — пайплайн должен укладываться в 10 секунд.
SLA_SECONDS = 10.0
INPUT_FILE  = "sweep_results.json"
OUTPUT_FILE = "sweep_plot.png"


def load(path: str = INPUT_FILE) -> list:
    """Загружает результаты sweep из JSON-файла."""
    with open(path) as f:
        return json.load(f)


def main():
    data = load()

    # Группируем строки по num_workers: каждая группа — одна кривая на графике.
    # defaultdict(list) автоматически создаёт новый список при первом обращении.
    by_workers: dict[int, list] = defaultdict(list)
    for row in sorted(data, key=lambda r: (r["num_workers"], r["num_resellers"])):
        by_workers[row["num_workers"]].append(row)

    worker_counts = sorted(by_workers.keys())

    # Цветовая шкала viridis: от фиолетового (мало воркеров) до жёлтого (много).
    # linspace(0.1, 0.9) обрезает крайние (почти белые) значения палитры.
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(worker_counts)))

    # Три субграфика в колонку; sharex=True = одна общая ось X.
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    fig.suptitle(
        "PowerSearch — Ingestion Pipeline Capacity Sweep\n"
        "Two cascaded M/M/c queues: processing workers -> ES indexing pool",
        fontsize=12,
    )
    ax_thr, ax_sr, ax_lat = axes

    for workers, color in zip(worker_counts, colors):
        rows = by_workers[workers]
        # Точки по оси X — число ресейлеров (прокси для нагрузки).
        xs      = [r["num_resellers"]   for r in rows]
        thr     = [r["throughput_rps"]  for r in rows]
        sr      = [r["success_rate"]    for r in rows]
        eff_p95 = [r["eff_latency_p95"] for r in rows]
        # raw_p95 может быть None (если все запросы дропнуты); заменяем 0 для графика.
        raw_p95 = [r["latency_p95"] or 0 for r in rows]

        lbl = f"{workers} workers"
        ax_thr.plot(xs, thr,     marker="o", ms=4, color=color, label=lbl)
        ax_sr.plot( xs, sr,      marker="o", ms=4, color=color)
        # Сплошная линия — честная p95 (effective), пунктир — raw (только успешные).
        ax_lat.plot(xs, eff_p95, marker="o", ms=4, color=color, label=f"{workers}w eff")
        ax_lat.plot(xs, raw_p95, marker="x", ms=3, color=color, ls="--", alpha=0.45,
                    label=f"{workers}w raw")

    # --- Идеальная пропускная способность: y = arrival_rate ---
    # Эта линия — потолок: при неограниченных воркерах throughput = arrival_rate.
    # Отставание реальных кривых от неё показывает потери из-за нехватки ресурсов.
    ideal_xs = sorted(set(r["num_resellers"] for r in data))
    rate_map  = {r["num_resellers"]: r["arrival_rate"] for r in data}
    ideal_ys  = [rate_map[x] for x in ideal_xs]
    ax_thr.plot(ideal_xs, ideal_ys, "k--", lw=1, alpha=0.45, label="ideal  y = arrival rate")

    # --- Красная линия SLA = 10 с на панели задержки ---
    ax_lat.axhline(SLA_SECONDS, color="red", lw=1.5, ls=":", label=f"SLA = {SLA_SECONDS} s")

    # --- Форматирование панелей ---
    ax_thr.set_ylabel("Throughput (events/s)")
    ax_thr.legend(fontsize=8, loc="upper left")
    ax_thr.grid(True, alpha=0.3)

    ax_sr.set_ylabel("Success rate")
    ax_sr.set_ylim(-0.05, 1.05)
    # Оранжевая линия 99% — минимальный приемлемый success_rate.
    ax_sr.axhline(0.99, color="orange", lw=1, ls=":", alpha=0.7)
    ax_sr.grid(True, alpha=0.3)
    ax_sr.legend(
        [f"{w}w" for w in worker_counts], fontsize=8, loc="lower left", title="workers"
    )

    ax_lat.set_ylabel("Pipeline latency (s)")
    # Логарифмическая шкала: позволяет одновременно видеть и миллисекунды, и десятки секунд.
    ax_lat.set_yscale("log")
    ax_lat.legend(fontsize=7, loc="upper left", ncol=2)
    # which="both" добавляет сетку и на основных, и на вспомогательных делениях лог-шкалы.
    ax_lat.grid(True, alpha=0.3, which="both")

    axes[-1].set_xlabel("Number of resellers")

    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches="tight")
    print(f"Saved {OUTPUT_FILE}")
    plt.show()


if __name__ == "__main__":
    main()
