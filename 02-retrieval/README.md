# 02 — Retrieval

> The system that identifies which portions of the corpus are relevant to a given request.

Retrieval is where most teams over-engineer. The temptation is to reach for a managed vector database and a 6-step rerank pipeline on day one. For most corpora — thousands of documents, not billions — a local FAISS index over Bedrock Titan embeddings beats the managed stack on cost, latency, and operational complexity.

This folder contains two scripts:

1. **`embed_corpus.py`** — reads the JSONL corpus from [`../01-corpus/`](../01-corpus/), embeds each ADR (full document + each section) with Titan Text Embeddings v2, and writes a local FAISS `IndexFlatIP` plus a metadata sidecar.

2. **`query.py`** — embeds a natural-language query, returns top-K matching chunks, and deduplicates by ADR so one decision doesn't drown out the others. The `--json` flag emits results in the shape the injection layer consumes.

---

## Run it

```bash
pip install -r requirements.txt

# Produce the corpus if you haven't already
python ../01-corpus/ingest_adrs.py ../01-corpus/sample-adrs --out ../01-corpus/corpus.jsonl

# Build the index (one Bedrock call per chunk)
python embed_corpus.py --corpus ../01-corpus/corpus.jsonl

# Ask it a question
python query.py "Should I use Postgres locally or H2?"
python query.py --json "Why are we rendering HTML on the server instead of a SPA?" > retrieved.json
```

Typical output:

```
Query: "Should I use Postgres locally or H2?"

  0.7812  ADR-002   decision        Use H2 in-memory database in development, PostgreSQL in production
  0.6431  ADR-002   consequences    Use H2 in-memory database in development, PostgreSQL in production
  0.4102  ADR-001   full            Use Spring Boot as the application framework
```

Configure via environment:

```bash
export AWS_REGION="us-east-1"
export BEDROCK_EMBED_MODEL_ID="amazon.titan-embed-text-v2:0"
```

---

## The retrieval question is simpler than most tutorials make it

Three decisions cover 90% of production retrieval:

1. **What do you embed?** Full ADR body, or chunk into sections (context / decision / consequences)? Chunking gives tighter matches but loses cross-section context. The default here embeds the whole ADR *plus* each section as its own vector, retrieves across both, and dedupes by ADR id. You get tight matches without losing the full-document signal.

2. **What do you retrieve against?** The user's raw question? A rephrased query? An HyDE-style synthetic answer? Rephrasing helps when questions are short and jargon-heavy (typical in engineering chat). Not implemented here — add a rephrase step in front of `embed_query()` if your queries are noisy.

3. **How much do you return?** Top-K is a coarse lever. Better: retrieve 20, rerank with a cheap cross-encoder or an LLM judge, keep 3–5. The token budget at injection time is the real constraint.

This implementation does (1) and (3, shallow). Reranking belongs in front of the injection layer — see [`../03-injection/`](../03-injection/).

---

## Why FAISS and not a managed vector DB

For a corpus the size of most organizations' ADR + design doc collection — say, 5,000 documents and 50,000 chunks — the working set fits in a few hundred MB. A local FAISS `IndexFlatIP` runs a query in single-digit milliseconds on a laptop and costs nothing to operate.

Managed vector databases earn their keep above roughly 1M vectors, or when you need multi-tenant isolation, or when the index needs to be queried from a fleet of stateless servers. Below that, the operational cost (monitoring, credential rotation, query-side latency from a network hop) exceeds the engineering cost of running FAISS yourself.

This is the point [_The real cost of knowledge_](https://www.outcomeops.ai/blogs/the-real-cost-of-knowledge-why-most-ai-engineering-platforms-over-engineer-rag) makes at length — most RAG infrastructure is solving problems the team doesn't actually have yet.

---

## Further reading

**Retrieval and embeddings**
- [facebookresearch/faiss](https://github.com/facebookresearch/faiss) — the index used here; the README and wiki cover index types beyond `IndexFlatIP`
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) — Liu et al., 2023; the empirical basis for why position of retrieved context matters
- [Context engineering for agents](https://blog.langchain.com/context-engineering-for-agents/) — LangChain on the write/select/compress/isolate strategies applied during retrieval

**Practitioner perspectives (outcomeops.ai)**
- [The real cost of knowledge: why most AI engineering platforms over-engineer RAG](https://www.outcomeops.ai/blogs/the-real-cost-of-knowledge-why-most-ai-engineering-platforms-over-engineer-rag)
- [OutcomeOps: self-documenting architecture — when code becomes queryable](https://www.outcomeops.ai/blogs/outcomeops-self-documenting-architecture-when-code-becomes-queryable)
- [Same context, three models — the floor isn't zero](https://www.outcomeops.ai/blogs/same-context-three-models-the-floor-isnt-zero)

Previous: [`../01-corpus/`](../01-corpus/) — the input to this layer.
Next: [`../03-injection/`](../03-injection/) — what happens to the retrieved chunks.
