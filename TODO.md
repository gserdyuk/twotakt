# twotakt — TODO

## Identity (locked)

**Name:** twotakt
**Tagline:** An AI-native methodology for building simulation models
**Subtitle:** Two phases: Audit together. Simulate autonomously.

---

## README (done)

### What README should convey in 2 minutes

- What this is (methodology + tool, not just SimPy templates)
- Why (audit-first: understand the system before writing code)
- How to start (entry point)
- Structure (skills/ + examples/)

### Entry points

**A. You have an architecture:**
> "I have a service architecture — I want to find the bottlenecks under load"
→ Open Claude + twotakt → run audit → get model → see where it breaks

**B. You are designing a system:**
> "I'm designing a system — I want to estimate capacity before writing code"
→ Same flow, at design time

Entry phrase for README:
> *"I have an architecture. Where does it break under load?"*

---

## FaxRx — remaining work

- [ ] `plot_sweep.py` — sweep visualisation (4 panels)
- [ ] Run plot, verify curves are readable
- [ ] `SIM_REPORT.md` — final report for FaxRx

---

## Agent architecture — next step

### Design: one dialogue + three agents

```
[Dialogue: audit] ←────────────────────────┐
        ↓                                   │ (if model is wrong)
     MODEL.md → [Agent: build] → [Agent: sweep] → [Agent: report]
      ↑ gate           ↑____________________↑
    human         bugs fixed inside agents
```

- [ ] Phase 2 = three agents: Build → Sweep → Report
- [ ] Each agent: clear input (file) + clear output (file)
- [ ] Build agent: writes server_sim.py, runs smoke test, self-fixes — only ships green
- [ ] Sweep agent: runs sweep, saves JSON
- [ ] Report agent: writes SIM_REPORT.md from JSON + MODEL.md
- [ ] Human reads artifact at each transition and says "go"
- [ ] Return to audit if sweep reveals model mismatch

### Future improvements

- [ ] Auto-orchestrator (remove human from transitions 2→3→4)
- [ ] Living model — agent connected to monitoring, updates parameters via Jain

---

## Product positioning

- [x] Name justified: twotakt = Phase 1 (audit) + Phase 2 (simulation)
- [x] Form: GitHub + README (lab project)
- [x] Entry point defined: "I have an architecture — find the bottlenecks"
- [x] Claude dependency: not a problem at this stage
- [x] README written
