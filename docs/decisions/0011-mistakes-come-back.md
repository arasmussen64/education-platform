# ADR-0011: Mistakes come back as fresh questions until relearned

- **Status:** Accepted (the owner kept the proposed defaults; two refinements, made while building it, are marked below)
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
- **A miss opens a follow-up** for each skill the item tests, in practice, a proof check, or a review. Outcomes are judged per item per day:
  - a **question** is missed if any answer to it that day was wrong;
  - a **code exercise** is missed only if none of that day's Checks passed. *(Refinement: failing Checks while working something out are part of solving it, not mistakes. Counting each one would flood the list.)*
- **A follow-up asks a different question on the same skill** (the owner's choice). It prefers questions the learner has never seen, then the ones seen longest ago. If the missed question is the only candidate left, it can come back.
- **Timing, from the research** (the owner asked for "whatever the science says will make it stick best"):
  - The first follow-up is due the next day. After a correct day it comes back 3 days later, then 7 days later.
  - Another miss starts over: due the next day, with earlier progress cleared.
- **Relearned:** a follow-up is closed once the learner answers that skill correctly on **3 different days** after the miss. Correct answers on the day of the miss don't count.
- **Why those numbers:**
  - Successive relearning gives durable retention with **at least 3 relearning sessions**, each ending in a correct retrieval. Beyond 3 the gains shrink ([Rawson & Dunlosky, 2011](../learning-science.md#references); a classroom study, Rawson, Dunlosky & Sciartelli, 2013).
  - **Growing gaps** help long-term memory, and the best gap grows with how long you need to remember (Cepeda et al., 2008).
  - After that, topic reviews ([ADR-0009](0009-reviews.md)) keep the topic fresh with ever-longer gaps.
  - *History:* the first draft said "2 days" with gaps of 1, 3 and 7 days, but a 2-day rule never reaches the 7.
- **Not built yet:** the same research also gets learners right about 3 times in the *first* session. Its benefit mostly fades once the relearning sessions happen, so it's a candidate for later: "try another one before you leave".
- **Where it shows:** the Today page lists due follow-ups as "Mistakes to revisit". This is the "relearning practice" slot of [F12](../specs/v1.md#f12-today-page).
- **Derived from the event log** by a pure function, like topic progress. Follow-up answers are ordinary `answer` and `code_check` events with `context: review`. Because it reads past events, misses recorded before this feature existed are included.
- **Mastery:** a topic can't become Mastered while any of its skills has an open follow-up. This adds to [ADR-0002](0002-mastery-and-gating.md); it doesn't weaken it.
- **Order:** built after topic 2 (the owner's choice). Skills are part of the content format from now on, so every topic is written ready for it.

## Alternatives considered

- **Re-ask the exact same question.** Simplest, with no extra content, but a learner can remember the answer instead of relearning the rule.
- **Rely on topic reviews alone.** They don't aim at the specific mistake, and they only begin once a topic is Learned.
- **Anki-style cards per question, self-rated.** That's self-report, which ADR-0002 rules out.

## How it's built

- `web/src/followups/followUps.ts` is the pure function: graded attempts plus the skills of each item give the open follow-ups, and picks each one's question.
- The Today page reads the learner's graded attempts from the server, page by page, and adds the events on this device that may not have arrived yet. It loads content only for topics with a miss. Questions are chosen once per visit, so a card doesn't change while it's being answered.
- One miss can open several follow-ups (an item can test several skills). Each gets a different question where possible. When a skill's only remaining question is already on the page, that question is asked once, for both.
- A test (`web/src/followups/everyItem.test.ts`) checks the promise against the real content. Missing any question or exercise in any ready topic must bring back a different question on each skill it tests.
- Answers on the Today page are saved with `context: review`. Hints are off there, as in all reviews.

## Consequences

- More content: each skill needs at least 2 follow-up candidates. The content checker enforces it.
- The Today page gains a list, and the follow-up function needs thorough tests, including that rebuilding from scratch matches updating step by step.
- The gaps and the "2 different days" rule are educated guesses. The owner's own data can tune them later, as part of the ML capstone.
- Today reads the learner's whole graded history each visit. That's fine for months, but it grows. When it gets slow, cache the derived state in a table that can be rebuilt from events, like `topic_progress` ([ADR-0008](0008-event-log.md)).
