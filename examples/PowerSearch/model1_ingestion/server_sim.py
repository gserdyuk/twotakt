"""
SimPy simulation — PowerSearch Ingestion Pipeline (Model 1).

Что моделируется:
  Кролеры PowerSearch непрерывно обходят сайты ресейлеров и отправляют
  события обновления цен в Kafka. Воркеры читают эти события, нормализуют
  схему, проверяют на дубли, детектируют изменение цены и пишут результат
  в Elasticsearch. После этого товар становится видимым пользователям.

Структура модели — две последовательные ограниченные очереди (M/M/c):
  Kafka → [очередь] → воркеры обработки → [очередь] → пул коннектов ES → готово

Ключевые вопросы, на которые отвечает модель:
  - Сколько воркеров нужно, чтобы уложиться в SLA 10 с при N ресейлерах?
  - Где узкое место при росте: воркеры или пул коннектов ES?

Запуск: python server_sim.py   (smoke test)
Sweep:  python sweep.py        (полный перебор параметров)
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass
from typing import Optional

import simpy  # дискретно-событийный симулятор: время продвигается скачками от события к событию


# ---------------------------------------------------------------------------
# Config — единственное место, где живут все числа модели.
# Правило: ни одной "магической" константы вне этого класса.
# Это позволяет sweep.py перебирать любые сочетания параметров без правки кода.
# ---------------------------------------------------------------------------

@dataclass
class Config:

    # --- Нагрузка --------------------------------------------------------
    # Интенсивность входного потока = num_resellers * update_rate_per_reseller.
    # num_resellers — основная swept-переменная: Год 1 = 15, Год 5 = 115.
    num_resellers: int = 15

    # Сколько событий в секунду генерирует один ресейлер.
    # 10 событий/с ≈ 10 000 товаров за ~17 мин непрерывного обхода.
    update_rate_per_reseller: float = 10.0

    sim_time: float = 600.0   # длительность симуляции в секундах (10 минут)
    seed: int = 42             # зерно ГСЧ — для воспроизводимости результатов

    # --- Время обработки одного события ----------------------------------
    # Нормализация + дедупликация + детектирование изменения цены.
    # Используется экспоненциальное распределение: среднее = processing_time_mean,
    # но конкретное значение для каждого события — случайное.
    processing_time_mean: float = 0.05   # 50 мс на воркере

    # Запись документа в Elasticsearch (один REST-запрос, сетевой I/O).
    es_indexing_time_mean: float = 0.15  # 150 мс на ES-коннект

    # --- Ограниченные ресурсы (пулы) ------------------------------------
    # Каждый пул моделируется как simpy.Resource(capacity=N).
    # Если все N слотов заняты — событие встаёт в очередь и ждёт.

    num_workers: int = 10    # размер пула воркеров обработки (вторичная sweep-переменная)
    es_pool_size: int = 200  # количество коннектов к ES для индексации

    # --- Деградация по закону USL (Universal Scalability Law) -----------
    # При alpha=beta=0 модель — чистый M/M/c (нет деградации от конкуренции).
    # Поля оставлены для будущих экспериментов: что если воркеры делят CPU?
    # alpha — линейная деградация (закон Амдала: сериализованные секции кода)
    # beta  — квадратичная деградация (contention: lock-convoy, cache coherency)
    alpha: float = 0.0
    beta: float = 0.0

    # --- Защитные механизмы (backpressure) ------------------------------
    # max_threads: жёсткий лимит на одновременно обрабатываемых событий.
    #   None = без лимита (очередь Kafka бесконечна в данной модели).
    max_threads: Optional[int] = None

    # sla_seconds: дедлайн на полное прохождение пайплайна.
    #   Если событие не прошло оба пула за 10 с — оно считается "потерянным".
    sla_seconds: Optional[float] = 10.0


# ---------------------------------------------------------------------------
# RequestRecord — паспорт одного события на всём его пути через систему.
# Заполняется постепенно: arrival при создании, start когда получен воркер,
# finish когда ES-запись завершена (или SLA истёк).
# ---------------------------------------------------------------------------

@dataclass
class RequestRecord:
    rid: int             # порядковый номер события (для отладки)
    arrival: float       # момент прихода в систему (симулированное время, секунды)
    start: Optional[float] = None    # момент, когда событие захватило воркер
    finish: Optional[float] = None   # момент завершения (успех или дроп)
    outcome: str = "pending"         # итог: ok | dropped_buffer | dropped_timeout

    @property
    def wait(self) -> Optional[float]:
        """Время ожидания в очереди до первого воркера (= start - arrival).
        Растёт при перегрузке воркерного пула."""
        return None if self.start is None else self.start - self.arrival

    @property
    def latency(self) -> Optional[float]:
        """Сквозная latency от прихода события до его видимости в ES.
        Это и есть та метрика, которую сравниваем с SLA 10 с."""
        return None if self.finish is None else self.finish - self.arrival


# ---------------------------------------------------------------------------
# IngestionServer — главный объект симуляции.
# Владеет двумя пулами-ресурсами и списком записей о каждом событии.
# ---------------------------------------------------------------------------

class IngestionServer:
    def __init__(self, env: simpy.Environment, cfg: Config):
        self.env = env
        self.cfg = cfg

        # simpy.Resource — это очередь + счётчик занятых слотов.
        # capacity = сколько событий может обрабатываться одновременно.
        # Остальные встают в виртуальную очередь и ждут освобождения слота.
        self.workers = simpy.Resource(env, capacity=cfg.num_workers)
        self.es_pool = simpy.Resource(env, capacity=cfg.es_pool_size)

        # Счётчик событий, находящихся "в системе" (включая ожидающих в очереди).
        # Нужен для формулы USL; при alpha=beta=0 не влияет на результат.
        self.active = 0

        self.records: list[RequestRecord] = []  # история всех событий

    def degradation_multiplier(self, n_active: int) -> float:
        """Вычисляет замедление воркера по закону USL при n_active конкурентных событиях.

        При alpha=beta=0 всегда возвращает 1.0 (замедления нет — чистый M/M/c).
        При alpha>0 появляется линейное замедление: воркеры делят CPU или блокируются.
        При beta>0 добавляется квадратичное замедление: cache-flush, lock-convoy.

        Формула: slowdown = 1 + alpha*(N-1) + beta*N*(N-1)
        """
        a, b = self.cfg.alpha, self.cfg.beta
        n = max(n_active, 1)
        return 1.0 + a * (n - 1) + b * n * (n - 1)

    def handle_request(self, rid: int):
        """Точка входа каждого нового события. Это SimPy-генератор:
        вместо обычных вызовов функций используется 'yield' — симулятор
        приостанавливает генератор до наступления нужного события во времени.

        Логика:
        1. Зарегистрировать событие.
        2. Если пул переполнен (max_threads) — отклонить немедленно.
        3. Иначе — запустить _serve() под часами SLA.
           Если SLA истёк до завершения — прервать _serve() и записать дроп.
        """
        rec = RequestRecord(rid=rid, arrival=self.env.now)
        self.records.append(rec)

        # Жёсткий лимит на буфер (аналог reject при полной очереди).
        cap = self.cfg.max_threads
        if cap is not None and self.active >= cap:
            rec.outcome = "dropped_buffer"
            rec.finish = self.env.now
            return  # в генераторе без yield — процесс завершается мгновенно

        self.active += 1
        try:
            sla = self.cfg.sla_seconds
            if sla is None:
                # Без SLA — ждём сколько угодно.
                yield self.env.process(self._serve(rec))
            else:
                # Запускаем _serve() и одновременно таймер SLA.
                # "inner | deadline" — ждём того, кто сработает первым.
                inner = self.env.process(self._serve(rec))
                deadline = self.env.timeout(sla)
                result = yield inner | deadline

                if inner not in result:
                    # Таймер сработал раньше _serve() — событие опоздало.
                    # interrupt() посылает исключение внутрь _serve(),
                    # что приводит к освобождению занятых ресурсов.
                    inner.interrupt()
                    rec.outcome = "dropped_timeout"
                    rec.finish = self.env.now
        finally:
            # finally гарантирует, что счётчик уменьшится даже при дропе.
            self.active -= 1

    def _serve(self, rec: RequestRecord):
        """Жизненный цикл одного события: два последовательных пула.

        Это тоже генератор SimPy. Каждый 'yield' означает "жди, пока не произойдёт X":
          - yield req   → жди свободного слота в пуле воркеров
          - yield conn  → жди свободного коннекта к ES
          - yield timeout → жди истечения времени обработки

        Конструкция 'with resource.request() as req' автоматически
        освобождает слот при выходе из блока (даже при прерывании).
        """
        cfg = self.cfg
        try:
            # === Фаза 1: воркер обработки ===================================
            # Событие встаёт в очередь к пулу воркеров и ждёт свободного слота.
            with self.workers.request() as req:
                yield req  # <-- симулятор передаёт управление другим процессам, пока слот занят

                # Фиксируем момент начала обработки (= конец ожидания в очереди).
                if rec.start is None:
                    rec.start = self.env.now

                # Время обработки = экспоненциальная случайная величина * коэффициент USL.
                # expovariate(1/mean) генерирует значения со средним = mean.
                # При alpha=beta=0 mult=1.0, поэтому USL не меняет ничего.
                mult = self.degradation_multiplier(self.active)
                yield self.env.timeout(
                    random.expovariate(1.0 / cfg.processing_time_mean) * mult
                )
            # Слот воркера освобождается здесь (выход из 'with').

            # === Фаза 2: коннект к Elasticsearch ============================
            # После воркера событие встаёт в очередь к пулу ES-коннектов.
            # Это второй "узкий ресурс": при большом числе ресейлеров он
            # может стать узким местом даже при достаточных воркерах.
            with self.es_pool.request() as conn:
                yield conn  # ждём свободного ES-коннекта

                # Время записи в ES (сетевой I/O: HTTP-запрос + ответ).
                yield self.env.timeout(
                    random.expovariate(1.0 / cfg.es_indexing_time_mean)
                )
            # Коннект освобождается здесь. Товар теперь видим в индексе.

            rec.outcome = "ok"
            rec.finish = self.env.now

        except simpy.Interrupt:
            # Получено прерывание от handle_request() (SLA истёк).
            # SimPy автоматически освобождает все удерживаемые ресурсы
            # при выходе из блоков 'with', поэтому утечек не будет.
            return


# ---------------------------------------------------------------------------
# arrival_process — генератор входного потока событий.
# Моделирует поток Kafka-событий от всего парка кролеров.
# ---------------------------------------------------------------------------

def arrival_process(env: simpy.Environment, server: IngestionServer):
    """Пуассоновский поток с постоянной интенсивностью.

    Пуассоновский поток — стандартная модель "независимых редких событий":
    каждое событие приходит независимо, среднее число в единицу времени = rate.
    Интервал между событиями распределён экспоненциально с параметром rate.

    Интенсивность = num_resellers * update_rate_per_reseller.
    При 15 ресейлерах по 10 событий/с = 150 событий/с суммарно.
    """
    rid = 0
    # Общая интенсивность = сумма всех кролеров (суперпозиция пуассоновских потоков).
    rate = server.cfg.num_resellers * server.cfg.update_rate_per_reseller
    while True:
        # Ждём случайный интервал (экспоненциальное распределение с мат. ожиданием 1/rate).
        yield env.timeout(random.expovariate(rate))
        # Запускаем обработку нового события как отдельный параллельный процесс SimPy.
        # env.process() не блокирует: генератор arrival_process продолжает работу,
        # пока handle_request выполняется независимо.
        env.process(server.handle_request(rid))
        rid += 1


# ---------------------------------------------------------------------------
# run / summarize — запуск симуляции и сбор метрик.
# ---------------------------------------------------------------------------

def run(cfg: Config) -> dict:
    """Запускает одну симуляцию с заданной конфигурацией и возвращает метрики."""
    random.seed(cfg.seed)          # фиксируем ГСЧ для воспроизводимости
    env = simpy.Environment()      # создаём симулированные "часы"
    server = IngestionServer(env, cfg)
    env.process(arrival_process(env, server))  # регистрируем генератор событий
    env.run(until=cfg.sim_time)    # прокручиваем время до cfg.sim_time секунд
    return summarize(server, cfg)


def _percentile(xs: list, p: float):
    """Возвращает p-й перцентиль списка xs.

    Перцентиль P означает: P% значений меньше или равны этому числу.
    p95 latency = 95% запросов обработаны быстрее этого значения.
    """
    if not xs:
        return None
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round((p / 100.0) * (len(xs) - 1)))))
    return xs[k]


def summarize(server: IngestionServer, cfg: Config) -> dict:
    """Агрегирует записи о каждом событии в итоговые метрики.

    ВАЖНО: всегда включает effective latency и success_rate.
    Нельзя убирать — это требование метрик-чеклиста (Phase 8 протокола).

    Почему effective latency важнее raw latency:
      При перегрузке успешные запросы — это те, кто успел до дедлайна.
      Медленные запросы упали по таймауту. Если смотреть только на успешные,
      p95 выглядит нормально, хотя половина запросов уже дропается.
      Effective latency = latency успешных + sla_seconds для каждого дропа.
      Это честная картина из перспективы пользователя.
    """
    recs = server.records

    ok          = [r for r in recs if r.outcome == "ok"]
    dropped_buf = sum(1 for r in recs if r.outcome == "dropped_buffer")
    dropped_to  = sum(1 for r in recs if r.outcome == "dropped_timeout")

    latencies = [r.latency for r in ok]   # только успешные (сырая latency)
    waits     = [r.wait    for r in ok]   # время ожидания воркера у успешных

    # Effective latency: дропы по таймауту считаются как sla_seconds.
    sla = cfg.sla_seconds
    latencies_eff = latencies + [sla] * dropped_to if sla is not None else latencies

    return {
        "config":        cfg.__dict__.copy(),
        "arrival_rate":  cfg.num_resellers * cfg.update_rate_per_reseller,

        # --- Счётчики событий ---
        "total_arrivals":  len(recs),      # всего пришло
        "completed_ok":    len(ok),         # успешно прошли оба пула
        "dropped_buffer":  dropped_buf,     # отклонены из-за max_threads (буфер переполнен)
        "dropped_timeout": dropped_to,      # не уложились в SLA

        # --- Основные метрики производительности ---
        # success_rate = доля событий, дошедших до ES. При перегрузке падает ниже 1.
        "success_rate":    len(ok) / len(recs) if recs else None,
        # throughput = сколько событий реально проиндексировано в секунду.
        # При перегрузке throughput отстаёт от arrival_rate.
        "throughput_rps":  len(ok) / cfg.sim_time,

        # --- Latency успешных запросов (сырая, только OK) ---
        # ОСТОРОЖНО при перегрузке: это смещённая выборка (survivorship bias).
        "latency_mean": statistics.mean(latencies) if latencies else None,
        "latency_p50":  _percentile(latencies, 50),
        "latency_p95":  _percentile(latencies, 95),
        "latency_p99":  _percentile(latencies, 99),

        # --- Effective latency (честная метрика для SLA) ---
        # Дропы по таймауту считаются как sla_seconds.
        # Именно эту метрику нужно сравнивать с SLA = 10 с.
        "eff_latency_p50": _percentile(latencies_eff, 50),
        "eff_latency_p95": _percentile(latencies_eff, 95),
        "eff_latency_p99": _percentile(latencies_eff, 99),

        # Среднее время ожидания воркера (у успешных).
        # Если wait_mean ≈ 0 — очереди нет, система здорова.
        # Если растёт — воркеров не хватает.
        "wait_mean": statistics.mean(waits) if waits else None,
    }


def print_result(r: dict, header: str = ""):
    if header:
        print(header)
    cfg = r["config"]
    print(
        f"  resellers={cfg['num_resellers']}  workers={cfg['num_workers']}  "
        f"es_pool={cfg['es_pool_size']}  arrival={r['arrival_rate']:.0f}/s"
    )
    for k, v in r.items():
        if k in ("config", "arrival_rate"):
            continue
        if isinstance(v, float):
            print(f"  {k:24s} {v:.4f}")
        else:
            print(f"  {k:24s} {v}")


if __name__ == "__main__":
    # Smoke test: Год 1 — ожидаем здоровую систему (success_rate ≈ 1.0)
    print_result(run(Config()), header="=== Smoke test: Year 1 (15 resellers, 10 workers) ===")
    print()

    # Год 5 с дефолтными 10 воркерами — ожидаем перегрузку
    print_result(
        run(Config(num_resellers=115, num_workers=10)),
        header="=== Year 5 load, 10 workers (expected: overloaded) ===",
    )
    print()

    # Год 5 с 60 воркерами — ожидаем стабильную работу
    print_result(
        run(Config(num_resellers=115, num_workers=60)),
        header="=== Year 5 load, 60 workers (expected: stable) ===",
    )
