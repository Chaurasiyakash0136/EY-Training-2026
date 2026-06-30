# src/llm/llm_factory.py
# ============================================================
# LLM Factory with Gemini → OpenAI automatic fallback.
#
# BUG FIX: Removed @lru_cache on provider instances.
# The old code used lru_cache(maxsize=1) which baked in the
# provider at first call. This caused settings changes to be
# silently ignored. Now providers are module-level singletons
# that are only instantiated when first needed.
# ============================================================
from __future__ import annotations
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Quota / rate-limit error signals
_FALLBACK_SIGNALS = (
    "quota", "rate", "limit", "429", "resource_exhausted",
    "resourceexhausted", "unavailable", "overloaded", "timeout",
    "deadline", "503", "500", "internal",
)

# Module-level provider cache (reset when needed)
_chat_provider_cache    = None
_fallback_provider_cache = None
_embedding_provider_cache = None


def _is_quota_error(exc: Exception) -> bool:
    msg       = str(exc).lower()
    type_name = type(exc).__name__.lower()
    return any(s in msg or s in type_name for s in _FALLBACK_SIGNALS)


def _make_provider(key: str):
    from src.llm.openai_provider import OpenAIProvider
    from src.llm.gemini_provider  import GeminiProvider
    registry = {"openai": OpenAIProvider, "gemini": GeminiProvider}
    if key not in registry:
        raise ValueError(f"Unknown provider '{key}'. Available: {list(registry.keys())}")
    provider = registry[key]()
    logger.info("Provider instantiated: %s", provider.provider_name)
    return provider


def _get_chat_provider():
    global _chat_provider_cache
    if _chat_provider_cache is None:
        _chat_provider_cache = _make_provider(settings.LLM_PROVIDER)
    return _chat_provider_cache


def _get_fallback_provider():
    global _fallback_provider_cache
    if _fallback_provider_cache is None:
        _fallback_provider_cache = _make_provider("openai")
    return _fallback_provider_cache


def _get_embedding_provider():
    global _embedding_provider_cache
    if _embedding_provider_cache is None:
        _embedding_provider_cache = _make_provider(settings.EMBEDDING_PROVIDER)
    return _embedding_provider_cache


def clear_provider_cache() -> None:
    """Call this to force re-initialisation (e.g. after settings change)."""
    global _chat_provider_cache, _fallback_provider_cache, _embedding_provider_cache
    _chat_provider_cache      = None
    _fallback_provider_cache  = None
    _embedding_provider_cache = None
    logger.info("LLM provider cache cleared.")


def invoke_with_fallback(messages: list) -> str:
    """
    Invoke the LLM with automatic Gemini → OpenAI fallback.
    Returns the response content string.

    This is the RECOMMENDED way to call the LLM throughout the app.
    """
    # Try primary provider (Gemini)
    try:
        llm      = _get_chat_provider().get_chat_model()
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as primary_exc:
        if _is_quota_error(primary_exc) and settings.LLM_PROVIDER == "gemini":
            logger.warning(
                "Gemini quota/rate error: %s — switching to OpenAI fallback.",
                primary_exc,
            )
            try:
                llm_fallback = _get_fallback_provider().get_chat_model()
                response     = llm_fallback.invoke(messages)
                logger.info("OpenAI fallback succeeded.")
                return response.content.strip()
            except Exception as fallback_exc:
                logger.error(
                    "Both Gemini and OpenAI failed. Gemini: %s | OpenAI: %s",
                    primary_exc,
                    fallback_exc,
                )
                raise RuntimeError(
                    f"Both AI providers failed.\n"
                    f"Gemini error: {primary_exc}\n"
                    f"OpenAI error: {fallback_exc}"
                ) from fallback_exc
        raise


def get_embeddings() -> Embeddings:
    """Return the configured embedding model."""
    return _get_embedding_provider().get_embeddings()


def get_chat_model() -> BaseChatModel:
    """Return the primary chat model."""
    return _get_chat_provider().get_chat_model()
