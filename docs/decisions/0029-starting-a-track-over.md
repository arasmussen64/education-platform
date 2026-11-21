# ADR-0029: Starting a track over

- **Status:** Accepted (the owner, 2026-11-21)
- **Date:** 2026-11-21

## Context

The owner asked on 2026-11-21: "Give me a way to reset my progress on each track so I can start fresh." The owner has been building and testing the platform while learning on it, so their progress on a track can be a mix of real study and trying features out, and a clean start is worth having.

Two rules stand in the way of the obvious design, deleting the track's events:

- Learner data is an append-only event log ([ADR-0008](0008-event-log.md)). The database lets a learner insert and read events, never update or delete them.
- Answer and review logs are future ML training data (CLAUDE.md), so they must never be deleted or rewritten.

## Decision

- **A reset is one more event.** Starting a track over appends a `track_reset` event whose `topic_id` is the track's id (as a placement's is, [ADR-0021](0021-placement-test.md)), with context `learn` and no item or verdict. One migration adds the type to the database's list.
- **Progress counts nothing on that track from before its newest reset.** The track's graded events, its checkpoint steps opened, and its placement results (a whole-track run, or the foundations list of one of its modules) from before the reset are left out when progress is worked out (`web/src/resets/resets.ts`). So every topic on the track is back to not started, with no reviews due and no mistakes coming back. Resetting again later moves the line to the new reset.
- **What describes the learner stays.** Practice hours, weeks practised, the day's review limit, the usual answer times ([ADR-0009](0009-reviews.md), amended 2026-11-16), the personal forgetting curve, the confidence calibration ([ADR-0028](0028-confidence-before-the-answer.md)) and a diagnostic's placement, like math, are about the person, not the track. Starting over doesn't take back the hours or throw away what the scheduler has learned about their memory.
- **Other tracks are untouched.** A topic on another track that builds on the reset track's topics keeps its own progress, but may be locked again until those topics are learned again, as prerequisites work today.
- **The device forgets the track too.** Drafts, the last part viewed and the last place on each of the track's topics are cleared from the browser where the reset was made, so editors open on their starters. These were never records.
- **It's on the Account page,** one row per track, behind a second step that says exactly what goes and what stays.

## Alternatives considered

- **Delete the track's events.** Breaks ADR-0008 and loses training data. Rejected.
- **A new account.** Starts every track over, not one, and splits the learner's history across two accounts.
- **Reset everything, including hours and the forgetting curve.** Simpler to explain, but it throws away the scheduler's fit to the learner's memory, which takes 100 reviews to earn, and practice that really happened. By the project's tests (the best learning experience, then the best retention) keeping them wins.
- **A per-topic reset.** Possible later with the same mechanism; the owner asked for tracks.

## Consequences

- A reset is reversible in code: the events are all still there, so a future "undo" would only have to ignore a reset.
- Every reader of progress has to apply the resets. Today that's `useProgress` and `usePlacements`; anything new that reads attempts for a topic's state must use `afterResets` too. `ProgressState` carries both `attempts` (after resets) and `allAttempts` (everything) so the choice is explicit.
- The migration reached the live database on 2026-11-21, the day it was written, so resets are saved like any other event.
- The ML capstone sees every event, resets included, and can choose whether to honour them.
