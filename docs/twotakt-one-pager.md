# Twotakt — Audit together. Simulate autonomously.

**AI turns an architecture description into an executable simulation model — in hours, not weeks.**

For IT-systems architects: performance modeling, capacity planning, bottleneck analysis.

---

## Architects don't model. And until now they were right.

Performance decisions are made on experience and intuition, bottlenecks are discovered in production, capacity planning is done in spreadsheets. This was a rational calculation — each alternative had its own cost:

- a **model** required weeks of specialist work and went stale along with the architecture;
- **load testing** requires an already-finished system;
- **spreadsheets** can't see queues and cascading degradations.

At that cost of verification, the architect justifiably relied on intuition.

**The cost of verification just dropped by an order of magnitude. The calculation is due for a rethink.**

## How Twotakt works

At its core are two input documents, each with its own role:

- **Architecture** — components, pools, queues, flows: how the system is built. The architect produces it. **Architecture produces the model.**
- **Requirements** — load, SLA, questions about the system. This is your original spec, not a new document created for the tool; the AI helps shape it in conversation. **Requirements produce the testbench and the acceptance criteria.**

Then:

1. The AI builds an executable model from the architecture and records it in **MODEL.md**: components, flows, assumptions, parameters.
2. From the requirements it assembles load scenarios and criteria — what the model is checked against.
3. **You confirm both the model and the criteria — before the simulation runs.** Misunderstandings are visible and fixed here.
4. The model is compiled into a simulation (SimPy) and run across the scenarios from the requirements.
5. Report: throughput, latencies, queues, bottlenecks, degradation under load — against your acceptance criteria.

The principle is **audit-first**: you trust not the AI, but the model you verified yourself. The AI speeds up construction; the decision about correctness stays with the human. The same dichotomy as in hardware verification: architecture is the design, requirements are the testbench.

## "Models are only approximate anyway"

True — which is why Twotakt doesn't offer exact numbers. It answers questions that are robust to error: **what breaks first** (the order of bottlenecks), **option A or B** (a comparison on identical scenarios), **what happens at 10× load** (the character of degradation). These are exactly the questions intuition answers worst — queues and cascades are nonlinear.

And one more thing: an architect's intuition is also a model, just an implicit one. MODEL.md makes it explicit and presentable: "I'm confident — here's the model and the run" is more convincing in an architecture review board than "I'm confident because of experience."

## What exists now

- A methodology with explicit steps — architecture + requirements → model + acceptance criteria → confirmation → simulation → report; the artifacts are formalized.
- A growing library of examples — four classes of systems: a web backend under load, a backend with a DB pool, a search aggregator (two pipelines, capacity planning), telecom fax processing. Each pilot adds a new class.
- Open source: https://github.com/gserdyuk/twotakt.

## The offer

**Give us your system's architecture and requirements — and two hours of your time.**

The output: a MODEL.md of your system and a bottleneck report. The model will either confirm your expectations — and they turn into a document you can show your team and your client — or reveal something you didn't expect. Before production, not in production.

Gennadiy Serdyuk — gserdyuk@gmail.com / https://www.linkedin.com/in/gserdyuk
