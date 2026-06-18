"""
agents.py — Planner · Executor · Verifier logic
"""

import os, json
from typing import TypedDict, List, Callable, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun

# ── LLM & Search ──────────────────────────────────────────────────────────────

def get_llm(api_key: str) -> ChatGroq:
    return ChatGroq(
        temperature=0,
        model_name="llama-3.1-8b-instant",
        groq_api_key=api_key,
    )

search_tool = DuckDuckGoSearchRun()

# ── State Schema ───────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    goal:       str
    tasks:      List[str]
    results:    List[str]
    critique:   str
    approved:   bool
    iterations: int
    scores:     dict          # verifier score breakdown

# ── Agents ────────────────────────────────────────────────────────────────────

def planner(state: AgentState, llm: ChatGroq,
            log: Optional[Callable] = None) -> AgentState:
    """Break a goal into ≤5 actionable tasks."""
    system = (
        "You are a planning agent. Break the user's goal into at most 5 "
        "concrete, actionable tasks. Respond ONLY with a valid JSON array "
        "of strings. No preamble, no markdown."
    )
    messages = [
        SystemMessage(content=system),
        HumanMessage(content=f"Goal: {state['goal']}"),
    ]
    response = llm.invoke(messages).content.strip()
    try:
        clean = response.replace("```json", "").replace("```", "").strip()
        tasks = json.loads(clean)
    except json.JSONDecodeError:
        tasks = [response]

    if log:
        log(f"✅ Planner generated **{len(tasks)} tasks**")
        for i, t in enumerate(tasks):
            log(f"  **{i+1}.** {t}")

    return {**state, "tasks": tasks}


def executor(state: AgentState, llm: ChatGroq,
             log: Optional[Callable] = None) -> AgentState:
    """Execute each task, optionally using web search for context."""
    results   = []
    critique_ctx = (
        f"\n\nPrevious attempt was rejected. Critique: {state['critique']}"
        if state["critique"] else ""
    )

    for i, task in enumerate(state["tasks"]):
        system = (
            f"You are an execution agent. Complete the task thoroughly. "
            f"Use the web-search context if provided.{critique_ctx}"
        )
        search_ctx = ""
        search_used = False
        try:
            search_result = search_tool.run(task[:100])
            search_ctx = f"\n\nWeb search context:\n{search_result[:800]}"
            search_used = True
        except Exception:
            pass

        messages = [
            SystemMessage(content=system),
            HumanMessage(content=f"Task: {task}{search_ctx}"),
        ]
        result = llm.invoke(messages).content

        results.append(result)
        if log:
            icon = "🌐" if search_used else "🤖"
            log(f"  {icon} **Task {i+1}** completed {'(web search used)' if search_used else ''}")

    return {**state, "results": results, "iterations": state["iterations"] + 1}


def verifier(state: AgentState, llm: ChatGroq,
             log: Optional[Callable] = None) -> AgentState:
    """Score results 0-1; approve or request retry (max 3 iterations)."""
    if state["iterations"] >= 3:
        if log:
            log("⚠️ Max iterations reached — force approving.")
        return {**state, "approved": True}

    combined = "\n\n".join(
        f"Task {i+1}: {t}\nResult: {r}"
        for i, (t, r) in enumerate(zip(state["tasks"], state["results"]))
    )
    system = (
        'You are a quality verifier. Evaluate results against the original goal.\n'
        'Rubric:\n'
        '  - completeness_score: 0–0.4  (does it fully address the goal?)\n'
        '  - accuracy_score:     0–0.3  (correct and specific?)\n'
        '  - clarity_score:      0–0.3  (well-structured?)\n'
        'Return ONLY valid JSON:\n'
        '{"score": 0.9, "completeness_score": 0.35, "accuracy_score": 0.28, '
        '"clarity_score": 0.27, "approved": true, "critique": "..."}'
    )
    messages = [
        SystemMessage(content=system),
        HumanMessage(content=f"Original goal: {state['goal']}\n\nResults:\n{combined}"),
    ]
    raw = llm.invoke(messages).content.strip()
    scores = {}
    try:
        clean   = raw.replace("```json", "").replace("```", "").strip()
        verdict = json.loads(clean)
        approved = bool(verdict.get("approved", False))
        critique = verdict.get("critique", "")
        scores = {
            "total":        round(float(verdict.get("score", 0)), 2),
            "completeness": round(float(verdict.get("completeness_score", 0)), 2),
            "accuracy":     round(float(verdict.get("accuracy_score", 0)), 2),
            "clarity":      round(float(verdict.get("clarity_score", 0)), 2),
        }
    except Exception:
        approved, critique, scores = False, raw, {}

    if log:
        total = scores.get("total", 0)
        icon  = "✅" if approved else "🔁"
        log(f"  {icon} Score: **{total:.2f}** | Approved: **{approved}**")
        if not approved:
            log(f"  💬 Critique: _{critique}_")

    return {**state, "approved": approved, "critique": critique, "scores": scores}
