import type { EventRow } from './types.ts'

// The outbox keeps events on this device until the server confirms it has
// them (v1 spec, F6), so closing the tab or losing the connection loses
// nothing. It lives in the browser's localStorage.
//
// It holds two lists. The first is events waiting to be sent. The second is
// events the server refused: they're moved there so one bad event can't hold
// up the others, and they're tried again later (see retryRefused in
// sync.ts). Nothing is ever dropped from the second list except an event the
// server has since accepted.
//
// Several tabs can share it, so every change reads the latest copy and writes
// it straight back, with no waiting in between: one tab never overwrites
// another's events with an old copy.

const OUTBOX_KEY = 'learner-events-outbox-v1'
// The key says "rejected", this file's first word for "refused". It stays,
// because browsers already hold events under it.
const REFUSED_KEY = 'learner-events-rejected-v1'

/** An event the server refused, kept on the device to be tried again. */
export type RefusedEvent = {
  event: EventRow
  /** What the server said the last time it was tried. */
  reason: string
  /** When it was last tried, as an ISO 8601 time. */
  at: string
  /** How many times the server has refused it. */
  attempts: number
}

/**
 * A refused event as it sits in storage. Ones saved before retries existed
 * have no `attempts`, and a damaged entry could lack anything.
 */
type StoredRefusal = Partial<RefusedEvent>

export type Outbox = ReturnType<typeof createOutbox>

/** `storage` is for tests; the app uses the browser's localStorage. */
export function createOutbox(storage?: Storage) {
  // Looked up on each use, inside try: with storage switched off, even
  // reading window.localStorage throws.
  const store = () => storage ?? window.localStorage

  function read<T>(key: string): T[] {
    try {
      const saved = JSON.parse(store().getItem(key) ?? '[]') as unknown
      return Array.isArray(saved) ? (saved as T[]) : []
    } catch {
      // Unreadable (or storage is switched off): treat it as empty.
      return []
    }
  }

  function write<T>(key: string, items: T[]): boolean {
    try {
      store().setItem(key, JSON.stringify(items))
      return true
    } catch (error) {
      // Storage is full or switched off. Rare, but say so in the console.
      console.error('Could not save to the outbox', error)
      return false
    }
  }

  /** The oldest unsent events of one learner, at most `limit` of them. */
  function pending(userId: string, limit = Infinity): EventRow[] {
    return read<EventRow>(OUTBOX_KEY)
      .filter((event) => event.user_id === userId)
      .slice(0, limit)
  }

  /** Forgets events the server has confirmed. */
  function remove(ids: string[]): void {
    const sent = new Set(ids)
    write(
      OUTBOX_KEY,
      read<EventRow>(OUTBOX_KEY).filter((event) => !sent.has(event.id)),
    )
  }

  /** The refused list exactly as stored: every learner's, damaged or not. */
  const storedRefusals = () => read<StoredRefusal | null>(REFUSED_KEY)

  return {
    pending,
    remove,

    add(event: EventRow): void {
      write(OUTBOX_KEY, [...read<EventRow>(OUTBOX_KEY), event])
    },

    count(userId: string): number {
      return pending(userId).length
    },

    /**
     * Records that the server refused an event, and moves it out of the way
     * of the others. Refused before: its entry gets the new reason and time,
     * and one more attempt.
     */
    refuse(event: EventRow, reason: string, now = Date.now()): void {
      const all = storedRefusals()
      const earlier = all.find((entry) => entry?.event?.id === event.id)
      const refusal: RefusedEvent = {
        event,
        reason,
        at: new Date(now).toISOString(),
        attempts: (earlier ? (earlier.attempts ?? 1) : 0) + 1,
      }
      // In place, so the list keeps its order and every other entry.
      const updated = earlier
        ? all.map((entry) => (entry === earlier ? refusal : entry))
        : [...all, refusal]
      // Only leaves the outbox once it's safely on the refused list.
      if (write(REFUSED_KEY, updated)) remove([event.id])
    },

    /** One learner's refused events, in the order they were first refused. */
    refused(userId: string): RefusedEvent[] {
      return storedRefusals().flatMap((entry) =>
        entry?.event?.user_id === userId
          ? [
              {
                event: entry.event,
                reason: entry.reason ?? '',
                at: entry.at ?? '',
                attempts: entry.attempts ?? 1,
              },
            ]
          : [],
      )
    },

    /** Forgets a refused event the server has now accepted. */
    forgetRefused(id: string): void {
      const all = storedRefusals()
      const others = all.filter((entry) => entry?.event?.id !== id)
      // Skipping the write when nothing matched keeps a tab holding an old
      // copy from touching the list at all.
      if (others.length < all.length) write(REFUSED_KEY, others)
    },
  }
}
