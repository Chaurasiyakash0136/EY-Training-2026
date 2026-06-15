# Day 13 – Task 2: RAG Metrics Evaluation and Latency Analysis

## Objective

The objective of this task is to investigate the latency variation observed in the Day 12 Hybrid RAG pipeline and analyze whether retrieval quality metrics influence overall response time.

The evaluation focuses on three key RAG metrics:

1. Context Precision
2. Answer Relevance
3. Faithfulness

along with:

* Token Count
* Retrieval Latency
* Generation Latency
* Total Response Latency

---

# Background

In Day 12, a Hybrid Retrieval-Augmented Generation (RAG) system was implemented using:

* Vector Search
* Hybrid Retrieval
* LLM-based Generation
* Latency Profiling

It was observed that response latency varied across different user queries.

This task investigates the possible causes of that variation using standard RAG evaluation metrics.

---

# RAG Evaluation Framework

The evaluation follows the RAG triad:

```text
              Query
             /     \
            /       \
           /         \
Context ----------- Response
```

### Context Precision

Measures whether the retrieved documents are actually relevant to the user query.

Higher Context Precision indicates better retrieval quality.

---

### Answer Relevance

Measures how well the generated answer addresses the user's question.

Higher Answer Relevance indicates that the response directly answers the query.

---

### Faithfulness

Measures whether the generated answer is supported by the retrieved context.

Higher Faithfulness indicates lower hallucination risk.

---

# Latency Components

Total response latency consists of:

```text
Embedding Time
      +
Retrieval Time
      +
Prompt Construction Time
      +
Generation Time
```

Generation latency is typically the largest contributor to overall response time.

---

# Relationship Between Metrics and Latency

## Context Precision vs Latency

When retrieval quality is low:

* More irrelevant documents are retrieved.
* The model processes additional context.
* Generation becomes less efficient.

This can increase overall latency.

When Context Precision is high:

* Relevant information is retrieved quickly.
* Less reasoning is required.
* Responses are generated more efficiently.

---

## Answer Relevance vs Latency

Queries requiring more detailed explanations often generate:

* Longer answers
* More output tokens
* Increased generation time

This may improve Answer Relevance but also increase latency.

---

## Faithfulness vs Latency

Highly faithful answers require:

* Better retrieval
* More grounding
* Additional context processing

As a result, improved Faithfulness may sometimes increase response latency.

However, the trade-off is improved reliability and reduced hallucinations.

---

# Token Count and Latency

Token count has a direct impact on latency.

Each query introduces:

* Query Tokens
* Retrieved Context Tokens
* Generated Answer Tokens

As token count increases:

* Model computation increases
* Generation time increases
* Overall latency increases

---

# Key Findings

The primary factors influencing latency variation are:

1. Retrieved Context Size
2. Total Token Count
3. Query Complexity
4. Output Length
5. Retrieval Quality
6. Context Precision
7. Answer Relevance
8. Faithfulness

The evaluation indicates that latency variation is not caused by infrastructure limitations but rather by differences in retrieval workload and generation complexity.

---

# Conclusion

The Day 12 Hybrid RAG pipeline demonstrates that response latency varies naturally across different queries.

Queries requiring larger context windows, longer answers, more reasoning steps, or higher-quality retrieval generally produce increased response times.

From a RAG evaluation perspective:

* Context Precision measures retrieval quality.
* Answer Relevance measures response usefulness.
* Faithfulness measures grounding accuracy.

Together, these metrics provide a more complete explanation of latency variation than latency measurements alone.

Therefore, latency should be interpreted alongside retrieval quality and answer quality metrics when evaluating production-grade RAG systems.
