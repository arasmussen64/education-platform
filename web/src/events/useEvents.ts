import { useContext, useSyncExternalStore } from 'react'
import type { EventLogStatus } from './eventLog.ts'
import { EventLogContext } from './eventLogContext.ts'
import type { NewEvent } from './types.ts'

/** Returns the function that records a learner event. */
export function useRecordEvent(): (event: NewEvent) => void {
  return useContext(EventLogContext).record
}

/** How many events are waiting to be saved, kept up to date. */
export function useEventLogStatus(): EventLogStatus {
  const log = useContext(EventLogContext)
  return useSyncExternalStore(log.subscribe, log.getStatus)
}
