# ADR-0009: Reviews are per topic and graded automatically

- **Status:** Proposed
- **Date:** 2026-11-05

## Context

Flashcard apps like Anki schedule a card for each fact and ask learners to rate themselves ("Hard", "Good"). That's self-report, which this platform avoids (ADR-0002). And reviewing the same card over and over can mean memorizing answers instead of keeping a skill. Math Academy instead schedules reviews per topic and uses fresh problems.

## Decision

- **One FSRS card per learner per topic.** Checkpoints don't get cards.
- **The card starts when the topic becomes Learned.** That counts as a first review rated Good.
- **A review session** is a short set of items drawn from the topic's review pool. In v1 that's 2 items, at least one of them code or predict-the-output. Pools have at least 3 items, and the app avoids repeating the previous review's items.
- **Ratings come from performance, not self-assessment:**
  - all items correct → Good
  - some correct → Hard
  - none correct → Again

  "Easy" isn't used in v1.
- **Defaults:** standard FSRS parameters, a 90% target retention, and at most 20 topic reviews a day.
- **No tutor during reviews.**

## Later

- **Implicit repetition:** practicing an advanced topic gives partial review credit to the topics it builds on, like Math Academy's FIRe.
- **Personal FSRS parameters** fitted to the owner's own history, as part of the ML capstone.
- **Using answer time** to tell Good from Easy.

## Alternatives considered

- **One card per item, self-rated (Anki-style).** Proven for facts, but it's self-report, and learners can end up memorizing specific answers.
- **Fixed review intervals.** Simpler, but they ignore how fast each learner actually forgets.

## Consequences

- Fewer, more meaningful reviews.
- Every topic needs a review pool, which is more content to write.
- The rating rules are a guess until real data tests them, which is exactly what the capstone is for.
