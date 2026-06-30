# src/orchestrator/orchestrator.py
# ============================================================
# Orchestrator — coordinates the three agents.
# Manages the full pipeline: ingest → analyse → chat → plan.
# ============================================================
from __future__ import annotations
import math
from pathlib import Path
from src.agents.document_agent import DocumentIntelligenceAgent
from src.agents.chat_agent import ChatAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.models.schemas import (
    AIRecommendations, ChatMessage, DocumentMetadata,
    DocumentSummary, PlatformState, RiskAssessment,
    RetirementInput, RetirementResult,
)
from src.retrieval.sampling import extract_financial_sample
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AgentOrchestrator:
    def __init__(self) -> None:
        self._doc_agent       = DocumentIntelligenceAgent()
        self._retrieval_agent = RetrievalAgent()
        self._chat_agent      = ChatAgent()

    # ── Document Ingestion ───────────────────────────────────

    def ingest_document(
        self,
        file_path: str | Path,
        metadata:  DocumentMetadata,
        state:     PlatformState,
    ) -> DocumentSummary:
        logger.info("Ingesting: %s", metadata.file_name)
        summary, chunks = self._doc_agent.process(file_path, metadata)

        if chunks:
            self._retrieval_agent.index_documents(chunks)
            state.vector_store_ready = True

        state.summaries[metadata.file_name] = summary
        return summary

    def refresh_intelligence(self, state: PlatformState) -> None:
        """
        Generate combined summary + validated dynamic questions.
        Called after all documents are processed.
        """
        if not state.summaries:
            return

        logger.info(
            "refresh_intelligence for %d documents.",
            len(state.summaries),
        )

        all_text = "\n\n---\n\n".join(
            f"Document: {name}\n{extract_financial_sample(s.raw_extracted_text, 2000)}"
            for name, s in state.summaries.items()
        )

        # 1 — Combined summary
        try:
            state.combined_summary = self._chat_agent.generate_combined_summary(
                state.summaries, all_text
            )
            logger.info(
                "Combined summary done. Entity: %s",
                state.combined_summary.entity_type.value,
            )
        except Exception as exc:
            logger.error("Combined summary failed: %s", exc)

        # 2 — Dynamic questions with validation
        if state.combined_summary:
            try:
                risk_score = state.risk_assessment.risk_score if state.risk_assessment else None
                state.suggested_questions = self._chat_agent.generate_questions(
                    state.combined_summary,
                    list(state.summaries.keys()),
                    risk_score,
                    retrieval_agent=self._retrieval_agent,
                )
            except Exception as exc:
                logger.error("Question generation failed: %s", exc)

    # ── Risk Assessment ──────────────────────────────────────

    def run_risk_analysis(self, state: PlatformState) -> RiskAssessment | None:
        if not state.summaries:
            logger.warning("No summaries for risk analysis.")
            return None

        combined = "\n\n---\n\n".join(
            f"Document: {name}\n{extract_financial_sample(s.raw_extracted_text, 3000)}"
            for name, s in state.summaries.items()
        )

        risk = self._chat_agent.assess_risk(combined)
        state.risk_assessment = risk
        logger.info("Risk: %.1f (%s)", risk.risk_score, risk.risk_level.value)

        # Refresh questions with risk context
        if state.combined_summary:
            try:
                state.suggested_questions = self._chat_agent.generate_questions(
                    state.combined_summary,
                    list(state.summaries.keys()),
                    risk.risk_score,
                    retrieval_agent=self._retrieval_agent,
                )
            except Exception as exc:
                logger.warning("Post-risk question refresh failed: %s", exc)

        return risk

    # ── Recommendations ──────────────────────────────────────

    def run_recommendations(self, state: PlatformState) -> AIRecommendations:
        if state.risk_assessment is None:
            result = self.run_risk_analysis(state)
            if result is None:
                return AIRecommendations(
                    financial_recommendations=["Upload documents first."]
                )

        summary_text = "\n\n".join(
            f"{name}: {s.executive_summary}\n{s.financial_overview}"
            for name, s in state.summaries.items()
        )
        recs = self._chat_agent.generate_recommendations(
            state.risk_assessment, summary_text
        )
        state.recommendations = recs
        return recs

    # ── Retirement Planner ───────────────────────────────────

    def calculate_retirement(
        self,
        inputs: RetirementInput,
        state:  PlatformState,
    ) -> RetirementResult:
        """
        Calculate retirement corpus, SIP requirement, and gap analysis.
        Uses compound interest and inflation-adjusted projections.
        """
        logger.info("Calculating retirement plan for age %d → %d", inputs.current_age, inputs.planned_retirement_age)

        years = max(inputs.planned_retirement_age - inputs.current_age, 1)
        post  = max(inputs.life_expectancy - inputs.planned_retirement_age, 1)

        r_annual   = inputs.expected_return  / 100.0
        inf_annual = inputs.inflation_rate   / 100.0
        r_monthly  = r_annual / 12.0

        # Future monthly expenses (inflation adjusted)
        future_monthly_expenses = (
            inputs.monthly_expenses
            * inputs.lifestyle_multiplier
            * (1 + inf_annual) ** years
        )

        # Retirement corpus needed
        # Using real return = (1 + nominal) / (1 + inflation) - 1
        real_annual  = (1 + r_annual) / (1 + inf_annual) - 1
        real_monthly = real_annual / 12.0

        if real_monthly > 0:
            corpus_needed = (
                future_monthly_expenses * 12
                * (1 - (1 + real_monthly) ** (-post))
                / real_monthly
            )
        else:
            corpus_needed = future_monthly_expenses * 12 * post

        # Current savings grow to retirement date
        current_savings_fv = inputs.current_savings * (1 + r_annual) ** years

        # Existing SIP grows to retirement date
        if r_monthly > 0 and inputs.current_sip > 0:
            months = years * 12
            existing_sip_fv = inputs.current_sip * (
                ((1 + r_monthly) ** months - 1) / r_monthly
            ) * (1 + r_monthly)
        else:
            existing_sip_fv = inputs.current_sip * years * 12

        total_current_fv = current_savings_fv + existing_sip_fv
        gap = max(corpus_needed - total_current_fv, 0.0)

        # Required additional monthly SIP to close gap
        months = years * 12
        if r_monthly > 0 and gap > 0:
            required_sip = gap * r_monthly / ((1 + r_monthly) ** months - 1)
        elif gap > 0:
            required_sip = gap / months
        else:
            required_sip = 0.0

        total_sip = required_sip + inputs.current_sip

        # Feasibility: what % of surplus income is needed
        monthly_surplus = max(inputs.monthly_income - inputs.monthly_expenses, 1.0)
        feasibility_pct = (total_sip / monthly_surplus) * 100
        is_achievable   = feasibility_pct <= 60.0  # safe if SIP ≤ 60% of surplus

        result = RetirementResult(
            corpus_needed           = round(corpus_needed, 0),
            current_savings_fv      = round(current_savings_fv, 0),
            gap                     = round(gap, 0),
            required_monthly_sip    = round(required_sip, 0),
            total_sip_needed        = round(total_sip, 0),
            years_to_retirement     = years,
            future_monthly_expenses = round(future_monthly_expenses, 0),
            post_retirement_years   = post,
            is_achievable           = is_achievable,
            feasibility_pct         = round(feasibility_pct, 1),
        )

        # Generate AI-powered plain language advice
        try:
            result.ai_summary = self._chat_agent.generate_retirement_advice(inputs, result)
        except Exception as exc:
            logger.warning("Retirement AI advice failed: %s", exc)
            result.ai_summary = self._default_retirement_advice(result, inputs)

        state.retirement_input  = inputs
        state.retirement_result = result
        return result

    @staticmethod
    def _default_retirement_advice(result: RetirementResult, inputs: RetirementInput) -> str:
        if result.is_achievable:
            return (
                f"✅ Your retirement goal appears achievable! "
                f"You need a total monthly investment of ₹{result.total_sip_needed:,.0f} "
                f"to build a retirement corpus of ₹{result.corpus_needed/1e7:.1f} crore by age {inputs.planned_retirement_age}. "
                f"Start your SIP today — time is your biggest advantage."
            )
        else:
            return (
                f"Your retirement goal needs some adjustments. "
                f"The required monthly SIP of ₹{result.total_sip_needed:,.0f} "
                f"is {result.feasibility_pct:.0f}% of your surplus income. "
                f"Consider extending your retirement age by 2-3 years, reducing expenses, "
                f"or increasing your income to make this plan more manageable."
            )

    # ── Chat ─────────────────────────────────────────────────

    def chat(self, question: str, state: PlatformState) -> ChatMessage:
        user_msg = ChatMessage(role="user", content=question)
        state.chat_history.append(user_msg)

        retrieved = self._retrieval_agent.retrieve(question)
        response  = self._chat_agent.answer_question(question, retrieved)
        state.chat_history.append(response)
        return response

    # ── Status / Reset ───────────────────────────────────────

    @property
    def vector_store_ready(self) -> bool:
        return self._retrieval_agent.is_ready

    def reset(self) -> None:
        """Clear in-memory index AND delete persisted FAISS files."""
        self._retrieval_agent.reset_index(delete_persisted=True)
        logger.info("Orchestrator reset complete.")
