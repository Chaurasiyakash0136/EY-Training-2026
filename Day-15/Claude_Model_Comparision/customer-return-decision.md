# Claude Model Comparison — Customer Return Policy Decision

> **Prompt tested across three Claude models:**
> *"A customer bought a jacket 47 days ago. Your return policy is 45 days. The customer says the zipper broke on day 44 but they were travelling. No receipt, but the order is in your system. They're a 6-year customer with 23 orders. Should you accept the return? Write one paragraph with reasoning."*

---

## Table of Contents

- [Overview](#overview)
- [Model Responses](#model-responses)
  - [Claude Haiku 4.5](#1-claude-haiku-45)
  - [Claude Sonnet 4.6](#2-claude-sonnet-46)
  - [Claude Opus 4.8](#3-claude-opus-48)
- [Comparative Analysis](#comparative-analysis)
- [Verdict](#verdict)
- [Rephrased Prompt](#rephrased-prompt)

---

## Overview

This document captures the same customer service decision prompt submitted to three Claude models — **Haiku 4.5**, **Sonnet 4.6**, and **Opus 4.8** — and evaluates the quality, nuance, and decision-making rigour of each response. The task is straightforward: recommend whether to accept a return that is technically 2 days past the stated 45-day window, given specific customer context.

---

## Model Responses

### 1. Claude Haiku 4.5

**Response:**

Yes, accept the return. The zipper broke during the return window (day 44), and the brief 2-day delay is justified by travel. A 6-year customer with 23 orders is valuable — losing them over a late return caused by a product defect is not worth it. The order is confirmed in your system, so no receipt is needed. Accept the return to preserve the relationship.

**Analysis:**

Haiku delivers the correct answer with practical reasoning. It identifies the core factors: the defect occurred within the window, the customer has long-term value, and the system verification solves the receipt problem. The response is concise and action-oriented.

**Strengths:**
- Direct and decisive
- Identifies customer lifetime value
- Fast and easy to understand
- Appropriate for rapid decision-making

**Weaknesses:**
- Does not distinguish between a "defect claim" vs. a "late return exception" — treats them as the same issue
- Minimal exploration of policy implications
- Does not frame the communication strategy for the customer
- Lacks depth on risk/precedent considerations

---

### 2. Claude Sonnet 4.6

**Response:**

Yes — frame this as a defect resolution, not a policy exception. A zipper breaking on day 44 is a product failure, not a late return; the 45-day window governs change-of-mind returns, and a 2-day overage caused by a manufacturing defect is distinct from a customer simply deciding they don't want the jacket anymore. The order in your system is stronger proof than a paper receipt. The real consideration is customer lifetime value: a 6-year, 23-order customer represents significant repeat revenue, and refusing them over two days and a broken zipper would be a false economy. Accept the return, make the distinction explicit in your response ("we treat defects differently from late change-of-mind returns"), and use it as a service recovery moment.

**Analysis:**

Sonnet provides the correct answer with sophisticated framing. It distinguishes the defect claim from a policy exception, suggests how to communicate the decision, and weighs the lifetime-value calculation. The response is concise but substantive.

**Strengths:**
- Distinguishes defect claim from late return — a critical nuance
- Recommends a specific communication strategy
- Balances policy integrity with customer value
- Frames the decision as goodwill, not capitulation
- Appropriate length and depth for a professional context

**Weaknesses:**
- Does not explore edge cases or precedent risk
- Could have mentioned documentation for future reference
- Slight assumption that the zipper failure can be verified (not addressed)

---

### 3. Claude Opus 4.8

**Response:**

Yes, absolutely accept the return, and here's why this decision is straightforward if you separate three things that are often conflated. First: the zipper failed on day 44, which is within your 45-day window. The fact that the customer didn't report it until day 47 is a reporting lag, not a defect-discovery lag — the failure itself is on-policy. Second: the distinction between "product defect" and "policy exception" is critical. Your 45-day window exists to balance buyer's remorse (which should be time-limited) with the need for customers to catch problems and report them. A zipper breaking is a manufacturing failure, not a case of the customer changing their mind, so treating it as a policy override misdiagnoses the issue entirely. Third: customer lifetime value. This is a 6-year customer with 23 orders — that's roughly $150–300k in lifetime revenue depending on jacket price. The cost of a replacement or refund is likely under $200, making this a 750:1 return-on-investment just in terms of retention. The missing receipt is irrelevant because your order system provides the necessary verification. The risk of refusing is that a loyal customer perceives you as penny-wise and pound-foolish, they leave, they speak negatively about the experience, and you lose not just their future revenue but also the customers they influence. Accept the return, document it as a defect claim (not a policy exception), and communicate the reason to the customer so they understand you're backing your product quality, not bending rules on demand. This turns a potential reputation risk into a loyalty moment.

**Analysis:**

Opus provides the most comprehensive response. It explicitly separates three layers of the decision (temporal, categorical, and financial), explains why each matters, and provides a decision framework that protects policy integrity while delivering the right outcome. It anticipates objections and explains the long-term risk calculus.

**Strengths:**
- Most rigorous breakdown of the decision logic
- Explains the distinction between defect and exception with authority
- Calculates lifetime value and shows the math
- Addresses reputational risk explicitly
- Recommends documentation approach
- Most useful for building a defensible policy going forward
- Anticipates how the customer will perceive the decision

**Weaknesses:**
- Longer response (may be overkill for a simple decision)
- More verbose than necessary for operational speed
- Makes assumptions about price point (though reasonable ones)

---

## Comparative Analysis

| Criterion | Haiku 4.5 | Sonnet 4.6 | Opus 4.8 |
|---|---|---|---|
| **Correct decision** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Defect vs. exception distinction** | ❌ Absent | ✅ Explicit | ✅ Detailed |
| **Communication strategy** | ❌ None | ✅ Recommended | ✅ Detailed |
| **Lifetime value analysis** | ⚠️ Mentioned | ✅ Framed | ✅ Quantified |
| **Risk/precedent consideration** | ❌ None | ⚠️ Implicit | ✅ Explicit |
| **Documentation guidance** | ❌ None | ❌ None | ✅ Mentioned |
| **Conciseness** | ✅ High | ✅ Balanced | ⚠️ Verbose |
| **Actionability** | ✅ High | ✅ High | ✅ High |
| **Policy framework utility** | ❌ Low | ✅ Medium | ✅ High |
| **Best for operations** | Quick triage | Daily decisions | Policy design |

---

## Verdict

### 🏆 Best overall response: **Claude Sonnet 4.6**

Sonnet delivered the optimal balance for a real-world customer service decision. It provided sufficient nuance to protect policy integrity (the defect vs. exception distinction), a concrete communication strategy, and enough depth to be defensible without being so detailed that it slows down the decision. For a customer service manager making this call in real-time, Sonnet's response was immediately actionable and included the key reasoning needed to explain the decision to stakeholders.

**When to use each model for this task type:**

| Use case | Recommended model |
|---|---|
| Rapid front-line decision-making (support agent, chat) | **Haiku 4.5** |
| Customer service manager approving individual cases | **Sonnet 4.6** |
| Building or refining return/warranty policy framework | **Opus 4.8** |

---

## Model Performance Summary

**Haiku 4.5:** Correct outcome, but lacks the nuance to prevent similar cases from becoming contentious. Best for speed when the policy is clear; not suitable for edge cases.

**Sonnet 4.6:** Best practical balance. Delivers the right decision with the reasoning and communication approach needed to execute it professionally. The defect/exception distinction is the key insight, and Sonnet surfaces it clearly without over-explaining.

**Opus 4.8:** Most comprehensive. Provides the decision *and* a framework for thinking about future similar cases. Best used by policy makers rather than individual case handlers, but overkill for a single decision.

---

## Rephrased Prompt

The original prompt was conversational and somewhat ambiguous. Below is a structured version optimised for more consistent, high-quality output across all tiers:

---

**Rephrased prompt:**

> You are a customer service decision-maker. A customer requests a return under these circumstances:
>
> **Customer profile:**
> - Account age: 6 years
> - Total orders: 23
> - Current order: jacket purchased 47 days ago
>
> **Return request details:**
> - Your policy: 45-day return window
> - Customer claim: zipper broke on day 44 of ownership
> - Reason for late submission: customer was travelling and unable to contact support until day 47
> - Proof of purchase: no receipt provided, but order verified in system
>
> **Your task:**
> 1. Make a clear yes/no recommendation.
> 2. Distinguish between: (a) a defect claim, (b) a policy exception, and (c) a customer service decision.
> 3. Explain how to frame this decision in your response to the customer.
> 4. Consider customer lifetime value in your reasoning.
> 5. Note any risk or precedent implications.

---

**Why this version is better:**

- Separates customer profile, request details, and decision criteria clearly
- Asks for explicit distinction between defect and policy exception
- Requests communication strategy (important for execution)
- Prompts for lifetime value analysis
- Includes risk consideration
- Produces more structured, comparable responses across all three models

---

## Conclusion

All three models reached the correct decision. The difference is in the depth, nuance, and applicability of the reasoning:

- **Haiku** is right but unfinished — it doesn't give you the tools to handle the next similar case.
- **Sonnet** is right and complete — it gives you a decision, reasoning, and how to communicate it.
- **Opus** is right and comprehensive — it gives you a decision framework for the category of decisions.

For most customer service teams, **Sonnet is the best fit** — it provides the professional judgment needed without the overhead of Opus, and significantly more strategic thinking than Haiku.

---

*Generated using Claude model comparison methodology · Responses captured from identical prompt across Haiku 4.5, Sonnet 4.6, and Opus 4.8 · For evaluation and decision-making guidance purposes*
