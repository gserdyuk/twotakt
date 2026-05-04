"""
SimPy simulation — PowerSearch User Query Pipeline (Model 2).

Что моделируется:
  Пользователи отправляют поисковые запросы. Запрос обрабатывается search-воркером
  (подготовка и отправка запроса к ES), затем Elasticsearch его выполняет.
  Особенность: нагрузка не постоянная — раз в burst_interval секунд случается
  всплеск в burst_multiplier раз (5x) на burst_duration секунд.

Структура модели — две последовательные ограниченные очереди (M/M/c):
  Запрос → [очередь] → search-воркеры → [очередь] → пул ES-коннектов → ответ

Ключевые вопросы:
  - При каком числе воркеров система удерживает p95 < 500 мс во время всплесков?
  - Как survivorship bias маскирует реальную деградацию (raw vs effective latency)?

Запуск: python server_sim.py   (smoke test + bias check)
Sweep:  python sweep.py        (полный перебор параметров)
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass
from typing import Optional

import simpy


# ---------------------------------------------------------------------------
# Config — все параметры модели в одном месте.
# ---------------------------------------------------------------------------

@dataclass
class Config:

    # --- Базовая нагрузка -----------------------------------------------
    # Пользователи приходят по закону Пуассона со средней интенсивностью base_arrival_rate.
    base_arrival_rate: float = 100.0   # запросов в секунду (в спокойное время)

    # --- Параметры всплеска (burst) -------------------------------------
    # Раз в burst_interval секунд нагрузка резко вырастает в burst_multiplier раз
    # на burst_duration секунд. Это моделирует вечерний пик, маркетинговую акцию
    # или просто неравномерность поведения пользователей.
    burst_multiplier: float = 5.0    # нагрузка во всплеске = base * 5 = 500 req/s
    burst_duration:   float = 30.0   # всплеск длится 30 секунд
    burst_interval:   float = 120.0  # каждые 120 с начинается новый всплеск
    # При sim_time=600 с успеет произойти 5 всплесков — достаточно для стабильного p95.

    sim_time: float = 600.0
    seed: int = 42

    # --- Время обработки одного запроса ---------------------------------
    # Фаза 1: воркер разбирает запрос и формирует ES-запрос.
    search_time_mean: float = 0.02   # 20 мс (быстрая логика)

    # Фаза 2: Elasticsearch выполняет полнотекстовый поиск с фасетами.
    es_query_time_mean: float = 0.08  # 80 мс (сетевой I/O + ES)

    # --- Ограниченные ресурсы (пулы) ------------------------------------
    num_search_workers: int = 25   # основная sweep-переменная
    es_query_pool_size: int = 100  # коннекты к ES для поисковых запросов

    # --- Деградация по USL (зарезервировано) ----------------------------
    # Воркеры I/O-bound, поэтому alpha=beta=0 (нет конкуренции за CPU).
    # При желании можно включить для исследования эффекта CPU-bound воркеров.
    alpha: float = 0.0
    beta:  float = 0.0

    # --- Backpressure ---------------------------------------------------
    max_threads: Optional[int]   = None   # без жёсткого лимита буфера
    sla_seconds: Optional[float] = 0.5   # SLA: p95 должен быть < 500 мс


# ---------------------------------------------------------------------------
# RequestRecord — паспорт одного поискового запроса.
# ---------------------------------------------------------------------------

@dataclass
class RequestRecord:
    rid: int             # порядковый номер запроса
    arrival: float       # время прихода (симулированное время, с)
    start:   Optional[float] = None   # время захвата search-воркера
    finish:  Optional[float] = None   # время получения ответа (или дроп по SLA)
    outcome: str = "pending"          # ok | dropped_buffer | dropped_timeout

    @property
    def wait(self) -> Optional[float]:
        """Ожидание до воркера. При здоровой системе ≈ 0."""
        return None if self.start is None else self.start - self.arrival

    @property
    def latency(self) -> Optional[float]:
        """Сквозная задержка от запроса до ответа. Сравниваем с SLA 500 мс."""
        return None if self.finish is None else self.finish - self.arrival


# ---------------------------------------------------------------------------
# QueryServer — симулятор query-пайплайна.
# ---------------------------------------------------------------------------

class QueryServer:
    def __init__(self, env: simpy.Environment, cfg: Config):
        self.env = env
        self.cfg = cfg

        # Два пула. Если все слоты заняты — запрос ждёт в очереди.
        self.search_workers  = simpy.Resource(env, capacity=cfg.num_search_workers)
        self.es_query_pool   = simpy.Resource(env, capacity=cfg.es_query_pool_size)

        self.active = 0   # запросов "в системе" (ожидающих + обрабатываемых)
        self.records: list[RequestRecord] = []

    def degradation_multiplier(self, n_active: int) -> float:
        """Коэффициент замедления по формуле USL. При alpha=beta=0 всегда 1.0."""
        a, b = self.cfg.alpha, self.cfg.beta
        n = max(n_active, 1)
        return 1.0 + a * (n - 1) + b * n * (n - 1)

    def handle_request(self, rid: int):
        """Точка входа каждого нового запроса.

        Регистрирует запрос, проверяет буфер, запускает _serve() под часами SLA.
        Если таймер SLA срабатывает раньше — прерывает _serve() и записывает дроп.
        """
        rec = RequestRecord(rid=rid, arrival=self.env.now)
        self.records.append(rec)

        cap = self.cfg.max_threads
        if cap is not None and self.active >= cap:
            # Буфер переполнен — немедленный отказ (аналог 503 Too Many Requests).
            rec.outcome = "dropped_buffer"
            rec.finish  = self.env.now
            return

        self.active += 1
        try:
            sla = self.cfg.sla_seconds
            if sla is None:
                yield self.env.process(self._serve(rec))
            else:
                # Гонка двух процессов: _serve vs таймер SLA.
                # Победитель определяется оператором |.
                inner    = self.env.process(self._serve(rec))
                deadline = self.env.timeout(sla)
                result   = yield inner | deadline

                if inner not in result:
                    # Таймер победил — SLA нарушен. Прерываем _serve().
                    inner.interrupt()
                    rec.outcome = "dropped_timeout"
                    rec.finish  = self.env.now
        finally:
            self.active -= 1  # всегда уменьшаем счётчик, даже при дропе

    def _serve(self, rec: RequestRecord):
        """Жизненный цикл запроса: два последовательных пула.

        Фаза 1: захватить воркер → подготовить запрос → освободить воркер.
        Фаза 2: захватить ES-коннект → дождаться ответа ES → освободить коннект.

        При прерывании (SLA истёк) симпи автоматически освобождает все
        удерживаемые ресурсы через context manager 'with'.
        """
        cfg = self.cfg
        try:
            # === Фаза 1: search worker ======================================
            with self.search_workers.request() as req:
                yield req   # ждём свободный слот воркера

                # rec.start — момент начала реальной обработки (конец очереди).
                if rec.start is None:
                    rec.start = self.env.now

                mult = self.degradation_multiplier(self.active)
                # Время подготовки запроса — экспоненциально с мат. ожиданием search_time_mean.
                yield self.env.timeout(
                    random.expovariate(1.0 / cfg.search_time_mean) * mult
                )
            # Воркер освобождён — он может взять следующий запрос из очереди.

            # === Фаза 2: ES query connection ================================
            with self.es_query_pool.request() as conn:
                yield conn  # ждём свободный ES-коннект

                # Время выполнения поиска в ES (полнотекст + фасеты).
                yield self.env.timeout(
                    random.expovariate(1.0 / cfg.es_query_time_mean)
                )
            # ES-коннект освобождён. Ответ готов, latency зафиксирована.

            rec.outcome = "ok"
            rec.finish  = self.env.now

        except simpy.Interrupt:
            # Прерывание от handle_request() — SLA истёк пока запрос ждал или обрабатывался.
            return


# ---------------------------------------------------------------------------
# arrival_process — генератор запросов с периодическими всплесками.
# ---------------------------------------------------------------------------

def arrival_process(env: simpy.Environment, server: QueryServer):
    """Пуассоновский поток с прямоугольной модуляцией (square-wave burst).

    В каждый момент времени определяем: внутри всплеска или нет.
    Если env.now % burst_interval < burst_duration — мы во всплеске,
    и скорость прихода запросов = base * burst_multiplier.
    Иначе — base_arrival_rate.

    Это простейшая модель "прайм-тайма": каждые 120 с система на 30 с
    испытывает 5-кратный рост нагрузки.
    """
    rid = 0
    cfg = server.cfg
    while True:
        # Определяем текущую фазу цикла (0..burst_interval).
        phase = env.now % cfg.burst_interval
        if phase < cfg.burst_duration:
            # Мы во всплеске: интенсивность поднята в burst_multiplier раз.
            rate = cfg.base_arrival_rate * cfg.burst_multiplier
        else:
            # Спокойный период.
            rate = cfg.base_arrival_rate

        # Случайный интервал до следующего запроса (Пуассон ≡ экспоненциальные интервалы).
        yield env.timeout(random.expovariate(rate))
        env.process(server.handle_request(rid))
        rid += 1


# ---------------------------------------------------------------------------
# run / summarize
# ---------------------------------------------------------------------------

def run(cfg: Config) -> dict:
    """Запускает одну симуляцию и возвращает словарь метрик."""
    random.seed(cfg.seed)
    env = simpy.Environment()
    server = QueryServer(env, cfg)
    env.process(arrival_process(env, server))
    env.run(until=cfg.sim_time)
    return summarize(server, cfg)


def _percentile(xs: list, p: float):
    """p-й перцентиль: p% значений меньше или равны результату."""
    if not xs:
        return None
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round((p / 100.0) * (len(xs) - 1)))))
    return xs[k]


def summarize(server: QueryServer, cfg: Config) -> dict:
    """Агрегирует данные всех запросов в итоговые метрики.

    Два вида latency — обязательно оба:
      latency_p95     — сырая p95 только успешных запросов.
                        Вводит в заблуждение при перегрузке (survivorship bias).
      eff_latency_p95 — честная p95: дропы считаются как sla_seconds.
                        Именно её нужно сравнивать с SLA 500 мс.

    Survivorship bias: при перегрузке медленные запросы падают по таймауту.
    В выборке успешных остаются только быстрые. raw p95 выглядит нормально,
    хотя значительная доля пользователей уже получает ошибку таймаута.
    """
    recs = server.records
    ok          = [r for r in recs if r.outcome == "ok"]
    dropped_buf = sum(1 for r in recs if r.outcome == "dropped_buffer")
    dropped_to  = sum(1 for r in recs if r.outcome == "dropped_timeout")

    latencies = [r.latency for r in ok]
    waits     = [r.wait    for r in ok]

    # Effective latency: добавляем sla_seconds за каждый дроп по таймауту.
    sla = cfg.sla_seconds
    latencies_eff = latencies + [sla] * dropped_to if sla is not None else latencies

    return {
        "config":           cfg.__dict__.copy(),
        "total_arrivals":   len(recs),
        "completed_ok":     len(ok),
        "dropped_buffer":   dropped_buf,
        "dropped_timeout":  dropped_to,
        # Доля запросов, получивших ответ. Основная метрика SLA с точки зрения бизнеса.
        "success_rate":     len(ok) / len(recs) if recs else None,
        # Реальная пропускная способность (успешно обработанных запросов в секунду).
        "throughput_rps":   len(ok) / cfg.sim_time,
        # Latency успешных (только для диагностики, не для SLA-проверки).
        "latency_mean":     statistics.mean(latencies) if latencies else None,
        "latency_p50":      _percentile(latencies, 50),
        "latency_p95":      _percentile(latencies, 95),
        "latency_p99":      _percentile(latencies, 99),
        # Effective latency — для SLA-compliance.
        "eff_latency_p50":  _percentile(latencies_eff, 50),
        "eff_latency_p95":  _percentile(latencies_eff, 95),
        "eff_latency_p99":  _percentile(latencies_eff, 99),
        # Среднее время ожидания воркера. ≈0 = здоровая система, растёт = нехватка воркеров.
        "wait_mean":        statistics.mean(waits) if waits else None,
    }


def print_result(r: dict, header: str = ""):
    if header:
        print(header)
    cfg = r["config"]
    print(
        f"  workers={cfg['num_search_workers']}  base_rate={cfg['base_arrival_rate']}/s"
        f"  burst={cfg['burst_multiplier']}x{cfg['burst_duration']}s/{cfg['burst_interval']}s"
    )
    for k, v in r.items():
        if k == "config":
            continue
        if isinstance(v, float):
            print(f"  {k:24s} {v:.4f}")
        else:
            print(f"  {k:24s} {v}")


if __name__ == "__main__":
    # Smoke test: без всплесков — ждём success_rate ≈ 1.0, wait_mean ≈ 0
    print_result(
        run(Config(burst_multiplier=1.0, burst_duration=0.0)),
        header="=== Smoke test: no burst (100 req/s, 25 workers) ===",
    )
    print()

    # Дефолтный сценарий: 5x всплески каждые 120 с
    print_result(
        run(Config()),
        header="=== Default: 5x burst, 30 s every 120 s ===",
    )
    print()

    # Явная перегрузка: 5 воркеров не хватит на пик 500 req/s
    print_result(
        run(Config(num_search_workers=5)),
        header="=== 5 workers (expected: severely overloaded) ===",
    )
    print()

    # Демонстрация survivorship bias: при перегрузке raw p95 < eff p95
    r = run(Config(base_arrival_rate=200, num_search_workers=20))
    raw = r["latency_p95"]    or 0
    eff = r["eff_latency_p95"] or 0
    sr  = r["success_rate"]    or 0
    print("=== Survivorship bias check (200 req/s, 20 workers) ===")
    print(f"  success_rate    {sr:.3f}    <- только {sr*100:.0f}% запросов успешны")
    print(f"  raw p95         {raw:.4f} s  <- 'хорошо выглядит', но это смещённая выборка!")
    print(f"  eff p95         {eff:.4f} s  <- честная картина с учётом дропов")
    print(f"  bias visible    {eff > raw}    <- eff_p95 > raw_p95 = bias подтверждён")
