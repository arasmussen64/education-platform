# ADR-0008: Learner data is an append-only event log

- **Status:** Accepted
- **Date:** 2026-11-05

## Context

- Learner answers and reviews are the training data for the owner's ML capstone: fitting the review scheduler and a knowledge-tracing model.
- Rules and models will change (mastery thresholds, scheduler parameters, new models). When they do, we'll want to recompute progress from the full history.
- The app must not lose answers when the network drops.
- Progress must never be self-reported (ADR-0002). A full history makes it auditable.

## Decision

- Every meaningful learner action is stored as an **event**: a row that is never updated or deleted. Database policies allow only inserting and reading.
- Each event has an ID created in the browser, so a retried upload can't create duplicates. The app keeps unsent events in a local outbox until the server confirms them.
- Each event records the revision of the content item and the content build it was answered against.
- Progress (topic states and review schedules) is **derived** from events and content by one pure function. It's cached in a table that can be deleted and rebuilt at any time.
- Event details are capped at 16 KB. Keystrokes are not logged.

## Alternatives considered

- **Editable progress tables only.** Simpler, but the history is lost, so models can't be re-fit and bugs in progress rules can't be repaired.
- **An event log plus hand-edited progress.** Two sources of truth that drift apart.

## Consequences

- More storage. A few hundred events a day for one learner comes to roughly 100 MB a year, well within the free tier. Revisit near the limit, for example by archiving old events to file storage.
- The progress function needs thorough tests, including "rebuilding from scratch gives the same result as updating incrementally".
- Fixing a progress bug is a code change plus a rebuild, with no hand-editing of data.

## Amendment (2026-11-10): events the server refuses are tried again

The decision says the app keeps unsent events in a local outbox until the server confirms them. That held for trouble that passes, such as a lost connection. It didn't hold for a **refusal**: an answer from the server that says it won't take the data itself (any HTTP status other than 0, 401, 408, 429 or 5xx).

What happened before: a refused event was moved to a second list in the browser's `localStorage`, so that it couldn't hold up the events behind it. Nothing read that list again. The event was never re-sent, the page said nothing, and "Download my data" left it out. An audit on 2026-11-10 found this, and found it was live: the app deploys when a pull request merges, a database migration waits for the owner to apply it, and in between the server refuses every event of a kind the migration adds. Placement-test events were in that state. That breaks this ADR's own rule that the app must not lose answers.

What is true now:

- **Refused events are retried.** After any save that goes through, the browser sends each of the signed-in learner's refused events whose last attempt was more than 12 hours ago, one at a time. Accepted: it leaves the list. Refused again: it stays, with the new reason and time, and the attempt counted. A passing problem: the browser stops and leaves the rest for next time.
- **None is ever dropped, and there's no limit on attempts.** An event the server will never take costs one small request every 12 hours at most. Giving up would mean deleting learner data, which this ADR rules out.
- **One bad event still can't block the others,** because refused events sit in their own list and are sent singly. Another learner's events on the same device are never sent or removed.
- **The learner is told.** The header shows a line while they have refused events, and the account page says how many and what it means.
- **The export has them,** under `refused_events`, apart from the saved history in `events`.

A retry can't create a duplicate, for the reason already in the decision: the server ignores an event `id` it has seen.

Why 12 hours: a refusal is fixed by a person (applying a migration, deploying a fix), not by waiting a few seconds, so quick retries would only repeat the same refusal. Twice a day gets the events saved within a day of the fix. The details are in the [data model](../specs/data-model.md#events-the-server-refuses).

Still open: until a refused event is saved it exists in one browser only, so clearing that browser's site data loses it. And if `localStorage` itself can't be written (full, or switched off), an event can still be lost; that case isn't handled yet. (Handled since 2026-11-11: see the next amendment.)

Since 2026-11-11 editor drafts, the code and explanations a learner has typed but not yet passed, share `localStorage` with the outbox (`web/src/drafts/drafts.ts`). They keep to 250,000 characters of storage in all, measured as saved (one draft may hold at most 50,000 characters of text), and drop their oldest first, so they can't crowd the outbox out. Drafts are never sent to the server and aren't events.

## Amendment (2026-11-11): events the device can't store are sent from memory

Decided under the owner's delegation of 2026-11-11 and recorded in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".

What happened before: when the browser wouldn't let the page write to `localStorage` (it was full, or site data was switched off), a new event never reached the outbox. The page still counted it, so a passed proof showed as passed, but the event was never sent, the header said nothing was waiting, and it was gone on the next reload. The audit of 2026-11-10 found this.

What is true now:

- **Nothing counted on the page goes unsent.** When the outbox can't store an event, the event log keeps it in a second outbox that lives in the page's memory, and sends it from there in the same way: in batches, retried after a passing problem, moved to the refused list (also in memory) if the server refuses it.
- **The learner is told what's at risk.** While any such event is unsent, the header says "Not saved yet: this device can't keep it if the page closes". Closing the page then would lose it, and nothing can change that.
- **The events go no further than the page.** They aren't copied into `localStorage` later if it starts working again, and the next visit doesn't know about them.

## Amendment (2026-11-11): every event records the learner's own day and time zone

Decided under the owner's delegation of 2026-11-11 and recorded in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".

The decision says progress is derived from events by one pure function. One part wasn't: an event's `occurred_at` is in UTC, and its calendar day, which decides when a missed skill comes back ([ADR-0011](0011-mistakes-come-back.md)), was worked out in the time zone of whichever device was showing it. The same history gave different follow-up days on a device set to UTC, after travelling, or rebuilt in Python for the ML capstone. Because the log is append-only, a day that isn't recorded at the time can never be recovered.

What is true now:

- **Every event recorded from 2026-11-11 has two more fields in its `data`:** `local_day`, the learner's calendar day when it happened (like `"2026-11-06"`), and `utc_offset_minutes`, how many minutes their clock was ahead of UTC (`-480` in Los Angeles in winter, `330` in India).
- **An event's day is the one it recorded,** on any device in any zone (`dayOf` in `web/src/days.ts`, given the event rather than only its time). A recorded day that can't be right (it isn't the UTC day or one either side of it) is ignored. When this amendment was written, the follow-ups code still gave `dayOf` only an event's time, so follow-up days use the recorded day only once it passes the event itself.
- **Older events have neither field and keep the old rule:** their day is the day on the viewing device's clock. Nothing stored is changed.

## Amendment (2026-11-11): a Check that couldn't run is saved with no verdict

Decided under the owner's delegation of 2026-11-11 and recorded in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".

A Check is saved as a graded attempt, so a wrong one opens a follow-up and lowers a review's rating. Before, a Check that never ran was saved as wrong: Python didn't start, a package didn't download, the worker crashed, the exercise's own tests couldn't load, or the exercise had no tests. Those say nothing about the learner, and in an append-only log a false miss stays.

What is true now:

- **Such a Check is saved with `correct` left empty,** the way an explanation that couldn't be graded already is. Its `data` still says what happened (`outcome: "failed"` and the message), so the log keeps the full story. The rule is `checkCorrect` in `web/src/events/checkGrade.ts`.
- **It counts nowhere:** not as a miss, not as an attempt in a review, not as a failed try at a checkpoint's build, and its time carries on to the next real attempt. The learner is told it doesn't count and can press Check again.
- **Code that runs past its time limit still counts as wrong.** That is almost always a loop that never ends, which is the learner's own result.
- **Checks saved as wrong before 2026-11-11 for these reasons still count as wrong,** for now. They can be told apart (`data.outcome` is `"failed"`, or `data.status` is `"error"` with a message starting "The tests couldn't be loaded.", or `data.status` is `"ok"` with `data.total` 0), so the code that turns events into attempts can skip them later without changing a stored row. `savedCheckCouldNotRun` in the same file applies the same rule to saved data.
