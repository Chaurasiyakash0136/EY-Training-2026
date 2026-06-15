# RAG Metrics and Latency Evaluation Report

This report summarizes the RAG evaluation across queries, including token counts, latencies, and quality metrics.

## Metrics

| Metric            | Meaning                                      |
| ----------------- | -------------------------------------------- |
| Total Tokens      | Total tokens in prompt/context + answer      |
| Latency (ms)      | Embedding + retrieval + generation (ms)      |
| Answer Relevance  | Cosine similarity between query and answer   |
| Faithfulness      | Fraction of answer terms in retrieved context|
| Context Precision | Fraction of retrieved chunks relevant        |

## Final Summary

- Average total tokens: 191.62
- Average total latency (ms): 53.66
- Average answer relevance: 0.423
- Average faithfulness: 1.000
- Average context precision: 0.375

## Correlation Findings

The analysis shows:

- Tokens vs Latency correlation: 0.756
- Context Precision vs Latency correlation: 0.163
- Answer Relevance vs Latency correlation: 0.247

Generation latency is influenced by token count and answer complexity.
Higher context precision and relevance indicate better grounding and answer quality.

## Output Graphs

- `plots/all_queries_summary.png`
- `plots/q1_metrics.png`
- `plots/q2_metrics.png`
- `plots/q3_metrics.png`
- `plots/q4_metrics.png`
- `plots/q5_metrics.png`
- `plots/q6_metrics.png`
- `plots/q7_metrics.png`
- `plots/q8_metrics.png`
- `plots/tokens_vs_latency.png`