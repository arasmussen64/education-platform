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

## Amendment, 2026-11-22: starting everything over

The owner started every track over the day after this was accepted, saw the Today page still showing practice hours, and asked: "I want to wipe everything so I start fresh." That is the third alternative above, asked for by name. The owner's history so far is mostly trying features out while building, so the hours and the forgetting curve fitted to it don't describe real study.

- **Starting a track over is unchanged.** It still keeps what describes the learner.
- **Starting everything over is a second choice on the Account page,** under the tracks. It appends the same `track_reset` event with `everything` where the track's id would be. No track may have that id (a test checks), and no migration is needed: the event type is already allowed.
- **Nothing from before it counts, anywhere.** Every track's progress, reviews, mistakes coming back and placement results, as for a track. And what a track's reset keeps: practice hours, weeks practised, the day's review limit, the usual answer times, the personal forgetting curve, the confidence calibration and a diagnostic's placement, like math.
- **Nothing is deleted.** The events stay in the log and in "Download my data" ([ADR-0008](0008-event-log.md) and the training-data rule both hold). The app stops counting them.
- **Kept:** the study plan (a setting, not history) and the sign-in.
- **On the device,** every topic's drafts, last part and place, and any guess waiting for its answer are cleared.

In code, `ProgressState.allAttempts` now means every attempt since the learner last started everything over, so its readers (hours, weeks, the review limit, answer times, the curve) follow without changes of their own. `wasReset` answers yes for anything before that time, whatever its track. The calibration summary reads answers from that time on.

## Second amendment, 2026-11-22: starting everything over deletes

The first amendment hid the history behind one event and kept every row. The owner read that and answered: "with the deletion make it a true deletion." So starting everything over now **deletes the learner's events from the database, for good**. Starting a single track over is unchanged: it hides, and can be undone in code.

- **One function does it:** `public.erase_my_history()` (migration `20261122200000`). It deletes the events of whoever calls it, all of them, and nothing else; it takes no arguments, and its permission to delete lasts only for its own transaction. Learners still have no right to delete events themselves, and an admin's plain `delete` is still refused.
- **An exception to [ADR-0008](0008-event-log.md) and to the training-data rule,** made on purpose: a learner's history is theirs to erase. The cost is real and accepted: the deleted answers and reviews are gone as training data, and no code change can bring them back.
- **The button says so first:** that it can't be undone, and that "Download my data" saves a copy.
- **The marker event stays.** After the deletion the app records the same `track_reset` for `everything` as before. It is the only event left, and it covers what the deletion can't reach: an old answer still waiting on another device, which would otherwise arrive later and count.
- **What isn't deleted:** the profile and sign-in, problem reports (messages to the owner), and `ai_calls`, the spending ledger the monthly cap is counted from ([ADR-0013](0013-explain-grading.md)). The weekly backup files made before the deletion still hold the old events until they age out.
- **If it fails** (no connection, or the migration not yet applied to the live database), the page says so and changes nothing.
