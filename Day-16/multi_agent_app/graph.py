"""
graph.py — LangGraph StateGraph wiring
"""

from langgraph.graph import StateGraph, END
from agents import AgentState, planner, executor, verifier
from typing import Callable, Optional
from langchain_groq import ChatGroq


def build_graph(llm: ChatGroq, log: Optional[Callable] = None):
    """Compile and return the planner→executor→verifier graph."""

    def _planner(state):  return planner(state,  llm, log)
    def _executor(state): return executor(state, llm, log)
    def _verifier(state): return verifier(state, llm, log)

    def route(state: AgentState) -> str:
        return "end" if state["approved"] else "executor"

    g = StateGraph(AgentState)
    g.add_node("planner",  _planner)
    g.add_node("executor", _executor)
    g.add_node("verifier", _verifier)

    g.add_edge("planner",  "executor")
    g.add_edge("executor", "verifier")
    g.add_conditional_edges("verifier", route, {"end": END, "executor": "executor"})
    g.set_entry_point("planner")

    return g.compile()


def initial_state(goal: str) -> AgentState:
    return {
        "goal":       goal,
        "tasks":      [],
        "results":    [],
        "critique":   "",
        "approved":   False,
        "iterations": 0,
        "scores":     {},
    }
