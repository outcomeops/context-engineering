# 01 — Corpus

> The body of organizational material that defines how the organization thinks, builds, and decides.

The corpus is the **first and hardest** component of a context engineering system. Without retrievable source material, the rest of the pipeline has nothing to ground on. A context engineering system is only as good as the corpus feeding it.

This folder contains two scripts:

1. **`ingest_adrs.py`** — reads a directory of Markdown ADRs, parses them into a normalized JSONL corpus with metadata (id, title, status, date, sections). This is the input to the retrieval layer in [`../02-retrieval/`](../02-retrieval/).

2. **`generate_adr_from_diff.py`** — takes a git diff and produces an ADR in the [Nygard format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) using Claude on Bedrock. This is how you bootstrap a corpus from a codebase that has none — the pattern described in [_AI-generated ADRs: from zero documentation to queryable architecture_](https://www.outcomeops.ai/blogs/ai-generated-adrs-from-zero-documentation-to-queryable-architecture).

The sample corpus in [`sample-adrs/`](./sample-adrs/) mirrors the three ADRs discussed in [_How 3 ADRs changed everything: Spring PetClinic proof_](https://www.outcomeops.ai/blogs/how-3-adrs-changed-everything-spring-petclinic-proof). Read that blog for the full narrative; this folder gives you the artifacts to run against.

---

## Run it

```bash
pip install -r requirements.txt

# Ingest the sample ADRs into a normalized corpus file
python ingest_adrs.py ./sample-adrs --out corpus.jsonl

# Generate a new ADR from a git diff
git diff HEAD~1 HEAD | python generate_adr_from_diff.py --title "Switch from H2 to PostgreSQL in dev"
```

Configure Bedrock via environment:

```bash
export AWS_REGION="us-east-1"
export BEDROCK_MODEL_ID="us.anthropic.claude-sonnet-4-5-20250929-v1:0"
```

---

## What a corpus actually contains

ADRs are a starting point, not the whole corpus. A production corpus typically includes:

- **ADRs** — decisions with their context, tradeoffs, and consequences
- **Code maps** — structural signals: ownership, module boundaries, dependency graphs
- **Design documents** — higher-level system diagrams and flows
- **Compliance frameworks** — SOC 2, HIPAA, PCI-DSS controls and the code they govern
- **Runbooks** — operational procedures and incident response
- **Internal wikis** — onboarding docs, glossaries, conventions

The ingestion pattern is the same for all of them: parse into a normalized schema with `{id, title, type, source, chunks, metadata}`, then hand off to retrieval.

---

## Why ADRs specifically

ADRs are the densest, highest-signal artifact in most corpora. A single ADR captures:

- **What** was decided (the decision)
- **Why** (the context and forces)
- **What we gave up** (the consequences)

That structure is already shaped like what an LLM needs at decision time. When a developer asks "should I use X?", the relevant ADR answers both directly (the decision) and defensively (the reasoning the decision turned on).

If your organization has no ADRs, `generate_adr_from_diff.py` is where to start. Point it at recent merges and you'll have a seeded corpus in a day.

---

## Further reading

- [What is an ADR and why they're critical for AI-powered development](https://www.outcomeops.ai/blogs/what-is-an-adr-and-why-theyre-critical-for-ai-powered-development)
- [AI-generated ADRs: from zero documentation to queryable architecture](https://www.outcomeops.ai/blogs/ai-generated-adrs-from-zero-documentation-to-queryable-architecture)
- [How 3 ADRs changed everything: Spring PetClinic proof](https://www.outcomeops.ai/blogs/how-3-adrs-changed-everything-spring-petclinic-proof)
- [Making legacy SAP codebases queryable: ADR generation from ABAP](https://www.outcomeops.ai/blogs/making-legacy-sap-codebases-queryable-adr-generation-from-abap)
- [OutcomeOps: self-documenting architecture — when code becomes queryable](https://www.outcomeops.ai/blogs/outcomeops-self-documenting-architecture-when-code-becomes-queryable)

Next: [`../02-retrieval/`](../02-retrieval/) — turning this corpus into something the model can query.
