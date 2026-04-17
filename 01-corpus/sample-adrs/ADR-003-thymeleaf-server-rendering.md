# ADR-003: Use Thymeleaf for server-side rendering

Status: Accepted
Date: 2026-01-20

## Context

The PetClinic UI is a traditional CRUD interface — list, view, create, edit
pets, owners, visits, vets. Page transitions are infrequent and most views are
simple form-driven flows. The application does not require real-time updates,
offline capability, or complex client-side state.

Options considered:

- **Server-side rendering with Thymeleaf** — renders HTML on the JVM,
  integrates natively with Spring MVC form binding and validation.
- **Single-page app (React/Vue) backed by a REST API** — richer client
  experience but doubles the surface area: two build toolchains, two
  deployment artifacts, a separate state management story, and CORS.
- **htmx + server-rendered fragments** — modern middle ground but less
  familiar to the current team.

The user-facing complexity does not justify the operational complexity of an
SPA. CSRF, form validation errors, and accessibility are all easier on the
server.

## Decision

We use Thymeleaf 3 for all HTML rendering, with layout inheritance via
`spring-boot-starter-thymeleaf` and the Thymeleaf Layout Dialect. Form binding
uses Spring MVC's `@ModelAttribute` and `BindingResult`.

## Consequences

- **Easier:** form handling — validation errors, field binding, and CSRF
  protection are integrated end-to-end with no JavaScript plumbing.
- **Easier:** SEO and accessibility — HTML is complete on first response.
- **Easier:** deployment — one artifact, one process.
- **Harder:** building highly interactive features later — adding a dynamic
  widget means reaching for vanilla JS or introducing a client-side framework
  for that surface.
- **Constrains:** templates are tightly coupled to controller models;
  restructuring one often requires changing the other.
