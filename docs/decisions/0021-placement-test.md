# ADR-0021: The placement test walks the map by halving, and proves nothing

- **Status:** Accepted (the owner asked for Phase 2 to be built on 2026-11-09; this is its placement item)
- **Date:** 2026-11-09

## Context

- The vision promises a placement test that "walks the map to find where your knowledge runs out, math included" ([vision](../vision.md)), and the roadmap's Phase 2 starts with it. v1 shipped "Prove it now" instead ([ADR-0002](0002-mastery-and-gating.md), [F8](../specs/v1.md#f8-topic-states-gating-prove-it-now)): a learner who already knows a topic can take its three proofs and skip the lesson, one topic at a time.
- Mastery never comes from a test of recognition. ADR-0002 is explicit: the placement test and "prove it now" take the same checks. So the placement test can estimate, but it can't tick anything off.
- Every ready topic already has a review pool of three or more recall questions (multiple choice, predict the output, Parsons, predict the shell), written to be answered without the lesson open. They're the natural probes.
- A subject with prerequisites has a knowledge structure: knowing a topic implies knowing what it builds on. Knowledge space theory turns that into efficient placement (Doignon & Falmagne; [learning-science.md](../learning-science.md)). Our tracks are close to a chain, so what a learner knows is, near enough, a prefix of the track's topics in order.
- The math the machine-learning track leans on has no topics yet (Phase 3), but a learner can still find out now whether it's in their way.

## Decision

1. **A walk by halving.** For a track, the candidates are its open topics the learner hasn't learned, in track order. The test probes the middle one with up to three of its review questions; a probe passes with two right and fails with two wrong, so it stops early. Passing counts the topic and everything before it as known; failing counts it and everything after as not. The next probe is the middle of what's left. Thirty topics take at most five probes, ten to fifteen questions, about ten minutes.
2. **The result is an estimate and a plan, never a state.** It names where the knowledge seems to run out (the place to start) and lists the topics before it as _topics to prove_, in order, each through its own "Prove it now". Nothing changes on the map until a proof passes. If the estimate was generous, the proof catches it; if it was stingy, the learner spends a short lesson on something familiar. Both are cheap, so ties and topics with nothing to ask get the benefit of the doubt.
3. **No feedback until the end.** Questions say "Answer recorded" instead of right or wrong, and show no explanation. The test measures; teaching mid-test would both change what it measures and spoil review questions the learner will meet again. Hints and the tutor are off, as in reviews and proofs ([ADR-0003](0003-ai-roles-and-guardrails.md)).
4. **A math diagnostic walks a ladder the same way.** A _diagnostic_ is a new, small kind of content: `content/diagnostics/<id>.yaml`, a ladder of levels, each with a few original multiple-choice questions and a link to a free refresher. `math` has seven levels, from arithmetic to the first ideas of calculus. Its result says how far up the ladder is solid and where to refresh, with the links, until the platform's own math refresher exists (roadmap, Phase 2 content). Diagnostics pass the content validator like everything else.
5. **Everything is in the event log, and only there.** Each answer is an `answer` event with the context `placement` and the run's id in its data; a finished run is one `placement` event naming what's known and where to start. Progress derivation skips placement answers (they must not turn an unopened topic "in progress"), and so do the follow-ups (a placement miss isn't a practice mistake). Practice time counts them: they're effortful retrieval. The event table's `type` and `context` checks gain the two values in a migration.
6. **Where it lives.** `/placement`, offered from the Today page until a run exists, and from every track's map header. Today then shows each subject's latest result in a line. Reviews, mistakes to revisit and Next up are unchanged.

## Alternatives considered

- **Mark estimated-known topics Learned, or unlock them.** Forbidden by ADR-0002, and for good reason: recognition isn't ability, and four-choice questions can be guessed (two of three right by luck is about one time in six).
- **A linear walk from the start.** Simple, but thirty topics would mean thirty probes. Halving gets the same answer in five.
- **Probing the prerequisite graph properly** (ALEKS-style, over the whole partial order). Our tracks are chains with few branches, so the prefix is a good approximation and far simpler to explain. If a track's graph ever branches a lot, this is where to revisit.
- **Free-response math questions.** Better than multiple choice against guessing, but a new item type with its own grading. Multiple choice with distractors built from the common mistakes is the standard for a first diagnostic; numeric answers can come with the math content.
- **Feedback after each question.** It's what practice does, and it's exactly what a test shouldn't.

## Consequences

- A migration (`placement_events`) widens the `events` table's checks. It has to reach the live project before a placement can be saved there; until then the outbox keeps placement events on the device and reports them as refused.
- `PracticeItem` gains a `placement` context and a quiet mode for its question components; the question components gain a `quiet` prop. Nothing else about practice changes.
- The walk's math is a pure module (`web/src/placement/placement.ts`) with its own tests, so it can be reasoned about and, later, replaced by a model fitted to the owner's data (Phase 4).
- The answers are a new, labelled signal for the knowledge-tracing work: "did the learner know this before studying it".
- Writing diagnostics is now a content task like any other: `content/README.md` says how.

## Amendment (2026-11-10): "I don't know this"

Every placement question offers an "I don't know this" answer beside its choices: a last option on a multiple-choice question, a button beside Check on a prediction or a Parsons problem. It counts as a wrong answer for the probe and is saved as one, with `dont_know: true` and a null `choice`, `prediction` or `program` in the answer's data, so that a learner who doesn't know needn't guess. A lucky guess would place them past what they know, and the proofs would catch it later at a cost of time; the honest answer places them right the first time. The option exists only in the placement test: in practice and reviews a wrong guess is followed by the explanation, which is the point there. The owner asked for this on 2026-11-10.

## Amendment (2026-11-10): refused placement events are tried again

The first consequence above says the outbox "reports them as refused". At the time it reported nothing and never re-sent them. Since 2026-11-10 the header and the account page say how many events are waiting, and the browser tries them again at most every 12 hours until the server accepts them, so placements recorded before the migration arrived are saved once it has ([ADR-0008](0008-event-log.md), amendment of the same date).

## Amendment (2026-11-11): a tie passes, as decision 2 says

Decision 2 says ties get the benefit of the doubt, but the code passed a probe only when more than half its answers were right, so a tie failed. An audit on 2026-11-11 found it mattered for 11 of the 100 ready regular topics: their review pools have only two recall questions, so one slip placed the learner before the topic. Six of the 11 are the math refresher (`ml.math.*`) that the placement test exists to route around; the others are `ml.py.classes`, `ml.py.dataclasses-and-typing`, `ml.py.writing-tests`, `py.arithmetic` and `py.values-and-types`. The Context's "a review pool of three or more recall questions" isn't true for them.

Since 2026-11-11 a probe passes once at least half its answers are right (`needed = ceil(size / 2)` in `web/src/placement/placement.ts`).

- **What changes.** Only probes of two questions: one right and one wrong now passes. A probe of three still needs two right, the math diagnostic is unchanged (every level has three questions), and a probe with nothing to ask still passes.
- **Stopping early, both ways.** A decided probe still stops at once. With two questions, a first right answer now decides it, since the second could only make a tie; before, a first wrong answer decided it the other way. Either way such a probe rests on one question. That's the generous side of the trade-off decision 2 accepts: the topic's proofs catch an estimate that was too generous.
- **Earlier results.** A finished placement is one event naming what it found, so results saved before this change are kept as they were and not worked out again.
- **Alternative considered: keep the stricter rule and write a third recall question for each of the 11 topics.** More evidence per probe would be better, and the pools can still grow, but until then the rule should be the one this ADR states.

Decided under the owner's delegation of 2026-11-11 and recorded in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".
