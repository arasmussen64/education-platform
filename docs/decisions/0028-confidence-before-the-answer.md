# ADR-0028: Saying how sure you are, as part of answering

- **Status:** Proposed. Designed under the owner's delegation of 2026-11-11 (the best learning experience, then memory retention, then free), and built on until the owner rules; listed in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".
- **Date:** 2026-11-16

## Context

A quick question (multiple choice, predict the output, Parsons, an estimate, a typed answer) is answered with one button, Check. The answer is saved as right or wrong, and nothing records whether the learner knew it or got lucky.

Two findings make the learner's certainty worth asking for:

- **Hypercorrection.** Errors made with high confidence are, once corrected, remembered better than errors made with low confidence (Butterfield and Metcalfe, 2001, _Journal of Experimental Psychology: Learning, Memory, and Cognition_). The surprise of being sure and wrong makes the correction stick, provided the learner reads it. Asking for confidence first creates that moment, and the page can point at it.
- **Calibration is a skill.** Knowing what you know is what lets a learner decide what to review, and what an engineer needs when they say "I'm sure" in a design review. Learners are usually overconfident, and seeing the numbers is how they find out.

A guess that happens to be right also says something the right-or-wrong log can't: the item isn't known yet.

## Decision

Every graded quick question, in practice, reviews and anywhere else it is answered for real, asks how sure the learner is as part of answering.

1. **Three buttons instead of Check:** "Guessing", "Fairly sure" and "Certain", under the words "How sure are you?". Pressing one checks the answer; there is no extra step. They are ordinary buttons in the page's tab order, so a keyboard reaches each with Tab and presses it with Enter or Space. In an estimate or a typed answer, Enter in the box doesn't check (it would have to pick a confidence for the learner): it moves focus to the three buttons, and an answer the box can't read is still told how to type it first.
2. **The event.** The answer event gains `confidence` in its `data`: `guess`, `fair` or `sure` ([ADR-0008](0008-event-log.md)). No new event type and no migration: `data` is JSON, the database checks only its size, and an older answer without `confidence` keeps its meaning (it was given before the question was asked).
3. **It changes no grade.** Confidence never changes whether an answer is right, a review's rating ([ADR-0009](0009-reviews.md)), Learned or Mastered ([ADR-0002](0002-mastery-and-gating.md)), or which mistakes come back ([ADR-0011](0011-mistakes-come-back.md)). A right guess counts as right, as it did before. The schedule may one day use it, but only with its own ADR, after the log shows how it relates to forgetting.
4. **Feedback that uses it.** After a wrong answer given as "Certain", the page adds one line before the explanation: this is the kind of mistake that sticks once it's corrected, so read why. After a right answer given as "Guessing", one line says it was right but a guess, so it's worth reading why it's right. Nothing is added otherwise.
5. **A calibration summary on the Account page.** For each level with at least five answers: how often the learner is right when they say it ("When you're certain, you're right 92% of the time, in 25 answers"). It is worked out in the browser from the learner's own answer events that carry `confidence`, saved or still waiting on this device. With fewer than five at every level, it says so and what to do.
6. **Where it isn't asked.** The placement test keeps its single Check and "I don't know this" ([ADR-0021](0021-placement-test.md)): it measures, says nothing about each answer, and should be quick. Proof checks (a build, a debug, an explanation) are not quick questions and are left alone: their Check runs tests or a grader, and adding a question in front of a proof would slow the thing that matters most.

## Alternatives considered

- **Asking after the answer is checked.** The learner already knows if they were right, so the rating is no longer a prediction, and hypercorrection needs the confidence to exist before the feedback.
- **A separate step before Check** (choose a level, then press Check). One more click on every question, for nothing the three buttons don't do.
- **Two levels** (sure, not sure). Simpler, but "fairly sure" is where most answers sit, and without it the summary can't show a gradient.
- **A percentage slider.** More precise, but slow to use with a keyboard or a thumb, and few learners can tell 70% from 80% about themselves.
- **Optional confidence** (Check stays, with confidence beside it). Most learners would skip it, and the summary would describe only the learners who don't.
- **Letting confidence change the schedule** (a right guess scheduled like a miss). Plausible and maybe right, but it changes what Good means in reviews and when topics become Mastered, which [ADR-0002](0002-mastery-and-gating.md) and [ADR-0009](0009-reviews.md) settle. The log now records what's needed to decide it later.
- **Asking in the placement test too.** It would make the test longer, and the test already has its honest way out, "I don't know this".

## Consequences

- Every quick question shows three buttons instead of one. A learner answers with one press, as before, and thinks for a moment about how sure they are, which is part of the point.
- The answer log gains a field the ML capstone can use: the learner's own prediction next to the outcome.
- Older answers have no `confidence`, and the summary leaves them out.
- The summary is only as good as the learner's honesty. Nothing rewards picking one level over another, so there is no reason to game it.
