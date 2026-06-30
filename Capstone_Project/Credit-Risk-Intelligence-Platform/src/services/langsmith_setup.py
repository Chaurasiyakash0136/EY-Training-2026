# src/services/langsmith_setup.py
# ============================================================
# LangSmith Observability Setup
#
# When LANGCHAIN_API_KEY + LANGCHAIN_TRACING_V2=true are set,
# ALL LLM calls, embeddings, and RAG retrievals are traced
# automatically — no code changes needed beyond this call.
#
# View traces at: https://smith.langchain.com
# ============================================================
from __future__ import annotations
import os
from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def initialise() -> None:
    """
    Activate LangSmith tracing.
    Call this once at application startup, BEFORE any LangChain imports.
    """
    if not settings.LANGCHAIN_API_KEY:
        logger.info(
            "LangSmith tracing DISABLED — LANGCHAIN_API_KEY not set. "
            "Get a free key at https://smith.langchain.com"
        )
        return

    if not settings.LANGCHAIN_TRACING_V2:
        logger.info(
            "LangSmith tracing DISABLED — LANGCHAIN_TRACING_V2=false in .env. "
            "Set to true to enable tracing."
        )
        return

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"]    = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"]    = settings.LANGCHAIN_PROJECT

    logger.info(
        "LangSmith tracing ENABLED — Project: '%s'. "
        "View traces at https://smith.langchain.com",
        settings.LANGCHAIN_PROJECT,
    )


def status() -> dict[str, str]:
    return {
        "enabled": str(settings.langsmith_enabled),
        "project": settings.LANGCHAIN_PROJECT,
        "key_set": "Yes" if settings.LANGCHAIN_API_KEY else "No",
        "tracing": "Active" if settings.langsmith_enabled else "Inactive",
    }
