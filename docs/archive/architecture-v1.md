# twotakt / Architecture

## Vision

Natural language interface to discrete-event simulation.
The user describes a system. Claude builds a model, runs scenarios, explains results.

---

## User Journey

```
User → Claude Code (natural language)
Claude → clarifies scenario with user
Claude → calls MCP tools
MCP   → runs SimPy simulation
SimPy → returns results to Claude
Claude → explains or visualizes
```

---

## MCP Tools (8)

### build_model
Creates or refines a simulation model. Iterative — each call returns the same or new model_id.

```
build_model(
  resources: [...],       # list of Resource definitions
  activities: [...],      # list of ActivityType definitions
  sim: SimConfig,
  model_id: str | None    # None → new model, str → refine existing
) → model_id: str
```

If `model_id` is provided: load existing model, merge new params, return same id.
Claude calls this multiple times as the user refines the system description.

### run_bench
Runs a single simulation scenario against a model.
Claude decides which arrival rates to test — after discussing with the user.
Optional overrides allow what-if without rebuilding the model.

```
run_bench(
  model_id: str,
  arrival_rate: float,          # requests per second (scenario param)
  duration: float,              # simulation time in seconds
  tick: float,                  # time resolution (default 0.01)
  overrides: dict | None        # e.g. {"api.capacity": 200} — what-if
) → BenchResult
```

**BenchResult:**
```
{
  model_id: str,
  arrival_rate: float,
  overrides: dict,
  completed: int,               # activities that finished
  rejected: int,                # rejected (overflow=reject)
  response_times: [float],      # total time per activity (all steps)
  per_resource_utilization: {   # resource_id → [utilization per tick]
    "api": [0.8, 0.9, ...],
    "db":  [0.3, 0.4, ...]
  }
}
```

### show_model
Renders the model as a directed graph. Nodes are Resources and Activities, edges show demand relationships.

```
show_model(model_id: str) → image
```

Node labels: id, capacity/demand, duration, arrival_rate.
Edge labels: demand units consumed.
Claude shows this to the user to confirm the model before running simulations.

### load_model_from_graph
Loads or updates a model from a graph structure — the inverse of show_model.
Allows user to describe the model visually or paste a graph definition.

```
load_model_from_graph(
  graph: {
    nodes: [{id, type, ...params}],
    edges: [{from, to, demand}]
  },
  model_id: str | None    # None → new model, str → replace existing
) → model_id: str
```

### plot_histogram
Renders a histogram from data Claude already holds in context.

```
plot_histogram(
  data: {label: [float]}, # {scenario_label: response_times}
  title: str
) → image
```

---

## Core Models

twotakt-core оперирует общими примитивами дискретно-событийного симулятора:

```python
@dataclass
class Resource:
    id: str
    capacity: int           # общий ресурс (единицы)
    overflow: str           # "reject" | "degrade"

@dataclass
class Step:
    id: str
    resource_id: str
    demand: int             # единиц ресурса потребляет
    duration: float         # время при полном ресурсе
    next: list[tuple[str, float]]  # [(step_id, probability), ...], [] = done

@dataclass
class ActivityType:
    id: str
    entry: str              # id первого шага
    steps: list[Step]       # все шаги — граф с вероятностями

@dataclass
class SimConfig:
    duration: float
    tick: float = 0.01
    seed: int = 42
```

`arrival_rate` — параметр сценария (бенча), не модели.
Модель описывает *структуру* системы. Бенч описывает *нагрузку*.

Конкретные сущности (сервер, запрос, пациент, грузовик, автобус) — это **домен пользователя**.
Claude переводит описание пользователя в эти примитивы при вызове `build_model`.

**Граф — это модель.** Ресурсы образуют граф, активности движутся по нему.
Неважно что течёт — запросы через API→DB или автобусы через остановки.
Топология графа задаётся порядком шагов в `ActivityType.steps`.

```
API система:   request → [api: 1s] → [db: 0.05s] → done
Автобус:       bus     → [stop_A: 2min] → [stop_B: 2min] → [stop_C: 2min] → done
Склад:         order   → [picking: 5min] → [packing: 3min] → [dispatch: 1min] → done
```

Вероятностное ветвление — часть модели. Каждый шаг знает куда идти дальше и с какой вероятностью:

```
# кэш: 80% попадание, 20% идёт в DB
api_step.next = [("cache_hit", 0.8), ("db_query", 0.2)]

# последовательный pipeline — вероятность 1.0
api_step.next = [("db_step", 1.0)]

# конец пути
db_step.next = []
```

---

## Пример: API сервер под нагрузкой

Пользователь говорит: *"1 инстанс, 10% на запрос, 1с, деградация"*

Claude вызывает:
```
build_model(
  resources=[{id:"api", capacity:100, overflow:"degrade"}],
  activities=[{id:"request", resource:"api", demand:10, duration:1.0, arrival_rate:10}],
  sim={duration:300}
)
```

Это один из бесчисленных возможных сценариев. twotakt-core не знает что такое "инстанс" или "запрос" — он знает только Resource и Activity.

---

## Simulation Engine

**Processor sharing** при `overflow=degrade`:

```
every tick dt:
  rate = resource.capacity / sum(active activity demands)
  for each active activity:
    progress += rate * dt
    if progress >= 1.0 → complete, remove
```

**При `overflow=reject`:** если `sum(demands) + new_demand > capacity` → активность отклоняется.

---

## Persistence

Work is saved as a **workspace** — a directory containing model definition and bench results.

```
~/.twotakt/workspaces/
  my-api-v1/
    model.json       # Instance, overflow strategy
    benches/
      run_001.json   # arrival_rate, duration, results
      run_002.json
  colleague-shared/
    model.json
    benches/
      ...
```

Three additional MCP tools:

```
save_workspace(name)        → saves current model + all bench results
load_workspace(name)        → restores model + results into Claude context
list_workspaces()           → shows available workspaces (own + shared)
```

Sharing: workspaces are plain directories — can be copied, sent, placed in shared folder.
Claude loads a workspace and continues from where another user left off.

---

## Component Boundaries

| Component      | Responsibility                                      |
|----------------|-----------------------------------------------------|
| Claude Code    | NL understanding, scenario selection with user, result interpretation |
| twotakt-mcp    | MCP server, 6 tools, workspace I/O                  |
| twotakt-core   | SimPy engine, tick loop, statistics collection      |
| Workspace      | JSON files on disk — model + bench results          |

Claude holds simulation results in context.
MCP and core are stateless executors — no interpretation, no decisions.

---

## Out of Scope (for now)

- Queue (waiting room for requests)
- Multi-instance / load balancing
- Real metrics ingestion (probe)
- Time-varying arrival rates
