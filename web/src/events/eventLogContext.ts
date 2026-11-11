import { createContext } from 'react'
import type { EventLog, EventLogStatus } from './eventLog.ts'
import type { RefusedEvent } from './outbox.ts'
import type { EventRow } from './types.ts'

const NOTHING_WAITING: EventLogStatus = {
  pending: 0,
  syncing: false,
  refused: 0,
}
const NO_ROWS: EventRow[] = []
const NONE_REFUSED: RefusedEvent[] = []

/**
 * Used when there's no <EventsProvider> around a component, as in most
 * component tests: it records nothing. The app always has the provider
 * (main.tsx).
 */
const RECORDS_NOTHING: EventLog = {
  record() {},
  setUser() {},
  async sync() {},
  subscribe: () => () => {},
  getStatus: () => NOTHING_WAITING,
  getLocalRows: () => NO_ROWS,
  getPendingRows: () => NO_ROWS,
  getRefusedEvents: () => NONE_REFUSED,
  stop() {},
}

export const EventLogContext = createContext<EventLog>(RECORDS_NOTHING)
