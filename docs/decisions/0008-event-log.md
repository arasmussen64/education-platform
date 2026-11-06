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
