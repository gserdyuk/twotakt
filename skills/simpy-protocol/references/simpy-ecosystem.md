# SimPy Ecosystem — Research Results

> Исследование проведено 2026-05. Использовать для улучшения simpy-protocol скилла
> и как базу для будущего simpy-reference скилла.

---

## Релевантно для simpy-protocol (IT-инфраструктура)

| Проект | Что моделирует | Чем полезен для скилла |
|---|---|---|
| [yinchi/simpy-examples](https://github.com/yinchi/simpy-examples) | M/M/c queueing системы | Учебные примеры, сравнение паттернов |
| [ccfelius/queueing](https://github.com/ccfelius/queueing) | M/M/c с переменным числом серверов | Альтернативный подход к sweep |
| [ajdinm/lb-sim](https://github.com/ajdinm/lb-sim) | Load balancer | Паттерн распределения нагрузки |
| [MiSim](https://dqualizer.github.io/files/QRS22-FrankWagnerHakamianStraesserVanHoorn2022MiSim-preprint-nodoi.pdf) | Resilience микросервисов: circuit breaker, fault injection | Retry/backpressure механизмы которые сейчас вне скопа simpy-protocol |
| [the-average-dev/router-simulation](https://github.com/the-average-dev/router-simulation) | Пакетная маршрутизация, throughput/delay/drop | Паттерн для сетевых моделей |
| [SimPy Classic — List of Models](https://simpyclassic.readthedocs.io/en/latest/Manuals/Examples/ListOfModels.html) | Каталог готовых моделей | Справочник паттернов |

**Вывод для simpy-protocol:** MiSim — наиболее интересен. Показывает как моделировать
retry, circuit breaker, fault injection — механизмы которые сейчас в Q7 (out of scope).
При следующем проекте с этими механизмами — изучить MiSim перед расширением скилла.

---

## Ресурсы для будущего simpy-reference скилла (на холде)

### Здравоохранение
- [pythonhealthdatascience](https://github.com/pythonhealthdatascience) — воспроизводимые DES для NHS, большая организация
- [hsma-programme/simpy_visualisation](https://github.com/hsma-programme/simpy_visualisation) — SimPy + визуализация
- [health-data-science-OR/simpy-streamlit-tutorial](https://github.com/health-data-science-OR/simpy-streamlit-tutorial) — SimPy + Streamlit
- [BishnuTimilsena/Hospital-Simulation](https://github.com/BishnuTimilsena/Hospital-Simulation) — ED: регистрация → триаж → осмотр
- [misken/obsimpy](https://github.com/misken/obsimpy) — акушерский поток

### Сети / телекоммуникации
- [TL-System/ns.py](https://github.com/TL-System/ns.py) — зрелый сетевой симулятор (packet gen, links, schedulers)
- [dido18/simpynet](https://github.com/dido18/simpynet) — полный стек TCP/IP
- [altugkarakurt/Network-Simulations](https://github.com/altugkarakurt/Network-Simulations) — учебные сетевые симуляции
- [arman-bd/rpl-simulation](https://github.com/arman-bd/rpl-simulation) — IoT RPL-протокол

### Цепочки поставок и склады
- [anshul-musing/multi-echelon-inventory-optimization](https://github.com/anshul-musing/multi-echelon-inventory-optimization) — SimPy + SciPy + sklearn
- [arpitamangal/supply-chain-bullwhip-effect](https://github.com/arpitamangal/supply-chain-bullwhip-effect) — bullwhip-эффект
- [tpmarsha/FulfillmentCenter](https://github.com/tpmarsha/FulfillmentCenter) — фулфилмент-центр
- [SupplyChainSimulation/InventOpt](https://github.com/SupplyChainSimulation/InventOpt) — metamodel-based оптимизация

### Производство
- [heechulbae/simulation](https://github.com/heechulbae/simulation) — manufacturing + RL dispatch

### Справочники
- [simpy.readthedocs.io](https://simpy.readthedocs.io/) — официальная документация SimPy 4.x
- [SimPy Classic docs](https://simpyclassic.readthedocs.io/en/latest/Manuals/Examples/ListOfModels.html) — каталог старых моделей, много паттернов
- [arxiv 2405.01562](https://arxiv.org/html/2405.01562v1) — «Discrete Event Simulation. It's Easy with SimPy!» — обзорная статья
- [grotto-networking.com/DiscreteEventPython](https://www.grotto-networking.com/DiscreteEventPython.html) — DES для сетей, глубокий туториал
- [github.com/topics/simpy](https://github.com/topics/simpy) — 200+ репозиториев

---

## Паттерны из реальных проектов (повторяются везде)

| Паттерн | SimPy-примитив | Домены |
|---|---|---|
| Bounded pool | `Resource(capacity=N)` | везде |
| Priority queue | `PriorityResource` | healthcare (триаж), сети |
| Bounded buffer с отказом | `Resource` + проверка `len(queue)` | сети, серверы |
| Store / Container | `Store`, `Container` | склад, производство, pipeline |
| Preemption | `PreemptiveResource` | сети, manufacturing |
| Interrupt / cancel | `process.interrupt()` | SLA timeout, circuit breaker |
| Мониторинг в реальном времени | патч `request`/`release` | везде где нужны метрики |
| Визуализация | matplotlib, Streamlit | healthcare, обучение |
