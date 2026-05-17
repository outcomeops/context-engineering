# Case Study: OutcomeOps AI Assist — Governance Without the Drag

> Engineer's-eye view of an enterprise context-engineered platform. Full case study with metrics and business framing: [www.outcomeops.ai/case-studies/outcomeops-ai-assist](https://www.outcomeops.ai/case-studies/outcomeops-ai-assist).

**OutcomeOps AI Assist** is an enterprise RAG + agent platform that runs inside the customer's own AWS account. Six months of compounding development, 296 commits, 48 Lambda functions. The interesting thing for a context-engineering audience is not the headline numbers — it's that every new feature lands in days, not weeks, because the patterns are already in the corpus.

This page walks through three recent features and the engineering decisions behind them. Each one is the kind of thing a buyer's finance, security, or platform team asks for and never gets in a vendor SaaS.

---

## Why an engineer should care

Most enterprise RAG demos handle the happy path: ingest some docs, embed them, ask a question, get an answer with citations. Then the buyer's finance team asks "what stops a runaway workspace from burning $40K of Bedrock tokens this month?" and the buyer's InfoSec team asks "how does this appear in our SIEM?" and the demo stops being a demo.

The three features below are answers to those questions, built using the same five-component context-engineering pattern this repo documents. Each one is short enough to read end-to-end, and each one was shipped in days because the relevant ADRs already existed in the corpus.

---

## Feature 1: Per-workspace budget caps (shipped in 2 days)

**The requirement.** Org admins set a monthly cost cap on each workspace. The cap covers everything that touches a billing line — embedding calls, retrieval, generation tokens, rerank passes. The UI shows month-to-date spend per workspace and the cap next to it. When MTD crosses a threshold, an alert fires. Once. Per workspace. Per month.

**The shape of the implementation.**

- **Daily threshold check** — an EventBridge cron fires `analytics-cost-alert` once a day. The Lambda reads MTD spend from the analytics aggregates table and compares it against each workspace's budget. No streaming, no polling. The alert is a CFO conversation, not a kill switch — one check a day is enough.
- **Exactly-once alerts via conditional writes** — alert de-dup is a DynamoDB row keyed `PK=ALERT, SK=MTD#{YYYY-MM}#WS#{id}`. The conditional write fails if the alert already fired this month. The Lambda can run a hundred times; the SNS notification leaves the platform once.
- **Per-call cost rows + nightly aggregator** — every Bedrock invocation logs `tokens-in`, `tokens-out`, model, and computed cost via a shared recorder. `analytics-aggregator` rolls raw rows into MTD totals per workspace, so read-time queries are O(1) lookups, not table scans.

**Why this maps to the repo's five-component model.**

| Component | What's happening here |
|---|---|
| Corpus | ADR-009 (Decimal-over-float for money), ADR for analytics table layout |
| Retrieval | Aggregates table is the retrieval surface for "what did this workspace spend?" |
| Injection | The Lambda reads MTD + cap into its working memory before deciding to alert |
| Output | An SNS message, generated from a structured event, not free-text |
| Enforcement | The conditional DynamoDB write is the guardrail — it makes "alert once" a property of the system, not a property of the prompt |

---

## Feature 2: OCSF audit stream + SIEM export (shipped in 5 days)

**The requirement.** Every privileged action — workspace creation, membership change, system-prompt edit, integration connect/disconnect, chat refusal — writes an audit row. The UI shows the last N days with filters for critical actions and refusals, a date-range picker, and CSV/JSON export. That's the table-stakes layer. The differentiated layer is what happens after the row lands.

**The shape of the implementation.**

A DynamoDB Streams consumer (`audit-stream-publisher`) re-emits every audit `INSERT` as an [OCSF v1.3.0](https://schema.ocsf.io/) envelope into a Kinesis Data Stream. Customers point their own consumer at that stream — Splunk, Datadog, Sumo Logic, AWS Security Lake, or a Firehose into S3 — and filter on consumption.

Every row gets a proper `category_uid` / `class_uid` / `activity_id` / `severity_id`. Actor and `src_endpoint` structures populate from `user_email` / `source_ip` / `user_agent`. The raw payload is preserved under `unmapped`.

**Why OCSF specifically.** OCSF is the open security event format Splunk, AWS, Cisco, IBM, and CrowdStrike co-author. Emitting it natively means the buyer's analysts don't parse our logs — they query the events from the same dashboards they use for everything else.

**The split: we publish, they filter.** The stream carries every event. Customer-side `FilterCriteria` on the consumer event source mapping decides what reaches their SIEM. The platform never has to ship a feature for "export only logins between 2am and 4am" — the SIEM already does that.

**Why this is a context-engineering pattern, not a logging pattern.** The audit row is the *output* of an action that the platform took. OCSF is the schema the *enforcement* layer compels that output into. The buyer's SIEM is the *retrieval* surface their analysts use to ask "did this user do that thing?" Audit becomes a first-class artifact in the same five-component frame as the rest of the system.

---

## Feature 3: Two new integrations in a single day

**The requirement.** On 2026-05-11, OneDrive shipped to production and OneNote landed in the same release. Ten commits between the two, all on the same day.

**Why it was a one-day job.** Every connector follows the same three-Lambda shape — call it the *integration trio*:

```
oauth-handler      → handshake, token storage, refresh
file-enumerator    → list files for a workspace, dispatch into the ingestion queue
file-ingestion     → per-source processor inside the shared ingestion Lambda
```

The fourth piece — audit writing — is plumbed through automatically via the shared `audit_writer`. Adding OneNote was effectively a port: copy the OneDrive shape, swap the API client, register the new `source=` string, add an orphan-cleanup pass so deletes propagate from OneNote into the index.

**What "shipped" actually included for OneDrive that day:**

- Integration trio Lambda + `audit_writer` plumbing
- Terraform: Lambda trio + SQS + EventBridge cron
- 75 new unit tests for the trio
- `file-ingestion` dispatch updated for `source=onedrive`
- Orphan cleanup on every sync to propagate deletes from OneDrive into the index

**The compounding effect.** The pattern isn't a happy accident. It came from the same ADR library Claude Code queries on every product. The sixteenth RetrieveIT connector cost less than the first. The eighth OutcomeOps connector cost less than the seventh. This is what "the corpus compounds" means in practice: each new integration is mostly a copy of the previous one, with the deltas isolated to a thin per-source processor.

---

## The methodology, in one paragraph

The ADRs that mandate `terraform-aws-modules/lambda/aws v8.1.2` built every one of these 48 Lambda functions. The pytest layout from ADR-003 + autouse AWS mocks from ADR-012 made the 75 OneDrive tests cheap to write. The Decimal-over-float discipline from ADR-009 kept the cost analytics honest down to the fraction of a cent. The OutcomeOps MCP server is how Claude Code reads it. Every product we ship — and every product we sell — runs on the same loop.

---

## Further reading on outcomeops.ai

- **Canonical case study** — [OutcomeOps AI Assist: workspace budgets, OCSF audit, and two integrations in a day](https://www.outcomeops.ai/case-studies/outcomeops-ai-assist)
- **All case studies** — [www.outcomeops.ai/case-studies](https://www.outcomeops.ai/case-studies)
- **The methodology** — [What is context engineering?](https://www.outcomeops.ai/context-engineering)
- **The corporate evolution thesis** — [OutcomeOps and context engineering: the next corporate evolution beyond DevOps](https://www.outcomeops.ai/blogs/outcomeops-and-context-engineering-the-next-corporate-evolution-beyond-devops)
- **Why ADRs are the unit of context** — [What is an ADR and why they're critical for AI-powered development](https://www.outcomeops.ai/blogs/what-is-an-adr-and-why-theyre-critical-for-ai-powered-development)
- **Why the corpus compounds** — [OutcomeOps: self-documenting architecture — when code becomes queryable](https://www.outcomeops.ai/blogs/outcomeops-self-documenting-architecture-when-code-becomes-queryable)
