# src/prompts/risk_prompts.py
from __future__ import annotations

RISK_SYSTEM_PROMPT = """You are a credit risk officer assessing a loan application.
Analyse the financial data objectively. ONLY use data provided — never fabricate or estimate numbers.
Explain your findings in plain language that a non-finance person can understand.
Use a traffic-light approach: green = good, yellow = needs attention, red = serious problem."""


def build_risk_prompt(combined_text: str) -> str:
    return f"""Analyse the financial data below and produce a credit risk assessment.
Use ONLY the data provided. Do NOT make up numbers.

---FINANCIAL DATA---
{combined_text}
---END---

Respond in valid JSON (no markdown fences, no extra text):
{{
  "risk_score": <0-100; higher = more risk; e.g. 25 = low risk, 65 = high risk>,
  "risk_level": "<Low|Moderate|High|Critical>",
  "credit_health": "<Excellent|Good|Fair|Poor|Critical>",
  "loan_eligibility": "<Eligible|Conditionally Eligible|Not Eligible>",
  "strengths": [
    "Plain language strength 1 — e.g. 'Consistent profit growth of 18% over 3 years'",
    "Strength 2",
    "Strength 3"
  ],
  "weaknesses": [
    "Plain language weakness — e.g. 'High debt: owes ₹200 crore, income only ₹50 crore/year'",
    "Weakness 2",
    "Weakness 3"
  ],
  "red_flags": [
    "Specific red flag — e.g. '12% of loans are not being repaid (gross NPA), above the safe limit of 5%'",
    "Red flag 2 if any"
  ],
  "missing_information": [
    "What document or data is missing — e.g. 'No cash flow statement found'",
    "Missing item 2 if any"
  ],
  "debt_to_income_ratio": <number between 0-5 or null if cannot be calculated>,
  "monthly_income_estimate": <monthly income in INR or null>,
  "monthly_expense_estimate": <monthly expenses in INR or null>
}}"""
