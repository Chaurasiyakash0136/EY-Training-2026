# app.py — Credit Risk Intelligence Platform v2.0
# ============================================================
# Streamlit entry point.
# Run: streamlit run app.py
# ============================================================
from __future__ import annotations
import sys
from pathlib import Path

# Ensure project root is always on the path
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

# LangSmith must be initialised BEFORE any LangChain imports
from src.services.langsmith_setup import initialise as _init_langsmith
_init_langsmith()

from src.orchestrator.orchestrator import AgentOrchestrator
from src.models.schemas import PlatformState
from ui.sidebar import render as render_sidebar
from ui.theme import inject_global_css

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Credit Risk Intelligence Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_global_css()

# ── Session state bootstrap ───────────────────────────────────────────────────

def _init_state() -> None:
    if "platform_state" not in st.session_state:
        st.session_state["platform_state"] = PlatformState()
    if "orchestrator" not in st.session_state:
        st.session_state["orchestrator"] = AgentOrchestrator()
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Dashboard"


_init_state()
state:        PlatformState    = st.session_state["platform_state"]
orchestrator: AgentOrchestrator = st.session_state["orchestrator"]

# Keep vector_store_ready in sync
state.vector_store_ready = orchestrator.vector_store_ready

# ── Navigation ────────────────────────────────────────────────────────────────
page = render_sidebar(state)

# ── Page routing ──────────────────────────────────────────────────────────────
match page:
    case "Dashboard":
        from ui.pages.dashboard import render
        render(state)

    case "Upload Documents":
        from ui.pages.upload import render
        render(state, orchestrator)

    case "Document Summary":
        from ui.pages.summary import render
        render(state)

    case "Risk Analysis":
        from ui.pages.risk_analysis import render
        render(state, orchestrator)

    case "AI Recommendations":
        from ui.pages.recommendations import render
        render(state, orchestrator)

    case "Retirement Planner":
        from ui.pages.retirement_planner import render
        render(state, orchestrator)

    case "AI Chat":
        from ui.pages.chat import render
        render(state, orchestrator)

    case _:
        st.error(f"Unknown page: {page}. Navigating to Dashboard.")
        st.session_state["current_page"] = "Dashboard"
        st.rerun()
