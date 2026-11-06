# ADR-0002: Mastery definition and gating

- **Status:** Accepted
- **Date:** 2026-11-05

## Context

The platform's core promise is that learners can *apply* what they learn, not just recognize it, and that they keep it. Self-reported progress (roadmap.sh's checkboxes) and one-time quizzes show neither. The owner chose the strictest option: all four kinds of proof.

## Decision

### Proof required

1. **Blank-editor challenge:** build something from only a spec and hidden tests. No scaffolding, no AI.
2. **Explain it back:** explain the concept in your own words; AI checks it for gaps and misconceptions against a rubric.
3. **Debug unfamiliar code:** find and fix bugs in code you didn't write that uses the concept.
4. **Survives spaced review:** still correct on a review at least about a week later.

Small topics get quick versions (for example, a short function, a two-sentence explanation, a one-line bug). Each module ends with full-size versions of all four.

### Topic states

- **Locked:** prerequisites not yet Learned. Previewing is allowed but earns nothing.
- **Available:** ready to start.
- **Learned:** passed checks 1–3.
- **Mastered:** Learned, and passed a review at least ~7 days later.
- **Fading:** a review is due, and the map shows the topic fading. Passing the review returns it to Mastered. Failing it schedules relearning and lowers the topic's strength.

### Gating

A topic unlocks when all its prerequisites are **Learned**. Requiring Mastered would force a week's wait between levels. If a prerequisite later fails a review, the topics that depend on it stay unlocked, but the system prioritizes fixing the prerequisite.

### Test-out

The placement test and a "prove it now" option let learners skip lessons for topics they can already prove. They take the same checks.

## Alternatives considered

- **Suggested path with free jumping:** more freedom, but learners would build on gaps.
- **Free-roam map (like roadmap.sh):** nothing locked and no warnings. It defeats the core promise.

## Consequences

- Progress looks slower than on platforms that count watched videos, but it's real.
- Every topic needs machine-verifiable exercises (ADR-0004) and AI grading for explanations (ADR-0003).
- Mastery must never come from self-report. Any shortcut needs a new ADR.
