# Decision records

We record significant decisions as short ADRs (Architecture Decision Records), so future us, and future Claude sessions, know *what* was decided and *why*.

## When to write one

When a choice is hard to reverse, affects many parts of the platform, or would make someone later ask "why did we do it this way?" Product decisions count, not just technical ones.

## How

1. Copy [template.md](template.md) to `NNNN-short-title.md`, using the next number.
2. Set the status to **Proposed** and fill it in.
3. When the owner accepts it, the status becomes **Accepted**.
4. Never delete or rewrite an accepted ADR. To change a decision, write a new ADR and mark the old one **Superseded by ADR-NNNN**.

## Index

| ADR | Title | Status |
|---|---|---|
| [0001](0001-record-decisions.md) | Record decisions as ADRs | Accepted |
| [0002](0002-mastery-and-gating.md) | Mastery definition and gating | Accepted |
| [0003](0003-ai-roles-and-guardrails.md) | AI roles and guardrails | Accepted |
| [0004](0004-content-model.md) | Content model | Accepted |
| [0005](0005-free-hosting-first.md) | Free hosting first | Accepted |
| [0006](0006-working-name.md) | "Switchback" is a working name | Accepted |
| [0007](0007-tech-stack.md) | Tech stack | Accepted |
| [0008](0008-event-log.md) | Learner data is an append-only event log | Accepted |
| [0009](0009-reviews.md) | Reviews are per topic and graded automatically | Accepted |
