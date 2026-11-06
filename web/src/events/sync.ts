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
 */
export async function syncOutbox(
  outbox: Outbox,
  client: EventsClient,
  userId: string,
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
        console.error('The server refused an event', single.message, event)
        outbox.reject(event, single.message)
      }
    }
  }
}
