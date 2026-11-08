import { useRef } from 'react'

/**
 * Time spent on an attempt: from the learner's first touch of the item, or
 * from their previous attempt, until now. Time spent reading the lesson above
 * doesn't count.
 */
export function useAttemptTimer() {
  const startedAt = useRef<number | null>(null)
  return {
    start() {
      startedAt.current ??= Date.now()
    },
    /** The time since the start, then starts timing the next attempt. */
    lap(): number | null {
      const now = Date.now()
      const started = startedAt.current
      startedAt.current = now
      return started === null ? null : now - started
    },
  }
}
