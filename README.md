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
- AWS account with Bedrock access in a region where Claude is available (e.g. `us-east-1`)
- Claude model access enabled via the Bedrock console
- Python 3.11+
- AWS credentials configured (`aws configure` or env vars)

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

## Further reading

### From the broader community

Foundational and high-signal sources on context engineering as a discipline:

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic engineering, on curating and limiting what an agent sees
- [The rise of context engineering](https://blog.langchain.com/the-rise-of-context-engineering/) — LangChain, the article that gave the term widespread uptake
- [Context engineering for agents](https://blog.langchain.com/context-engineering-for-agents/) — LangChain, the write/select/compress/isolate framing
- [Context Engineering: Bringing Engineering Discipline to Prompts](https://addyo.substack.com/p/context-engineering-bringing-engineering) — Addy Osmani
- [Context Engineering Guide](https://www.promptingguide.ai/guides/context-engineering-guide) — PromptingGuide.ai reference
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) — Michael Nygard's original ADR essay (the format used throughout this repo)

### Companion repositories

- [bonigarcia/context-engineering](https://github.com/bonigarcia/context-engineering) — book companion from Boni García; organized by chapter with polyglot examples
- [davidkimai/Context-Engineering](https://github.com/davidkimai/Context-Engineering) — concepts, patterns, and techniques
- [Meirtz/Awesome-Context-Engineering](https://github.com/Meirtz/Awesome-Context-Engineering) — curated list of papers, tools, and articles
- [joelparkerhenderson/architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record) — the definitive ADR resource list

### From outcomeops.ai



**Corpus**
- [What is an ADR and why they're critical for AI-powered development](https://www.outcomeops.ai/blogs/what-is-an-adr-and-why-theyre-critical-for-ai-powered-development)
- [AI-generated ADRs: from zero documentation to queryable architecture](https://www.outcomeops.ai/blogs/ai-generated-adrs-from-zero-documentation-to-queryable-architecture)
- [How 3 ADRs changed everything: Spring PetClinic proof](https://www.outcomeops.ai/blogs/how-3-adrs-changed-everything-spring-petclinic-proof)
- [Making legacy SAP codebases queryable: ADR generation from ABAP](https://www.outcomeops.ai/blogs/making-legacy-sap-codebases-queryable-adr-generation-from-abap)

**Retrieval**
- [The real cost of knowledge: why most AI engineering platforms over-engineer RAG](https://www.outcomeops.ai/blogs/the-real-cost-of-knowledge-why-most-ai-engineering-platforms-over-engineer-rag)
- [OutcomeOps: self-documenting architecture — when code becomes queryable](https://www.outcomeops.ai/blogs/outcomeops-self-documenting-architecture-when-code-becomes-queryable)

**Injection**
- [How I refactored a 1348-line Lambda using context engineering](https://www.outcomeops.ai/blogs/how-i-refactored-a-1348-line-lambda-using-context-engineering)
- [Same context, three models — the floor isn't zero](https://www.outcomeops.ai/blogs/same-context-three-models-the-floor-isnt-zero)
- [6.6M tokens, $4,800, zero visibility — so I built a dashboard](https://www.outcomeops.ai/blogs/6-6m-tokens-4800-zero-visibility-so-i-built-a-dashboard)

**Output**
- [The outcome is writing itself](https://www.outcomeops.ai/blogs/the-outcome-is-writing-itself)
- [The OutcomeOps way: stop prompting, start co-engineering](https://www.outcomeops.ai/blogs/the-outcomeops-way-stop-prompting-start-co-engineering)

**Enforcement**
- [Your pull request is the guardrail](https://www.outcomeops.ai/blogs/your-pull-request-is-the-guardrail)
- [Engineers who own the outcome](https://www.outcomeops.ai/blogs/engineers-who-own-the-outcome)
- [From fixing code to teaching systems](https://www.outcomeops.ai/blogs/from-fixing-code-to-teaching-systems)

**Comparisons & positioning**
- [Context engineering vs Nova Forge](https://www.outcomeops.ai/blogs/context-engineering-vs-nova-forge)
- [Anthropic says: build skills, not agents](https://www.outcomeops.ai/blogs/anthropic-says-build-skills-not-agents)
- [You're probably using the wrong Bedrock model](https://www.outcomeops.ai/blogs/youre-probably-using-the-wrong-bedrock-model)
- [OutcomeOps and context engineering: the next corporate evolution beyond DevOps](https://www.outcomeops.ai/blogs/outcomeops-and-context-engineering-the-next-corporate-evolution-beyond-devops)

---

## About

Built by Brian Carpio at [OutcomeOps](https://www.outcomeops.ai). Questions, corrections, or contributions welcome via issues and PRs.

## License

MIT — see [LICENSE](./LICENSE).
