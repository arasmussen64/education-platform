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

Still open: until a refused event is saved it exists in one browser only, so clearing that browser's site data loses it. And if `localStorage` itself can't be written (full, or switched off), an event can still be lost; that case isn't handled yet.
