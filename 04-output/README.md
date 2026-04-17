# 04 — Output

> What the AI produces, shaped by the retrieved context. In enterprise software development, this is usually code, documentation, or a pull request.

Most AI tooling stops at "the model returned some text." Context engineering treats the output as an artifact to be structured, validated, and audited — not a conversation turn. The output layer is what separates a chat assistant from infrastructure.

This folder contains:

1. **`schema.py`** — JSON schema for a structured PR description. Single source of truth: used to constrain Claude's output *and* to validate it downstream in enforcement.

2. **`generate_pr_description.py`** — takes a diff plus the retrieved ADRs, calls Bedrock with a tool-use spec that forces the output into the schema, validates the result, and renders Markdown suitable for pasting into a pull request.

---

## Run it

```bash
pip install -r requirements.txt

# 1. Produce a diff (any real diff; for demo, stage a change and diff it)
git diff HEAD > diff.patch

# 2. Retrieve the ADRs most relevant to the diff
cd ../02-retrieval
python query.py --json "$(cat ../04-output/diff.patch)" > ../04-output/retrieved.json
cd ../04-output

# 3. Generate the structured PR description
python generate_pr_description.py \
  --retrieved retrieved.json \
  --diff-file diff.patch \
  --out pr.json

# 4. Render as Markdown
python generate_pr_description.py --render pr.json
```

The structured output looks like:

```json
{
  "summary": "Switch the development profile from H2 to a Testcontainers-backed PostgreSQL instance.",
  "motivation": "ADR-002 uses H2 in development to keep new-contributor setup frictionless, but drift between H2 and production PostgreSQL has caused three migration failures this quarter. This PR moves dev to Testcontainers, accepting the setup cost called out as a consequence in ADR-002.",
  "cited_adrs": [
    {
      "adr_id": "ADR-002",
      "relationship": "overrides",
      "note": "Overrides the H2-in-dev decision. Risk of behavior divergence (explicitly called out in ADR-002 consequences) has materialized."
    }
  ],
  "files_changed": ["pom.xml", "src/test/resources/application-dev.properties"],
  "risks": ["Contributors need Docker running locally — not previously required."],
  "test_plan": ["./mvnw verify -Pdev"]
}
```

---

## Why structured output matters

A model that returns free-form Markdown gives you no automation handles. A model that returns schema-validated JSON gives you:

- **CI enforcement** — a downstream job can check that `cited_adrs` is non-empty and that every id exists in the corpus.
- **Reviewer handoff** — the `cited_adrs` block tells the reviewer which ADRs to re-read before approving.
- **Corpus growth** — the structured output can itself be indexed, so the rationale for this PR becomes retrievable context for the next one.

This is the loop that makes a context engineering system compound. The outputs of today's decisions become the corpus for tomorrow's — the pattern described in [_OutcomeOps: self-documenting architecture — when code becomes queryable_](https://www.outcomeops.ai/blogs/outcomeops-self-documenting-architecture-when-code-becomes-queryable).

---

## Tool-use vs freeform with JSON instructions

Two ways to get structured JSON out of Claude:

1. **Prompt for JSON** — ask in the system prompt, hope for valid output, re-prompt on parse errors.
2. **Tool-use** — declare a tool with a JSON schema, force Claude to call it via `toolChoice`. Bedrock validates the arguments against the schema before returning.

This codebase uses option 2. The failure mode of option 1 — Claude returning near-JSON with a stray markdown fence or trailing comma — doesn't happen with tool-use. The cost is one extra concept in the prompt and the requirement to read the tool-use block from the response instead of the text block.

---

## What the schema enforces vs what it doesn't

The schema enforces *shape*: the fields exist, types are right, ADR ids match the `ADR-\d+` pattern, the ADR list is non-empty.

The schema does not enforce *truth*: Claude can still cite an ADR that is irrelevant, or claim `relationship: "respects"` for a diff that flagrantly violates the ADR.

That second layer is the job of [`../05-enforcement/`](../05-enforcement/).

---

## Further reading

- [JSON Schema](https://json-schema.org/) — the schema vocabulary used by `schema.py`
- [Amazon Bedrock user guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html) — Converse API and tool-use reference material
- [The outcome is writing itself](https://www.outcomeops.ai/blogs/the-outcome-is-writing-itself) (OutcomeOps) — generated artifacts as first-class outputs
- [The OutcomeOps way: stop prompting, start co-engineering](https://www.outcomeops.ai/blogs/the-outcomeops-way-stop-prompting-start-co-engineering) (OutcomeOps) — the structured-output mindset
- [What AI-assisted development actually looks like in two years](https://www.outcomeops.ai/blogs/what-ai-assisted-development-actually-looks-like-in-two-years) (OutcomeOps) — how the developer role shifts around structured outputs
- [The rise of the outcome engineer](https://www.outcomeops.ai/blogs/the-rise-of-the-outcome-engineer) (OutcomeOps) — who is producing these outputs
- [OutcomeOps: self-documenting architecture — when code becomes queryable](https://www.outcomeops.ai/blogs/outcomeops-self-documenting-architecture-when-code-becomes-queryable) (OutcomeOps) — today's outputs become tomorrow's corpus

Previous: [`../03-injection/`](../03-injection/) — how context got into the model.
Next: [`../05-enforcement/`](../05-enforcement/) — how we verify the output actually used it.
