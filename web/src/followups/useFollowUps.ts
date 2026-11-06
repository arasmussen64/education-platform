import {
  useContext,
  useEffect,
  useMemo,
  useState,
  useSyncExternalStore,
} from 'react'
import { getTopic, isOpen, loadTopicContent } from '../content/content.ts'
import type { TopicContent } from '../content/types.ts'
import type { EventLog } from '../events/eventLog.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import {
  type Attempt,
  type FollowUp,
  openFollowUps,
  skillsIn,
  topicsWithMisses,
} from './followUps.ts'
import { fetchAttempts, mergeAttempts, toAttempt } from './history.ts'

export type FollowUpsState =
  | { status: 'loading' }
  | { status: 'failed'; retry: () => void }
  | {
      status: 'ready'
      /** The whole history, server and this device together. */
      attempts: Attempt[]
      /** Content for every topic with a miss, by topic ID. */
      contents: Map<string, TopicContent>
      open: FollowUp[]
    }

type Loaded = { fetched: Attempt[]; contents: Map<string, TopicContent> }

function localAttempts(log: EventLog): Attempt[] {
  return log
    .getLocalRows()
    .map(toAttempt)
    .filter((attempt) => attempt !== null)
}

/** Reads the history, then loads the topics where something was missed. */
async function loadHistory(
  load: () => Promise<Attempt[]>,
  log: EventLog,
): Promise<Loaded> {
  const fetched = await load()
  const topicIds = topicsWithMisses(
    mergeAttempts(fetched, localAttempts(log)),
  ).filter((id) => {
    const topic = getTopic(id)
    return topic !== undefined && isOpen(topic)
  })
  const contents = new Map<string, TopicContent>()
  for (const content of await Promise.all(topicIds.map(loadTopicContent))) {
    if (content) contents.set(content.topic.id, content)
  }
  return { fetched, contents }
}

/**
 * The signed-in learner's follow-ups (ADR-0011). The history is read from
 * the server once; after that, answers given on this device update the
 * result straight away, with no reload.
 */
export function useFollowUps(
  load: () => Promise<Attempt[]> = fetchAttempts,
): FollowUpsState {
  const log = useContext(EventLogContext)
  const localRows = useSyncExternalStore(log.subscribe, log.getLocalRows)
  const [loaded, setLoaded] = useState<Loaded | 'loading' | 'failed'>('loading')
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let active = true
    loadHistory(load, log).then(
      (result) => {
        if (active) setLoaded(result)
      },
      () => {
        if (active) setLoaded('failed')
      },
    )
    return () => {
      active = false
    }
  }, [load, log, attempt])

  return useMemo<FollowUpsState>(() => {
    if (loaded === 'loading') return { status: 'loading' }
    if (loaded === 'failed') {
      return {
        status: 'failed',
        retry: () => {
          setLoaded('loading')
          setAttempt((count) => count + 1)
        },
      }
    }
    const local = localRows.map(toAttempt).filter((attempt) => attempt !== null)
    const attempts = mergeAttempts(loaded.fetched, local)
    return {
      status: 'ready',
      attempts,
      contents: loaded.contents,
      open: openFollowUps(attempts, skillsIn(loaded.contents)),
    }
  }, [loaded, localRows])
}
