# src/agents/retrieval_agent.py
# ============================================================
# Agent 2 — Vector store management and retrieval.
# Updates:
#   - Top-K = 6 (was 12, too noisy)
#   - MMR (Maximal Marginal Relevance) for diverse results
#   - validate_questions() to guarantee suggested questions work
# ============================================================
from __future__ import annotations
from langchain_core.documents import Document
from src.llm.llm_factory import get_embeddings
from src.retrieval.vector_store import create_vector_store
from src.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class RetrievalAgent:
    def __init__(self) -> None:
        self._vs = None

    def _get_store(self):
        if self._vs is None:
            embeddings = get_embeddings()
            self._vs   = create_vector_store(embeddings)
            # NOTE: We do NOT auto-load persisted index on startup.
            # This prevents ghost-document answers from previous sessions.
        return self._vs

    def index_documents(self, chunks: list[Document]) -> None:
        if not chunks:
            logger.warning("index_documents called with empty chunk list.")
            return
        store = self._get_store()
        logger.info("Indexing %d chunks.", len(chunks))
        store.build(chunks)

    def retrieve(
        self,
        query:   str,
        top_k:   int | None  = None,
        use_mmr: bool | None = None,
    ) -> list[Document]:
        """
        Retrieve top-k most relevant chunks.
        Default: K=6 with MMR (both configurable via settings).
        """
        _k   = top_k   if top_k   is not None else settings.RETRIEVER_TOP_K
        _mmr = use_mmr if use_mmr is not None else settings.RETRIEVER_USE_MMR

        store = self._get_store()
        if not store.is_ready:
            logger.warning("retrieve() called but vector store not ready.")
            return []

        results = store.similarity_search(query, k=_k, use_mmr=_mmr)
        logger.info(
            "retrieve('%s...') → %d results (MMR=%s)",
            query[:40],
            len(results),
            _mmr,
        )
        return results

    def validate_question(self, question: str) -> bool:
        """
        Check whether a question has at least one retrievable answer.
        Used to pre-validate suggested questions so system-generated
        questions never return empty answers.

        Returns True if at least 1 chunk with content was found.
        """
        if not self.is_ready:
            return False
        try:
            results = self.retrieve(question, top_k=3, use_mmr=False)
            return len(results) > 0 and any(
                len(doc.page_content.strip()) > 50 for doc in results
            )
        except Exception as exc:
            logger.warning("Question validation failed for '%s': %s", question[:50], exc)
            return False

    def reset_index(self, delete_persisted: bool = False) -> None:
        if self._vs:
            self._vs.reset(delete_files=delete_persisted)
        self._vs = None
        logger.info("Vector store reset (delete_persisted=%s).", delete_persisted)

    @property
    def is_ready(self) -> bool:
        if self._vs is None:
            return False
        return self._vs.is_ready
