# ADR-002: Use H2 in-memory database in development, PostgreSQL in production

Status: Accepted
Date: 2026-01-12

## Context

The PetClinic application needs a relational database. Development, CI, and
production have materially different constraints:

- **Development** — contributors should be able to clone the repo and run the
  app with zero external dependencies. Requiring a local PostgreSQL install is
  a meaningful friction for occasional contributors.
- **CI** — test runs should be fast and deterministic; provisioning a database
  per job adds wall-clock time and flakiness.
- **Production** — durability, concurrent write performance, and ecosystem
  tooling (pgbouncer, logical replication, extensions) matter.

A single-database strategy would mean either running PostgreSQL everywhere
(burdening development) or running H2 everywhere (unacceptable in production).
Testcontainers was considered for CI but adds Docker-in-Docker complexity on
hosted runners.

## Decision

Spring profiles drive database selection:

- `default` profile uses H2 in-memory with `spring.jpa.hibernate.ddl-auto=create-drop`.
- `prod` profile uses PostgreSQL 16 with Flyway-managed migrations and
  `spring.jpa.hibernate.ddl-auto=validate`.

Entity definitions are written against the JPA subset that works on both
engines. Database-specific SQL lives in Flyway migrations under
`db/migration/postgres/` and is never executed against H2.

## Consequences

- **Easier:** new-contributor setup — `./mvnw spring-boot:run` works immediately.
- **Easier:** CI — no external services required for the unit and integration
  test suites.
- **Harder:** schema changes — every migration must be reviewed for
  PostgreSQL-specific syntax; developers who only run H2 locally may not
  catch issues that only surface in production.
- **Risk:** behavior divergence between H2 and PostgreSQL (e.g. case
  sensitivity, `CONCAT` semantics). Mitigated by a nightly CI job that runs
  the integration suite against a PostgreSQL container.
- **Constrains:** we cannot use PostgreSQL-only features (JSONB operators,
  array columns, partial indexes) in JPA-mapped entities without breaking the
  development workflow.
