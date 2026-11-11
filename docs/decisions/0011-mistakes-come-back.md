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

## Amendment (2026-11-11): what counts towards relearning, and Mastered

A right day now moves a follow-up on only if all three hold:

1. **It's on or after the day the follow-up is due.** Before, any later day counted, so getting the skill right three days in a row closed the follow-up within three days, without the growing gaps of 1, 3 and 7 days that the research above rests on. Right answers before the due day change nothing: they don't move it on, and they don't start it over.
2. **One of that day's right answers is on an item other than those missed.** Getting the missed question right again can be remembering its answer, which is why a follow-up asks a different question in the first place. If the skill has no other question to ask, the missed one counts, so a follow-up can always close. The items of a checkpoint's tests are named in full, so passing the same checkpoint build again doesn't count, but passing one of its fresh versions does.
3. **The item isn't a worked example.** A worked example shows its answer as it goes, so a lab walkthrough's Check, right or wrong, neither opens nor closes a follow-up. Python worked examples were never graded (they only Run), so this makes the two runtimes agree.

The rest is unchanged: a miss starts the follow-up over, due the next day; 3 counted days close it; days are the learner's own calendar days.

- **Mastered.** The clause above, that a topic can't become Mastered while any of its skills has an open follow-up, wasn't in the code. Now it is ([ADR-0002](0002-mastery-and-gating.md), amendment of the same date).
- **An item's `rev`.** Answers to an earlier `rev` of an item count like any other, misses included. Bumping a `rev` records that the item changed; it doesn't set the learner's history aside.
- **How it's built now.** The app no longer downloads every topic with a miss to learn its items' skills. A small index of every question's and exercise's skills, stage and test skills is built from `content/` with the app (`virtual:skill-index`: `web/vite.config.ts` builds it, `web/src/followups/skillIndex.ts` reads it), and `skillIndex.test.ts` checks it against the full content of every topic. `useProgress` works out the follow-ups from the history and the index, so every page that shows a topic's state applies the Mastered clause. A topic page reads only the history of the topic and its prerequisites, so it doesn't yet see what a checkpoint's tests said about the topic's skills: a follow-up that a checkpoint's test opened, or moved on, can leave the topic page showing a different state from the map until the topic page reads those events too. The map and the Today page see the whole history. The Today page reads the history once for all its sections, and downloads in full only the topics of the reviews and questions it shows. If one of those downloads fails, the section says so and offers to try again.
- **What a learner with history sees.** The follow-ups are worked out from the event log on every visit, so the new rule covers past answers too, and nothing stored changes. A follow-up that was closed by getting the missed question right again, by right days before it was due, or by a worked example, is open again, and comes back on the Today page (at once, if its due day has passed). It then needs its right days at the proper gaps, on other questions. A follow-up opened only by a lab walkthrough that never passed is gone.
- **Why.** The audit of 2026-11-10 found that a follow-up could be closed by answering the missed question, whose answer and explanation had been shown, on three days in a row, or by pasting a walkthrough's lab result. The literal rule ("correct on 3 different days") was met; its purpose, fresh questions at growing gaps, wasn't.
- Decided under the owner's delegation of 2026-11-11 (best learning experience and retention, and free), and recorded in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".
