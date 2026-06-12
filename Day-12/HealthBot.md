# HealthBot: Clinical RAG at Enterprise Scale

## Problem Statement

A large hospital network requires an AI-powered assistant for approximately 3,000 clinicians. The system must answer questions using more than 2 million pages of clinical guidelines, drug interaction references, and internal hospital protocols while maintaining:

* Response latency below 3 seconds
* Answer accuracy above 92%
* HIPAA compliance
* Azure-only data residency

---

# Architecture Decisions

## 1. Azure AI Search vs Weaviate on AKS

### Decision

Azure AI Search

### Justification

The healthcare environment requires strict compliance, security, and operational reliability. Azure AI Search provides:

* Built-in HIPAA-compliant capabilities
* Azure-native security and access controls
* Hybrid search (BM25 + Vector Search)
* Semantic ranking
* Reduced operational overhead

While Weaviate offers greater customization, Azure AI Search is the better choice for enterprise healthcare workloads because compliance and maintainability are higher priorities.

---

## 2. Chunk Size Selection

### Decision

256-token chunks

### Justification

Clinical documents contain highly specific information such as:

* Drug dosages
* Treatment procedures
* Contraindications
* Medical guidelines

Smaller chunks improve retrieval precision and reduce irrelevant context. This increases the probability that the retrieved information directly answers the clinician's question.

---

## 3. Large Context Window vs Retrieval-Augmented Generation

### Decision

Use RAG Architecture

### Justification

Although modern LLMs support large context windows, the knowledge base contains more than 2 million pages.

Using retrieval provides:

* Lower inference cost
* Faster response times
* Better scalability
* Easier knowledge updates
* Reduced hallucination risk

The model receives only the most relevant information instead of processing large document collections.

---

## 4. Multi-Index Strategy

### Decision

Separate indexes by medical specialty

### Example Indexes

* Cardiology
* Oncology
* Radiology
* Neurology
* Pediatrics

### Justification

Benefits include:

* Faster retrieval
* Reduced search space
* Better relevance
* Easier maintenance
* Specialty-specific optimization

A query router can identify the medical domain and direct the search to the appropriate index.

---

# Proposed System Architecture

```text
                    Clinician Query
                            |
                            v
                    Query Router
                  (Domain Detection)
                            |
        -----------------------------------------
        |                  |                    |
        v                  v                    v
   Cardiology         Oncology            Radiology
      Index             Index                Index
        \                |                   /
         \               |                  /
          ----------------------------------
                           |
                           v
                Azure AI Search Hybrid
                 (BM25 + Vector Search)
                           |
                           v
                  Top Relevant Chunks
                     (256 Tokens)
                           |
                           v
                    Large Language Model
                 (Claude / GPT / Azure OpenAI)
                           |
                           v
                 Grounded Clinical Answer
                     (< 3 Seconds)
```

---

# Final Recommendation

The recommended architecture uses Azure AI Search with Hybrid Search, 256-token chunking, Retrieval-Augmented Generation (RAG), and domain-specific indexes.

This approach satisfies the key business requirements:

* HIPAA compliance
* Azure-only deployment
* High retrieval accuracy
* Low latency
* Enterprise scalability

The design balances performance, compliance, maintainability, and clinical reliability for large-scale healthcare deployments.
