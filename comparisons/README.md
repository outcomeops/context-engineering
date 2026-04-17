# Comparisons

> Side-by-side demonstrations: the same task with and without context engineering, and how context engineering differs from adjacent categories.

The point of this folder is not to disparage adjacent tools — each solves a real problem. The point is to make the category boundaries concrete, so teams can pick the right tool for the job instead of conflating them.

The examples in this folder will show:

- **`same_task_both_ways.py`** — the same refactor request answered with a generic Copilot-style prompt vs. a context-engineered prompt that injects the relevant ADRs. Diffs the outputs and scores each against the ADRs.
- **`vs_rag/`** — a minimal RAG system (retrieve + inject) compared against the full CE pipeline (retrieve + inject + structured output + enforcement). Shows where RAG stops and CE continues.
- **`vs_agents/`** — a task given to an autonomous coding agent vs. the same task given to a context-engineered pipeline with explicit human review gates. Shows the accountability difference.

**Status:** coming next.

---

## How context engineering differs from adjacent categories

| Category | Example tools | What it optimizes | What it misses |
|---|---|---|---|
| **AI coding assistants** | GitHub Copilot, Cursor | Inline code completion latency | No organizational context — suggestions match the current file, not the organization's decisions |
| **RAG frameworks** | LangChain, LlamaIndex | Developer ergonomics for retrieval | Leaves output structure and enforcement to the application developer |
| **Enterprise search** | Glean, Elastic | Human search over documents | Retrieves for humans to read, not for AI to reason over at decision time |
| **Autonomous agents** | Devin, OpenHands | End-to-end task completion | No enforcement that the completion respected organizational context |
| **Context engineering** | OutcomeOps, in-house platforms | Organization-specific, auditable AI output | Requires a corpus (organizations without documented decisions don't benefit) |

Context engineering is not a replacement for any of these — it is the discipline that ties them into a governable system.

---

## Further reading

- [Context engineering vs Nova Forge](https://www.outcomeops.ai/blogs/context-engineering-vs-nova-forge)
- [Anthropic says: build skills, not agents](https://www.outcomeops.ai/blogs/anthropic-says-build-skills-not-agents)
- [You're probably using the wrong Bedrock model](https://www.outcomeops.ai/blogs/youre-probably-using-the-wrong-bedrock-model)
- [Two extremes, one missing middle](https://www.outcomeops.ai/blogs/two-extremes-one-missing-middle)
- [OutcomeOps and context engineering: the next corporate evolution beyond DevOps](https://www.outcomeops.ai/blogs/outcomeops-and-context-engineering-the-next-corporate-evolution-beyond-devops)
- [The 75 billion offshore consulting industry dies](https://www.outcomeops.ai/blogs/the-75-billion-offshore-consulting-industry-dies)
