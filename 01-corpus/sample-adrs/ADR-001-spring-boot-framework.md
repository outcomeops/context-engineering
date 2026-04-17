# ADR-001: Use Spring Boot as the application framework

Status: Accepted
Date: 2026-01-08

## Context

The PetClinic application needs a JVM-based web framework that supports embedded
HTTP serving, dependency injection, production observability (metrics, health
checks), and a large ecosystem of starters for common concerns (persistence,
security, validation).

Candidates considered were Spring Boot, Micronaut, Quarkus, and plain Servlet
with hand-rolled DI. The team has ten years of collective Spring experience and
the target deployment environment (Tomcat-backed EC2 and, eventually, ECS
Fargate) is well-documented with Spring Boot. Micronaut and Quarkus offer
faster startup and lower memory, but neither advantage is material for a
long-running web application.

## Decision

We use Spring Boot 3.x as the application framework, with `spring-boot-starter-web`,
`spring-boot-starter-data-jpa`, `spring-boot-starter-thymeleaf`, and
`spring-boot-starter-actuator` as the baseline set of starters.

## Consequences

- **Easier:** hiring — Spring is the default JVM web framework; onboarding is fast.
- **Easier:** operations — Actuator endpoints give us `/health`, `/metrics`, and
  `/info` for free, compatible with our existing Prometheus scrape config.
- **Easier:** testing — `@SpringBootTest` and `MockMvc` are well-understood.
- **Harder:** cold-start time — a Spring Boot application takes 3–5 seconds to
  start. This rules out Lambda-style packaging for this service.
- **Constrains:** future decisions about persistence, security, and
  server-side rendering default to the Spring ecosystem (see ADR-002, ADR-003).
