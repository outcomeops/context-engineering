# 04 — Output

> What the AI produces, shaped by the retrieved context. In enterprise software development, this is usually code, documentation, or a pull request.

Most AI tooling stops at "the model returned some text." Context engineering treats the output as an artifact to be structured, validated, and audited — not a conversation turn. The output layer is what separates a chat assistant from infrastructure.

The examples in this folder will show:

- **`generate_pr_description.py`** — given a diff and the retrieved ADRs, produce a structured PR description in JSON (summary, motivation, cited ADRs, risk areas, test plan) and render it as Markdown.
- **`structured_refactor.py`** — propose a refactor that explicitly cites which ADR it respects. Uses Bedrock's tool-use schema to constrain the output shape.
- **`schema.py`** — JSON schemas for the output types, so downstream CI can validate them.

**Status:** coming next.

---

## Why structured output matters

A model that returns "here is the refactored code" gives you no handles for automation. A model that returns:

```json
{
  "refactor_summary": "...",
  "cited_adrs": ["ADR-002"],
  "files_changed": ["src/main/java/..."],
  "risks": ["migration order with H2 vs Postgres"],
  "tests_added": ["OwnerRepositoryIntegrationTest#findById"]
}
```

…gives CI something to enforce, reviewers something to audit, and future retrieval something to index. The output becomes part of the corpus for the next decision.

This is the loop that makes a context engineering system compound. The outputs of today's decisions become the corpus for tomorrow's.

---

## Further reading

- [The outcome is writing itself](https://www.outcomeops.ai/blogs/the-outcome-is-writing-itself)
- [The OutcomeOps way: stop prompting, start co-engineering](https://www.outcomeops.ai/blogs/the-outcomeops-way-stop-prompting-start-co-engineering)
- [What AI-assisted development actually looks like in two years](https://www.outcomeops.ai/blogs/what-ai-assisted-development-actually-looks-like-in-two-years)
- [The rise of the outcome engineer](https://www.outcomeops.ai/blogs/the-rise-of-the-outcome-engineer)

Previous: [`../03-injection/`](../03-injection/) — how context got into the model.
Next: [`../05-enforcement/`](../05-enforcement/) — how we verify the output actually used it.
