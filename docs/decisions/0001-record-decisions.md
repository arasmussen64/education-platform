# ADR-0001: Record decisions as ADRs

- **Status:** Accepted
- **Date:** 2026-11-05

## Context

This project is built by a learner working with AI assistants across many sessions. Without a written record, the reasons behind decisions get lost, and each new session, human or AI, risks re-arguing settled questions or quietly breaking them.

## Decision

Record significant product and technical decisions as short ADRs in `docs/decisions/`, following the process in [README.md](README.md). Accepted ADRs are never rewritten; newer ADRs supersede them.

## Consequences

- A small amount of writing for each big decision.
- Claude Code reads `CLAUDE.md`, which points here, so decisions carry across sessions.
- The ADR log doubles as a record of how the project's thinking evolved.
