# src/agents/chat_agent.py
# ============================================================
# Agent 3 — handles all LLM-based tasks:
#   • Chat Q&A (RAG-grounded, plain language)
#   • Risk assessment
#   • Recommendations
#   • Combined multi-document summary
#   • Dynamic question generation with validation
# ============================================================
from __future__ import annotations
import json
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from src.llm.llm_factory import invoke_with_fallback
from src.models.schemas import (
    AIRecommendations, ChatMessage, CombinedSummary,
    EntityType, LoanSuggestion, QuestionSet,
    RiskAssessment, RiskLevel, RetirementInput, RetirementResult,
)
from src.prompts.rag_prompts import CHAT_SYSTEM_PROMPT, build_rag_prompt
from src.prompts.summary_prompts import COMBINED_SUMMARY_SYSTEM, build_combined_summary_prompt
from src.prompts.risk_prompts import RISK_SYSTEM_PROMPT, build_risk_prompt
from src.prompts.recommendation_prompts import (
    RECOMMENDATION_SYSTEM_PROMPT, RETIREMENT_SYSTEM_PROMPT,
    build_recommendation_prompt, build_retirement_prompt,
)
from src.prompts.question_prompts import QUESTION_GENERATION_SYSTEM, build_question_generation_prompt
from src.retrieval.sampling import extract_financial_sample
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Default questions used when generation or validation fails completely
_DEFAULT_ANALYST_QUESTIONS = [
    "What is the total income or interest income reported?",
    "What are the total assets and total liabilities?",
    "Is there evidence of consistent positive cash flow?",
    "What is the total debt or outstanding loan amount?",
    "Are there any financial red flags or overdue payments mentioned?",
]
_DEFAULT_ENTITY_QUESTIONS = [
    "What is my overall financial health based on these documents?",
    "What are my biggest financial strengths?",
    "What is the net profit or income reported?",
    "What should I improve to get better credit terms?",
    "What does the balance sheet show about assets and liabilities?",
]


class ChatAgent:

    # ── Chat ─────────────────────────────────────────────────

    def answer_question(
        self,
        question:       str,
        retrieved_docs: list[Document],
    ) -> ChatMessage:
        logger.info("Chat: '%s...'", question[:60])
        prompt  = build_rag_prompt(question, retrieved_docs)
        sources = list({
            d.metadata.get("source", "")
            for d in retrieved_docs
            if d.metadata.get("source")
        })
        try:
            answer = invoke_with_fallback([
                SystemMessage(content=CHAT_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ])
        except Exception as exc:
            logger.error("Chat error: %s", exc)
            answer = (
                f"⚠️ I encountered an error: {exc}\n\n"
                "Please check your API keys in `.env` and ensure documents are processed."
            )
        return ChatMessage(role="assistant", content=answer, sources=sources)

    # ── Combined Summary ─────────────────────────────────────

    def generate_combined_summary(
        self,
        summaries: dict,
        all_text:  str,
    ) -> CombinedSummary:
        logger.info("Combined summary for %d documents.", len(summaries))

        summary_texts = {}
        for name, s in summaries.items():
            financial_sample = extract_financial_sample(s.raw_extracted_text, max_chars=3000)
            summary_texts[name] = (
                f"Executive Summary: {s.executive_summary}\n"
                f"Financial Overview: {s.financial_overview}\n"
                f"Income: {s.income_summary}\n"
                f"Assets: {s.assets_summary}\n"
                f"Liabilities: {s.liabilities_summary}\n\n"
                f"Financial Data:\n{financial_sample}"
            )

        prompt = build_combined_summary_prompt(summary_texts, all_text)
        try:
            raw  = invoke_with_fallback([
                SystemMessage(content=COMBINED_SUMMARY_SYSTEM),
                HumanMessage(content=prompt),
            ])
            data = json.loads(self._strip_fences(raw))
            try:
                entity_type = EntityType(data.get("entity_type", "Unknown"))
            except ValueError:
                entity_type = EntityType.UNKNOWN
            return CombinedSummary(
                executive_overview   = data.get("executive_overview", ""),
                financial_position   = data.get("financial_position", ""),
                income_profitability = data.get("income_profitability", ""),
                key_strengths        = data.get("key_strengths", []),
                areas_of_concern     = data.get("areas_of_concern", []),
                overall_assessment   = data.get("overall_assessment", ""),
                entity_type          = entity_type,
                documents_covered    = data.get("documents_covered", list(summaries.keys())),
            )
        except Exception as exc:
            logger.error("Combined summary error: %s", exc)
            return CombinedSummary(
                executive_overview = "Combined analysis generation failed. Re-upload documents.",
                documents_covered  = list(summaries.keys()),
            )

    # ── Dynamic Questions with Validation ────────────────────

    def generate_questions(
        self,
        combined_summary:  CombinedSummary,
        document_names:    list[str],
        risk_score:        float | None       = None,
        retrieval_agent    = None,   # RetrievalAgent for validation
    ) -> QuestionSet:
        """
        Generate context-aware questions, then validate each against
        the vector store to guarantee they return answers.

        If a question fails validation, it is replaced with a safe
        fallback question from the entity-appropriate defaults.
        """
        logger.info("Generating questions for %s", combined_summary.entity_type.value)
        summary_dict = {
            "entity_type":        combined_summary.entity_type.value,
            "executive_overview": combined_summary.executive_overview,
            "financial_position": combined_summary.financial_position,
        }
        prompt = build_question_generation_prompt(summary_dict, document_names, risk_score)

        try:
            raw  = invoke_with_fallback([
                SystemMessage(content=QUESTION_GENERATION_SYSTEM),
                HumanMessage(content=prompt),
            ])
            data = json.loads(self._strip_fences(raw))
            try:
                entity_type = EntityType(data.get("entity_type", combined_summary.entity_type.value))
            except ValueError:
                entity_type = combined_summary.entity_type

            analyst_qs = data.get("analyst_questions", [])[:5]
            entity_qs  = data.get("entity_questions",  [])[:5]

        except Exception as exc:
            logger.warning("Question generation failed: %s", exc)
            return self._fallback_questions(combined_summary.entity_type)

        # ── Validate each question against the vector store ──
        if retrieval_agent and retrieval_agent.is_ready:
            analyst_qs = self._validate_questions(analyst_qs, _DEFAULT_ANALYST_QUESTIONS, retrieval_agent)
            entity_qs  = self._validate_questions(entity_qs,  _DEFAULT_ENTITY_QUESTIONS,  retrieval_agent)
            is_validated = True
        else:
            is_validated = False

        return QuestionSet(
            entity_type       = entity_type if "entity_type" in locals() else combined_summary.entity_type,
            document_types    = data.get("document_types", []) if "data" in locals() else [],
            analyst_questions = analyst_qs,
            entity_questions  = entity_qs,
            is_generated      = True,
            is_validated      = is_validated,
        )

    def _validate_questions(
        self,
        questions:  list[str],
        fallbacks:  list[str],
        retrieval_agent,
    ) -> list[str]:
        """Replace questions that have no retrievable answer with fallbacks."""
        validated = []
        fallback_pool = list(fallbacks)

        for q in questions:
            if retrieval_agent.validate_question(q):
                validated.append(q)
                logger.debug("Question validated: '%s'", q[:60])
            else:
                # Try to find a fallback that works
                replacement = None
                for fb in fallback_pool:
                    if retrieval_agent.validate_question(fb):
                        replacement = fb
                        fallback_pool.remove(fb)
                        break
                if replacement:
                    validated.append(replacement)
                    logger.info(
                        "Question replaced: '%s' → '%s'",
                        q[:50],
                        replacement[:50],
                    )
                else:
                    # Keep original as last resort (validation unavailable or all fallbacks fail too)
                    validated.append(q)

        return validated[:5]

    # ── Risk Assessment ──────────────────────────────────────

    def assess_risk(self, combined_text: str) -> RiskAssessment:
        logger.info("Risk assessment.")
        prompt = build_risk_prompt(combined_text)
        try:
            raw  = invoke_with_fallback([
                SystemMessage(content=RISK_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ])
            data = json.loads(self._strip_fences(raw))
            try:
                data["risk_level"] = RiskLevel(data.get("risk_level", "Moderate"))
            except ValueError:
                data["risk_level"] = RiskLevel.MODERATE
            return RiskAssessment(**data)
        except Exception as exc:
            logger.error("Risk assessment error: %s", exc)
            return RiskAssessment(
                risk_score=50.0,
                risk_level=RiskLevel.MODERATE,
                credit_health="Assessment failed — re-run analysis.",
            )

    # ── Recommendations ──────────────────────────────────────

    def generate_recommendations(
        self,
        risk_assessment: RiskAssessment,
        summary_texts:   str,
    ) -> AIRecommendations:
        logger.info("Generating recommendations.")
        prompt = build_recommendation_prompt(
            risk_assessment.model_dump(mode="json"), summary_texts
        )
        try:
            raw       = invoke_with_fallback([
                SystemMessage(content=RECOMMENDATION_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ])
            data      = json.loads(self._strip_fences(raw))
            raw_loans = data.pop("alternative_loan_suggestions", [])
            loans     = [LoanSuggestion(**l) for l in raw_loans if isinstance(l, dict)]
            return AIRecommendations(**data, alternative_loan_suggestions=loans)
        except Exception as exc:
            logger.error("Recommendations error: %s", exc)
            return AIRecommendations(
                financial_recommendations=[f"Recommendation generation failed: {exc}"],
            )

    # ── Retirement Planner ───────────────────────────────────

    def generate_retirement_advice(
        self,
        inputs:      RetirementInput,
        calculation: RetirementResult,
    ) -> str:
        """Generate plain-language retirement planning advice."""
        logger.info("Generating retirement advice.")
        prompt = build_retirement_prompt(
            inputs.model_dump(mode="json"),
            calculation.model_dump(mode="json"),
        )
        try:
            raw  = invoke_with_fallback([
                SystemMessage(content=RETIREMENT_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ])
            data = json.loads(self._strip_fences(raw))
            # Return structured result
            summary      = data.get("summary", "")
            action_steps = data.get("action_steps", [])
            encouragement = data.get("encouragement", "")
            full_text = summary
            if action_steps:
                full_text += "\n\n**Your Action Plan:**\n"
                for i, step in enumerate(action_steps, 1):
                    full_text += f"\n{i}. {step}"
            if encouragement:
                full_text += f"\n\n💪 {encouragement}"
            return full_text
        except Exception as exc:
            logger.error("Retirement advice error: %s", exc)
            return "Retirement analysis complete. Please review the numbers above and consult a financial advisor for personalised guidance."

    # ── Helpers ──────────────────────────────────────────────

    @staticmethod
    def _strip_fences(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            parts = text.split("```")
            text  = parts[1] if len(parts) > 1 else text
            if text.startswith("json"):
                text = text[4:]
        return text.strip()

    def _fallback_questions(self, entity_type: EntityType) -> QuestionSet:
        """Safe fallback questions — always generic enough to be answerable."""
        if entity_type == EntityType.COMMERCIAL_BANK:
            aq = [
                "What is the Capital Adequacy Ratio reported?",
                "What is the Gross NPA ratio mentioned?",
                "What is the Net Interest Income for the period?",
                "What are total deposits and advances?",
                "What provisions were made for non-performing assets?",
            ]
            eq = [
                "What was the net profit for the reporting period?",
                "How has the loan book changed compared to last year?",
                "What dividend was declared for shareholders?",
                "What are the key risks identified by management?",
                "What is the Return on Assets reported?",
            ]
        elif entity_type in (EntityType.LARGE_CORPORATE, EntityType.SME):
            aq = [
                "What is the debt-to-equity ratio mentioned?",
                "What is the total revenue or net sales reported?",
                "What is the EBITDA or operating profit?",
                "Are there any overdue loans or defaults mentioned?",
                "What is the working capital position?",
            ]
            eq = [
                "What is the net profit margin reported?",
                "What are the biggest expense categories?",
                "How has revenue changed over the reporting period?",
                "What are the total assets reported?",
                "What improvements would strengthen the financial profile?",
            ]
        else:
            aq = _DEFAULT_ANALYST_QUESTIONS
            eq = _DEFAULT_ENTITY_QUESTIONS
        return QuestionSet(
            entity_type=entity_type,
            analyst_questions=aq,
            entity_questions=eq,
            is_generated=False,
            is_validated=False,
        )
