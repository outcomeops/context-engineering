# Context Engineering

A working reference implementation of **context engineering** — the discipline of designing, retrieving, and injecting the information an AI system needs to produce accurate, organization-specific outputs.

This repo is the code companion to [**What Is Context Engineering?**](https://www.outcomeops.ai/context-engineering) on outcomeops.ai. The glossary defines the concepts; this repo shows them running end-to-end against a real corpus on Amazon Bedrock.

> Context engineering treats context as a first-class engineering artifact — version-controlled, retrievable, and enforceable — rather than as prompts typed into a chat window.

---

## The five components

A context engineering system has five components. Each folder implements one against the same running example (a Spring PetClinic codebase with ADRs):

| # | Component | What it does | Folder |
|---|---|---|---|
| 1 | **Corpus** | The organizational material that defines how you think, build, and decide | [`01-corpus/`](./01-corpus) |
| 2 | **Retrieval** | Identifies which portions of the corpus are relevant to a given request | [`02-retrieval/`](./02-retrieval) |
| 3 | **Injection** | Gets retrieved context into the model's working memory at decision time | [`03-injection/`](./03-injection) |
| 4 | **Output** | Produces reviewable artifacts (code, PRs, docs) shaped by that context | [`04-output/`](./04-output) |
| 5 | **Enforcement** | Ensures the generated output actually reflects the retrieved context | [`05-enforcement/`](./05-enforcement) |

Plus [`comparisons/`](./comparisons) — the same task run with and without context engineering, plus how CE differs from RAG, Copilot, and agent frameworks.

A system with only components 1–3 is a RAG system. The output and enforcement layers are what make CE different — they make the generated content reviewable and governable.

---

## Running the examples

All examples use **Amazon Bedrock** with Claude. Each folder has its own `requirements.txt` and `README.md` with a runnable command.

**Prerequisites:**

- Python 3.11+
- AWS account with credentials configured (`aws configure` or env vars)
- AWS region that supports Claude and Titan (e.g. `us-east-1`, `us-west-2`)

This repo uses Anthropic Claude for generation and Amazon Titan for embeddings. Titan and most Bedrock foundation models are **auto-enabled** on first invocation — no action needed.

**Anthropic Claude requires a one-time First Time Use (FTU) form per AWS account.** If your account has never used Anthropic models on Bedrock, the first script run will fail with `AccessDeniedException`. To fix:

1. Open any Anthropic Claude model in the [Bedrock model catalog](https://console.aws.amazon.com/bedrock/home#/model-catalog)
2. Fill the First Time Use form (company, use case — about a minute)
3. Submit — access is granted immediately, no review queue

If you're in an AWS Organization child account, the form must be submitted from the management account to inherit access.

**Quickstart:**

```bash
git clone https://github.com/outcomeops/context-engineering.git
cd context-engineering/01-corpus
pip install -r requirements.txt
python ingest_adrs.py ./sample-adrs
```

Set the model via environment variable if you want to override the default:

```bash
export BEDROCK_MODEL_ID="us.anthropic.claude-sonnet-4-5-20250929-v1:0"
export AWS_REGION="us-east-1"
```

---

## Why this repo exists

Most AI coding assistants produce generic output. An engineer using a generic assistant still has to adapt the output to local patterns — the assistant doesn't know what your team decided last quarter, what your compliance framework requires, or why you picked one library over another.

A context-engineered system produces output that already conforms to local patterns, because the retrieval layer has fed the model the relevant ADRs, code, and standards at decision time. The enforcement layer ensures the output actually cites what it relied on.

This repo exists to show the pattern in code, end-to-end, so teams can build it themselves or evaluate commercial tools that claim to do it.

---

## Context engineering changes organizations, not just code

The five-component model is the technical frame. Teams that actually deploy it consistently discover the harder shift is organizational. Roles, KPIs, and decision rights in a traditional software org were shaped by a world where AI could not read the corpus. Once it can, the middle layers of that structure start to look different — and the repo above is only useful in the first place because of those changes.

- [The rise of the outcome engineer](https://www.outcomeops.ai/blogs/the-rise-of-the-outcome-engineer) — the emerging role
- [Engineers who own the outcome](https://www.outcomeops.ai/blogs/engineers-who-own-the-outcome) — the operating model
- [OutcomeOps and context engineering: the next corporate evolution beyond DevOps](https://www.outcomeops.ai/blogs/outcomeops-and-context-engineering-the-next-corporate-evolution-beyond-devops) — what comes after DevOps
- [Death of the traditional product owner](https://www.outcomeops.ai/blogs/death-of-the-traditional-product-owner) — the product-side role shift
- [Measuring what actually matters](https://www.outcomeops.ai/blogs/measurng-what-actually-matters) — the KPI shift

---

## Further reading

Foundational articles, reference guides, and practitioner writeups on context engineering as a discipline:

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (Anthropic, Sep 2025) — curating and limiting what an agent sees
- [The rise of context engineering](https://blog.langchain.com/the-rise-of-context-engineering/) (LangChain, Jun 2025) — the article that made the term widely used
- [Context engineering for agents](https://blog.langchain.com/context-engineering-for-agents/) (LangChain, Jul 2025) — write/select/compress/isolate framing
- [Context Engineering: Bringing Engineering Discipline to Prompts](https://addyo.substack.com/p/context-engineering-bringing-engineering) (Addy Osmani, Jul 2025) — engineering-discipline framing
- [Context Engineering Guide](https://www.promptingguide.ai/guides/context-engineering-guide) (PromptingGuide.ai) — reference entry
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) (Michael Nygard, 2011) — the original ADR essay; the format used throughout this repo
- [OutcomeOps and context engineering: the next corporate evolution beyond DevOps](https://www.outcomeops.ai/blogs/outcomeops-and-context-engineering-the-next-corporate-evolution-beyond-devops) (OutcomeOps) — the organizational thesis behind this repo
- [OutcomeOps: self-documenting architecture — when code becomes queryable](https://www.outcomeops.ai/blogs/outcomeops-self-documenting-architecture-when-code-becomes-queryable) (OutcomeOps) — how ADR corpora compound as code evolves
- [The real cost of knowledge: why most AI engineering platforms over-engineer RAG](https://www.outcomeops.ai/blogs/the-real-cost-of-knowledge-why-most-ai-engineering-platforms-over-engineer-rag) (OutcomeOps) — against premature retrieval infrastructure
- [What AI-assisted development actually looks like in two years](https://www.outcomeops.ai/blogs/what-ai-assisted-development-actually-looks-like-in-two-years) (OutcomeOps) — the working developer's view

## Companion repositories

- [bonigarcia/context-engineering](https://github.com/bonigarcia/context-engineering) — book companion from Boni García; organized by chapter with polyglot examples
- [davidkimai/Context-Engineering](https://github.com/davidkimai/Context-Engineering) — concepts, patterns, and techniques
- [Meirtz/Awesome-Context-Engineering](https://github.com/Meirtz/Awesome-Context-Engineering) — curated list of papers, tools, and articles
- [joelparkerhenderson/architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record) — the definitive ADR resource list

## Deep dives by component

Each folder's README has its own curated reading list; the quick index:

- **Corpus** — see [`01-corpus/`](./01-corpus#further-reading) — ADR formats, corpus bootstrapping, self-documenting architecture
- **Retrieval** — see [`02-retrieval/`](./02-retrieval#further-reading) — FAISS, "Lost in the Middle," retrieval economics
- **Injection** — see [`03-injection/`](./03-injection#further-reading) — prompt structure, token budgets, inference cost
- **Output** — see [`04-output/`](./04-output#further-reading) — JSON Schema, Bedrock tool-use, the outcome engineer
- **Enforcement** — see [`05-enforcement/`](./05-enforcement#further-reading) — LLM-as-judge research, PR-as-guardrail
- **Comparisons** — see [`comparisons/`](./comparisons#further-reading) — CE vs RAG vs agents vs enterprise search

---

## About

Built by Brian Carpio at [OutcomeOps](https://www.outcomeops.ai). Questions, corrections, or contributions welcome via issues and PRs.

## License

MIT — see [LICENSE](./LICENSE).
