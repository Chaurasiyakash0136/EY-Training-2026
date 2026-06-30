# ui/pages/retirement_planner.py — NEW: Early Retirement Planner
from __future__ import annotations
import streamlit as st
from src.orchestrator.orchestrator import AgentOrchestrator
from src.models.schemas import (
    EntityType, PlatformState, RetirementInput,
)
from ui.theme import C, empty_state, info_box, kpi_card, page_header, section_header
from config.settings import settings


def render(state: PlatformState, orchestrator: AgentOrchestrator) -> None:
    page_header(
        "Early Retirement Planner",
        "Calculate your retirement corpus, required SIP, and get a personalised plan.",
    )

    # Show notice for non-individual entity types
    if (
        state.combined_summary
        and state.combined_summary.entity_type not in (
            EntityType.INDIVIDUAL, EntityType.UNKNOWN
        )
    ):
        st.markdown(
            f"<div style='background:{C['warning_bg']};border-left:4px solid {C['warning']};"
            f"padding:14px 18px;border-radius:0 8px 8px 0;margin-bottom:16px'>"
            f"<strong style='color:{C['warning']}'>⚠️ Note:</strong> "
            f"<span style='color:{C['text']}'>"
            f"This feature is designed for <strong>individual users</strong>. "
            f"Your uploaded documents appear to be from a {state.combined_summary.entity_type.value}. "
            f"The calculations below are most accurate for personal financial planning."
            f"</span></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='background:{C['blue_dim']};border-left:4px solid {C['blue']};"
            f"padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:16px;"
            f"font-size:0.84rem;color:{C['text']}'>"
            f"🏖️ <strong>For Individual Users Only</strong> — "
            f"Enter your details below to calculate your retirement plan. "
            f"If you've uploaded personal financial documents, values will be pre-filled."
            f"</div>",
            unsafe_allow_html=True,
        )

    # Auto-extract values from documents if available
    prefill = _extract_from_documents(state)

    tab_inputs, tab_results = st.tabs(["📝  Your Details", "📊  Results"])

    with tab_inputs:
        inputs = _render_inputs(state, prefill)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("🧮  Calculate My Retirement Plan", type="primary", use_container_width=False):
            with st.spinner("Calculating your retirement plan…"):
                result = orchestrator.calculate_retirement(inputs, state)
            st.success("✅  Plan calculated! View the Results tab.")
            st.rerun()

    with tab_results:
        if not state.retirement_result:
            info_box(
                "Fill in your details in the 'Your Details' tab and click "
                "<strong>Calculate My Retirement Plan</strong> to see results.",
                "info",
            )
            return
        _render_results(state)


def _extract_from_documents(state: PlatformState) -> dict:
    """Try to extract financial values from uploaded documents."""
    prefill: dict = {}
    if not state.risk_assessment:
        return prefill

    ra = state.risk_assessment
    if ra.monthly_income_estimate and ra.monthly_income_estimate > 0:
        prefill["monthly_income"]   = ra.monthly_income_estimate
        prefill["auto_extracted"]   = True
    if ra.monthly_expense_estimate and ra.monthly_expense_estimate > 0:
        prefill["monthly_expenses"] = ra.monthly_expense_estimate
        prefill["auto_extracted"]   = True
    if ra.debt_to_income_ratio and ra.monthly_income_estimate:
        # Estimate monthly debt payment
        estimated_emi = (ra.debt_to_income_ratio * ra.monthly_income_estimate)
        prefill["estimated_emi"] = estimated_emi

    return prefill


def _render_inputs(state: PlatformState, prefill: dict) -> RetirementInput:
    """Render editable input form. Returns RetirementInput object."""

    # Show auto-extraction notice if values were found
    if prefill.get("auto_extracted"):
        st.markdown(
            f"<div style='background:{C['teal_dim']};padding:10px 14px;"
            f"border-radius:8px;border:1px solid rgba(0,180,166,0.3);"
            f"font-size:0.82rem;color:{C['teal']};margin-bottom:12px'>"
            f"✨ Some values were automatically detected from your uploaded documents. "
            f"Please review and adjust as needed."
            f"</div>",
            unsafe_allow_html=True,
        )

    # Restore previous inputs if available
    prev = state.retirement_input

    section_header("👤", "Personal Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        current_age = st.number_input(
            "Your current age",
            min_value=18, max_value=75, step=1,
            value=int(prev.current_age) if prev else 30,
        )
    with col2:
        retirement_age = st.number_input(
            "Planned retirement age",
            min_value=current_age + 1, max_value=75, step=1,
            value=int(max(prev.planned_retirement_age, current_age + 1)) if prev else 50,
        )
    with col3:
        life_expectancy = st.number_input(
            "Life expectancy (years)",
            min_value=retirement_age + 1, max_value=100, step=1,
            value=int(max(prev.life_expectancy, retirement_age + 1)) if prev else settings.RETIREMENT_DEFAULT_LIFE_EXP,
        )

    section_header("💰", "Monthly Finances")
    col4, col5, col6 = st.columns(3)
    with col4:
        monthly_income = st.number_input(
            "Monthly income (₹)",
            min_value=0, step=1000,
            value=int(prefill.get("monthly_income", prev.monthly_income if prev else 100000)),
            help="Your total monthly take-home income",
        )
    with col5:
        monthly_expenses = st.number_input(
            "Monthly expenses (₹)",
            min_value=0, step=1000,
            value=int(prefill.get("monthly_expenses", prev.monthly_expenses if prev else 60000)),
            help="Total monthly spending including EMIs, rent, food, etc.",
        )
    with col6:
        current_sip = st.number_input(
            "Existing monthly SIP/investment (₹)",
            min_value=0, step=500,
            value=int(prev.current_sip if prev else 0),
            help="If you already invest a fixed amount monthly, enter it here",
        )

    section_header("🏦", "Current Financial Position")
    col7, col8, col9 = st.columns(3)
    with col7:
        current_savings = st.number_input(
            "Total savings & investments (₹)",
            min_value=0, step=10000,
            value=int(prev.current_savings if prev else 500000),
            help="Fixed deposits, mutual funds, stocks, PPF, etc.",
        )
    with col8:
        total_assets = st.number_input(
            "Total assets (₹)",
            min_value=0, step=10000,
            value=int(prev.total_assets if prev else 0),
            help="Property, gold, vehicles, other investments",
        )
    with col9:
        total_liabilities = st.number_input(
            "Total loans/liabilities (₹)",
            min_value=0, step=10000,
            value=int(prev.total_liabilities if prev else 0),
            help="Home loan, car loan, personal loans outstanding",
        )

    section_header("📈", "Planning Assumptions")
    col10, col11 = st.columns(2)
    with col10:
        expected_return = st.slider(
            "Expected annual return (%)",
            min_value=6.0, max_value=20.0, step=0.5,
            value=float(prev.expected_return if prev else settings.RETIREMENT_DEFAULT_RETURN),
            help="Conservative: 10-12%, Moderate: 12-15%, Aggressive: 15-18%",
        )
        inflation_rate = st.slider(
            "Expected inflation rate (%)",
            min_value=3.0, max_value=10.0, step=0.5,
            value=float(prev.inflation_rate if prev else settings.RETIREMENT_DEFAULT_INFLATION),
        )
    with col11:
        lifestyle_goal = st.selectbox(
            "Desired retirement lifestyle",
            options=["Minimal", "Comfortable", "Luxurious"],
            index=["Minimal", "Comfortable", "Luxurious"].index(
                prev.lifestyle_goal if prev else "Comfortable"
            ),
            help="Minimal: basic needs only | Comfortable: current lifestyle | Luxurious: premium lifestyle",
        )
        lifestyle_multiplier = {"Minimal": 0.7, "Comfortable": 1.0, "Luxurious": 1.4}[lifestyle_goal]

        emergency_months = st.number_input(
            "Emergency fund target (months)",
            min_value=3, max_value=24, step=1,
            value=int(prev.emergency_fund_months if prev else 6),
            help="How many months of expenses you want as emergency backup",
        )

    # Validation
    if retirement_age <= current_age:
        st.error("Retirement age must be greater than current age.")
    if monthly_expenses >= monthly_income and monthly_income > 0:
        st.warning("⚠️ Your expenses are equal to or greater than income. Check your numbers.")

    return RetirementInput(
        current_age            = current_age,
        planned_retirement_age = retirement_age,
        life_expectancy        = life_expectancy,
        monthly_income         = float(monthly_income),
        monthly_expenses       = float(monthly_expenses),
        current_savings        = float(current_savings),
        current_sip            = float(current_sip),
        total_assets           = float(total_assets),
        total_liabilities      = float(total_liabilities),
        expected_return        = expected_return,
        inflation_rate         = inflation_rate,
        emergency_fund_months  = emergency_months,
        lifestyle_goal         = lifestyle_goal,
        lifestyle_multiplier   = lifestyle_multiplier,
        auto_extracted         = bool(prefill.get("auto_extracted", False)),
    )


def _render_results(state: PlatformState) -> None:
    """Render retirement calculation results."""
    r = state.retirement_result
    i = state.retirement_input

    # Hero KPIs
    section_header("📊", "Your Retirement Numbers")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            kpi_card(
                "Corpus Needed",
                f"₹{r.corpus_needed / 1e7:.1f} Cr",
                f"At age {i.planned_retirement_age}",
                accent=C["blue"], icon="🏦", icon_bg=C["blue_dim"],
            ),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            kpi_card(
                "Monthly SIP Required",
                f"₹{r.total_sip_needed:,.0f}",
                f"Including ₹{r.required_monthly_sip:,.0f} additional",
                accent=C["teal"], icon="📈", icon_bg=C["teal_dim"],
            ),
            unsafe_allow_html=True,
        )
    with c3:
        gap_color = C["success"] if r.gap == 0 else C["warning"] if r.gap < r.corpus_needed * 0.3 else C["danger"]
        gap_label = "No Gap!" if r.gap == 0 else f"₹{r.gap / 1e7:.1f} Cr shortfall"
        st.markdown(
            kpi_card(
                "Funding Gap",
                gap_label,
                "Difference to cover",
                color=gap_color, accent=gap_color,
                icon="⚖️", icon_bg=f"{gap_color}18",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Feasibility assessment
    _feasibility_card(r, i)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Detailed breakdown
    section_header("🔍", "Detailed Breakdown")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            f"<div style='background:{C['surface']};border:1px solid {C['border']};"
            f"border-radius:10px;padding:16px'>"
            f"<div style='font-size:0.72rem;font-weight:700;color:{C['text3']};"
            f"text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px'>"
            f"📅 Timeline</div>",
            unsafe_allow_html=True,
        )
        _detail_row("Years to retirement", f"{r.years_to_retirement} years")
        _detail_row("Post-retirement years", f"{r.post_retirement_years} years")
        _detail_row("Future monthly expenses", f"₹{r.future_monthly_expenses:,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown(
            f"<div style='background:{C['surface']};border:1px solid {C['border']};"
            f"border-radius:10px;padding:16px'>"
            f"<div style='font-size:0.72rem;font-weight:700;color:{C['text3']};"
            f"text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px'>"
            f"💰 Funding Sources</div>",
            unsafe_allow_html=True,
        )
        _detail_row("Current savings at retirement", f"₹{r.current_savings_fv / 1e5:.1f} lakh")
        _detail_row("Total corpus needed", f"₹{r.corpus_needed / 1e7:.2f} crore")
        _detail_row("Additional SIP needed", f"₹{r.required_monthly_sip:,.0f}/month")
        st.markdown("</div>", unsafe_allow_html=True)

    # AI Recommendations
    if r.ai_summary:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        section_header("🤖", "AI Recommendations")
        st.markdown(
            f"<div style='background:{C['surface']};border:1px solid {C['border']};"
            f"border-top:3px solid {C['blue']};border-radius:0 0 10px 10px;"
            f"padding:18px 22px;font-size:0.9rem;line-height:1.75;color:{C['text']}'>"
            f"{r.ai_summary.replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        f"<div style='font-size:0.75rem;color:{C['text3']};text-align:center'>"
        f"📌 All projections use compound interest calculations with annual inflation adjustment. "
        f"Actual results will vary. Consult a certified financial planner for personalised advice."
        f"</div>",
        unsafe_allow_html=True,
    )


def _feasibility_card(r, i) -> None:
    if r.is_achievable:
        icon, title, msg, color = (
            "✅", "Early Retirement Appears Achievable!",
            f"Your required total monthly investment of ₹{r.total_sip_needed:,.0f} "
            f"represents {r.feasibility_pct:.0f}% of your monthly surplus — which is manageable.",
            C["success"],
        )
    elif r.feasibility_pct <= 80:
        icon, title, msg, color = (
            "⚠️", "Achievable with Some Adjustments",
            f"You'd need to invest ₹{r.total_sip_needed:,.0f}/month ({r.feasibility_pct:.0f}% of surplus). "
            f"Consider reducing expenses, increasing income, or adjusting your retirement age by 2-3 years.",
            C["warning"],
        )
    else:
        icon, title, msg, color = (
            "🔴", "Significant Adjustments Needed",
            f"The required SIP of ₹{r.total_sip_needed:,.0f}/month exceeds available surplus. "
            f"Extending retirement age, reducing lifestyle expectations, or significantly increasing income "
            f"would make this plan more realistic.",
            C["danger"],
        )

    st.markdown(
        f"<div style='padding:18px 22px;background:{color}12;"
        f"border:1px solid {color}30;border-radius:12px;"
        f"border-left:5px solid {color}'>"
        f"<div style='font-size:1rem;font-weight:700;color:{color};margin-bottom:6px'>"
        f"{icon} {title}</div>"
        f"<div style='font-size:0.875rem;color:{C['text']};line-height:1.6'>{msg}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _detail_row(label: str, value: str) -> None:
    st.markdown(
        f"<div style='display:flex;justify-content:space-between;"
        f"padding:6px 0;border-bottom:1px solid {C['border2']}'>"
        f"<span style='font-size:0.82rem;color:{C['text2']}'>{label}</span>"
        f"<span style='font-size:0.82rem;font-weight:600;color:{C['text']}'>{value}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
