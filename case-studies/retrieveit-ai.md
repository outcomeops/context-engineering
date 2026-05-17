# Case Study: RetrieveIT.ai — A Multi-Tenant SaaS in 6 Days

> Engineer's-eye view of a multi-tenant semantic-search SaaS built end-to-end in six days. Full case study with metrics and business framing: [www.outcomeops.ai/case-studies/retrieveit-ai](https://www.outcomeops.ai/case-studies/retrieveit-ai).

**RetrieveIT.ai** is a multi-tenant semantic-search platform — connect your Google Drive, GitHub repos, or Gmail, then ask questions in plain English and get synthesized answers with citations. Domain registered on 2024-12-31. Launched 2025-01-06. First paying customers on day 7.

The interesting engineering claim isn't "we shipped fast." It's that the patterns that made every architectural decision a five-minute choice instead of a five-hour debate were already in the corpus. The ADR library is the product behind the product.

---

## The timeline

| Day | Output |
|---|---|
| 1 | Domain + passwordless magic-link auth working by midnight |
| 2–3 | Semantic search on Bedrock, multi-tenant workspaces, conversation memory |
| 4–5 | Google Drive / GitHub / Gmail OAuth, Stripe subscriptions, automated tests, GitHub Actions CI/CD |
| 6 | Marketing site, production deploy via CI/CD, first signups within hours |

Zero architecture meetings. Zero discovery phases. Zero months of planning. Not because corners were cut — because the corners were already drawn.

---

## Why this matters to a context-engineering audience

The case study is interesting at two levels:

1. **The product is itself a context-engineering tool.** RetrieveIT.ai is "ask, don't search" — semantic retrieval over a customer's documents, with citations. It's an exemplar of components 1–3 of the model this repo describes (corpus, retrieval, injection), packaged as a consumer SaaS.

2. **The product was *built* using context engineering.** Every load-bearing decision — multi-tenant isolation, OAuth encryption, fail-closed billing, the serverless boundary — was an ADR lookup, not a design exercise. The pattern library compounds across products; nothing on RetrieveIT had to be invented from scratch.

---

## Feature 1: Multi-tenant isolation as a property of the system

The hardest thing about a multi-tenant SaaS is making it provably impossible for one tenant's data to leak into another's. RetrieveIT.ai handles this by encoding tenant ID into every key — DynamoDB partition keys, S3 object prefixes, OpenSearch index names. There is no code path that fetches data without a tenant scope; the absence of a tenant ID is a hard error, not a default.

**Why this maps to the repo's five-component model.** The corpus the model retrieves from is partitioned at the storage layer, not at the prompt layer. Component 2 (retrieval) cannot return another tenant's data because component 1 (corpus) makes that retrieval syntactically impossible. The enforcement is structural, not aspirational.

---

## Feature 2: OAuth integrations on day 4 because the integration shape is solved

Three OAuth providers in a single day: Google Drive, GitHub, Gmail. Every connector follows the same three-Lambda shape — call it the *integration trio*:

```
oauth-handler      → handshake, encrypted token storage, refresh
file-enumerator    → list files for a workspace, dispatch into the ingestion queue
file-ingestion     → per-source processor inside the shared ingestion Lambda
```

The fourth piece — audit writing — is plumbed through automatically via the shared `audit_writer`. Adding a new connector is effectively a port: copy the shape, swap the API client, register a new `source=` string.

The same pattern shipped two new connectors (OneDrive + OneNote) in a single day on the [OutcomeOps AI Assist platform](./outcomeops-ai-assist.md). The compounding is the point — the sixteenth RetrieveIT connector cost less than the first.

**OAuth tokens are encrypted at rest with KMS.** This isn't a feature added later when InfoSec asked. It's a property of the `oauth-handler` template every connector inherits.

---

## Feature 3: Fail-closed billing as the enforcement layer

If Stripe fails, queries stop. No "free tier by accident." The boundary between paid and unpaid is enforced at the request path, not at a nightly batch reconciler. A billing failure is a 402, not a free quarter of usage that the company eats.

**Why this maps to the repo's five-component model.** This is component 5 — enforcement — applied to revenue protection rather than to output quality. The system reflects the policy ("only paying tenants run inference") at the point of execution, not as an after-the-fact audit. Same pattern as "alert exactly once per workspace per month" on the AI Assist case study: the conditional check is in the path, not in a downstream job.

---

## What was already documented before any of this was coded

The 6-day timeline is a function of what *didn't* need a decision. From the inherited ADR library, every one of these was a lookup:

- Terraform module versions (every Lambda uses `terraform-aws-modules/lambda/aws`, pinned)
- Lambda handler structure and auth pattern
- Pytest layout + autouse AWS mocks so missing fixtures can't leak to billable AWS calls
- Secrets management
- CI/CD workflow shape (GitHub Actions, dev applies automated, prod gated)
- React + Tailwind frontend conventions
- AWS resource tagging
- Decimal-over-float for money math

The model was never asked to invent infrastructure patterns. It was asked to execute the next milestone using patterns that were already approved.

---

## The methodology, in one paragraph

Six days for a production multi-tenant SaaS isn't a stunt — it's the natural cadence when nothing on the critical path is a research question. The corpus had the answers; the AI looked them up. That's context engineering applied to product development itself: the same five-component pattern this repo documents, used to ship the company *and* the product. The pattern library compounded across RetrieveIT.ai, [OutcomeOps AI Assist](./outcomeops-ai-assist.md), and [MyFantasy.ai](./myfantasy-ai.md) — three products, one library, declining marginal cost per feature.

---

## Further reading on outcomeops.ai

- **Canonical case study** — [How we built RetrieveIT.ai: from domain to launch in 6 days](https://www.outcomeops.ai/case-studies/retrieveit-ai)
- **The OAuth platform deep dive** — [RetrieveIT.ai OAuth platform](https://www.outcomeops.ai/case-studies/retrieveit-ai-oauth-platform)
- **All case studies** — [www.outcomeops.ai/case-studies](https://www.outcomeops.ai/case-studies)
- **The methodology** — [What is context engineering?](https://www.outcomeops.ai/context-engineering)
- **Why ADRs are the unit of context** — [What is an ADR and why they're critical for AI-powered development](https://www.outcomeops.ai/blogs/what-is-an-adr-and-why-theyre-critical-for-ai-powered-development)
- **The cost framing** — [The real cost of knowledge: why most AI engineering platforms over-engineer RAG](https://www.outcomeops.ai/blogs/the-real-cost-of-knowledge-why-most-ai-engineering-platforms-over-engineer-rag)
