# src/prompts/recommendation_prompts.py
from __future__ import annotations

RECOMMENDATION_SYSTEM_PROMPT = (
    "You are a friendly financial advisor giving personalised, practical advice. "
    "Use simple, encouraging language. Focus on what the person CAN do, not just problems. "
    "Every recommendation should be specific and actionable — no vague advice."
)

RETIREMENT_SYSTEM_PROMPT = (
    "You are a retirement planning expert helping someone plan their early retirement. "
    "Use encouraging, simple language. Show them realistic steps they can take right now. "
    "Be honest about challenges but focus on solutions."
)


def build_recommendation_prompt(risk_assessment: dict, summary_texts: str) -> str:
    return f"""Generate personalised financial recommendations based on this assessment.

RISK ASSESSMENT:
{risk_assessment}

FINANCIAL SUMMARY:
{summary_texts[:4000]}

RULES:
- Use simple, friendly language
- Make every recommendation specific and actionable (not vague like "improve credit")
- Include realistic timelines where possible
- Sort actions by urgency: what to do THIS WEEK vs this month vs this year

Respond in valid JSON (no markdown fences):
{{
  "credit_improvement_checklist": [
    "Specific action 1 — e.g. 'Reduce credit card outstanding below ₹50,000 in the next 30 days'",
    "Specific action 2",
    "Specific action 3",
    "Specific action 4",
    "Specific action 5"
  ],
  "alternative_loan_suggestions": [
    {{
      "loan_type": "e.g. Secured Home Loan",
      "amount": "e.g. ₹25 lakh",
      "interest_rate_range": "e.g. 8.5% - 9.5% per year",
      "rationale": "Why this loan fits their profile in 1 sentence",
      "urgency": "High|Medium|Low"
    }}
  ],
  "financial_recommendations": [
    "Plain language recommendation 1 — e.g. 'Build an emergency fund of 6 months expenses (about ₹3 lakh) before applying for any new loan'",
    "Recommendation 2",
    "Recommendation 3"
  ],
  "safer_loan_amount": "e.g. ₹15 lakh — because monthly EMI would be ₹16,000, which is 35% of income (safe limit is 40%)",
  "next_best_actions": [
    "THIS WEEK: One urgent action",
    "THIS MONTH: One medium-term action",
    "THIS YEAR: One longer-term action"
  ],
  "risk_simulator_data": [
    {{"year": 1, "risk_score": 55, "action": "After reducing debt by 20%"}},
    {{"year": 2, "risk_score": 45, "action": "After building emergency fund"}},
    {{"year": 3, "risk_score": 35, "action": "After consistent on-time payments"}}
  ],
  "urgency_sorted_actions": [
    {{"action": "Action description", "urgency": "High", "timeline": "This week", "impact": "Reduces risk score by ~10 points"}},
    {{"action": "Action 2", "urgency": "Medium", "timeline": "This month", "impact": "Improves credit eligibility"}},
    {{"action": "Action 3", "urgency": "Low", "timeline": "3-6 months", "impact": "Long-term credit building"}}
  ]
}}"""


def build_retirement_prompt(inputs: dict, calculation: dict) -> str:
    return f"""Help this person plan for early retirement. Be encouraging and specific.

THEIR FINANCIAL SITUATION:
{inputs}

CALCULATION RESULTS:
{calculation}

Write a personalised retirement plan analysis. Be honest but encouraging.
Focus on: Is this achievable? What are the 3 most important actions they should take?

Respond in valid JSON (no markdown fences):
{{
  "summary": "3-4 sentences: Is early retirement at [age] achievable? What is the key challenge? What is the biggest opportunity? Use plain language, no jargon.",
  "key_message": "One sentence: the single most important thing they need to know about their retirement plan",
  "action_steps": [
    "Step 1: Most important action with specific number — e.g. 'Start a monthly SIP of ₹25,000 in a diversified equity mutual fund today'",
    "Step 2: Second most important action",
    "Step 3: Third action"
  ],
  "encouragement": "One sentence of genuine, realistic encouragement based on their actual situation"
}}"""
