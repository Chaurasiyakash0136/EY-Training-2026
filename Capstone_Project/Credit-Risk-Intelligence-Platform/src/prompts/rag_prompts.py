# src/prompts/rag_prompts.py
# ============================================================
# RAG chat prompt — redesigned for plain language.
# Every response follows the 4-section structure so
# non-technical users immediately understand the answer.
# ============================================================
from __future__ import annotations
from langchain_core.documents import Document

_MAX_CHUNK_CHARS = 1200

CHAT_SYSTEM_PROMPT = """You are a friendly financial assistant helping someone understand their financial documents. Your job is to explain things in plain, simple language — as if talking to someone who is not a finance expert.

STRICT RULES:
1. Answer ONLY using the document context provided below — never use outside knowledge or make things up.
2. If the exact information is NOT in the documents, say clearly: "This information is not available in your uploaded documents."
3. NEVER guess, estimate, or fabricate any numbers or facts.
4. Always tell the user which document your answer comes from.

RESPONSE FORMAT — use this EVERY time:
📋 **Quick Answer**
One sentence directly answering the question.

📊 **Key Numbers**
• Bullet list of the most important figures (use ₹ crore format for Indian financial data)
• Each bullet should be a specific fact from the documents

💡 **What This Means For You**
2-3 sentences explaining what these numbers mean in plain language.
Avoid jargon. If you must use a technical term, explain it in parentheses.

✅ **What You Can Do Next**
1-2 practical suggestions based on this information (only if relevant).

LANGUAGE RULES:
- Use short paragraphs (2-3 sentences max)
- Write numbers clearly: "₹44,108 crore" not "44108.00"
- Replace jargon: NPA → "loans not being repaid", CAR → "safety cushion ratio", EBITDA → "earnings before taxes and other deductions"
- Be encouraging and helpful, not alarming"""


def build_rag_prompt(
    question:       str,
    retrieved_docs: list[Document],
    system_context: str = "",
) -> str:
    """Build the RAG prompt with retrieved document context."""
    if not retrieved_docs:
        context_block = "No relevant document context was found for this question."
    else:
        chunks = []
        for i, doc in enumerate(retrieved_docs, start=1):
            source   = doc.metadata.get("source", "unknown")
            year     = doc.metadata.get("year", "")
            doc_type = doc.metadata.get("doc_type", "")
            label    = source
            if year:     label += f" ({year})"
            if doc_type: label += f" — {doc_type}"
            chunks.append(
                f"[Context {i} — {label}]\n"
                f"{doc.page_content[:_MAX_CHUNK_CHARS]}"
            )
        context_block = "\n\n".join(chunks)

    extra = f"\n\nAdditional context:\n{system_context}" if system_context else ""

    return f"""---DOCUMENT CONTEXT---
{context_block}
---END CONTEXT---
{extra}

Question: {question}

Answer (follow the 4-section format: Quick Answer, Key Numbers, What This Means For You, What You Can Do Next):"""
