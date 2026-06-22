# Agent Architecture Design: Four Industry Scenarios
> **Author:** RG | **Date:** June 2026 | **Domain:** AI Systems Design — Single Agent vs Multi-Agent

---

## Table of Contents

1. [Architecture Decision Framework](#1-architecture-decision-framework)
2. [Scenario 1 — ShopIQ · E-Commerce / Retail](#2-scenario-1--shopiq--e-commerce--retail)
3. [Scenario 2 — Apollo Diagnostics · Healthcare / Clinical AI](#3-scenario-2--apollo-diagnostics--healthcare--clinical-ai)
4. [Scenario 3 — ContractIQ · Legal / LegalTech](#4-scenario-3--contractiq--legal--legaltech)
5. [Scenario 4 — CloudOps Sentinel · DevOps / Platform Engineering](#5-scenario-4--cloudops-sentinel--devops--platform-engineering)
6. [Comparative Summary & Core Heuristics](#6-comparative-summary--core-heuristics)

---

## 1. Architecture Decision Framework

Every architecture choice below is grounded in the following decision matrix. Read this before evaluating any scenario.

| Decision Signal | Favours → Single Agent | Favours → Multi-Agent |
|---|---|---|
| **Context sharing** | One shared context object; no domain handoff | Each step owns its own domain/tool context |
| **Latency budget** | Tight (< 3s) — orchestration overhead is unaffordable | Looser, or parallel throughput offsets overhead |
| **Domain specialisation** | One domain, one tool surface | Multiple distinct knowledge domains, different tool access |
| **Failure isolation** | Uniform failure mode — skip & log | Each step can fail independently, needs separate retry |
| **Parallelism pattern** | Sequential, linear — no fan-out benefit | Embarrassingly parallel workloads (map-reduce, DAG) |
| **Human-in-the-loop** | Not required | Approval gates between steps required by policy or risk |
| **Audit / compliance** | Single trace sufficient | Per-step audit trail required (HIPAA, legal, SOC2) |
| **Scale unit** | Scale the whole agent horizontally | Scale individual stages independently |

> **The trap:** choosing Multi-Agent because a workflow has multiple steps. Multiplicity of steps ≠ multiplicity of agents. What matters is whether those steps require domain isolation, parallel throughput, durable checkpoints, or independent failure semantics.

---

## 2. Scenario 1 — ShopIQ · E-Commerce / Retail

### 2.1 Full Problem Statement

> ShopIQ runs a **nightly batch job** to send personalised recommendation emails to **4 million users**.
>
> For each user:
> - Pull their **6-month purchase and browse history**
> - Run a **collaborative-filtering model** to get top-10 candidates
> - Apply **business rules** (exclude out-of-stock, exclude recently-purchased)
> - Write a **short personalised intro paragraph**
> - Assemble the **email HTML**
>
> The model call, rules, copywriting, and assembly **all use the same user context object** and must complete in **under 3 seconds per user**.

### 2.2 Key Constraints

| Constraint | Value | Architectural Implication |
|---|---|---|
| Batch volume | 4 million users/night | Needs horizontal scale — but at user level, not step level |
| Latency SLA | < 3 seconds per user | Orchestration overhead is unaffordable |
| Shared state | Single user context object | No handoff serialisation needed or desired |
| Steps | 5 sequential operations | All on the same domain and data object |
| Parallelism unit | Per user (not per step) | Worker-pool pattern, not pipeline fan-out |

---

### 2.3 ✅ Architecture Choice: Single Agent

### 2.4 Justification

**1. The shared user context object makes inter-agent handoffs actively harmful.**
All five steps — history retrieval, collaborative filtering, rule application, copywriting, and HTML assembly — operate on the *same user context object*. In a multi-agent design, this object must be serialised at each agent boundary, transmitted over a message bus, and deserialised by the next agent. At 4M users × 4 handoffs per user = 16M serialisation operations per night. The latency and CPU tax of this is architecturally unjustifiable when a single agent simply passes the object by reference through its internal execution.

**2. The 3-second SLA makes orchestration overhead fatal.**
A multi-agent orchestrator introduces a minimum of 50–200ms per agent invocation: network hop, context injection, queue scheduling, cold-start probability. With 4–5 sub-agents, you burn 200–1000ms in orchestration alone — up to 33% of the entire latency budget — before a single token of copywriting is generated. A single agent executing all steps in-process pays zero orchestration tax.

**3. No domain specialisation boundary justifies splitting.**
The five steps are not distinct *knowledge domains* — they are sequential data operations on user state. Collaborative filtering is a model call. Rule application is a deterministic filter function. Copywriting is constrained generation. None require specialised context isolation that separate agents provide. Splitting them would be architectural cosplay, not engineering necessity.

**4. The natural unit of parallelism is the user, not the pipeline stage.**
Scale is achieved by running K workers in parallel, each processing one user end-to-end. This is a classic worker-pool pattern requiring zero inter-agent coordination. Contrast with a multi-agent pipeline where parallelising stage 2 (CF model) independently of stage 3 (rules) adds coordination complexity without meaningful throughput gain — the bottleneck is the LLM call, not the rules engine.

**5. Failure semantics are radically simpler at scale.**
Single agent failure = mark that user as failed, push to dead-letter queue, retry or skip. Multi-agent failure = determine which of 5 stages failed, whether intermediate state is reusable, whether to replay from that stage, and whether partial output is safe to use. At 4M users per night, the operational surface area of multi-agent failure handling is a significant reliability liability.

---

### 2.5 Block Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║               NIGHTLY BATCH SCHEDULER (cron / Airflow)              ║
║                  Triggers job at 00:00 for 4M users                 ║
╚══════════════════════════╦═══════════════════════════════════════════╝
                           ║ enqueues 4M user_ids
                           ▼
╔══════════════════════════════════════════════════════════════════════╗
║              DISTRIBUTED JOB QUEUE (Kafka / SQS / Redis)            ║
║                     4,000,000 messages                               ║
╚══╦═══════════╦═══════════╦═══════════╦═══════════╦══════════════════╝
   ║           ║           ║           ║           ║
   ▼           ▼           ▼           ▼           ▼
┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐
│ W-1  │   │ W-2  │   │ W-3  │   │ W-4  │   │ W-N  │   ← K workers
│      │   │      │   │      │   │      │   │      │      horizontally
│      │   │      │   │      │   │      │   │      │      scaled
└──┬───┘   └──┬───┘   └──┬───┘   └──┬───┘   └──┬───┘
   │                     │                      │
   │     (each worker runs identical pipeline)  │
   ▼                                            ▼
╔══════════════════════════════════════════════════════════════════════╗
║                     SINGLE AGENT  (per-user)                         ║
║                                                                      ║
║  ┌──────────────────────────────────────────────────────────────┐   ║
║  │                   USER CONTEXT OBJECT                         │   ║
║  │  user_id · purchase_history[6mo] · browse_history[6mo]        │   ║
║  │  preferences · segment · locale · opt-out flags               │   ║
║  └──────────────────────────┬───────────────────────────────────┘   ║
║                             │ (passed by reference — no copy)       ║
║               ┌─────────────▼─────────────┐                        ║
║               │   STEP 1: HISTORY          │                        ║
║               │   RETRIEVAL                │                        ║
║               │   Feature Store / Redis    │                        ║
║               │   → enrich context object  │                        ║
║               └─────────────┬─────────────┘                        ║
║                             │                                       ║
║               ┌─────────────▼─────────────┐                        ║
║               │   STEP 2: CF MODEL CALL    │                        ║
║               │   Collaborative Filtering  │                        ║
║               │   → top-10 candidates      │                        ║
║               │   (item embeddings + ANN)  │                        ║
║               └─────────────┬─────────────┘                        ║
║                             │                                       ║
║               ┌─────────────▼─────────────┐                        ║
║               │   STEP 3: BUSINESS RULES   │                        ║
║               │   ENGINE                   │                        ║
║               │   · exclude out-of-stock   │                        ║
║               │   · exclude recently       │                        ║
║               │     purchased (30d window) │                        ║
║               │   · exclude price-capped   │                        ║
║               │   → filtered candidate set │                        ║
║               └─────────────┬─────────────┘                        ║
║                             │                                       ║
║               ┌─────────────▼─────────────┐                        ║
║               │   STEP 4: COPYWRITING      │                        ║
║               │   LLM call (constrained)   │                        ║
║               │   → short personalised     │                        ║
║               │     intro paragraph        │                        ║
║               │   (uses user context +     │                        ║
║               │    filtered candidates)    │                        ║
║               └─────────────┬─────────────┘                        ║
║                             │                                       ║
║               ┌─────────────▼─────────────┐                        ║
║               │   STEP 5: HTML ASSEMBLY    │                        ║
║               │   Jinja2 / Handlebars      │                        ║
║               │   template render          │                        ║
║               │   → final email HTML       │                        ║
║               └─────────────┬─────────────┘                        ║
║                             │                                       ║
╚═════════════════════════════╬════════════════════════════════════════╝
                              │
                              ▼
               ╔══════════════════════════╗
               ║  EMAIL DELIVERY QUEUE    ║
               ║  (AWS SES / SendGrid)    ║
               ║  → send to user inbox    ║
               ╚══════════════════════════╝
                              │
                              ▼
               ╔══════════════════════════╗
               ║  DEAD-LETTER QUEUE       ║
               ║  failed users → retry    ║
               ║  or skip + alert         ║
               ╚══════════════════════════╝
```

**Throughput sizing:** With K=100 workers, avg 2s per user → 100 users/s throughput → 4M users in ~11 hours. Tune K to fit nightly window. No inter-agent communication. Each worker is stateless and disposable.

---

## 3. Scenario 2 — Apollo Diagnostics · Healthcare / Clinical AI

### 3.1 Full Problem Statement

> Apollo wants to **automate the end-to-end workflow** when a chest CT scan arrives:
>
> 1. A **radiologist-grade model** reads the scan and drafts a findings report
> 2. A **clinical-decision-support system** cross-checks findings against the patient's medication history for contraindications
> 3. A **scheduling agent** books the recommended follow-up (e.g. biopsy, PET scan) in the hospital's EMR
> 4. A **communication agent** drafts the GP letter and patient-facing summary
>
> Each step has a **distinct tool**, **knowledge domain**, and **failure mode**.

### 3.2 Key Constraints

| Constraint | Value | Architectural Implication |
|---|---|---|
| Steps | 4 sequential, each distinct | Each step is a different knowledge domain |
| Distinct domains | Radiology · Clinical pharmacology · EMR scheduling · Medical writing | Cannot share a single agent's tool surface |
| Gate pattern | Sequential with hard gates | Step N cannot begin until Step N-1 is validated |
| Failure modes | 4 independent failure modes | Each step must fail and recover independently |
| Tool access | DICOM · Drug DB · EMR API · Messaging | Least-privilege: no single agent should hold all access |
| Regulatory | HIPAA | Per-step audit trail required; each domain has its own accountability boundary |

---

### 3.3 ✅ Architecture Choice: Multi-Agent (Sequential Pipeline with Gates)

### 3.4 Justification

**1. Four genuinely distinct knowledge domains require specialised agents.**
Radiology image interpretation, clinical pharmacology (contraindication detection), EMR scheduling logic, and medical communication drafting are not variants of the same task. Each requires different model fine-tuning, different grounding knowledge, and different output schemas. A single agent attempting all four would produce a dangerous knowledge soup — a radiology model making scheduling decisions it has no business making.

**2. Sequential gate pattern is a patient-safety design requirement, not just a data dependency.**
Step 2 (contraindication check) *must not begin* until Step 1 produces a validated, schema-compliant findings report. Step 3 (scheduling) *must not proceed* if Step 2 flags unresolved contraindications. These are clinical safety gates, not just ETL dependencies. A multi-agent orchestrator with explicit gate contracts enforces this structurally — you cannot accidentally skip a gate. A single agent's internal control flow offers no such structural guarantee.

**3. Each step has an independent failure mode requiring isolated recovery.**
The DICOM service can be unavailable (Step 1 fails). The drug interaction DB can be down (Step 2 fails). The EMR API can time out (Step 3 fails). In a multi-agent pipeline with durable state at each handoff checkpoint, you can replay from the failed step without discarding prior work. In a single agent, an EMR API failure at Step 3 would require rerunning the expensive radiology model call from scratch.

**4. Different tool access profiles satisfy least-privilege and reduce blast radius.**
The radiology agent needs DICOM read access. The scheduling agent needs EMR write access. The communication agent needs the patient portal API. Granting all of these to a single agent violates the principle of least privilege, creates a catastrophic blast radius on compromise, and produces an HIPAA audit nightmare where a single agent's API key touches every system.

**5. HIPAA compliance demands per-step audit trails.**
In clinical AI, each decision step must be independently logged, timestamped, and attributable to a specific model version and agent role. A multi-agent architecture produces this naturally — each agent writes its own audit record. A single agent's internal reasoning trace is a monolith that cannot be cleanly mapped to the regulatory checkpoints auditors require.

---

### 3.5 Block Diagram

```
    ┌──────────────────────────────────────────────────────────────┐
    │               CHEST CT SCAN ARRIVAL EVENT                    │
    │           (HL7 FHIR trigger / RIS notification)              │
    └─────────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
╔══════════════════════════════════════════════════════════════════════╗
║               APOLLO ORCHESTRATOR                                    ║
║           (Clinical Workflow State Machine)                          ║
║                                                                      ║
║  Responsibilities:                                                   ║
║  · Manage sequential state transitions                               ║
║  · Enforce gates (validate outputs before advancing)                ║
║  · Route gate failures to HUMAN_REVIEW queue                        ║
║  · Write master audit log entry at each gate                        ║
║  · Maintain durable checkpoint per step for replay                  ║
╚══════════════════════════════════════════════════════════════════════╝
                                  │
                    ┌─────────────▼─────────────┐
                    │       AGENT 1              │
                    │   RADIOLOGY READER         │
                    │                            │
                    │  Knowledge domain:         │
                    │  Thoracic radiology        │
                    │                            │
                    │  Tools:                    │
                    │  · DICOM viewer / parser   │
                    │  · Radiology foundation    │
                    │    model (fine-tuned)      │
                    │  · Prior scan archive      │
                    │  · RSNA terminology DB     │
                    │                            │
                    │  Outputs:                  │
                    │  · Structured findings     │
                    │    report (FHIR DiagRpt)   │
                    │  · Confidence score        │
                    │  · Highlighted ROIs        │
                    └─────────────┬─────────────┘
                                  │
                    ══════════════╪══════════════
                    ✅  GATE 1    │
                    · findings schema valid      │
                    · confidence ≥ threshold     │
                    · no critical flag pending   │
                    ✗ FAIL → HUMAN_REVIEW queue  │
                    ══════════════╪══════════════
                                  │
                    ┌─────────────▼─────────────┐
                    │       AGENT 2              │
                    │   CLINICAL DECISION        │
                    │   SUPPORT (CDS)            │
                    │                            │
                    │  Knowledge domain:         │
                    │  Clinical pharmacology     │
                    │  & contraindication logic  │
                    │                            │
                    │  Tools:                    │
                    │  · Patient medication       │
                    │    history (EHR read-only) │
                    │  · Drug interaction DB     │
                    │    (e.g. Lexicomp / Medi-  │
                    │    span)                   │
                    │  · Contraindication rule   │
                    │    engine                  │
                    │  · Allergy registry        │
                    │                            │
                    │  Outputs:                  │
                    │  · CLEARED or FLAGGED      │
                    │    status per finding      │
                    │  · Recommended care        │
                    │    pathway                 │
                    │  · Contraindication report │
                    └─────────────┬─────────────┘
                                  │
                    ══════════════╪══════════════
                    ✅  GATE 2    │
                    · no unresolved contraind.   │
                    · care pathway confirmed     │
                    ✗ FAIL → radiologist review  │
                      + clinical pharmacist flag │
                    ══════════════╪══════════════
                                  │
                    ┌─────────────▼─────────────┐
                    │       AGENT 3              │
                    │   SCHEDULING AGENT         │
                    │                            │
                    │  Knowledge domain:         │
                    │  Hospital scheduling &     │
                    │  EMR workflow logic        │
                    │                            │
                    │  Tools:                    │
                    │  · EMR API (read + write)  │
                    │  · Hospital calendar /     │
                    │    slot availability       │
                    │  · Procedure booking       │
                    │    system                  │
                    │  · Insurance pre-auth      │
                    │    checker                 │
                    │                            │
                    │  Outputs:                  │
                    │  · Confirmed appointment   │
                    │    (date, time, location)  │
                    │  · EMR encounter entry     │
                    │  · Pre-auth reference no.  │
                    └─────────────┬─────────────┘
                                  │
                    ══════════════╪══════════════
                    ✅  GATE 3    │
                    · appointment confirmed      │
                    · EMR entry written          │
                    · pre-auth obtained          │
                    ✗ FAIL → scheduling team     │
                      manual intervention queue  │
                    ══════════════╪══════════════
                                  │
                    ┌─────────────▼─────────────┐
                    │       AGENT 4              │
                    │   COMMUNICATION AGENT      │
                    │                            │
                    │  Knowledge domain:         │
                    │  Medical writing (two      │
                    │  registers: clinical &     │
                    │  plain language)           │
                    │                            │
                    │  Tools:                    │
                    │  · Medical writing LLM     │
                    │  · GP secure messaging     │
                    │    portal (NHS / Apollo)   │
                    │  · Patient portal API      │
                    │  · Translation service     │
                    │    (if locale ≠ English)   │
                    │                            │
                    │  Outputs:                  │
                    │  · GP referral letter      │
                    │    (clinical register)     │
                    │  · Patient-facing summary  │
                    │    (plain English)         │
                    │  · Appointment reminder    │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────────┐
                    │   AUDIT LOG (immutable)       │
                    │   · Agent ID + version        │
                    │   · Timestamp per gate        │
                    │   · Input/output hashes       │
                    │   · Human overrides recorded  │
                    │   Written to: clinical record │
                    └──────────────────────────────┘
```

**Safety invariant:** The orchestrator never silently advances past a failed gate. All gate failures are durable events that create a work item in the `HUMAN_REVIEW` queue with full context.

---

## 4. Scenario 3 — ContractIQ · Legal / LegalTech

### 4.1 Full Problem Statement

> A PE firm uploads **800 supplier and employment contracts** ahead of an acquisition. ContractIQ must:
>
> - **Extract** key obligations and risk clauses from each document *(parallelisable across contracts)*
> - **Cross-reference** extracted clauses against a jurisdiction-specific regulatory checklist
> - **Identify inter-contract dependencies** (e.g. change-of-control clauses that cascade)
> - **Produce an executive risk summary** with a red/amber/green heat map
>
> Total turnaround required: **under 4 hours**.
> Documents are **independent at extraction stage** but **interdependent at the synthesis stage**.

### 4.2 Key Constraints

| Constraint | Value | Architectural Implication |
|---|---|---|
| Volume | 800 contracts | Sequential extraction takes ~6.7 hrs → SLA breach |
| SLA | < 4 hours end-to-end | Only achievable with parallel extraction workers |
| Extraction independence | Documents are isolated at extraction | Embarrassingly parallel map phase |
| Synthesis interdependence | Cross-doc dependencies exist | Requires a dedicated reduce/synthesis phase |
| Jurisdiction variance | Multiple legal jurisdictions | Compliance check agent must load per-jurisdiction rules |
| Output | Executive RAG heat map | Aggregated output requiring all extraction results |

---

### 4.3 ✅ Architecture Choice: Multi-Agent (Map-Reduce Pattern)

### 4.4 Justification

**1. The 4-hour SLA is mathematically impossible without parallelism.**
800 contracts × 30 seconds per extraction = 400 minutes = 6.7 hours sequential. That blows the SLA by 67%. With 50 concurrent extraction agents: 800 × 30s / 50 = 8 minutes for extraction. Synthesis, compliance checking, and report generation add ~75 minutes. Total: ~83 minutes — well within the 4-hour window. This is not a preference for parallelism; it is a mathematical requirement.

**2. The workload has a textbook map-reduce structure that multi-agent is designed for.**
Extraction is embarrassingly parallel — each document is independent of all others at this stage. Synthesis requires the full corpus of extraction outputs. This is precisely the pattern that multi-agent map-reduce handles: an orchestrator fans out to N extraction agents, collects structured outputs, and routes to a synthesis agent. Trying to do this in a single agent is either sequential (too slow) or requires the agent to manage its own concurrency — which is just reinventing the orchestrator inside the agent.

**3. Cross-document synthesis is a structurally distinct second-phase task.**
The synthesis agent's work — building a cross-contract dependency graph, identifying change-of-control cascades, producing a RAG heat map — requires the *complete set* of extraction outputs as its input. It has entirely different tools, different context, and different reasoning requirements from extraction. These are not two stages of the same task; they are two different jobs that happen to be connected by a data handoff.

**4. Jurisdiction-specific compliance checking is an isolated concern that should not pollute extraction.**
Checking extracted clauses against a UK/US/EU regulatory checklist requires loading different rule sets per jurisdiction and running deterministic validation logic. This is not a natural extension of clause extraction — it is a separate verification pass that should run after extraction and before synthesis, with its own failure mode (checklist DB unavailable) that must not invalidate extraction results.

**5. Extraction failures should not block the pipeline.**
If 12 of 800 documents fail extraction (corrupt PDFs, encoding issues, password-protected files), the system should: flag them, quarantine to a retry queue, complete the remaining 788, and proceed to synthesis with a clearly documented partial dataset. A single-agent sequential approach would require explicit branching logic to handle partial completion. The orchestrator's fan-out failure semantics handle this naturally.

---

### 4.4 Block Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║            DOCUMENT INGESTION (800 contracts uploaded)               ║
║            · PDF / DOCX / TIFF normalisation                         ║
║            · OCR for scanned documents                               ║
║            · Metadata extraction (jurisdiction, contract type)       ║
╚══════════════════════════════════════════════════════════════════════╝
                                  │
                                  ▼
╔══════════════════════════════════════════════════════════════════════╗
║                 CONTRACTIQ ORCHESTRATOR                              ║
║             (Map-Reduce Coordinator)                                 ║
║                                                                      ║
║  · Partitions 800 docs into extraction batches                       ║
║  · Fans out to N extraction workers                                  ║
║  · Tracks completion, handles failures, manages retry queue          ║
║  · Collects all structured outputs before advancing                  ║
╚══════════════════════════════════════════════════════════════════════╝
       │
       │  ══════════════ MAP PHASE ══════════════
       │
       ├──────────────────┬──────────────────┬──────────────── · · · ─┐
       ▼                  ▼                  ▼                         ▼
┌────────────┐    ┌────────────┐    ┌────────────┐           ┌────────────┐
│ EXTRACTION │    │ EXTRACTION │    │ EXTRACTION │    · · ·  │ EXTRACTION │
│  AGENT 1   │    │  AGENT 2   │    │  AGENT 3   │           │  AGENT N   │
│            │    │            │    │            │           │            │
│ docs 1–16  │    │ docs 17–32 │    │ docs 33–48 │           │ docs ...   │
│            │    │            │    │            │           │            │
│ Tools:     │    │ Tools:     │    │ Tools:     │           │ Tools:     │
│ · PDF/DOCX │    │ · PDF/DOCX │    │ · PDF/DOCX │           │ · PDF/DOCX │
│   parser   │    │   parser   │    │   parser   │           │   parser   │
│ · NLP      │    │ · NLP      │    │ · NLP      │           │ · NLP      │
│   clause   │    │   clause   │    │   clause   │           │   clause   │
│   extractor│    │   extractor│    │   extractor│           │   extractor│
│ · Legal    │    │ · Legal    │    │ · Legal    │           │ · Legal    │
│   NER      │    │   NER      │    │   NER      │           │   NER      │
│            │    │            │    │            │           │            │
│ Outputs:   │    │ Outputs:   │    │ Outputs:   │           │ Outputs:   │
│ Structured │    │ Structured │    │ Structured │           │ Structured │
│ clause JSON│    │ clause JSON│    │ clause JSON│           │ clause JSON│
│ per doc    │    │ per doc    │    │ per doc    │           │ per doc    │
└─────┬──────┘    └─────┬──────┘    └─────┬──────┘           └─────┬──────┘
      │                 │                 │                         │
      └─────────────────┴─────────────────┴─────────────────────────┘
                                  │
                        800 structured clause JSONs
                        (+ failure flags for unprocessable docs)
                                  │
       ══════════════ INTERMEDIATE PHASE ══════════════
                                  │
                                  ▼
╔══════════════════════════════════════════════════════════════════════╗
║               COMPLIANCE CHECK AGENT                                 ║
║                                                                      ║
║  Input: all 800 clause JSONs + jurisdiction metadata                 ║
║                                                                      ║
║  Tools:                                                              ║
║  · Jurisdiction rule engine (UK / US / EU / APAC rule sets)          ║
║  · Regulatory checklist DB                                           ║
║  · Risk scoring model (per clause category)                          ║
║                                                                      ║
║  Output:                                                             ║
║  · Per-contract compliance flags                                     ║
║  · Per-clause risk scores                                            ║
║  · Jurisdiction-specific breach alerts                               ║
╚══════════════════════════════════════════════════════════════════════╝
                                  │
       ══════════════ REDUCE PHASE ══════════════
                                  │
                                  ▼
╔══════════════════════════════════════════════════════════════════════╗
║               SYNTHESIS AGENT                                        ║
║                                                                      ║
║  Input: 800 clause JSONs + compliance flags + risk scores            ║
║                                                                      ║
║  Tools:                                                              ║
║  · Cross-document dependency graph builder                           ║
║  · Change-of-control cascade analyser                                ║
║    (identifies clauses that trigger across contract boundaries)      ║
║  · RAG retrieval over full clause corpus                             ║
║    (semantic search for similar risk patterns)                       ║
║  · Risk cluster aggregator                                           ║
║                                                                      ║
║  Tasks:                                                              ║
║  1. Build contract dependency graph                                  ║
║  2. Flag CoC clauses that cascade to other contracts                 ║
║  3. Cluster risks: IP · Liability · Termination · CoC · IP · Data    ║
║  4. Assign RAG status per cluster and per contract                   ║
║                                                                      ║
║  Output: risk matrix + dependency graph                              ║
╚══════════════════════════════════════════════════════════════════════╝
                                  │
                                  ▼
╔══════════════════════════════════════════════════════════════════════╗
║               REPORT GENERATION AGENT                                ║
║                                                                      ║
║  Output: Executive Due Diligence Pack                                ║
║  · 🔴🟡🟢 Red/Amber/Green heat map (contract × risk category)        ║
║  · Top 20 critical risk clauses ranked by severity                   ║
║  · Inter-contract dependency visualisation                           ║
║  · Change-of-control cascade map                                     ║
║  · Deal structuring recommendations                                  ║
║  · Quarantined documents list (extraction failures)                  ║
╚══════════════════════════════════════════════════════════════════════╝

─────────────────────────────────────────────────────────────────────
  SLA BREAKDOWN  (50 extraction workers, 30s avg per doc)
─────────────────────────────────────────────────────────────────────
  Ingestion & normalisation    ~5  min
  MAP — extraction (×50)       ~8  min   [800 docs / 50 workers × 30s]
  Compliance check             ~20 min
  REDUCE — synthesis           ~35 min
  Report generation            ~15 min
  ────────────────────────────────────
  TOTAL                        ~83 min   ✅  well within 4-hour SLA
─────────────────────────────────────────────────────────────────────
```

---

## 5. Scenario 4 — CloudOps Sentinel · DevOps / Platform Engineering

### 5.1 Full Problem Statement

> An alert fires: **p99 API latency has spiked to 4.2s** on the payments service.
> CloudOps Sentinel must:
>
> **(a)** Query **metrics (Datadog)** to identify which pods are degraded
> **(b)** Check **recent deployment logs (GitHub Actions)** for a root cause
> **(c)** Query the **DB slow-query log (AWS RDS)**
> **(d)** If confident, **execute a rollback or pod restart via kubectl**
> **(e)** Post a **structured RCA to the #incidents Slack channel**
>
> Steps **(a), (b), (c)** can run **concurrently**.
> Step **(d)** requires **human approval if confidence < 80%**.
> Step **(e)** always runs last.

### 5.2 Key Constraints

| Constraint | Value | Architectural Implication |
|---|---|---|
| Concurrent investigations | (a), (b), (c) are independent | Must fan out in parallel — sequential would triple MTTR |
| Tool surfaces | Datadog · GitHub Actions · AWS RDS · kubectl · Slack | 5 completely different APIs/auth surfaces |
| Human-in-the-loop | Required when confidence < 80% | Needs durable pause-and-resume state — not just an `if` statement |
| Ordering constraint | (e) must always run last | DAG join: all paths converge before RCA post |
| Blast radius | Payments service rollback / pod restart | High-consequence action; approval gate is a risk control, not optional logic |
| Audit | SOC2 / change management | Every action must be traceable with actor (human or agent) |

---

### 5.3 ✅ Architecture Choice: Multi-Agent (DAG with Concurrent Fan-out + HITL Gate)

### 5.4 Justification

**1. Steps (a), (b), (c) are genuinely concurrent — sequential execution would triple time-to-diagnosis.**
Querying Datadog metrics, pulling GitHub Actions deployment logs, and fetching AWS RDS slow-query logs are entirely independent investigations. None depends on the output of another. Running them sequentially adds 2× unnecessary wait time at the most critical moment of an incident. A multi-agent architecture dispatches all three sub-agents simultaneously; wall-clock time for investigation is bounded by the slowest single query, not their sum.

**2. Each sub-investigation uses a completely different tool surface with different auth models.**
Datadog uses its own API key and query DSL. GitHub Actions has a REST API with OAuth. AWS RDS slow-query logs require IAM-authenticated CloudWatch Logs queries. These are not just different endpoints — they are different authentication domains, different rate limits, and different response schemas. A single agent context-switching between them sequentially is architecturally identical to a disguised sequential pipeline, just without the structural benefits of agent isolation.

**3. The confidence-gated human approval is a durable state requirement, not a conditional branch.**
"If confidence < 80%, require human approval before executing rollback" cannot be correctly implemented as a simple `if` statement inside a single agent. The agent would either block (holding a live API connection and burning tokens while waiting for a human), time out, or lose state. A multi-agent orchestrator models this as a **durable pause state**: the orchestrator serialises its state, emits a structured approval request (PagerDuty + Slack), and resumes execution only when a human responds via API webhook. This pause can last minutes or hours without burning resources.

**4. Step (d) — the remediation action — has a catastrophic blast radius requiring structural isolation.**
Executing `kubectl rollout undo` on the payments service is a high-impact, irreversible (in the short term) action on production infrastructure. Isolating this to a dedicated remediation agent with its own kubectl credentials, its own audit log, and an explicit activation gate means that no other part of the system can accidentally trigger production changes. This is defence-in-depth at the architectural level.

**5. Step (e) must structurally join all paths — this is a DAG, not a linear pipeline.**
The RCA Slack post must always execute last, regardless of whether the remediation path took the auto-execution branch or the human-approval branch. This is a DAG join node: two paths (high confidence → auto-remediate; low confidence → human approval → remediate) must converge before (e) executes. Multi-agent DAG orchestration models this join explicitly and verifiably. A single agent's control flow cannot express this with the same structural clarity.

---

### 5.5 Block Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                       ALERT TRIGGER                                  ║
║             p99 latency = 4.2s · payments service                    ║
║          (PagerDuty webhook → CloudOps Sentinel API)                 ║
╚══════════════════════════════════════════════════════════════════════╝
                                  │
                                  ▼
╔══════════════════════════════════════════════════════════════════════╗
║              CLOUDOPS SENTINEL ORCHESTRATOR                          ║
║          (Incident State Machine Controller)                         ║
║                                                                      ║
║  Responsibilities:                                                   ║
║  · Fan out sub-agents (a), (b), (c) concurrently                     ║
║  · Collect and join results                                          ║
║  · Compute confidence score                                          ║
║  · Enforce HITL gate (confidence < 0.80)                            ║
║  · Route to remediation agent                                        ║
║  · Guarantee (e) always runs last                                    ║
║  · Write full audit trail                                            ║
╚══════════════════════════════════════════════════════════════════════╝
       │
       │  ══════ CONCURRENT DISPATCH ══════
       │
       ├──────────────────────┬──────────────────────┐
       ▼                      ▼                      ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ SUB-AGENT A │      │ SUB-AGENT B │      │ SUB-AGENT C │
│  METRICS    │      │ DEPLOYMENT  │      │  DB SLOW-   │
│ INVESTIGATOR│      │ LOG CHECKER │      │   QUERY     │
│             │      │             │      │  ANALYSER   │
│ Tool:       │      │ Tool:       │      │ Tool:       │
│ Datadog API │      │ GitHub      │      │ AWS RDS     │
│ (metrics    │      │ Actions API │      │ CloudWatch  │
│  query DSL) │      │ (REST/OAuth)│      │ Logs (IAM)  │
│             │      │             │      │             │
│ Outputs:    │      │ Outputs:    │      │ Outputs:    │
│ · Degraded  │      │ · Last      │      │ · Top slow  │
│   pod list  │      │   deploy    │      │   queries   │
│ · Latency   │      │   timestamp │      │ · Lock      │
│   heatmap   │      │   & SHA     │      │   waits     │
│   (per pod) │      │ · Services  │      │ · Full      │
│ · Error     │      │   changed   │      │   table     │
│   rates     │      │ · Test      │      │   scans     │
│ · CPU/mem   │      │   results   │      │ · Index     │
│   spikes    │      │   on deploy │      │   misses    │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                            │
                  all 3 results collected
                  (partial ok: flag missing sources)
                            │
                            ▼
╔══════════════════════════════════════════════════════════════════════╗
║                    SYNTHESIS AGENT                                   ║
║                                                                      ║
║  Input: outputs from sub-agents (a), (b), (c)                        ║
║                                                                      ║
║  Tasks:                                                              ║
║  · Correlate metrics spike → deployment delta → DB query pattern     ║
║  · Build root cause hypothesis                                       ║
║  · Select proposed remediation action                                ║
║    (rollback deploy X  |  restart pod Y  |  scale up Z)             ║
║  · Compute confidence score [0.00 – 1.00]                           ║
║    based on: evidence completeness, pattern match, novelty score     ║
║                                                                      ║
║  Output: {hypothesis, proposed_action, confidence, evidence_refs}    ║
╚══════════════════════════════════════════════════════════════════════╝
                            │
                ┌───────────▼───────────┐
                │    CONFIDENCE GATE    │
                │   confidence ≥ 0.80?  │
                └──────┬────────┬───────┘
                  YES  │        │  NO
                       │        │
                       │        ▼
                       │  ╔══════════════════════════════════╗
                       │  ║   HUMAN APPROVAL REQUEST         ║
                       │  ║   (durable pause state)          ║
                       │  ║                                  ║
                       │  ║  Channels:                       ║
                       │  ║  · PagerDuty P1 alert            ║
                       │  ║  · Slack #incidents thread with  ║
                       │  ║    approve / reject buttons      ║
                       │  ║                                  ║
                       │  ║  Payload shown to approver:      ║
                       │  ║  · Root cause hypothesis         ║
                       │  ║  · Evidence summary              ║
                       │  ║  · Proposed action + risk level  ║
                       │  ║  · Confidence: XX%               ║
                       │  ║  · Blast radius estimate         ║
                       │  ║                                  ║
                       │  ║  Awaits: APPROVE / REJECT        ║
                       │  ║  · REJECT → escalate to SRE      ║
                       │  ║  · Timeout (15m) → auto-escalate ║
                       │  ╚═════════════════┬════════════════╝
                       │              APPROVE│
                       │                    │
                       └────────────────────┘
                                    │
                                    ▼
                    ╔═══════════════════════════════╗
                    ║     REMEDIATION AGENT         ║
                    ║                               ║
                    ║  Tool: kubectl (kubeconfig    ║
                    ║  scoped to payments ns only)  ║
                    ║                               ║
                    ║  Actions (mutually exclusive):║
                    ║  · kubectl rollout undo       ║
                    ║    deployment/payments-api    ║
                    ║  · kubectl rollout restart    ║
                    ║    deployment/payments-api    ║
                    ║  · kubectl scale              ║
                    ║    --replicas=N               ║
                    ║                               ║
                    ║  Post-action:                 ║
                    ║  · Poll p99 latency for 60s   ║
                    ║  · Record: action taken,      ║
                    ║    result, new latency        ║
                    ╚═══════════════════╦═══════════╝
                                        ║
                    ════════════════════╪═══════════
                         DAG JOIN       ║
                    (both paths merge   ║
                     here before (e))   ║
                    ════════════════════╪═══════════
                                        ║
                                        ▼
                    ╔═══════════════════════════════╗
                    ║   RCA COMMUNICATION AGENT     ║
                    ║   (ALWAYS runs last)           ║
                    ║                               ║
                    ║  Tool: Slack API              ║
                    ║  Channel: #incidents          ║
                    ║                               ║
                    ║  Posts structured RCA:        ║
                    ║  · Incident timeline          ║
                    ║  · Root cause (+ evidence)    ║
                    ║  · Action taken (or escalated)║
                    ║  · Current p99 latency        ║
                    ║  · Follow-up ticket owners    ║
                    ║  · Confidence score at time   ║
                    ║    of decision                ║
                    ║  · Human approver (if HITL)   ║
                    ╚═══════════════════════════════╝

─────────────────────────────────────────────────────────────────────
  TIMING (typical incident, high confidence path)
─────────────────────────────────────────────────────────────────────
  Alert receipt → orchestrator boot       < 2s
  Concurrent sub-agent investigation      15–30s   (wall-clock)
  Synthesis + confidence scoring          5–10s
  Remediation execution                   10–20s
  RCA post                                3–5s
  ──────────────────────────────────────────────
  TOTAL (auto-remediation path)           < 70s    from alert to RCA
─────────────────────────────────────────────────────────────────────
```

---

## 6. Comparative Summary & Core Heuristics

### 6.1 Decision Matrix

| Dimension | ShopIQ | Apollo Diagnostics | ContractIQ | CloudOps Sentinel |
|---|---|---|---|---|
| **Architecture** | ✅ Single Agent | 🔀 Multi-Agent | 🔀 Multi-Agent | 🔀 Multi-Agent |
| **Pattern** | Worker pool | Sequential pipeline with gates | Map-Reduce | DAG with concurrent fan-out |
| **Primary driver** | 3s SLA + shared context object | 4 distinct clinical domains + safety gates | 4hr SLA requires parallel extraction | Concurrent investigations + HITL gate |
| **Parallelism** | Per user (not per step) | None — sequential by design | Per document (map phase) | Per investigation tool (sub-agents a/b/c) |
| **Human-in-the-loop** | ❌ No | ⚠️ Gate failures only → review queue | ❌ No | ✅ Confidence < 80% on remediation |
| **Failure handling** | Dead-letter queue per user | Gate fail → human review; durable checkpoint per step | Partial dataset → synthesis with flags | Partial investigation → HITL escalation |
| **Tool surfaces** | 1 (feature store + LLM) | 4 distinct (DICOM, EHR, EMR, messaging) | 3 distinct (PDF parser, compliance DB, synthesis) | 5 distinct (Datadog, GH, RDS, kubectl, Slack) |
| **Audit / compliance** | GDPR (minimal) | HIPAA — per-step audit trail mandatory | Legal privilege, attorney work product | SOC2 / change management log |
| **Scale unit** | User (K workers) | Workflow instance | Document (extraction workers) | Incident (sub-agents per investigation) |
| **Durable state needed** | ❌ No | ✅ Yes — checkpoint per gate | ✅ Yes — between map and reduce | ✅ Yes — HITL pause state |

---

### 6.2 The Core Heuristics

> **Heuristic 1 — The Shared Context Test:**
> If all steps operate on the same in-memory object and there is no reason to cross a domain boundary, use a Single Agent. Handoffs cost. Don't pay them without reason.

> **Heuristic 2 — The SLA Arithmetic Test:**
> Calculate sequential worst-case time. If it breaches SLA, you need parallelism. Parallelism at scale = Multi-Agent fan-out. There is no other architectural option.

> **Heuristic 3 — The Domain Boundary Test:**
> If two steps require genuinely different knowledge, different tools, or different regulatory accountability, they belong in different agents. "Different step" is not the same as "different domain."

> **Heuristic 4 — The Failure Mode Test:**
> If a step failing should not invalidate prior steps' work, use a Multi-Agent pipeline with durable checkpoints. If all steps are equally worthless when any one fails, a Single Agent is fine.

> **Heuristic 5 — The Human Gate Test:**
> If a human must approve an action before the system proceeds, and that wait could be minutes or hours, you need a durable pause state. Only a Multi-Agent orchestrator can model this correctly. A Single Agent will block, time out, or lose state.

---

*Document version: 2.0 · All block diagrams in ASCII for universal rendering compatibility · Author: RG · June 2026*
