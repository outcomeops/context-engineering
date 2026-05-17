# Example: Three ADRs Rewrote the Generated Code

> A reproducible A/B test for context engineering. Full writeup with screenshots and execution plans: [www.outcomeops.ai/blogs/how-3-adrs-changed-everything-spring-petclinic-proof](https://www.outcomeops.ai/blogs/how-3-adrs-changed-everything-spring-petclinic-proof).

This is the smoking-gun example for what context engineering does. Same model. Same prompt. Same codebase. The only delta is **three markdown files** in a `docs/adr/` directory. The output is a different architecture.

It runs against [Spring PetClinic](https://github.com/spring-projects/spring-petclinic) — the canonical Spring Boot reference app. 2,800+ stars. 43 contributors. 13 years of history. A codebase whose patterns are *implicit*: idiomatic to the maintainers, opaque to a generic LLM.

---

## The experiment

The same user story was implemented twice using the same AI coding workflow:

1. **First time** — no ADRs in the repo. The model sees the Spring PetClinic codebase and a feature request.
2. **Second time** — three ADRs added under `docs/adr/`. The repo was re-ingested. Same feature request.

Zero changes to the platform. Zero prompt engineering. Zero customization.

The branches are public:

- [Branch 12 — no ADRs](https://github.com/bcarpio/spring-petclinic/tree/12-cpe-12-add-pet-statistics-api-endpoint)
- [Branch 13 — with 3 ADRs](https://github.com/bcarpio/spring-petclinic/tree/13-cpe-13-add-pet-statistics-api-endpoint)
- [Full diff between them](https://github.com/bcarpio/spring-petclinic/compare/12-cpe-12-add-pet-statistics-api-endpoint...13-cpe-13-add-pet-statistics-api-endpoint)

---

## What changed in the output

### Branch 12 — no ADRs

Generic Spring Boot. Layers everywhere. DTOs. A service class. A custom exception. The kind of code every AI assistant produces by default, because it matches the median Spring Boot tutorial.

```
src/main/java/.../petclinic/
├── dto/
│   └── PetStatisticsDTO.java
├── service/
│   └── PetStatisticsService.java
├── controller/
│   └── PetStatisticsController.java
└── exception/
    └── StatisticsException.java
```

### Branch 13 — with 3 ADRs

Pure Spring PetClinic style. Domain packages. No service layer. Direct repository injection. The kind of code a Spring PetClinic maintainer would actually merge.

```
src/main/java/.../petclinic/
└── stats/
    ├── PetStatistics.java
    ├── PetStatisticsController.java
    └── PetStatisticsControllerTests.java
```

Same feature. One file *fewer*, in a single domain package, with the test class named `PetStatisticsControllerTests.java` (plural, matching the project convention) instead of being absent entirely.

---

## The three ADRs that did the work

Each ADR is one short markdown file under `docs/adr/`. The full text of each is a couple of paragraphs; the load-bearing rules are below.

### `ADR-003-controller-patterns.md`

```
Controllers follow domain packaging (owner/, vet/, visit/)
Use @Controller not @RestController
Inject repositories directly — no service layer
```

### `ADR-005-domain-models.md`

```
POJOs in domain packages, not DTOs
Return domain objects directly
JPA annotations on entities
```

### `ADR-006-testing-standards.md`

```
Test classes named *Tests.java (plural!)
Integration tests in same package
@SpringBootTest for controller tests
```

Three files. Roughly 200 words of content total. That's the entire delta between the two branches.

---

## The execution plans also changed

Before writing any code, the workflow generates an execution plan and writes it into the `issues/` directory on each branch. The plans diverge before a single line of Java is generated.

**Branch 12 plan (no ADRs):**

```
Step 1: Create DTO layer
Step 2: Create service layer
Step 3: Create controller with @RestController
Step 4: Create custom exception
```

**Branch 13 plan (with 3 ADRs):**

```
Step 1: Create domain POJO in stats package
Step 2: Create controller with @Controller
Step 3: Create integration tests (plural)
```

The architecture changed *before* the code did. That's the signature of a working context-engineering loop: the retrieval surface fed the model the relevant ADRs at planning time, and the planning artifact reflects them.

---

## What this maps to in the repo

This is the canonical example for the [`01-corpus/`](../01-corpus) → [`02-retrieval/`](../02-retrieval) → [`03-injection/`](../03-injection) flow this repo implements. Concretely:

| Component | What happened here |
|---|---|
| **Corpus** | Three markdown ADRs under `docs/adr/` |
| **Retrieval** | The "Pet statistics" feature request matched ADR-003, ADR-005, ADR-006 via semantic search |
| **Injection** | The three ADRs landed in the model's context window alongside the feature request |
| **Output** | A controller, an entity, a `*Tests.java` integration test — shaped by the ADRs, not by Spring Boot defaults |
| **Enforcement** | The execution plan diff is the audit trail — Branch 13's plan cites the patterns Branch 12's plan does not |

The repo's own running example uses the same Spring PetClinic codebase and the same ADR pattern; this experiment is the load-bearing demo of *why* the pattern matters.

---

## What to read after this

- **Full writeup with screenshots and execution-plan diffs** — [How 3 ADRs changed everything: the Spring PetClinic proof](https://www.outcomeops.ai/blogs/how-3-adrs-changed-everything-spring-petclinic-proof)
- **The unit of corpus** — [What is an ADR and why they're critical for AI-powered development](https://www.outcomeops.ai/blogs/what-is-an-adr-and-why-theyre-critical-for-ai-powered-development)
- **One Decimal ADR that stopped a recurring class of bug** — [The Decimal ADR: why Claude stopped making the same mistake](https://www.outcomeops.ai/blogs/the-decimal-adr-why-claude-stopped-making-the-same-mistake)
- **A longer worked example** — [How I refactored a 1,348-line Lambda using context engineering](https://www.outcomeops.ai/blogs/how-i-refactored-a-1348-line-lambda-using-context-engineering)
- **Why most teams don't have a queryable corpus yet** — [OutcomeOps: self-documenting architecture — when code becomes queryable](https://www.outcomeops.ai/blogs/outcomeops-self-documenting-architecture-when-code-becomes-queryable)
