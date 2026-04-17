# 03 — Injection

> The process by which retrieved context reaches the AI's working memory — typically the model's context window — at the moment of generation.

Injection is where prompt engineering and context engineering meet. Retrieval has given you a ranked list of relevant ADRs; injection decides how those ADRs show up in the model's input. Poor injection wastes a good retrieval: the right ADR is in the prompt, but buried behind noise, or formatted in a way the model ignores.

This folder contains two scripts:

1. **`build_prompt.py`** — assembles a structured prompt from the retrieved ADRs, drops the lowest-score ones if the token budget would be exceeded, and calls Claude on Bedrock. Supports `--dry-run` to print the assembled prompt without making an API call.

2. **`with_vs_without.py`** — runs the same question twice, once with injected ADRs and once with only a generic system prompt. The diff between the two answers is the value the corpus and retrieval layers add.

---

## Run it

```bash
pip install -r requirements.txt

# Retrieve first (from ../02-retrieval/)
cd ../02-retrieval
python query.py --json "Why are we using H2 in dev but Postgres in prod?" > ../03-injection/retrieved.json
cd ../03-injection

# See the assembled prompt without calling Bedrock
python build_prompt.py \
  --retrieved retrieved.json \
  --question "Why are we using H2 in dev but Postgres in prod?" \
  --dry-run

# Actually call Claude
python build_prompt.py \
  --retrieved retrieved.json \
  --question "Why are we using H2 in dev but Postgres in prod?"

# Side-by-side: generic prompt vs context-engineered prompt
python with_vs_without.py \
  --retrieved retrieved.json \
  --question "Why are we using H2 in dev but Postgres in prod?"
```

The `with_vs_without.py` output is the demo — the "without" answer is generically correct at best and wrong-but-plausible at worst; the "with" answer cites the specific ADRs and mirrors the team's actual decision.

---

## Injection decisions that actually move quality

- **Delimiters.** XML tags (`<adr id="ADR-002">...</adr>`) outperform Markdown headings for instruction-following in Claude. The model treats them as structural rather than prose. This codebase uses XML.

- **Ordering.** Claude weights content near the end of the context window slightly more than content in the middle. This codebase puts the ADR block first and the user question last — question last is the important half.

- **Cite-by-design.** The system prompt explicitly asks the model to cite ADR ids. This makes the enforcement layer ([`../05-enforcement/`](../05-enforcement/)) possible: if the output doesn't cite anything, something went wrong upstream.

- **Budget explicitly.** A 200K context window is not a budget to spend; it is a ceiling. `build_prompt.py` enforces a token budget and drops the lowest-score ADRs first. The heuristic used here (3.5 chars per token for English technical prose) is approximate — the real `inputTokens` from the Bedrock response is printed on stderr so you can tune the budget if needed.

- **Honesty over completeness.** The prompt tells Claude to say "none of the ADRs cover this" rather than answering from general knowledge. A context-engineered system that silently falls back to base-model knowledge is worse than one that admits the corpus is thin — the former hides the gap, the latter surfaces it as a corpus problem to fix.

---

## What this folder does *not* do

- **Query rephrasing.** If your users ask short, jargon-heavy questions ("can we add a JSONB column?"), embed a rephrased version ("Is it acceptable to use PostgreSQL-specific JSONB columns in our JPA entities given the H2 dev environment?") rather than the raw query. Belongs in front of `query.py`.

- **Reranking.** Retrieve 20, rerank with a cheap cross-encoder or LLM judge, inject 3–5. Belongs between retrieval and injection.

Both are worth adding once your corpus and query patterns stabilize. Premature on day one.

---

## Further reading

**Prompt construction and context window behavior**
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic engineering, on curating what reaches the model
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) — Liu et al., 2023; the paper behind the "put the question last" advice
- [Context Engineering Guide](https://www.promptingguide.ai/guides/context-engineering-guide) — PromptingGuide.ai reference on structuring model input

**Practitioner perspectives (outcomeops.ai)**
- [How I refactored a 1348-line Lambda using context engineering](https://www.outcomeops.ai/blogs/how-i-refactored-a-1348-line-lambda-using-context-engineering)
- [Same context, three models — the floor isn't zero](https://www.outcomeops.ai/blogs/same-context-three-models-the-floor-isnt-zero)
- [6.6M tokens, $4,800, zero visibility — so I built a dashboard](https://www.outcomeops.ai/blogs/6-6m-tokens-4800-zero-visibility-so-i-built-a-dashboard)
- [Your AI inference bill goes up every month](https://www.outcomeops.ai/blogs/your-ai-inference-bill-goes-up-every-month)

Previous: [`../02-retrieval/`](../02-retrieval/) — how the ADRs got selected.
Next: [`../04-output/`](../04-output/) — what the model produces with them.
