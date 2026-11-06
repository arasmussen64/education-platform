# ADR-0011: Mistakes come back as fresh questions until relearned

- **Status:** Proposed
- **Date:** 2026-11-06

## Context

- The owner asked for every wrong answer to be remembered and re-tested over time until they get it right. It came up after they missed a predict-the-output question about `print` with commas, in their first lesson.
- Wrong answers are already saved, permanently ([ADR-0008](0008-event-log.md)), but nothing brings them back.
- Topic reviews ([ADR-0009](0009-reviews.md)) keep Learned topics fresh. But they don't target a particular mistake, and they only start once a topic is Learned.
- **Successive relearning** works: retrieve until correct, then again in later, spaced sessions ([learning science](../learning-science.md)). Mistakes corrected with feedback are remembered well, especially confident ones.
- Asking the very same question again risks memorizing its answer instead of the rule. That's the same reason ADR-0009 uses fresh items for reviews.

## Decision

- **Every item names the skills it tests.**
  - Each topic declares its skills, with an ID and a short description. Recall items and exercises list the skills they test.
  - A **follow-up candidate** is any recall item, or any fill-in, write or `review_code` exercise.
  - Every skill needs at least 2 follow-up candidates, so a fresh one exists after a miss. 3 or more is better.
  - Proof checks (build and debug) list their skills too, but they're never used as follow-ups.
- **A miss opens a follow-up** for each skill the item tests. A miss is any graded attempt that isn't correct: a wrong answer or a failing Check, in practice, a proof check, or a review.
- **A follow-up asks a different question on the same skill** (the owner's choice). It prefers questions the learner has never seen, then the ones seen longest ago. If the missed question is the only candidate left, it can come back.
- **Timing:** the first follow-up is due the next day, then after about 3 days, then a week. A wrong answer starts the gaps again from one day.
- **Relearned:** a follow-up is closed once the learner answers that skill correctly on **2 different days** after the miss.
- **Where it shows:** the Today page lists due follow-ups as "Mistakes to revisit". This is the "relearning practice" slot of [F12](../specs/v1.md#f12-today-page).
- **Derived from the event log** by a pure function, like topic progress. Follow-up answers are ordinary `answer` and `code_check` events with `context: review`. Because it reads past events, misses recorded before this feature existed are included.
- **Mastery:** a topic can't become Mastered while any of its skills has an open follow-up. This adds to [ADR-0002](0002-mastery-and-gating.md); it doesn't weaken it.
- **Order:** built after topic 2 (the owner's choice). Skills are part of the content format from now on, so every topic is written ready for it.

## Alternatives considered

- **Re-ask the exact same question.** Simplest, with no extra content, but a learner can remember the answer instead of relearning the rule.
- **Rely on topic reviews alone.** They don't aim at the specific mistake, and they only begin once a topic is Learned.
- **Anki-style cards per question, self-rated.** That's self-report, which ADR-0002 rules out.

## Consequences

- More content: each skill needs at least 2 follow-up candidates. The content checker enforces it.
- The Today page gains a list, and the follow-up function needs thorough tests, including that rebuilding from scratch matches updating step by step.
- The gaps and the "2 different days" rule are educated guesses. The owner's own data can tune them later, as part of the ML capstone.
