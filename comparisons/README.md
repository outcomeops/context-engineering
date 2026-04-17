# Comparisons

> How context engineering differs from adjacent categories of tooling — and where the runnable side-by-side demo lives.

The point of this folder is not to disparage adjacent tools. Each one solves a real problem. The point is to make the category boundaries concrete so teams can pick the right tool for the job instead of conflating them.

This folder is **documentation only.** The runnable side-by-side demo — the same question answered with and without injected context — lives in [`../03-injection/with_vs_without.py`](../03-injection/with_vs_without.py). That's where you go to *see* the difference.

---

## How context engineering differs from adjacent categories

| Category | Example tools | What it optimizes | What it misses |
|---|---|---|---|
| **AI coding assistants** | GitHub Copilot, Cursor | Inline code completion latency | No organizational context — suggestions match the current file, not the organization's decisions |
| **RAG frameworks** | LangChain, LlamaIndex | Developer ergonomics for retrieval | Leaves output structure and enforcement to the application developer |
| **Enterprise search** | Glean, Elastic | Human search over documents | Retrieves for humans to read, not for AI to reason over at decision time |
| **Autonomous agents** | Devin, OpenHands | End-to-end task completion | No enforcement that the completion respected organizational context |
| **Context engineering** | OutcomeOps, in-house platforms | Organization-specific, auditable AI output | Requires a corpus — organizations without documented decisions don't benefit |

Context engineering is not a replacement for any of these — it is the discipline that ties them into a governable system.

---

## CE vs RAG — the specific confusion worth clearing up

Most "is this RAG?" questions are really asking whether components 4 and 5 are present.

- **Components 1–3 alone** (corpus + retrieval + injection) = a RAG system. It retrieves relevant material and hands it to a model. Most LangChain and LlamaIndex starter projects stop here.
- **Components 1–5** (+ structured output + enforcement) = a context engineering system. The output is a schema-validated artifact and the artifact is checked against the corpus before it can merge.

A team can ship components 1–3 and call it done. They will have a chatbot that knows the ADRs. What they will not have is a way to tell, three months from now, whether the code that got merged last week actually respected those ADRs.

That second question is what [`../05-enforcement/`](../05-enforcement/) exists to answer. Until it has an answer, "we have RAG" and "we have context engineering" are indistinguishable from the outside — and that ambiguity is where half the bad AI-platform purchases happen.

---

## CE vs autonomous agents — different ends of a continuum

Autonomous coding agents (Devin, OpenHands, Claude Code in agentic modes) bias toward **completion** — give them a task, they attempt it end to end, minimal human in the loop.

Context engineering biases toward **accountability** — every generated artifact cites the organizational material it relied on, and a human review gate validates the citation before the artifact lands.

These can coexist. You can run an agent whose output goes through a context-engineering enforcement layer. In practice most teams do not, because agent frameworks optimize for fewer interruptions and CE optimizes for more of them. Picking the right default for a given workflow is the real question — see [_Two extremes, one missing middle_](https://www.outcomeops.ai/blogs/two-extremes-one-missing-middle) and [_Anthropic says: build skills, not agents_](https://www.outcomeops.ai/blogs/anthropic-says-build-skills-not-agents).

---

## See the demo

```bash
# From the repo root:
cd 01-corpus && python ingest_adrs.py ./sample-adrs && cd ..
cd 02-retrieval && python embed_corpus.py && cd ..
cd 02-retrieval && python query.py --json "Should I use Postgres locally or H2?" > ../03-injection/retrieved.json && cd ..
cd 03-injection && python with_vs_without.py \
  --retrieved retrieved.json \
  --question "Should I use Postgres locally or H2?"
```

The "without" answer is generically correct at best and confidently wrong at worst. The "with" answer cites ADR-002 and mirrors the team's actual decision. That gap — between the same model with and without the organization's corpus — is the entire value proposition.

---

## Further reading

- [Context engineering vs Nova Forge](https://www.outcomeops.ai/blogs/context-engineering-vs-nova-forge)
- [Anthropic says: build skills, not agents](https://www.outcomeops.ai/blogs/anthropic-says-build-skills-not-agents)
- [You're probably using the wrong Bedrock model](https://www.outcomeops.ai/blogs/youre-probably-using-the-wrong-bedrock-model)
- [Two extremes, one missing middle](https://www.outcomeops.ai/blogs/two-extremes-one-missing-middle)
- [OutcomeOps and context engineering: the next corporate evolution beyond DevOps](https://www.outcomeops.ai/blogs/outcomeops-and-context-engineering-the-next-corporate-evolution-beyond-devops)
- [The 75 billion offshore consulting industry dies](https://www.outcomeops.ai/blogs/the-75-billion-offshore-consulting-industry-dies)
