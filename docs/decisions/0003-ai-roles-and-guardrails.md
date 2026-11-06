# ADR-0003: AI roles and guardrails

- **Status:** Accepted
- **Date:** 2026-11-05

## Context

AI can be a great tutor, or it can quietly do the learning for you. In a large field study, unrestricted answer-giving AI raised students' practice scores but lowered their later exam scores, while a tutor version with guardrails largely avoided that harm (Bastani et al., 2025). The owner chose four AI roles.

## Decision

1. **Socratic tutor.** Gives hints one step at a time and asks guiding questions. Never hands over a full solution. Switched off during "prove it" checks.
2. **Senior-engineer reviewer.** Once code passes its tests, reviews it like a mentor would: design, readability, edge cases. Also grades explain-it-back answers against a rubric.
3. **Practice generator.** Creates fresh variations of problems and projects. Nothing reaches a learner until it passes automatic verification (ADR-0004).
4. **AI-assisted coding track, "earn the AI".** Teaches how to direct and check AI coding tools. For each skill, it unlocks only after the learner has proven that skill *without* AI.

### Guardrails in the implementation

- All AI calls go through a server-side proxy. The API key never reaches the browser.
- The proxy applies each role's rules (system prompts) and enforces a monthly spending cap.
- AI features fail gracefully. If AI is unavailable or over budget, learning continues without it.
- AI interactions are logged (append-only) so tutor quality can be reviewed and improved.

## Alternatives considered

- **No AI:** cheaper and simpler, but it gives up personal tutoring, which is one of the most effective forms of teaching there is.
- **Unrestricted AI help:** what most learners already have. It's the source of the "can't build without AI" problem this platform exists to fix.

## Consequences

- Needs the Claude API, the one paid component (ADR-0005), so it needs a budget cap.
- The "hints, not answers" prompts need testing, because learners will try to extract answers.
- Explanation grading is subjective; it needs rubrics and spot-checks.
