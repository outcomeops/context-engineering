# 03 — Injection

> The process by which retrieved context reaches the AI's working memory — typically the model's context window — at the moment of generation.

Injection is where prompt engineering and context engineering meet. Retrieval has given you a ranked list of relevant ADRs; injection decides how those ADRs show up in the model's input. Poor injection wastes a good retrieval: the right ADR is in the prompt, but buried behind noise, or formatted in a way the model ignores.

The examples in this folder will show:

- **`build_prompt.py`** — assemble a structured system prompt from retrieved ADRs with token budget accounting. Shows what to drop when you exceed the window.
- **`with_vs_without.py`** — the same user question answered twice: once with injected ADRs, once without. Diffs the outputs side by side.
- **`token_budget.py`** — a utility for estimating how many ADRs fit in a given model's context window given a reserve for the response.

**Status:** coming next.

---

## Injection decisions that actually move quality

- **Ordering.** Claude weights content near the end of the context window slightly more than content in the middle. Put the user question last, the most relevant ADRs just before it, and lower-signal material (general guidelines, less-relevant ADRs) at the top.
- **Delimiters.** XML tags (`<adr id="ADR-002">...</adr>`) outperform Markdown headings for instruction-following in Claude. The model treats them as structural rather than prose.
- **Cite-by-design.** Ask the model to cite the ADR id it relied on in its output. This makes the enforcement layer ([`../05-enforcement/`](../05-enforcement/)) possible.
- **Budget explicitly.** A 200K context window is not a budget to spend; it is a ceiling. Track retrieved-context tokens + system prompt tokens + expected response tokens, and drop the lowest-score ADRs first.

---

## Further reading

- [How I refactored a 1348-line Lambda using context engineering](https://www.outcomeops.ai/blogs/how-i-refactored-a-1348-line-lambda-using-context-engineering)
- [Same context, three models — the floor isn't zero](https://www.outcomeops.ai/blogs/same-context-three-models-the-floor-isnt-zero)
- [6.6M tokens, $4,800, zero visibility — so I built a dashboard](https://www.outcomeops.ai/blogs/6-6m-tokens-4800-zero-visibility-so-i-built-a-dashboard)
- [Your AI inference bill goes up every month](https://www.outcomeops.ai/blogs/your-ai-inference-bill-goes-up-every-month)

Previous: [`../02-retrieval/`](../02-retrieval/) — how the ADRs got selected.
Next: [`../04-output/`](../04-output/) — what the model produces with them.
