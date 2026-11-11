import type { Outbox, RefusedEvent } from './outbox.ts'
import { type EventsClient, retryRefused, syncOutbox } from './sync.ts'
import type { EventRow, NewEvent } from './types.ts'

export type EventLogStatus = {
  /** Events on this device that the server doesn't have yet. */
  pending: number
  /** True while sending. */
  syncing: boolean
  /**
   * Events the server refused, kept on this device and tried again later.
   * They aren't part of `pending`.
   */
  refused: number
}

/** Records learner events and gets them to the server (v1 spec, F6). */
export type EventLog = {
  /** Adds an event (nothing happens while signed out). */
  record(event: NewEvent): void
  /** Who's signed in: an ID, null when signed out, undefined while loading. */
  setUser(userId: string | null | undefined): void
  /** Sends whatever is waiting, now. */
  sync(): Promise<void>
  /** For React's useSyncExternalStore: status changes. */
  subscribe(listener: () => void): () => void
  getStatus(): EventLogStatus
  /**
   * The signed-in learner's events that this device knows about: what's
   * still in the outbox, plus everything recorded since the page opened.
   * Kept even after it's sent, so a page reading history from the server
   * never misses an answer that's on its way there. A new array whenever it
   * changes, for React's useSyncExternalStore.
   */
  getLocalRows(): EventRow[]
  /**
   * The signed-in learner's events still waiting in this device's outbox,
   * read fresh each time, so it includes what other tabs recorded. The data
   * export adds these, because the server doesn't have them yet.
   */
  getPendingRows(): EventRow[]
  /**
   * The signed-in learner's events that the server refused, each with the
   * reason, the time it was last tried and how often. Read fresh each time.
   * The data export lists them, and the account page counts them.
   */
  getRefusedEvents(): RefusedEvent[]
  /** Cancels any scheduled retry. */
  stop(): void
}

/** A study session ends after this long without any activity. */
export const SESSION_IDLE_MS = 30 * 60 * 1000
/** After a failed send, wait this long, then twice as long, and so on... */
export const FIRST_RETRY_MS = 5_000
/** ...but never longer than this. */
const LONGEST_RETRY_MS = 5 * 60 * 1000
/** Events recorded before sign-in has loaded wait in memory: at most this many. */
const MAX_WAITING = 100

type Options = {
  outbox: Outbox
  /** Where events are sent. Only called when there's something to send. */
  client: () => EventsClient
  /** The git commit the app and content were built from. */
  contentBuild: string
  /** Tests pass fakes for the clock and the ID generator. */
  now?: () => number
  newId?: () => string
}

export function createEventLog({
  outbox,
  client,
  contentBuild,
  now = Date.now,
  newId = () => crypto.randomUUID(),
}: Options): EventLog {
  let userId: string | null | undefined = undefined
  let session = { id: newId(), lastActivity: now() }
  // Recorded while sign-in was still loading; they get the user ID later.
  let waiting: Omit<EventRow, 'user_id'>[] = []
  let syncing = false
  let syncAgain = false
  let retryTimer: ReturnType<typeof setTimeout> | undefined
  let retryDelay = FIRST_RETRY_MS
  let status: EventLogStatus = { pending: 0, syncing: false, refused: 0 }
  let localRows: EventRow[] = []
  const listeners = new Set<() => void>()

  function notify() {
    for (const listener of listeners) listener()
  }

  function updateStatus() {
    const pending = userId ? outbox.count(userId) : 0
    const refused = userId ? outbox.refused(userId).length : 0
    if (
      pending === status.pending &&
      syncing === status.syncing &&
      refused === status.refused
    ) {
      return
    }
    status = { pending, syncing, refused }
    notify()
  }

  function sessionId(time: number): string {
    if (time - session.lastActivity > SESSION_IDLE_MS) {
      session = { id: newId(), lastActivity: time }
    }
    session.lastActivity = time
    return session.id
  }

  /** Every column, filled in, so each row in a batch has the same shape. */
  function toRow(event: NewEvent): Omit<EventRow, 'user_id'> {
    const time = now()
    return {
      id: newId(),
      type: event.type,
      topic_id: event.topic_id,
      item_id: event.item_id ?? null,
      context: event.context,
      correct: event.correct ?? null,
      duration_ms:
        event.duration_ms == null
          ? null
          : Math.max(0, Math.round(event.duration_ms)),
      hints_used: event.hints_used ?? 0,
      item_rev: event.item_rev ?? null,
      content_build: contentBuild,
      session_id: sessionId(time),
      occurred_at: new Date(time).toISOString(),
      data: event.data ?? {},
    }
  }

  function scheduleRetry() {
    clearTimeout(retryTimer)
    retryTimer = setTimeout(() => void log.sync(), retryDelay)
    retryDelay = Math.min(retryDelay * 2, LONGEST_RETRY_MS)
  }

  /**
   * Gives the learner's refused events another try (see retryRefused). It
   * comes after a save that went through, and whatever happens here leaves
   * that save finished: no retry timer is started for it. The events wait
   * for the next save instead.
   */
  async function retryRefusedEvents(user: string): Promise<void> {
    try {
      // Stops if the sign-in changes partway through, as it can when the
      // learner signs out here or in another tab.
      await retryRefused(outbox, client(), user, now(), () => userId === user)
    } catch (error) {
      console.error('Retrying refused events failed', error)
    }
  }

  const log: EventLog = {
    record(event) {
      // Signed-out visitors' answers aren't saved anywhere.
      if (userId === null) return
      const row = toRow(event)
      if (userId === undefined) {
        if (waiting.length < MAX_WAITING) waiting.push(row)
        return
      }
      const stored = { ...row, user_id: userId }
      outbox.add(stored)
      localRows = [...localRows, stored]
      notify()
      void log.sync()
      updateStatus()
    },

    setUser(id) {
      if (id === userId) return
      userId = id
      clearTimeout(retryTimer)
      retryDelay = FIRST_RETRY_MS
      if (id) {
        for (const row of waiting) outbox.add({ ...row, user_id: id })
      }
      if (id !== undefined) waiting = []
      localRows = id ? outbox.pending(id) : []
      notify()
      updateStatus()
      void log.sync()
    },

    async sync() {
      if (!userId) return
      if (syncing) {
        // Already sending: go round once more afterwards for anything new.
        syncAgain = true
        return
      }
      const user = userId
      clearTimeout(retryTimer)
      syncing = true
      updateStatus()

      let result: 'done' | 'retry-later'
      try {
        result = await syncOutbox(outbox, client(), user, now())
      } catch (error) {
        console.error('Saving progress failed', error)
        result = 'retry-later'
      }
      // Still `syncing` here, so two retries can never run at once. Only for
      // whoever is signed in now: the server takes events from nobody else.
      if (result === 'done' && userId === user) await retryRefusedEvents(user)

      syncing = false
      if (result === 'done') {
        retryDelay = FIRST_RETRY_MS
      } else if (userId === user) {
        scheduleRetry()
      }
      updateStatus()
      if (syncAgain) {
        syncAgain = false
        void log.sync()
      }
    },

    subscribe(listener) {
      listeners.add(listener)
      return () => {
        listeners.delete(listener)
      }
    },

    getStatus: () => status,

    getLocalRows: () => localRows,

    getPendingRows: () => (userId ? outbox.pending(userId) : []),

    getRefusedEvents: () => (userId ? outbox.refused(userId) : []),

    stop() {
      clearTimeout(retryTimer)
    },
  }
  return log
}
