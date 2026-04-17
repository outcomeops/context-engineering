# 02 — Retrieval

> The system that identifies which portions of the corpus are relevant to a given request.

Retrieval is where most teams over-engineer. The temptation is to reach for a managed vector database and a 6-step rerank pipeline on day one. For most corpora — thousands of documents, not billions — a local FAISS index over Bedrock Titan embeddings beats the managed stack on cost, latency, and operational complexity.

The examples in this folder will show:

- **`embed_corpus.py`** — embed the JSONL corpus from `../01-corpus/` using Bedrock Titan embeddings and persist to a local FAISS index.
- **`query.py`** — semantic search over the index with top-K retrieval and score thresholding.
- **`hybrid_query.py`** — combine semantic similarity with structural signals (ADR status, recency, referenced files) for better ranking.

**Status:** coming next. The corpus layer is in place; this folder will consume its output.

---

## The retrieval question is simpler than most tutorials make it

Three decisions cover 90% of production retrieval:

1. **What do you embed?** Full ADR body, or chunk into sections (context / decision / consequences)? Chunking gives tighter matches but loses cross-section context. Our default: embed the whole ADR as one vector plus each section as its own vector, retrieve across both, dedupe by ADR id.

2. **What do you retrieve against?** The user's raw question? A rephrased query? An HyDE-style synthetic answer? Rephrasing helps when questions are short and jargon-heavy (typical in engineering chat).

3. **How much do you return?** Top-K is a coarse lever. Better: retrieve 20, rerank with a cheap cross-encoder or an LLM judge, keep 3–5. The token budget at injection time is the real constraint.

---

## Further reading

- [The real cost of knowledge: why most AI engineering platforms over-engineer RAG](https://www.outcomeops.ai/blogs/the-real-cost-of-knowledge-why-most-ai-engineering-platforms-over-engineer-rag)
- [OutcomeOps: self-documenting architecture — when code becomes queryable](https://www.outcomeops.ai/blogs/outcomeops-self-documenting-architecture-when-code-becomes-queryable)
- [Same context, three models — the floor isn't zero](https://www.outcomeops.ai/blogs/same-context-three-models-the-floor-isnt-zero)

Previous: [`../01-corpus/`](../01-corpus/) — the input to this layer.
Next: [`../03-injection/`](../03-injection/) — what happens to the retrieved chunks.
