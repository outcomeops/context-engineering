# 05 — Enforcement

> The mechanism that ensures the generated output actually reflects the retrieved context — typically code review, automated policy checks, or PR templates that cite the context used.

This is the component that turns a RAG system into a context engineering system. Without enforcement, the model can retrieve the right ADRs, inject them perfectly, and then happily contradict them in the output — and nobody notices until it's merged.

This folder contains:

1. **`check_pr_cites_adrs.py`** — two-layer CI check. A fast static layer verifies every cited ADR actually exists in the corpus. Then an LLM judge reads the diff alongside each cited ADR and returns a structured verdict (consistent / inconsistent / not-applicable). Exit code 2 blocks the merge.

2. **`pr-template.md`** — a GitHub-style PR template with the `cited ADRs` section that `check_pr_cites_adrs.py` keys off of. Drop in `.github/pull_request_template.md` of any repo that wants to adopt this pattern.

---

## Run it

```bash
pip install -r requirements.txt

# Assumes you have:
#   ../01-corpus/corpus.jsonl    (from 01-corpus/ingest_adrs.py)
#   ../04-output/pr.json         (from 04-output/generate_pr_description.py)
#   diff.patch                   (the actual diff the PR describes)

# Static check only — no Bedrock call
python check_pr_cites_adrs.py \
  --pr ../04-output/pr.json \
  --diff diff.patch \
  --corpus ../01-corpus/corpus.jsonl \
  --skip-judge

# Full check, including the LLM judge
python check_pr_cites_adrs.py \
  --pr ../04-output/pr.json \
  --diff diff.patch \
  --corpus ../01-corpus/corpus.jsonl
```

Typical output:

```
Checking 1 cited ADR(s) against corpus of 3
  STATIC PASS: all cited ADRs exist in the corpus
  JUDGE PASS: ADR-002 (overrides) — The diff replaces H2 with Testcontainers and the note acknowledges ADR-002's H2-in-dev decision is being reversed.
```

In CI, drop it into a GitHub Actions step with exit code propagation:

```yaml
- name: Check PR cites ADRs
  run: |
    python 05-enforcement/check_pr_cites_adrs.py \
      --pr pr.json --diff diff.patch --corpus 01-corpus/corpus.jsonl
```

---

## What enforcement looks like in practice

Three concrete layers, weakest to strongest:

1. **PR template** (`pr-template.md`). Requires the author to list cited ADRs. Cheap to add, catches nothing on its own, but creates the structured input for the next two layers.

2. **Static check.** Every cited ADR id exists in the corpus. Catches typos and hallucinated citations in milliseconds, no API call needed. This is the cheap, high-signal layer — run it on every PR.

3. **LLM judge.** Reads the diff against each cited ADR and decides whether the relationship is honest. Catches the case where the PR cites ADR-002 and says "respects" but the diff deliberately does the opposite. Slower and costs tokens — run it on non-draft PRs.

Layer 1 is documentation. Layers 2 and 3 are enforcement.

---

## What this does not catch

- **Missing citations.** If the diff should have cited ADR-003 but the author cited nothing, this check passes the static layer (because the cited list, while sparse, is internally consistent). Use retrieval on the diff to flag "the top retrieved ADRs are not in `cited_adrs`" as a separate warning.

- **Ambient corpus decay.** If the ADRs themselves are out of date, this layer will happily enforce stale decisions. Enforcement is only as honest as the corpus — which is why [`../01-corpus/`](../01-corpus/) is where the whole system starts and stops.

- **Judge bias.** The LLM judge is another model; its verdicts can be wrong. Run `temperature=0.0`, keep the judge prompt narrow, and treat the verdict as a reviewer aid, not a final authority. A human still merges the PR.

---

## Further reading

- [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) (Zheng et al., 2023) — foundational LLM-as-judge paper and the biases to watch for
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (Anthropic, Sep 2025) — applies equally to what the judge sees
- [Your pull request is the guardrail](https://www.outcomeops.ai/blogs/your-pull-request-is-the-guardrail) (OutcomeOps) — the thesis this folder implements
- [Engineers who own the outcome](https://www.outcomeops.ai/blogs/engineers-who-own-the-outcome) (OutcomeOps) — why enforcement still needs a human in the loop
- [From fixing code to teaching systems](https://www.outcomeops.ai/blogs/from-fixing-code-to-teaching-systems) (OutcomeOps) — what enforcement produces over time
- [The OutcomeOps way: stop prompting, start co-engineering](https://www.outcomeops.ai/blogs/the-outcomeops-way-stop-prompting-start-co-engineering) (OutcomeOps) — why the enforcement loop matters

Previous: [`../04-output/`](../04-output/) — the artifact being enforced.
