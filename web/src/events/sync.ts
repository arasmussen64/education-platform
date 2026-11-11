import type { Outbox } from './outbox.ts'
import type { EventRow } from './types.ts'

/** The result of sending events to the server. */
export type SendResult =
  | { ok: true }
  /**
   * `retryLater` is true for trouble that will pass (no connection, an
   * expired sign-in, a busy server) and false when the server refused the
   * data itself, which no retry will fix.
   */
  | { ok: false; retryLater: boolean; message: string }

/** Something that can store events on the server (see supabaseEvents.ts). */
export type EventsClient = {
  send(events: EventRow[]): Promise<SendResult>
}

const BATCH_SIZE = 50

/**
 * Sends one learner's unsent events, oldest first, removing each batch from
 * the outbox once the server has it. Sending an event twice is harmless: the
 * server ignores an ID it already has.
 *
 * Returns 'retry-later' if the connection or server failed partway through.
 * `now` is the time to note on anything the server refuses.
 */
export async function syncOutbox(
  outbox: Outbox,
  client: EventsClient,
  userId: string,
  now = Date.now(),
): Promise<'done' | 'retry-later'> {
  // IDs already sent in this run. If the outbox couldn't forget them (its
  // storage failing), this stops the loop from sending them forever.
  const sent = new Set<string>()

  for (;;) {
    const batch = outbox
      .pending(userId, BATCH_SIZE + sent.size)
      .filter((event) => !sent.has(event.id))
      .slice(0, BATCH_SIZE)
    if (batch.length === 0) return 'done'
    for (const event of batch) sent.add(event.id)

    const result = await client.send(batch)
    if (result.ok) {
      outbox.remove(batch.map((event) => event.id))
      continue
    }
    if (result.retryLater) return 'retry-later'

    // The server refused something in this batch. Send the events one at a
    // time, so a single bad event can't hold up all the others.
    for (const event of batch) {
      const single = await client.send([event])
      if (single.ok) {
        outbox.remove([event.id])
      } else if (single.retryLater) {
        return 'retry-later'
      } else {
        // Not lost: it moves to the refused list, and retryRefused (below)
        // tries it again later.
        console.error('The server refused an event', single.message, event)
        outbox.refuse(event, single.message, now)
      }
    }
  }
}

/**
 * How long a refused event waits before it's tried again. Long enough that
 * an event the server will never take costs a couple of requests a day, and
 * short enough that events refused only because the app was ahead of the
 * database (a migration that hadn't been applied yet) are saved within a day
 * of the fix.
 */
export const RETRY_REFUSED_AFTER_MS = 12 * 60 * 60 * 1000

/** True once a refused event has waited long enough for another try. */
function isDueForRetry(lastTriedAt: string, now: number): boolean {
  const lastTried = Date.parse(lastTriedAt)
  // A time that can't be read counts as long ago: better one request too
  // many than an event that's never tried again.
  return Number.isNaN(lastTried) || now - lastTried > RETRY_REFUSED_AFTER_MS
}

/**
 * Gives one learner's refused events another chance: each one last tried
 * more than 12 hours ago is sent again, on its own, so one that's refused
 * again can't hold up the others.
 *
 * - Accepted: it leaves the refused list. It's on the server now.
 * - Refused again: it stays, with the new reason and time, and one more
 *   attempt counted.
 * - A passing problem (no connection, a busy server): stop, and leave the
 *   rest exactly as they were for next time.
 *
 * Nothing is ever dropped, and another learner's events are never sent.
 */
export async function retryRefused(
  outbox: Outbox,
  client: EventsClient,
  userId: string,
  now = Date.now(),
): Promise<'done' | 'retry-later'> {
  const due = outbox
    .refused(userId)
    .filter((refusal) => isDueForRetry(refusal.at, now))

  for (const { event } of due) {
    const result = await client.send([event])
    if (result.ok) {
      outbox.forgetRefused(event.id)
    } else if (result.retryLater) {
      return 'retry-later'
    } else {
      outbox.refuse(event, result.message, now)
    }
  }
  return 'done'
}
