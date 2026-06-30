# src/evaluation/ragas_runner.py
# ============================================================
# RAGAS Evaluation — backend only, not visible in UI.
# Evaluates RAG pipeline quality after each chat response.
#
# SETUP (optional):
#   pip install ragas
#   No extra API key needed — uses the same OpenAI key.
#
# Metrics evaluated:
#   - faithfulness:        Does the answer stick to the context?
#   - answer_relevancy:    Does the answer address the question?
#   - context_recall:      Did we retrieve the right chunks?
#   - context_precision:   Are retrieved chunks precise?
#
# Results are logged to logs/eval_scores.jsonl (append-only).
# ============================================================
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from langchain_core.documents import Document
from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

_SCORES_FILE = Path("logs/eval_scores.jsonl")


def evaluate_rag_response(
    question:       str,
    answer:         str,
    retrieved_docs: list[Document],
    ground_truth:   str = "",
) -> dict | None:
    """
    Run RAGAS evaluation on a single RAG response.

    Parameters
    ----------
    question       : The user's question.
    answer         : The AI-generated answer.
    retrieved_docs : Document chunks used to generate the answer.
    ground_truth   : Optional reference answer (improves recall/precision).

    Returns
    -------
    dict with scores, or None if evaluation is disabled/unavailable.
    """
    if not settings.EVALUATION_ENABLED:
        return None

    if not settings.OPENAI_API_KEY:
        logger.warning("RAGAS requires OPENAI_API_KEY. Skipping evaluation.")
        return None

    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy
        from datasets import Dataset

        contexts = [doc.page_content for doc in retrieved_docs if doc.page_content.strip()]
        if not contexts:
            return None

        data = {
            "question":   [question],
            "answer":     [answer],
            "contexts":   [contexts],
        }
        if ground_truth:
            data["ground_truth"] = [ground_truth]

        dataset = Dataset.from_dict(data)

        metrics = [faithfulness, answer_relevancy]

        result = evaluate(dataset, metrics=metrics)
        scores = {
            "timestamp":        datetime.now(timezone.utc).isoformat(),
            "question":         question[:100],
            "faithfulness":     round(float(result["faithfulness"]), 3),
            "answer_relevancy": round(float(result["answer_relevancy"]), 3),
            "n_contexts":       len(contexts),
        }

        _append_score(scores)
        logger.info(
            "RAGAS scores — faithfulness: %.3f, relevancy: %.3f",
            scores["faithfulness"],
            scores["answer_relevancy"],
        )
        return scores

    except ImportError:
        logger.warning(
            "RAGAS not installed. Run: pip install ragas datasets\n"
            "Then set EVALUATION_ENABLED=true in .env"
        )
        return None
    except Exception as exc:
        logger.warning("RAGAS evaluation failed: %s", exc)
        return None


def _append_score(scores: dict) -> None:
    """Append evaluation scores to the JSONL log file."""
    try:
        _SCORES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _SCORES_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(scores) + "\n")
    except Exception as exc:
        logger.warning("Could not write eval scores: %s", exc)


def get_recent_scores(n: int = 20) -> list[dict]:
    """Return the last n evaluation scores for monitoring."""
    if not _SCORES_FILE.exists():
        return []
    try:
        lines = _SCORES_FILE.read_text(encoding="utf-8").strip().splitlines()
        return [json.loads(line) for line in lines[-n:]]
    except Exception:
        return []
