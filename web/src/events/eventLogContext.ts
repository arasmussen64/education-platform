import { createContext } from 'react'
import type { EventLog, EventLogStatus } from './eventLog.ts'

const NOTHING_WAITING: EventLogStatus = { pending: 0, syncing: false }

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
  stop() {},
}

export const EventLogContext = createContext<EventLog>(RECORDS_NOTHING)
