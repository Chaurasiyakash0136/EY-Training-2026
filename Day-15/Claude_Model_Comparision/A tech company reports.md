# Claude Model Comparison — Earnings Analysis Prompt

> **Prompt tested across three Claude models:**
> *"A tech company reports: Revenue up 12% YoY, but gross margins fell from 68% to 61%, operating expenses rose 31%, and the CFO mentioned 'investment in AI infrastructure.' The CEO said growth is 'on track.' Is this a healthy quarter? What should an analyst flag?"*

---

## Table of Contents

- [Overview](#overview)
- [Model Responses](#model-responses)
  - [Claude Opus 4.8](#1-claude-opus-48)
  - [Claude Sonnet 4.6](#2-claude-sonnet-46)
  - [Claude Haiku 4.5](#3-claude-haiku-45)
- [Comparative Analysis](#comparative-analysis)
- [Verdict](#verdict)
- [Rephrased Prompt](#rephrased-prompt)

---

## Overview

This document captures the same financial analysis prompt submitted to three Claude models — **Opus 4.8**, **Sonnet 4.6**, and **Haiku 4.5** — and evaluates the quality, depth, and analytical rigour of each response. The goal is to understand where each model excels and which is best suited for professional financial analysis tasks.

---

## Model Responses

### 1. Claude Opus 4.8

**Response summary:**

Opus led with an immediate diagnosis: the 12% revenue headline is misleading. It walked through the gross profit arithmetic precisely — indexing revenue to 100, showing gross profit moves from 68 to ~68.3 (essentially flat) despite a 12% top-line gain — before layering in the opex problem. It identified that with flat gross profit and +31% opex, operating income must have fallen sharply, even though no one in the earnings narrative said so.

**Key analytical points raised:**

- The 7-point gross margin drop is structural, not noise — possible causes: AI compute costs hitting COGS, product mix shift, pricing pressure, or one-time write-downs.
- "Investment in AI infrastructure" is doing too much explanatory work. The critical question is **capex vs. opex**: genuine infrastructure spend is typically capitalized and flows through depreciation slowly, not as a single-quarter opex spike.
- Opex composition matters — R&D growth reads as investment; G&A growth reads as bloat; S&M growth alongside only 12% revenue growth signals rising customer-acquisition costs.
- The conspicuous omissions (operating income, net income, FCF, forward guidance with numbers) are themselves a signal.
- "On track" is a redirect, not a metric. It answers a question about the top line while the real deterioration sits below it.

**Tone and framing:**

Balanced. Opus held the bearish read and the constructive counter-read simultaneously — explicitly noting that deliberately sacrificing near-term margins for an AI platform shift *can* be the right long-term decision, but only distinguishable from a margin collapse if management owns the tradeoff with numbers.

**Strengths:**
- Most mathematically precise response
- Best identification of the capex/opex distinction
- Strongest framing of omission as signal
- Appropriate epistemic humility — flagged working from limited data

**Weaknesses:**
- Response was long and dense; required careful reading to extract the hierarchy of flags
- No visual or structural summary

---

### 2. Claude Sonnet 4.6

**Response summary:**

Sonnet produced the same core diagnosis as Opus but added an interactive visual dashboard — metric cards, a waterfall chart showing the P&L deterioration, and a structured analyst flag list. The analytical content was largely equivalent but delivered with cleaner information hierarchy.

**Key analytical points raised:**

- Revenue +12% vs. gross profit ~flat: all incremental revenue consumed by margin compression.
- Opex growing 2.6× faster than revenue makes operating income a near-certain casualty.
- Capex vs. opex distinction on infrastructure spend.
- Conspicuous omissions in the earnings narrative.
- "On track" requires a reference point — is 12% an acceleration or deceleration?

**Tone and framing:**

Concise and structured. Delivered the same analytical substance as Opus with less verbosity, aided by the visual breakdown making the numbers immediately scannable.

**Strengths:**
- Best information hierarchy — findings surfaced clearly without burying the reader
- Visual waterfall chart made the double-squeeze intuitive
- Five analyst flags rendered as clean, scannable cards
- Equivalent analytical depth to Opus, higher readability

**Weaknesses:**
- Slightly less exploration of the constructive counter-case (where the margin sacrifice is intentional and rational)
- Visual elements are specific to the claude.ai interface; won't render in all environments

---

### 3. Claude Haiku 4.5

**Response summary:**

Haiku provided a correct and serviceable response covering the main flags: gross margin compression, opex outpacing revenue, and the ambiguity of management language. It identified the core problem accurately. However, it stayed at a shallower analytical depth — naming the issues without working through the arithmetic or exploring second-order implications.

**Key analytical points raised:**

- Gross margin drop signals rising costs or pricing pressure.
- Opex growth of 31% vs. 12% revenue is unsustainable.
- AI infrastructure spend needs clarity on nature and timeline.
- Management language is vague and should be pressed.

**Tone and framing:**

Direct and accessible. Appropriate for a quick briefing but not for a formal analytical note.

**Strengths:**
- Fast, clear, easy to read
- Correctly identifies all primary flags
- Good for non-specialist audiences or rapid triage

**Weaknesses:**
- Does not work through the gross profit arithmetic
- Misses the capex/opex distinction (a critical nuance for FCF analysis)
- Does not flag omissions as a signal in their own right
- No counter-read or nuanced framing
- Insufficient depth for a professional analyst context

---

## Comparative Analysis

| Criterion | Opus 4.8 | Sonnet 4.6 | Haiku 4.5 |
|---|---|---|---|
| **Gross profit arithmetic** | ✅ Precise | ✅ Correct | ❌ Not calculated |
| **Capex vs. opex distinction** | ✅ Detailed | ✅ Flagged | ❌ Missed |
| **Omissions as signal** | ✅ Strong | ✅ Flagged | ❌ Not raised |
| **Counter-read / nuance** | ✅ Explicit | ⚠️ Light | ❌ Absent |
| **Information hierarchy** | ⚠️ Dense | ✅ Clear | ✅ Clear |
| **Visual summary** | ❌ None | ✅ Dashboard | ❌ None |
| **Readability** | ⚠️ Verbose | ✅ Balanced | ✅ Concise |
| **Depth for professional use** | ✅ High | ✅ High | ⚠️ Moderate |
| **Speed / token efficiency** | ⚠️ Slow | ✅ Balanced | ✅ Fast |

---

## Verdict

### 🏆 Best overall response: **Claude Sonnet 4.6**

Sonnet delivered analytical depth equivalent to Opus with meaningfully better information design. The waterfall chart and structured flag cards reduced cognitive load without sacrificing rigour. For a professional analyst producing a client-ready briefing note or internal memo, Sonnet's output required the least post-processing.

**When to use each model for this task type:**

| Use case | Recommended model |
|---|---|
| Deep financial modelling, scenario analysis, regulatory nuance | **Opus 4.8** |
| Analyst briefings, investment memos, board summaries | **Sonnet 4.6** |
| Quick triage, first-pass screening, non-specialist audiences | **Haiku 4.5** |

---

## Rephrased Prompt

The original prompt was conversational and unstructured. Below is a rephrased version optimised for more consistent, high-quality model output across all tiers:

---

**Rephrased prompt:**

> You are a senior equity research analyst. A technology company has reported the following quarterly results:
>
> - Revenue: +12% year-over-year
> - Gross margin: declined from 68% to 61% (–7 percentage points)
> - Operating expenses: +31% year-over-year
> - CFO commentary: "continued investment in AI infrastructure"
> - CEO commentary: growth is "on track"
>
> **Task:**
> 1. Assess whether this is a healthy quarter. Show your arithmetic where relevant.
> 2. Identify the top five flags an analyst should raise, ranked by materiality.
> 3. For each flag, specify: (a) what you know, (b) what is ambiguous, and (c) what question you would ask management.
> 4. Note any material information that is conspicuously absent from this summary.
> 5. Provide a brief counter-read: under what conditions would this quarter actually be defensible?

---

*This structured version adds role context, requests arithmetic, forces a ranked flag list with the know/ambiguous/ask-management triad, explicitly prompts for omission analysis, and requires a counter-read — producing more actionable output from all three models.*

---

*Generated using Claude · Model comparison methodology: identical prompt, same conversation session, three model variants · For research and evaluation purposes*
