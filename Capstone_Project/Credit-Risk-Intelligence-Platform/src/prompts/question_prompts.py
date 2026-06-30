# src/prompts/question_prompts.py
from __future__ import annotations

QUESTION_GENERATION_SYSTEM = (
    "You design targeted financial analysis questions for a RAG chatbot. "
    "CRITICAL: questions must be FACTUAL (not analytical) so the chatbot can find "
    "the exact answer in the document text. Never use generic templates."
)


def build_question_generation_prompt(
    combined_summary: dict,
    document_names:   list[str],
    risk_score:       float | None = None,
) -> str:
    entity_type   = combined_summary.get("entity_type", "Unknown")
    exec_overview = combined_summary.get("executive_overview", "")
    fin_position  = combined_summary.get("financial_position", "")
    docs_list     = "\n".join(f"- {d}" for d in document_names)
    risk_context  = f"\nRisk Score: {risk_score:.0f}/100" if risk_score is not None else ""

    return f"""Generate 10 questions for a RAG chatbot that searches financial documents.

ENTITY: {entity_type}
DOCUMENTS:
{docs_list}{risk_context}

FINANCIAL CONTEXT:
{exec_overview}
{fin_position}

CRITICAL RULES:
1. FACTUAL questions only — the chatbot finds answers by text search, not by reasoning.
   GOOD: "What was the net profit reported?"
   BAD: "What caused the profit to increase?" (requires analysis)

2. Use EXACT financial terms that appear in the documents:
   Banks: net profit, interest income, gross NPA, Capital Adequacy Ratio, total advances, total deposits
   Corporate: revenue, EBITDA, net profit, total assets, debt-to-equity ratio
   Individual: monthly income, outstanding loans, savings

3. Do NOT ask about specific years or exact figures unless mentioned in the context.
   GOOD: "What is the total interest income reported?"
   BAD: "What was the interest income for Q3 FY2023?" (too specific)

4. Questions must be answerable from the documents provided.

5. Write 5 questions from a LENDER perspective and 5 from the BORROWER perspective.

Respond in valid JSON (no markdown fences):
{{
  "analyst_questions": ["Q1?", "Q2?", "Q3?", "Q4?", "Q5?"],
  "entity_questions":  ["Q1?", "Q2?", "Q3?", "Q4?", "Q5?"],
  "document_types":    ["type 1", "type 2"],
  "entity_type":       "{entity_type}"
}}"""
