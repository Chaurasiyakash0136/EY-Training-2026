"""
Coding Assignment — Observability for a Multi-Agent System
==========================================================
Adapted from the AWS S3 multipart upload ProgressListener pattern.
Standard library only. Python 3.9+. No pip install, no credentials, no network.

HOW TO RUN
----------
  python agents.py                # happy path  — all 4 agents succeed
  python agents.py --failure      # failure path — Writer fails at step 2
  python agents.py --timeline     # read trace.jsonl and print per-agent timeline

After every run:
  - Structured JSON events stream to stdout (one event per line)
  - Every event is also appended to trace.jsonl in the same folder
  - The exact save path is printed to stderr so you always know where it is

SUBMISSION NOTE
---------------
Next signal for a real agentic workload: token/cost per agent — LLM spend is
the dominant cost driver and hardest to attribute across a pipeline without
explicit per-agent instrumentation.

Where these events go in production: an OpenTelemetry collector (OTLP/HTTP).
Each event maps onto an OTEL span — trace_id → TraceId, span_id → SpanId —
so Jaeger / Grafana Tempo reconstructs the full pipeline timeline automatically.
"""

import json
import os
import random
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# trace.jsonl is always saved in the same folder as agents.py
TRACE_FILE        = Path(__file__).resolve().parent / "trace.jsonl"
STALL_THRESHOLD_S = 0.5   # seconds gap between steps → emits agent_stalled


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    """Return current UTC time as ISO-8601 string, e.g. 2026-06-24T09:14:02Z."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _emit(event: dict) -> None:
    """
    Emit one structured JSON event:
      stdout  — one JSON line (clean, machine-readable, pipeable)
      trace.jsonl — same line appended (persistent trace file, Stretch Goal 1)
    """
    line = json.dumps(event)
    print(line)                                       # stdout: JSON only
    with open(TRACE_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")                          # file: same JSON


def _progress_milestones(total_steps: int) -> set:
    """
    Pre-compute step numbers at the 25 / 50 / 75 / 100 % marks.
    Maximum 4 progress events per agent — over-emitting is its own failure mode.
    """
    milestones = set()
    for pct in [25, 50, 75, 100]:
        step = round(total_steps * pct / 100)
        if 1 <= step <= total_steps:
            milestones.add(step)
    return milestones


# ---------------------------------------------------------------------------
# Structured event emitters
# ---------------------------------------------------------------------------

def emit_agent_started(trace_id, span_id, agent,
                       total_steps, pipeline_pct, throughput):
    """Task 3 — lifecycle event: agent begins work."""
    _emit({
        "timestamp":    _now_iso(),
        "trace_id":     trace_id,           # Task 1 — run-level correlation
        "span_id":      span_id,            # Task 1 — per-agent correlation
        "event":        "agent_started",
        "agent":        agent,
        "total_steps":  total_steps,
        "pipeline_pct": round(pipeline_pct, 1),   # Task 2
        "throughput":   round(throughput, 2),      # Task 2
    })


def emit_agent_progress(trace_id, span_id, agent,
                        step, total_steps, pipeline_pct, throughput):
    """Task 3 — throttled progress: fires only at 25/50/75/100% milestones."""
    _emit({
        "timestamp":    _now_iso(),
        "trace_id":     trace_id,
        "span_id":      span_id,
        "event":        "agent_progress",
        "agent":        agent,
        "step":         step,
        "total_steps":  total_steps,
        "pct_complete": round(100.0 * step / total_steps, 1),
        "pipeline_pct": round(pipeline_pct, 1),
        "throughput":   round(throughput, 2),
    })


def emit_agent_completed(trace_id, span_id, agent,
                         total_steps, duration_s, pipeline_pct, throughput):
    """Task 3 — lifecycle event: agent finished all steps successfully."""
    _emit({
        "timestamp":    _now_iso(),
        "trace_id":     trace_id,
        "span_id":      span_id,
        "event":        "agent_completed",
        "agent":        agent,
        "total_steps":  total_steps,
        "duration_s":   round(duration_s, 3),      # Task 2 — per-agent timing
        "pipeline_pct": round(pipeline_pct, 1),
        "throughput":   round(throughput, 2),
    })


def emit_agent_failed(trace_id, span_id, agent,
                      step, total_steps, error, pipeline_pct, throughput):
    """Task 4 — which agent/step died, error message, pipeline % at that moment."""
    _emit({
        "timestamp":    _now_iso(),
        "trace_id":     trace_id,
        "span_id":      span_id,
        "event":        "agent_failed",
        "agent":        agent,
        "failed_step":  step,
        "total_steps":  total_steps,
        "error":        error,
        "pipeline_pct": round(pipeline_pct, 1),
        "throughput":   round(throughput, 2),
    })


def emit_agent_stalled(trace_id, span_id, agent,
                       step, gap_s, threshold_s):
    """Stretch Goal 2 — gap between consecutive steps exceeded threshold."""
    _emit({
        "timestamp":       _now_iso(),
        "trace_id":        trace_id,
        "span_id":         span_id,
        "event":           "agent_stalled",
        "agent":           agent,
        "stalled_at_step": step,
        "gap_s":           round(gap_s, 3),
        "threshold_s":     threshold_s,
        "warning":         (f"{agent} step gap {gap_s:.2f}s "
                            f"exceeds threshold {threshold_s}s"),
    })


def emit_run_summary(trace_id, status, total_duration_s,
                     agents_completed, failed_agent):
    """Task 4 — always the very last event emitted, success or failure."""
    _emit({
        "timestamp":        _now_iso(),
        "trace_id":         trace_id,
        "event":            "run_summary",
        "status":           status,                  # "success" | "failed"
        "total_duration_s": round(total_duration_s, 3),
        "agents_completed": agents_completed,
        "failed_agent":     failed_agent,            # None or {agent, step, error}
    })


# ---------------------------------------------------------------------------
# Agent — starter code preserved exactly
# ---------------------------------------------------------------------------

class Agent:
    """A simulated agent that does N steps of work. Pure simulation — no LLM, no network."""

    def __init__(self, name: str, steps: int, fail_at_step: int | None = None):
        self.name         = name
        self.steps        = steps
        self.fail_at_step = fail_at_step   # set to an int to force a deterministic failure

    def run(self, listener) -> None:
        for step in range(1, self.steps + 1):
            time.sleep(random.uniform(0.05, 0.2))   # simulate work / latency
            if self.fail_at_step and step == self.fail_at_step:
                raise RuntimeError(f"{self.name} failed at step {step}")
            listener(self.name, step, self.steps)


# ---------------------------------------------------------------------------
# Orchestrator — owns all observability
# ---------------------------------------------------------------------------

class Orchestrator:

    def __init__(self, agents: list, listener=None):
        self.agents             = agents
        self._external_listener = listener   # kept for API compat with starter code

        # Task 1 — single trace_id for the entire run
        self.trace_id: str = str(uuid.uuid4())

        # Task 2 — pipeline-level counters
        self._total_pipeline_steps    : int   = sum(a.steps for a in agents)
        self._completed_pipeline_steps: int   = 0
        self._run_start               : float = 0.0

    def _pipeline_pct(self) -> float:
        """Steps finished across ALL agents ÷ total steps × 100 (Task 2)."""
        if self._total_pipeline_steps == 0:
            return 100.0
        return 100.0 * self._completed_pipeline_steps / self._total_pipeline_steps

    def _throughput(self) -> float:
        """Steps per second since run started (Task 2)."""
        elapsed = time.monotonic() - self._run_start
        return (self._completed_pipeline_steps / elapsed) if elapsed > 1e-9 else 0.0

    def run(self) -> None:
        self._run_start   = time.monotonic()
        agents_completed  : list      = []
        failed_agent_info : dict|None = None
        final_status                  = "success"

        for agent in self.agents:
            # Task 1 — fresh span_id per agent execution
            span_id     = str(uuid.uuid4())
            agent_start = time.monotonic()

            emit_agent_started(
                self.trace_id, span_id, agent.name, agent.steps,
                self._pipeline_pct(), self._throughput(),
            )

            # Task 3 — pre-compute 25/50/75/100% milestone steps for this agent
            milestones     = _progress_milestones(agent.steps)
            last_step_time = [time.monotonic()]   # mutable cell for stall detection

            def _make_listener(span, ms, lst):
                def _listener(agent_name, step, total_steps):
                    now = time.monotonic()

                    # Stretch Goal 2 — stall detection
                    gap = now - lst[0]
                    if gap > STALL_THRESHOLD_S:
                        emit_agent_stalled(
                            self.trace_id, span,
                            agent_name, step, gap, STALL_THRESHOLD_S,
                        )
                    lst[0] = now

                    # Task 2 — advance pipeline counter
                    self._completed_pipeline_steps += 1

                    # Task 3 — throttled progress at milestones only
                    if step in ms:
                        emit_agent_progress(
                            self.trace_id, span, agent_name,
                            step, total_steps,
                            self._pipeline_pct(), self._throughput(),
                        )

                    if self._external_listener:
                        self._external_listener(agent_name, step, total_steps)

                return _listener

            try:
                agent.run(_make_listener(span_id, milestones, last_step_time))

                # Task 3 — agent_completed
                emit_agent_completed(
                    self.trace_id, span_id, agent.name, agent.steps,
                    time.monotonic() - agent_start,
                    self._pipeline_pct(), self._throughput(),
                )
                agents_completed.append(agent.name)

            except RuntimeError as exc:
                # Task 4 — agent_failed with exact location + pipeline % at death
                failed_step = _parse_failed_step(str(exc), agent.steps)
                emit_agent_failed(
                    self.trace_id, span_id, agent.name,
                    failed_step, agent.steps, str(exc),
                    self._pipeline_pct(), self._throughput(),
                )
                failed_agent_info = {
                    "agent": agent.name,
                    "step" : failed_step,
                    "error": str(exc),
                }
                final_status = "failed"
                break   # stop the pipeline cleanly on failure

        # Task 4 — run_summary is always the last event
        emit_run_summary(
            self.trace_id, final_status,
            time.monotonic() - self._run_start,
            agents_completed, failed_agent_info,
        )


def _parse_failed_step(msg: str, fallback: int) -> int:
    """Extract step number from 'AgentName failed at step N'."""
    m = re.search(r"step\s+(\d+)", msg)
    return int(m.group(1)) if m else fallback


# ---------------------------------------------------------------------------
# Stretch Goal 1 — Timeline viewer
# Reads trace.jsonl and prints a per-agent visual timeline for every run.
# Called by:  python agents.py --timeline
# ---------------------------------------------------------------------------

def print_timeline(trace_file: Path = TRACE_FILE) -> None:
    """Read trace.jsonl and print a per-agent visual timeline for every run."""

    if not trace_file.exists():
        print(f"[timeline] No trace file at: {trace_file}", file=sys.stderr)
        return

    events: list[dict] = []
    with open(trace_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    if not events:
        print("[timeline] trace.jsonl is empty.", file=sys.stderr)
        return

    # Group by trace_id — one group = one run
    runs: dict[str, list] = {}
    for e in events:
        runs.setdefault(e.get("trace_id", "unknown"), []).append(e)

    BAR = 40

    # ── print to stderr so it never pollutes the JSON stdout stream ──────────
    out = sys.stderr

    for run_idx, (trace_id, run_events) in enumerate(runs.items(), 1):
        summary     = next((e for e in run_events if e["event"] == "run_summary"), {})
        status      = summary.get("status", "unknown").upper()
        total_d     = summary.get("total_duration_s", 0)
        icon        = "✅" if status == "SUCCESS" else "❌"

        print(file=out)
        print("=" * 74, file=out)
        print(f"  RUN #{run_idx}  |  trace_id : {trace_id}", file=out)
        print(f"  Status : {icon} {status}   |   Total duration : {total_d:.3f}s", file=out)
        print("=" * 74, file=out)
        print(f"  {'AGENT':<14} {'RESULT':<14} {'STEPS':>6}  {'DURATION':>9}  PROGRESS", file=out)
        print(f"  {'-'*14} {'-'*14} {'-'*6}  {'-'*9}  {'-'*BAR}", file=out)

        # Build per-span buckets
        agent_spans: dict[str, dict] = {}
        for e in run_events:
            span = e.get("span_id")
            ag   = e.get("agent")
            if span and ag:
                agent_spans.setdefault(span, {"agent": ag, "events": []})["events"].append(e)

        for span_id, data in agent_spans.items():
            ag        = data["agent"]
            evts      = data["events"]
            completed = next((e for e in evts if e["event"] == "agent_completed"), None)
            failed    = next((e for e in evts if e["event"] == "agent_failed"),    None)
            stalled   = [e for e in evts if e["event"] == "agent_stalled"]
            progress  = [e for e in evts if e["event"] == "agent_progress"]

            if completed:
                result    = "✅ COMPLETED"
                duration  = f"{completed['duration_s']:.3f}s"
                steps_str = f"{completed['total_steps']}/{completed['total_steps']}"
                bar_fill  = BAR
            elif failed:
                result    = "❌ FAILED"
                duration  = "—"
                steps_str = f"{failed['failed_step']}/{failed['total_steps']}"
                bar_fill  = int(BAR * failed["failed_step"] / failed["total_steps"])
            else:
                result    = "⏭  SKIPPED"
                duration  = "—"
                steps_str = "—"
                bar_fill  = 0

            bar        = "█" * bar_fill + "░" * (BAR - bar_fill)
            stall_flag = "  ⚠ STALL" if stalled else ""
            print(f"  {ag:<14} {result:<14} {steps_str:>6}  {duration:>9}  {bar}{stall_flag}", file=out)

            for p in progress:
                pct = p.get("pct_complete", 0)
                pos = int(BAR * pct / 100)
                print(f"  {'':14} {'':14} {'':6}  {'':9}  {' '*pos}↑{pct}%", file=out)

            if failed:
                print(f"  {'':14} {'':14} {'':6}  {'error:':>9}  {failed['error']}", file=out)

            for s in stalled:
                print(f"  {'':14} {'':14} {'':6}  {'stall:':>9}  "
                      f"step {s['stalled_at_step']} gap={s['gap_s']:.2f}s", file=out)

        n_done = len(summary.get("agents_completed", []))
        n_all  = len(agent_spans)
        print(f"  {'-'*14} {'-'*14} {'-'*6}  {'-'*9}  {'-'*BAR}", file=out)
        print(f"  {'PIPELINE':<14} {icon+' '+status:<14} "
              f"{n_done}/{n_all} agents  {total_d:>6.3f}s", file=out)
        if summary.get("failed_agent"):
            fi = summary["failed_agent"]
            print(f"  ↳ FAILURE: {fi['agent']} crashed at step {fi['step']} "
                  f"— \"{fi['error']}\"", file=out)

    print(file=out)
    print(f"  {len(runs)} run(s)  ·  {len(events)} total events  ·  {trace_file}", file=out)
    print(file=out)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:

    # ── --timeline: read trace.jsonl and print visual timeline ───────────────
    if "--timeline" in sys.argv:
        print_timeline()
        return

    # ── choose run mode ───────────────────────────────────────────────────────
    demo_failure = (
        "--failure" in sys.argv
        or os.environ.get("DEMO_FAILURE", "0") == "1"
    )

    # ── informational header to stderr (never pollutes JSON stdout) ───────────
    mode = "FAILURE PATH  (Writer fails at step 2)" if demo_failure else "HAPPY PATH"
    print(f"{'='*60}", file=sys.stderr)
    print(f"  Multi-Agent Observability  —  {mode}", file=sys.stderr)
    print(f"  Trace file : {TRACE_FILE}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    agents = [
        Agent("Planner",    3),
        Agent("Researcher", 6),
        Agent("Writer",     4, fail_at_step=2 if demo_failure else None),
        Agent("Reviewer",   2),
    ]

    Orchestrator(agents).run()

    # ── save confirmation to stderr ───────────────────────────────────────────
    print(f"{'─'*60}", file=sys.stderr)
    print(f"  ✅  Trace saved → {TRACE_FILE}", file=sys.stderr)
    print(f"  💡  Run: python agents.py --timeline   to view all runs", file=sys.stderr)
    print(f"{'─'*60}", file=sys.stderr)

    # ── auto-print timeline to stderr after every run ─────────────────────────
    print_timeline()


if __name__ == "__main__":
    main()
