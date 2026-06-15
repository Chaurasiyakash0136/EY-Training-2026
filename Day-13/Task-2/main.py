#!/usr/bin/env python3
# main.py - Demo RAG Evaluation Script
# Steps to run:
#   pip install pandas numpy matplotlib scikit-learn
#   python main.py

from __future__ import annotations
import re
import time
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- Configuration ----------
TOP_K = 5  # Number of top documents to retrieve; change as needed
EMBEDDING_DIM = 512

OUTPUT_DIR = Path("output")
PLOTS_DIR = OUTPUT_DIR / "plots"
OUTPUT_DIR.mkdir(exist_ok=True)
PLOTS_DIR.mkdir(exist_ok=True)

# ---------- Data Classes ----------
@dataclass
class Article:
    title: str
    content: str

@dataclass
class QueryCase:
    query_id: str
    query: str
    expected_title: str
    reference_answer: str

# ---------- Document Corpus ----------
ARTICLES = [
    Article(
        title="Retrieval-Augmented Generation",
        content=(
            "Retrieval-Augmented Generation (RAG) combines retrieval and language generation. "
            "Relevant documents are retrieved and used as context to ground the answers. "
            "This helps reduce hallucination in model outputs by providing factual support."
        ),
    ),
    Article(
        title="Vector Search",
        content=(
            "Vector search uses embeddings and semantic similarity to find relevant content. "
            "It can match meaning even when exact keywords differ. "
            "This makes vector search useful for semantic information retrieval."
        ),
    ),
    Article(
        title="FAISS",
        content=(
            "FAISS is an efficient library for similarity search over vector embeddings. "
            "It enables local vector indexing and nearest-neighbour search without requiring external APIs. "
            "FAISS is useful for small RAG prototypes and experiments."
        ),
    ),
    Article(
        title="Azure AI Search",
        content=(
            "Azure AI Search is a cloud service that supports keyword, vector, and hybrid search. "
            "It can index documents and retrieve relevant chunks with low latency. "
            "Azure Search can also provide semantic ranking for RAG pipelines."
        ),
    ),
    Article(
        title="Answer Evaluation",
        content=(
            "Answer relevance measures how well a generated response addresses the question. "
            "Faithfulness measures whether the answer content is supported by the retrieved context. "
            "Context precision measures the fraction of retrieved chunks that are relevant. "
            "These metrics help evaluate the quality of RAG answers."
        ),
    ),
    Article(
        title="Latency in RAG",
        content=(
            "RAG systems involve embedding the query, retrieving context, and generating answers. "
            "Embedding and retrieval times are often stable and fast. "
            "Generation latency can vary widely based on output length and complexity. "
            "Long answers or complex reasoning increase generation time."
        ),
    ),
    # Additional articles for variability
    Article(
        title="Neural Networks",
        content=(
            "Neural networks are computational models inspired by the brain. "
            "They consist of layers of interconnected neurons. "
            "Training neural networks involves optimizing weights through backpropagation."
        ),
    ),
    Article(
        title="Large Language Models",
        content=(
            "Large language models are trained on vast text corpora. "
            "They can generate coherent text and answer questions. "
            "However, without grounding, they may produce hallucinated facts."
        ),
    ),
    Article(
        title="Data Science",
        content=(
            "Data science combines statistics, computing, and domain knowledge. "
            "It involves cleaning data, analyzing patterns, and building predictive models. "
            "Good data practices help ensure reliable insights."
        ),
    ),
    Article(
        title="Cloud Computing",
        content=(
            "Cloud computing provides on-demand resources over the internet. "
            "It allows scalable storage and computation. "
            "Businesses use cloud services to deploy AI and data pipelines."
        ),
    ),
    Article(
        title="Vector Embeddings",
        content=(
            "Vector embeddings map words or documents to numeric vectors. "
            "Techniques like Word2Vec, GloVe, or transformer embeddings capture semantics. "
            "Embeddings enable similarity calculations in search tasks."
        ),
    ),
    Article(
        title="Retrieval Techniques",
        content=(
            "Retrieval techniques include keyword matching, TF-IDF, and semantic search. "
            "Hybrid retrieval can combine keyword and vector methods. "
            "Effective retrieval is key to supporting generation in RAG."
        ),
    ),
]

# ---------- Query Cases (8) ----------
QUERY_CASES = [
    QueryCase(
        query_id="Q1",
        query="How does RAG reduce hallucination?",
        expected_title="Retrieval-Augmented Generation",
        reference_answer="RAG reduces hallucination by grounding answers in retrieved context."
    ),
    QueryCase(
        query_id="Q2",
        query="Why is FAISS useful for local RAG prototypes?",
        expected_title="FAISS",
        reference_answer="FAISS enables local vector search without a cloud database."
    ),
    QueryCase(
        query_id="Q3",
        query="What stages contribute to RAG latency variation?",
        expected_title="Latency in RAG",
        reference_answer="Generation contributes most because output length and reasoning vary."
    ),
    QueryCase(
        query_id="Q4",
        query="What does answer relevance measure?",
        expected_title="Answer Evaluation",
        reference_answer="Answer relevance measures how well the answer addresses the query."
    ),
    QueryCase(
        query_id="Q5",
        query="How does Azure AI Search support retrieval?",
        expected_title="Azure AI Search",
        reference_answer="Azure AI Search supports keyword, vector and hybrid retrieval."
    ),
    QueryCase(
        query_id="Q6",
        query="What is context precision in RAG evaluation?",
        expected_title="Answer Evaluation",
        reference_answer="Context precision measures the proportion of relevant retrieved chunks."
    ),
    QueryCase(
        query_id="Q7",
        query="How does vector search differ from keyword search?",
        expected_title="Vector Search",
        reference_answer="Vector search uses semantic similarity while keyword search relies on exact term matching."
    ),
    QueryCase(
        query_id="Q8",
        query="Why does generation latency vary more than retrieval latency?",
        expected_title="Latency in RAG",
        reference_answer="Generation latency varies because token count, context size and reasoning complexity vary."
    ),
]

# ---------- Embedding (Local Hashing) ----------
class LocalHashEmbedder:
    # Embeds text using HashingVectorizer and L2 normalization
    def __init__(self, dim: int) -> None:
        self.vectorizer = HashingVectorizer(
            n_features=dim,
            alternate_sign=False,
            norm=None,
            stop_words="english"
        )
    def embed_documents(self, texts: list[str]) -> np.ndarray:
        matrix = self.vectorizer.transform(texts)
        normalized = normalize(matrix, norm="l2", copy=False)
        return normalized.astype(np.float32).toarray()
    def embed_query(self, query: str) -> np.ndarray:
        return self.embed_documents([query])[0]

embedder = LocalHashEmbedder(dim=EMBEDDING_DIM)
article_vectors = embedder.embed_documents([article.content for article in ARTICLES])

# ---------- Helper Functions ----------
def token_count(text: str) -> int:
    # Count word tokens in text.
    return len(re.findall(r"\b\w+\b", text))

def content_words(text: str) -> set[str]:
    # Return set of content words (filtering common stopwords).
    stop_words = {
        "a","an","and","are","as","at","be","because","by","for","from","how","in",
        "is","it","of","on","or","that","the","to","what","when","where","which",
        "why","with",
    }
    return {
        word for word in re.findall(r"[a-z0-9]+", text.lower())
        if word not in stop_words and len(word) > 2
    }

def retrieve(query: str) -> tuple[list[Article], float, float]:
    # Retrieve top-K articles for the query and measure embedding/retrieval latency.
    start_time = time.perf_counter()
    q_vec = embedder.embed_query(query)
    embed_time = (time.perf_counter() - start_time) * 1000
    start_time = time.perf_counter()
    sims = cosine_similarity([q_vec], article_vectors)[0]
    top_indexes = np.argsort(sims)[::-1][:TOP_K]
    retrieved = [ARTICLES[i] for i in top_indexes]
    retrieval_time = (time.perf_counter() - start_time) * 1000
    return retrieved, embed_time, retrieval_time

def generate_grounded_answer(query: str, retrieved: list[Article]) -> tuple[str, float]:
    # Generate answer by selecting relevant sentences from retrieved chunks.
    start_time = time.perf_counter()
    query_terms = content_words(query)
    selected_sentences: list[str] = []
    for chunk in retrieved:
        sentences = re.split(r"(?<=[.!?])\s+", chunk.content)
        for sent in sentences:
            if content_words(sent) & query_terms:
                selected_sentences.append(sent.strip())
    if not selected_sentences and retrieved:
        first_chunk_sent = re.split(r"(?<=[.!?])\s+", retrieved[0].content)[0].strip()
        selected_sentences.append(first_chunk_sent)
    answer = " ".join(selected_sentences[:3])
    # Simulate generation latency (vary with answer length)
    time.sleep(min(0.05, 0.005 * token_count(answer)))
    gen_time = (time.perf_counter() - start_time) * 1000
    return answer, gen_time

def answer_relevance(query: str, answer: str) -> float:
    # Cosine similarity between query and answer embeddings.
    v = embedder.embed_documents([query, answer])
    return float(cosine_similarity([v[0]], [v[1]])[0][0])

def faithfulness(answer: str, retrieved: list[Article]) -> float:
    # Fraction of answer terms supported by retrieved context.
    answer_terms = content_words(answer)
    context_terms = content_words(" ".join(chunk.content for chunk in retrieved))
    if not answer_terms:
        return 0.0
    return round(len(answer_terms & context_terms) / len(answer_terms), 4)

def context_precision(query_case: QueryCase, retrieved: list[Article]) -> float:
    # Fraction of retrieved chunks relevant to expected answer.
    reference_terms = content_words(query_case.reference_answer)
    relevant_count = 0
    for chunk in retrieved:
        title_match = chunk.title.lower() == query_case.expected_title.lower()
        overlap = len(content_words(chunk.content) & reference_terms)
        if title_match or overlap >= 3:
            relevant_count += 1
    return round(relevant_count / len(retrieved), 4) if retrieved else 0.0

def plot_query_metrics(row: dict) -> None:
    # Bar charts for tokens vs latency and quality metrics for one query.
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].bar(["Tokens", "Latency (ms)"], [row["total_tokens"], row["total_latency_ms"]],
                color=["#2563eb", "#dc2626"])
    axes[0].set_title(f"{row['query_id']} Tokens & Latency")
    axes[0].grid(axis="y", alpha=0.3)
    axes[1].bar(["Relevance", "Faithfulness", "Context Precision"],
                [row["answer_relevance"], row["faithfulness"], row["context_precision"]],
                color=["#16a34a", "#9333ea", "#f59e0b"])
    axes[1].set_ylim(0, 1.05)
    axes[1].set_title(f"{row['query_id']} Quality Metrics")
    axes[1].tick_params(axis="x", rotation=15)
    axes[1].grid(axis="y", alpha=0.3)
    fig.suptitle(row["query"], fontsize=10)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / f"{row['query_id'].lower()}_metrics.png", dpi=150)
    plt.close(fig)

def plot_summary(results: list[dict]) -> None:
    # Summary plots and correlation
    frame = pd.DataFrame(results)
    print("\n" + "="*60)
    print("CORRELATION ANALYSIS")
    print("="*60)
    corr_tokens = frame["total_tokens"].corr(frame["total_latency_ms"])
    corr_context = frame["context_precision"].corr(frame["total_latency_ms"])
    corr_relevance = frame["answer_relevance"].corr(frame["total_latency_ms"])
    corr_faith = frame["faithfulness"].corr(frame["total_latency_ms"])
    print(f"Tokens vs Latency            : {corr_tokens:.3f}")
    print(f"Context Precision vs Latency : {corr_context:.3f}")
    print(f"Answer Relevance vs Latency  : {corr_relevance:.3f}")
    if np.isnan(corr_faith):
        print(f"Faithfulness vs Latency      : N/A")
    else:
        print(f"Faithfulness vs Latency      : {corr_faith:.3f}")
    plt.figure(figsize=(8,5))
    plt.scatter(frame["total_tokens"], frame["total_latency_ms"])
    plt.xlabel("Total Tokens")
    plt.ylabel("Total Latency (ms)")
    plt.title("Token Count vs Latency")
    plt.grid(True)
    plt.savefig(PLOTS_DIR / "tokens_vs_latency.png", dpi=150)
    plt.close()
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    axes[0].plot(frame["query_id"], frame["total_tokens"], marker="o", label="Total Tokens")
    axes[0].plot(frame["query_id"], frame["total_latency_ms"], marker="o", label="Latency (ms)")
    axes[0].set_title("Tokens & Latency by Query")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    for metric in ["answer_relevance", "faithfulness", "context_precision"]:
        axes[1].plot(frame["query_id"], frame[metric], marker="o", label=metric)
    axes[1].set_ylim(0, 1.05)
    axes[1].set_title("Quality Metrics by Query")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "all_queries_summary.png", dpi=150)
    plt.close(fig)

def write_report(results: list[dict]) -> None:
    # Write markdown report of results
    frame = pd.DataFrame(results)
    report_lines = [
        "# RAG Metrics and Latency Evaluation Report",
        "",
        "This report summarizes the RAG evaluation across queries, including token counts, latencies, and quality metrics.",
        "",
        "## Metrics",
        "",
        "| Metric            | Meaning                                      |",
        "| ----------------- | -------------------------------------------- |",
        "| Total Tokens      | Total tokens in prompt/context + answer      |",
        "| Latency (ms)      | Embedding + retrieval + generation (ms)      |",
        "| Answer Relevance  | Cosine similarity between query and answer   |",
        "| Faithfulness      | Fraction of answer terms in retrieved context|",
        "| Context Precision | Fraction of retrieved chunks relevant        |",
        "",
        "## Final Summary",
        "",
        f"- Average total tokens: {frame['total_tokens'].mean():.2f}",
        f"- Average total latency (ms): {frame['total_latency_ms'].mean():.2f}",
        f"- Average answer relevance: {frame['answer_relevance'].mean():.3f}",
        f"- Average faithfulness: {frame['faithfulness'].mean():.3f}",
        f"- Average context precision: {frame['context_precision'].mean():.3f}",
        "",
        "## Correlation Findings",
        "",
        "The analysis shows:",
        "",
        f"- Tokens vs Latency correlation: {frame['total_tokens'].corr(frame['total_latency_ms']):.3f}",
        f"- Context Precision vs Latency correlation: {frame['context_precision'].corr(frame['total_latency_ms']):.3f}",
        f"- Answer Relevance vs Latency correlation: {frame['answer_relevance'].corr(frame['total_latency_ms']):.3f}",
        "",
        "Generation latency is influenced by token count and answer complexity.",
        "Higher context precision and relevance indicate better grounding and answer quality.",
        "",
        "## Output Graphs",
        "",
        "- `plots/all_queries_summary.png`",
    ]
    for row in results:
        report_lines.append(f"- `plots/{row['query_id'].lower()}_metrics.png`")
    report_lines.append("- `plots/tokens_vs_latency.png`")
    (OUTPUT_DIR / "rag_metrics_report.md").write_text("\n".join(report_lines), encoding="utf-8")

def evaluate_query(query_case: QueryCase) -> dict:
    # Run retrieval, generation, and compute metrics for one query.
    retrieved, embed_ms, retrieval_ms = retrieve(query_case.query)
    answer, gen_ms = generate_grounded_answer(query_case.query, retrieved)
    total_latency = embed_ms + retrieval_ms + gen_ms
    context_text = " ".join(chunk.content for chunk in retrieved)
    total_tokens = token_count(query_case.query) + token_count(context_text) + token_count(answer)
    return {
        "query_id": query_case.query_id,
        "query": query_case.query,
        "expected_title": query_case.expected_title,
        "retrieved_titles": " | ".join(chunk.title for chunk in retrieved),
        "answer": answer,
        "input_tokens": token_count(query_case.query) + token_count(context_text),
        "output_tokens": token_count(answer),
        "total_tokens": total_tokens,
        "embedding_latency_ms": round(embed_ms, 3),
        "retrieval_latency_ms": round(retrieval_ms, 3),
        "generation_latency_ms": round(gen_ms, 3),
        "total_latency_ms": round(total_latency, 3),
        "answer_relevance": round(answer_relevance(query_case.query, answer), 4),
        "faithfulness": faithfulness(answer, retrieved),
        "context_precision": context_precision(query_case, retrieved),
    }

def main():
    results = []
    for qc in QUERY_CASES:
        results.append(evaluate_query(qc))
    # Save charts per query
    for row in results:
        plot_query_metrics(row)
    # Summary plots & correlation
    plot_summary(results)
    # Save data outputs
    frame = pd.DataFrame(results)
    frame.to_csv(OUTPUT_DIR / "rag_metrics_by_query.csv", index=False)
    (OUTPUT_DIR / "rag_metrics_by_query.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_report(results)
    print("RAG evaluation complete. Output folder:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
