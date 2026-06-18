# LTM & STM Components in Planner Architecture for Annual Budgeting
### Task 2 — Multi-Agent Systems | Planner → Executor → Verifier

---

## 1. Introduction

In AI-powered multi-agent systems using the **Planner Architecture**, memory plays a critical role in how agents reason, plan, and execute tasks. Memory is broadly categorised into two types:

| Memory Type | Full Form | Role in Agent |
|---|---|---|
| **STM** | Short-Term Memory | Holds current session context — active tasks, live results, iteration state |
| **LTM** | Long-Term Memory | Holds persistent knowledge — historical data, past decisions, domain expertise |

When applied to **Annual Budgeting** across domains like Commute, Defence, Agriculture, and Government, the distinction between LTM and STM becomes essential for producing accurate, context-aware budget plans.

---

## 2. Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                  PLANNER ARCHITECTURE                    │
│                                                          │
│   ┌─────────┐    ┌──────────┐    ┌──────────┐           │
│   │ PLANNER │───▶│ EXECUTOR │───▶│ VERIFIER │           │
│   └─────────┘    └──────────┘    └──────────┘           │
│        │               │               │                 │
│   ┌────▼───────────────▼───────────────▼────┐           │
│   │           AgentState (STM)               │           │
│   │  goal | tasks | results | critique |     │           │
│   │  approved | iterations | scores          │           │
│   └──────────────────────────────────────────┘           │
│                        │                                 │
│   ┌────────────────────▼─────────────────────┐           │
│   │           LTM Store (Persistent)          │           │
│   │  past budgets | domain policies |         │           │
│   │  approved results | historical trends     │           │
│   └──────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Short-Term Memory (STM) — Definition & Role

### What is STM?
STM is the **working memory of the current pipeline run**. It exists only for the duration of one agent execution cycle. It is implemented in our architecture as the `AgentState` TypedDict.

### STM Schema (from our implementation)
```python
class AgentState(TypedDict):
    goal:       str          # The current budgeting goal
    tasks:      List[str]    # Tasks broken down by Planner
    results:    List[str]    # Outputs produced by Executor
    critique:   str          # Feedback from Verifier on failure
    approved:   bool         # Whether Verifier approved results
    iterations: int          # How many retry loops have occurred
    scores:     dict         # Quality scores (completeness, accuracy, clarity)
```

### STM Characteristics
- ✅ **Temporary** — cleared after each run
- ✅ **Session-scoped** — only available within the current pipeline execution
- ✅ **Dynamic** — updated at every agent step (Planner → Executor → Verifier)
- ✅ **Fast** — stored in-memory (Python dict / TypedDict)
- ❌ **Not persistent** — lost when the session ends

---

## 4. Long-Term Memory (LTM) — Definition & Role

### What is LTM?
LTM is the **persistent knowledge base** that survives across multiple pipeline runs. It stores approved results, historical budget data, domain-specific policies, and past critiques that can inform future planning decisions.

### LTM Schema (conceptual)
```python
ltm_store = {
    "commute": {
        "approved_budgets": [...],        # Past approved budget plans
        "historical_trends": [...],       # Year-over-year spending trends
        "domain_policies": [...],         # Rules, caps, regulations
        "last_updated": "2025-04-01"
    },
    "defence": { ... },
    "agriculture": { ... },
    "government": { ... }
}
```

### LTM Characteristics
- ✅ **Persistent** — survives across sessions (stored in file/database)
- ✅ **Cumulative** — grows richer with every approved run
- ✅ **Cross-session** — available to future Planner runs as prior context
- ✅ **Domain-specific** — organised by budget domain
- ❌ **Slower to update** — requires explicit save/load operations

---

## 5. LTM vs STM — Side-by-Side Comparison

| Feature | STM (Short-Term Memory) | LTM (Long-Term Memory) |
|---|---|---|
| **Scope** | Current pipeline run only | Across all runs / sessions |
| **Storage** | Python in-memory (TypedDict) | File / Database (JSON, SQL) |
| **Lifespan** | Ends when run completes | Permanent until deleted |
| **Updated by** | Every agent in the pipeline | Only on Verifier approval |
| **Used by** | Planner, Executor, Verifier | Planner (as context injection) |
| **Speed** | Very fast | Slower (disk I/O) |
| **Example data** | Current tasks, live results | Past budgets, domain policies |
| **In our code** | `AgentState` TypedDict | `ltm_store.json` |

---

## 6. Domain-Wise Application — Annual Budgeting

### 6.1 🚌 Commute Budget

| Memory Type | Content | Example |
|---|---|---|
| **STM** | Current year's commute budget goal, tasks like "estimate fuel costs", live Executor results for this run | Goal: "Plan FY2026 urban commute budget" → Tasks: ["Analyse fuel prices", "Estimate ridership", "Calculate infrastructure costs"] |
| **LTM** | Past commute budgets (FY2023–2025), metro expansion policies, approved cost breakdowns, seasonal travel trends | "FY2025 commute budget was ₹4,200 Cr; metro Phase-3 added 15% ridership" |

**How LTM feeds STM:** The Planner reads LTM to understand that commute costs rose 12% last year and injects this as context into the Executor's task prompts.

---

### 6.2 🛡️ Defence Budget

| Memory Type | Content | Example |
|---|---|---|
| **STM** | Current defence budget planning goal, active tasks like "assess procurement costs", Verifier's critique on accuracy | Goal: "Estimate FY2026 defence allocation" → Tasks: ["Review equipment procurement", "Assess personnel costs", "Evaluate R&D spend"] |
| **LTM** | Multi-year defence spending history, approved procurement plans, strategic priority documents, geopolitical budget shifts | "India's defence budget grew 13% YoY; capital expenditure at 27% of total in FY2025" |

**How LTM feeds STM:** Planner retrieves LTM to recognise that defence R&D was under-budgeted last cycle (Verifier critique stored in LTM) and adjusts task scope accordingly.

---

### 6.3 🌾 Agriculture Budget

| Memory Type | Content | Example |
|---|---|---|
| **STM** | Current agriculture budget goal, tasks like "estimate MSP subsidy costs", live web-search results from Executor | Goal: "Plan FY2026 agriculture support budget" → Tasks: ["Calculate MSP subsidies", "Estimate irrigation costs", "Plan crop insurance allocation"] |
| **LTM** | Historical MSP data, approved crop subsidy plans, rainfall impact records, past Verifier-approved budget reports | "FY2025 agriculture budget: ₹1.27 lakh Cr; PM-KISAN allocation ₹60,000 Cr" |

**How LTM feeds STM:** Executor uses LTM context about drought years to justify higher irrigation allocation in current tasks.

---

### 6.4 🏛️ Government (General Administration) Budget

| Memory Type | Content | Example |
|---|---|---|
| **STM** | Current governance budget goal, tasks like "estimate salaries and pensions", Verifier scores for current run | Goal: "Plan FY2026 central government administration budget" → Tasks: ["Estimate salary revisions", "Plan pension fund", "Calculate ministry operational costs"] |
| **LTM** | Pay commission reports, past administration budgets, approved pension policy changes, multi-year fiscal deficit targets | "7th Pay Commission added 23.6% to salary bill; FY2025 admin budget ₹5.2 lakh Cr" |

**How LTM feeds STM:** Planner reads LTM about upcoming 8th Pay Commission recommendations and plans tasks to account for a 20–25% salary increase projection.

---

## 7. Memory Flow in the Pipeline

```
ANNUAL BUDGETING PIPELINE FLOW
═══════════════════════════════════════════════════════════

  LTM Store                     STM (AgentState)
  ─────────                     ────────────────
  Past budgets ──────────────▶  goal: "Plan FY2026 defence budget"
  Domain policies               tasks: []  ← Planner fills this
  Historical trends             results: [] ← Executor fills this
  Approved results              critique: "" ← Verifier fills this
                                approved: False
                                iterations: 0

       Step 1: PLANNER
       ───────────────
       Reads LTM context → Creates 5 tasks → Writes to STM.tasks

       Step 2: EXECUTOR
       ────────────────
       Reads STM.tasks → Runs each + web search → Writes to STM.results

       Step 3: VERIFIER
       ────────────────
       Reads STM.goal + STM.results → Scores → Writes STM.approved
       If approved → Saves results to LTM ✅
       If rejected → Writes critique to STM → Loops back to Executor 🔁

═══════════════════════════════════════════════════════════
```

---

## 8. Key Insight — Why Both Are Needed

> **STM alone** → The agent has no memory of past budget decisions. Every run starts from zero. Leads to inconsistent, uninformed budgets.

> **LTM alone** → The agent cannot track what it's currently doing. Cannot manage multi-step tasks or retry loops.

> **STM + LTM together** → The agent plans with historical wisdom (LTM), executes with focus (STM), and grows smarter with every approved run (LTM update).

This is exactly how **human budget analysts** work — they remember past budgets (LTM) while actively working on the current one (STM).

---

## 9. Summary Table

| Component | Type | Implemented As | Budget Role |
|---|---|---|---|
| `goal` | STM | `AgentState` field | Current year's budgeting objective |
| `tasks` | STM | `AgentState` field | Steps to achieve the budget goal |
| `results` | STM | `AgentState` field | Executor's budget analysis output |
| `critique` | STM | `AgentState` field | Verifier's improvement feedback |
| `iterations` | STM | `AgentState` field | Retry count for quality loops |
| Past budgets | LTM | `ltm_store.json` | Historical spending reference |
| Domain policies | LTM | `ltm_store.json` | Rules constraining budget allocations |
| Approved results | LTM | `ltm_store.json` | Verified outputs saved for future use |
| Trend data | LTM | `ltm_store.json` | YoY growth rates, inflation adjustments |

---

## 10. Conclusion

In the **Planner → Executor → Verifier** architecture:

- **STM** is the agent's **working desk** — everything needed for the current budgeting task sits here, gets updated in real time, and is cleared when the task is done.
- **LTM** is the agent's **filing cabinet** — accumulated knowledge from years of approved budget plans, domain policies, and historical trends, always available to inform the next run.

For **annual budgeting across Commute, Defence, Agriculture, and Government domains**, this separation ensures that each new budget cycle benefits from past wisdom (LTM) while maintaining sharp, focused execution on the current year's goals (STM) — making the multi-agent system both **intelligent and reliable**.

---

*Submitted by: Akash Chaurasiya | Course: Multi-Agent AI Systems | Date: June 2026*
