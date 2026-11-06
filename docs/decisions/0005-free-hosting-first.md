# ADR-0005: Free hosting first

- **Status:** Accepted
- **Date:** 2026-11-05

## Context

The platform starts as the owner's personal learning tool and stays free for a while. The owner wants free hosting for as long as possible, and no custom domain until much later.

## Decision

- Use only free tiers for hosting, the database, CI and similar services, until that's no longer possible.
- No custom domain for now. The host's free subdomain is fine.
- Prefer designs that need almost no server compute: static hosting, learners' code running in their own browser, and offline ML training.
- **The one paid exception:** the Claude API for the AI features, with a monthly spending cap.

## Revisit when

- A free-tier limit is reached, or a provider changes its terms.
- Reliability starts to hurt, for example a free database pausing after a week without use.
- The platform goes commercial and needs plans that allow that.

## Consequences

- Architecture choices lean toward static frontends and managed free services (ADR-0007).
- Choose portable technology (standard Postgres, static files) so switching providers stays cheap.
