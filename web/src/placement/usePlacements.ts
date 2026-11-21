import {
  useContext,
  useEffect,
  useMemo,
  useState,
  useSyncExternalStore,
} from 'react'
import { useAuth } from '../auth/useAuth.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import {
  fetchResets,
  latestResets,
  localResets,
  type TrackReset,
  trackOfPlacement,
  wasReset,
} from '../resets/resets.ts'
import {
  fetchPlacements,
  latestBySubject,
  localPlacements,
  mergePlacements,
  type PlacementRecord,
} from './history.ts'

export type PlacementsState =
  | { status: 'signed-out' }
  | { status: 'loading' }
  | { status: 'failed' }
  | {
      status: 'ready'
      /** Every finished run, oldest first. */
      all: PlacementRecord[]
      /** The newest run for each track or diagnostic. */
      latest: Map<string, PlacementRecord>
    }

type Fetched = {
  userId: string
  history: { records: PlacementRecord[]; resets: TrackReset[] } | 'failed'
}

/**
 * The signed-in learner's finished placements (ADR-0021). Read from the
 * server once; a run finished on this device shows straight away. A run on
 * a track the learner has since started over no longer counts (ADR-0029).
 */
export function usePlacements(
  load: () => Promise<PlacementRecord[]> = fetchPlacements,
): PlacementsState {
  const auth = useAuth()
  const log = useContext(EventLogContext)
  const localRows = useSyncExternalStore(log.subscribe, log.getLocalRows)
  const userId = auth.status === 'signed-in' ? auth.user.id : null
  const [fetched, setFetched] = useState<Fetched | null>(null)

  useEffect(() => {
    if (!userId) return
    let active = true
    Promise.all([load(), fetchResets()]).then(
      ([records, resets]) => {
        if (active) setFetched({ userId, history: { records, resets } })
      },
      () => {
        if (active) setFetched({ userId, history: 'failed' })
      },
    )
    return () => {
      active = false
    }
  }, [userId, load])

  return useMemo<PlacementsState>(() => {
    if (auth.status === 'signed-out') return { status: 'signed-out' }
    if (fetched === null || fetched.userId !== userId) {
      return { status: 'loading' }
    }
    if (fetched.history === 'failed') return { status: 'failed' }
    const resets = latestResets(fetched.history.resets, localResets(localRows))
    const all = mergePlacements(
      fetched.history.records,
      localPlacements(localRows),
    ).filter((record) => !wasReset(trackOfPlacement(record), record.at, resets))
    return { status: 'ready', all, latest: latestBySubject(all) }
  }, [auth.status, fetched, userId, localRows])
}
