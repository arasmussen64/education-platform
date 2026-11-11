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

## Amendment (2026-11-11): a failed review starts the week over, and open follow-ups hold Mastered back

Mastered is now: Learned, **and** a review rated Good at least 7 days after the later of two moments, when the topic became Learned and its most recent review rated Again, **and** no open follow-up on any of the topic's skills ([ADR-0011](0011-mistakes-come-back.md)).

- **What was wrong.** "Passed a review at least ~7 days later" was counted from the moment the topic became Learned, whatever happened in between. The audit of 2026-11-10 found that a learner who failed their first review on day 4 and passed the relearning reviews on days 5 and 9 got the star without ever having remembered the topic across a week. The fourth proof, survives a delayed review, was being met by a recall one to four days old.
- **A failed review** is one rated Again: none of its items right ([ADR-0009](0009-reviews.md)). It starts the week over, so the star needs a Good review at least 7 days after it. A Good review from before the failure no longer counts, so a Mastered topic that fails a review shows Learned (after Relearning) until it survives a week again.
- **Hard isn't a failure**, so it doesn't start the week over. A wrong question in it opens a follow-up, though (a code item counts as right if any Check of it passed that day), and an open follow-up holds the star back by itself until it closes.
- **Open follow-ups.** ADR-0011 already said a topic can't be Mastered while one of its skills has an open follow-up, but neither the code nor [data-model.md](../specs/data-model.md) did it. Now they do: the follow-ups are worked out from the same history as the progress, using a small index of every item's skills built with the app.
- **What a learner with history sees.** States are worked out from the event log on every visit, so the rule covers past reviews too, and nothing stored changes. A topic whose star came on a short gap after a failed review shows Learned until a Good review at least a week after that failure. A topic with a skill being relearned shows Learned until the follow-up closes, then Mastered again.
- **Why the stricter reading.** It's what "survives a delayed review" means, and the week-long gap is what the spacing research behind the review schedule rests on ([learning science](../learning-science.md)). It makes the star later for a learner who fails a review, never earlier.
- Decided under the owner's delegation of 2026-11-11 (best learning experience and retention, and free), and recorded in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".
