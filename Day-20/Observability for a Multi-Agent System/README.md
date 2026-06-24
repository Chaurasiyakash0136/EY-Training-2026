# Observability for a Multi-Agent System

**Assignment:** Coding Assignment — Observability for a Multi-Agent System  
**Adapted from:** AWS S3 Multipart Upload `ProgressListener` pattern  
**Runtime:** Python 3.9+ · Standard library only · No `pip install`, no credentials, no network

---

## What this does

Replaces the raw `print` statement in the starter code with a structured
observability layer that emits correlated, lifecycle-based JSON events — the
same pattern an AWS S3 `ProgressListener` uses, transplanted onto a
multi-agent pipeline (Planner → Researcher → Writer → Reviewer).

---

## How to run

### Happy path (all agents succeed)
```bash
python agents.py
```

### Failure path (Writer fails at step 2)
```bash
DEMO_FAILURE=1 python agents.py
```

---

## Event schema

Every event carries at minimum:

| Field | Description |
|---|---|
| `timestamp` | UTC ISO-8601 |
| `trace_id` | UUID — same for every event in one run (Task 1) |
| `span_id` | UUID — same for every event within one agent execution (Task 1) |
| `event` | `agent_started` / `agent_progress` / `agent_completed` / `agent_failed` / `run_summary` |
| `agent` | Agent name |
| `pipeline_pct` | Steps finished across ALL agents ÷ total steps × 100 (Task 2) |
| `throughput` | Steps per second since run started (Task 2) |

`agent_completed` additionally carries `duration_s` (Task 2).  
`agent_progress` is **throttled** — emitted roughly every 25% of an agent's steps (Task 3).  
`agent_failed` carries `failed_step`, `error`, and `pipeline_pct` at the moment it died (Task 4).  
`run_summary` is always the final event — status, total duration, completed agents, failed agent (Task 4).

---

## Example output (failure path, pretty-printed)

```json
{"event": "agent_started",   "agent": "Writer",  "pipeline_pct": 60.0, ...}
{"event": "agent_progress",  "agent": "Writer",  "step": 1, "pct_complete": 25.0, ...}
{"event": "agent_failed",    "agent": "Writer",  "failed_step": 2, "pipeline_pct": 66.7,
                              "error": "Writer failed at step 2", ...}
{"event": "run_summary",     "status": "failed", "agents_completed": ["Planner","Researcher"],
                              "failed_agent": {"agent":"Writer","step":2,...}}
```

---

## Acceptance criteria

| # | Criterion | Status |
|---|---|---|
| 1 | Emit structured JSON events, not free-text prints | ✅ |
| 2 | Correlate via run-level `trace_id` and per-agent `span_id` | ✅ |
| 3 | Report pipeline `pct`, throughput, and per-agent `duration_s` | ✅ |
| 4 | Throttle progress events (≈every 25% of agent's steps) | ✅ |
| 5 | Failure event localises agent/step + final `run_summary` | ✅ |
| 6 | Runs with `python agents.py` — standard library only | ✅ |

---

## Submission note

**Next signal for a real workload:** token/cost per agent — LLM spend is the
dominant cost driver and the hardest to attribute across a pipeline without
explicit instrumentation.

**Where these events would go in production:** an OpenTelemetry collector
(OTLP/HTTP). Each event maps cleanly onto an OTEL span — `trace_id` →
`TraceId`, `span_id` → `SpanId` — so a trace viewer like Jaeger or Grafana
Tempo reconstructs the parent/child tree automatically.
