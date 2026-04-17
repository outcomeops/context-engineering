# 05 — Enforcement

> The mechanism that ensures the generated output actually reflects the retrieved context — typically code review, automated policy checks, or PR templates that cite the context used.

This is the component that turns a RAG system into a context engineering system. Without enforcement, the model can retrieve the right ADRs, inject them perfectly, and then happily contradict them in the output — and nobody notices until it's merged.

The examples in this folder will show:

- **`check_pr_cites_adrs.py`** — a CI-style check that parses a PR description for cited ADR ids, pulls those ADRs from the corpus, and asks Claude whether the code changes are actually consistent with the cited decisions.
- **`review_against_corpus.py`** — given a diff, retrieve the relevant ADRs and flag any changes that appear to violate an ADR without citing and justifying the override.
- **`pr-template.md`** — a PR template that prompts authors to cite the ADRs they relied on, making enforcement possible downstream.

**Status:** coming next.

---

## What enforcement looks like in practice

Three concrete layers, weakest to strongest:

1. **PR template.** Requires the author to list cited ADRs. Cheap to add, catches nothing on its own, but creates the structured input for the next two layers.

2. **Automated check.** A CI job that reads the PR description, loads the cited ADRs, and uses an LLM to judge whether the diff is consistent with those ADRs. Blocks merge on disagreement.

3. **Reviewer-facing surface.** Surfaces retrieved ADRs to the human reviewer, so review comments can reference the same source material the author and the model saw. This is where context engineering becomes a team practice, not an individual productivity trick.

Layer 1 is documentation. Layers 2 and 3 are enforcement.

---

## Further reading

- [Your pull request is the guardrail](https://www.outcomeops.ai/blogs/your-pull-request-is-the-guardrail)
- [Engineers who own the outcome](https://www.outcomeops.ai/blogs/engineers-who-own-the-outcome)
- [From fixing code to teaching systems](https://www.outcomeops.ai/blogs/from-fixing-code-to-teaching-systems)
- [The OutcomeOps way: stop prompting, start co-engineering](https://www.outcomeops.ai/blogs/the-outcomeops-way-stop-prompting-start-co-engineering)

Previous: [`../04-output/`](../04-output/) — the artifact being enforced.
