import type { EventRow } from './types.ts'

// The outbox keeps events on this device until the server confirms it has
// them (v1 spec, F6), so closing the tab or losing the connection loses
// nothing. It lives in the browser's localStorage.
//
// Several tabs can share it, so every change reads the latest copy and writes
// it straight back, with no waiting in between: one tab never overwrites
// another's events with an old copy.

const OUTBOX_KEY = 'learner-events-outbox-v1'
const REJECTED_KEY = 'learner-events-rejected-v1'

/** An event the server refused, kept on the device for investigation. */
export type RejectedEvent = { event: EventRow; reason: string; at: string }

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

  return {
    pending,
    remove,

    add(event: EventRow): void {
      write(OUTBOX_KEY, [...read<EventRow>(OUTBOX_KEY), event])
    },

    count(userId: string): number {
      return pending(userId).length
    },

    /** Moves an event the server refused out of the way of the others. */
    reject(event: EventRow, reason: string): void {
      const rejected: RejectedEvent = {
        event,
        reason,
        at: new Date().toISOString(),
      }
      if (write(REJECTED_KEY, [...read(REJECTED_KEY), rejected])) {
        remove([event.id])
      }
    },

    rejected(): RejectedEvent[] {
      return read<RejectedEvent>(REJECTED_KEY)
    },
  }
}
