# Case Study: MyFantasy.ai — AI Suggests, Humans Decide, the Database Records

> Engineer's-eye view of a consumer AI product where the trust boundary is the architecture. Full case study with metrics and business framing: [www.outcomeops.ai/case-studies/myfantasy-ai](https://www.outcomeops.ai/case-studies/myfantasy-ai).

**MyFantasy.ai** is fantasy sports for reality TV — scoring events extracted from episodes (lip syncs, eliminations, alliances, untucked drama) with point values driven by a commissioner-editable ruleset. Currently live in beta against *RuPaul's Drag Race All Stars*. 60 Lambda functions, 178 commits, 22 days from `git init` to beta.

The interesting engineering claim isn't the speed. It's that the trust model — *AI suggests, humans approve, the database records* — was a documented constraint before the first Lambda shipped. The architecture enforces the trust boundary; it doesn't politely request it.

---

## The trust model, made structural

Most "AI case studies" lead with user counts. This one leads with the boundary the system refuses to cross.

The wrong way to build fantasy scoring is to let an LLM write directly to the scoring table. The right way is to treat the model as a research assistant and treat the database as a court reporter. MyFantasy.ai is the right way:

```
                          ┌────────────────────────┐
  Episode transcript ───▶ │ Bedrock Haiku 4.5      │
                          │ (extract candidates)   │
                          └───────────┬────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │ Deterministic hashing  │
                          │ (idempotent dedup)     │
                          └───────────┬────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │ /admin/scoring/review/ │
                          │ Human approves edits   │
                          │ or rejects each event  │
                          └───────────┬────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │ DynamoDB SCORE# rows   │
                          │ Standings recompute    │
                          └────────────────────────┘
```

**Stage 1 — Extract.** Bedrock Haiku 4.5 reads episode transcripts and produces *candidate* scoring events. The output is a queue of suggestions, not a write to the scoring table.

**Stage 2 — Dedupe.** Each candidate is fingerprinted as `SHA256(event_type + first_quote)[:8]`. Duplicates from re-runs collapse to the same row. The model can hallucinate the same event twice; the index will not.

**Stage 3 — Review.** An admin opens `/admin/scoring/review/` and approves, edits, or rejects each candidate. Nothing is auto-scored. The model is a draftsman; the human is the editor.

**Stage 4 — Finalize.** Approved events become `SCORE#` rows in the single-table DynamoDB design. Standings recompute atomically. A weekly Sonnet 4.5 analyst run summarizes performance per league.

---

## Why this maps to the repo's five-component model

This is one of the cleanest mappings in the case-study set, because every component is visibly present.

| Component | What's happening here |
|---|---|
| **Corpus** | Episode transcripts + the commissioner-editable ruleset (frequency-bucketed: `once_per_season`, `once_per_partner`, `per_event`, `per_episode`) |
| **Retrieval** | The extraction Lambda fetches transcript + ruleset for the current show/season |
| **Injection** | Both land in the Haiku 4.5 context window alongside the extraction prompt |
| **Output** | Candidate events in a structured schema — never free-text decisions |
| **Enforcement** | (a) Deterministic event hashing kills duplicates structurally. (b) The admin review queue is the human-in-the-loop guardrail. (c) The ruleset frequency bucket is pre-computed into the dedup key so rules apply *before* the scoring math, not after. |

The enforcement layer is the headline. The model can be wrong; the system catches it before the database does.

---

## Why it shipped in 22 days

First commit: 2026-04-17. Beta live against All Stars: early May. Between those dates — 178 commits, 60 Lambda functions, 34 UI pages, a working AI scoring pipeline.

The speed is real, and the explanation is unromantic: a separate repository (`outcomeops-adrs`) holds the ADR library covering Terraform, Lambda, testing, secrets, CI/CD, frontend, and analytics. The OutcomeOps MCP server indexes them as a RAG and serves them on demand. When Claude Code writes a Lambda, it queries the MCP for handler patterns. When it writes Terraform, it queries for module versions. The full library never enters the context window — only what the current task touches.

**What Claude Code didn't have to invent:**

- Terraform module versions (ADR-001 pins `terraform-aws-modules/lambda/aws` at 8.1.2 — every one of the 60 Lambdas uses it)
- Lambda handler structure and auth pattern (ADR-004)
- Pytest layout and AWS-mock fixtures (ADR-003, ADR-012)
- Secrets handling (ADR-006)
- CI/CD workflow shape (ADR-007)
- React + Tailwind v4 conventions (ADR-005, ADR-010)
- AWS resource tagging (ADR-011)
- Decimal-over-float for money/math (ADR-009)

**What Claude Code *did* decide.** ADRs cover the patterns, not every choice. One example: every Lambda in this app runs on arm64 / Graviton — roughly 20% cheaper than x86 at identical performance. That call isn't in any ADR yet. Claude Code made it independently on the first Lambda and stayed consistent across the other 59. Good outcome, and a candidate for the next ADR — that's how the library compounds.

---

## Bedrock economics, measured not estimated

These numbers come from real All Stars episodes, with CloudWatch token counts logged at every call. Not a pricing-page calculator — the receipts.

| Metric | Value | Notes |
|---|---|---|
| Bedrock Haiku 4.5 candidate extraction | **$0.031 / episode** | Includes transcript context window + structured-output overhead |
| Bedrock Sonnet 4.5 analyst rollup | **$0.020 / league / week** | The weekly recap that summarizes which players scored what and why |

At current beta scale (one season of All Stars) the inference bill rounds to a coffee. The cost model holds linearly — adding the next show is a finance question, not a re-architecture question.

This is the practical answer to the cost critique in [The real cost of knowledge](https://www.outcomeops.ai/blogs/the-real-cost-of-knowledge-why-most-ai-engineering-platforms-over-engineer-rag) — when retrieval is properly scoped and the model is doing extraction rather than open-ended reasoning, the per-call cost is small enough to bury in line items.

---

## A few patterns worth lifting

These are the engineering decisions that did the real work; each one is a candidate to reuse in another product.

**Deterministic event hashing.** A model that's asked to extract events from the same transcript twice should produce the same row, not two. The 8-character SHA256 prefix of `event_type + first_quote` turns idempotency into a database constraint instead of a hope. The model can be re-run for free.

**Frequency-bucketed rulesets.** Some events score once per season (winning the show). Some score once per partner (forming an alliance with someone new). Some score every time (an argument). The ruleset encodes the frequency semantics — `once_per_season`, `once_per_partner`, `per_event`, `per_episode` — and the extraction handler pre-computes the dedup key so the rule applies *before* the scoring math. Frequency is data, not control flow.

**Commissioner-editable rulesets with a state machine.** Every show owner gets a deep-merge of the default ruleset with their own overrides — gated by an allowlist of editable fields and a state machine that restricts what can change mid-season. Once a season is active, only `lineup_size` and `late_lineup_penalty_multiplier` stay mutable. The rules are flexible; the boundaries aren't.

**Single-table DynamoDB.** One table per environment holds leagues, shows, events, scores, standings, sessions, and chat. Composite keys (`PK`/`SK`) and per-entity prefixes do the work that schemas usually do. No Redis. No DAX. No leaderboard cache. DynamoDB is fast enough, and the design stays legible.

---

## Further reading on outcomeops.ai

- **Canonical case study** — [AI-suggested, human-approved: building MyFantasy.ai at $0.031 per episode](https://www.outcomeops.ai/case-studies/myfantasy-ai)
- **All case studies** — [www.outcomeops.ai/case-studies](https://www.outcomeops.ai/case-studies)
- **The methodology** — [What is context engineering?](https://www.outcomeops.ai/context-engineering)
- **The cost framing** — [The real cost of knowledge: why most AI engineering platforms over-engineer RAG](https://www.outcomeops.ai/blogs/the-real-cost-of-knowledge-why-most-ai-engineering-platforms-over-engineer-rag)
- **Why ADRs are the unit of context** — [What is an ADR and why they're critical for AI-powered development](https://www.outcomeops.ai/blogs/what-is-an-adr-and-why-theyre-critical-for-ai-powered-development)
- **A model-choice angle** — [You're probably using the wrong Bedrock model](https://www.outcomeops.ai/blogs/youre-probably-using-the-wrong-bedrock-model)
