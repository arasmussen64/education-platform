// Which fresh version of a checkpoint exercise to offer: of the main build,
// in the way through (Unstuck.tsx), or of a further part (MoreParts.tsx).
import { useContext, useEffect, useState } from 'react'
import { useAuth } from '../auth/useAuth.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import type { Attempt } from '../followups/followUps.ts'
import { localAttempt, mergeAttempts } from '../followups/history.ts'
import { chooseVersion } from './versions.ts'

/** Reads the learner's attempts in one topic. Tests pass a fake. */
export type LoadAttempts = (topicId: string) => Promise<Attempt[]>

/**
 * The fresh version to offer, chosen once from the learner's history so it
 * can't change while they work on it. Signed-out learners have no saved
 * history, so they get the first.
 */
export function useFreshVersion(
  topicId: string,
  versions: string[],
  loadAttempts: LoadAttempts,
): string | null {
  const auth = useAuth()
  const log = useContext(EventLogContext)
  const [fetched, setFetched] = useState<Attempt[] | null>(null)
  const [choice, setChoice] = useState<{ version: string | null } | null>(null)

  useEffect(() => {
    if (auth.status !== 'signed-in') return
    let active = true
    loadAttempts(topicId).then(
      (attempts) => {
        if (active) setFetched(attempts)
      },
      // Which version comes first is only a preference: without the
      // history, offer the first.
      () => {
        if (active) setFetched([])
      },
    )
    return () => {
      active = false
    }
  }, [auth.status, loadAttempts, topicId])

  const history = auth.status === 'signed-out' ? [] : fetched
  if (choice === null && history !== null) {
    // Checks from this visit may not have reached the server yet.
    const local = log
      .getLocalRows()
      .map(localAttempt)
      .filter((attempt) => attempt !== null)
    setChoice({
      version: chooseVersion(topicId, versions, mergeAttempts(history, local)),
    })
  }
  return choice?.version ?? null
}
