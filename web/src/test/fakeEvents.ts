// Stand-ins for saving learner events, for tests.
import { vi } from 'vitest'
import type { EventLog } from '../events/eventLog.ts'
import type { EventsClient, SendResult } from '../events/sync.ts'
import type { EventRow, NewEvent } from '../events/types.ts'

const NO_ROWS: EventRow[] = []

/**
 * An event log that only collects what's recorded. Put it around a component
 * with <EventLogContext value={log}> and look at `events`.
 */
export function recordingEventLog() {
  const events: NewEvent[] = []
  const log: EventLog = {
    record: (event) => {
      events.push(event)
    },
    setUser() {},
    async sync() {},
    subscribe: () => () => {},
    getStatus: () => ({ pending: 0, syncing: false }),
    getLocalRows: () => NO_ROWS,
    getPendingRows: () => NO_ROWS,
    stop() {},
  }
  return { log, events }
}

/** A fake server. By default it accepts everything it's sent. */
export function fakeEventsClient(result: SendResult = { ok: true }) {
  return {
    send: vi.fn((_events: EventRow[]): Promise<SendResult> =>
      Promise.resolve(result),
    ),
  } satisfies EventsClient
}

/** A complete event row, with whatever fields a test cares about. */
export function eventRow(overrides: Partial<EventRow> = {}): EventRow {
  return {
    id: crypto.randomUUID(),
    user_id: '11111111-1111-1111-1111-111111111111',
    type: 'answer',
    topic_id: 'py.variables',
    item_id: 'mcq-1',
    context: 'practice',
    correct: true,
    duration_ms: 1000,
    hints_used: 0,
    item_rev: 1,
    content_build: 'abc123',
    session_id: '22222222-2222-2222-2222-222222222222',
    occurred_at: '2026-11-06T12:00:00.000Z',
    data: {},
    ...overrides,
  }
}
