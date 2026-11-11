import { useEffect, useMemo, useState } from 'react'
import { loadTopicContent } from '../content/content.ts'
import type { TopicContent } from '../content/types.ts'

export type ContentsState =
  | { status: 'loading' }
  | { status: 'failed'; retry: () => void }
  | { status: 'ready'; contents: Map<string, TopicContent> }

/**
 * Loads the topics named in `key`, one ID per line, and gives back those
 * found, by ID (an unknown topic loads as null).
 */
async function loadAll(key: string): Promise<Map<string, TopicContent>> {
  const ids = key.split('\n').filter((id) => id !== '')
  const found = await Promise.all(ids.map(loadTopicContent))
  const contents = found.filter((content) => content !== null)
  return new Map(contents.map((content) => [content.topic.id, content]))
}

/**
 * The full content (lesson, questions and exercises) of the topics a page is
 * about to show, by topic ID: on the Today page, the topics of its review
 * sessions and of its mistakes to revisit. `ids` is null until the page
 * knows which topics those are, and is meant to be decided once.
 *
 * A download can fail: offline, or after a new version of the site has
 * replaced a file an open tab still asks for. Then `retry` tries again.
 */
export function useTopicContents(ids: readonly string[] | null): ContentsState {
  const [loaded, setLoaded] = useState<
    Map<string, TopicContent> | 'loading' | 'failed'
  >('loading')
  const [tries, setTries] = useState(0)
  // The IDs as one string, so a new list of the same topics loads nothing.
  const key = useMemo(() => (ids === null ? null : ids.join('\n')), [ids])

  useEffect(() => {
    if (key === null) return
    let active = true
    loadAll(key).then(
      (found) => {
        if (active) setLoaded(found)
      },
      () => {
        if (active) setLoaded('failed')
      },
    )
    return () => {
      active = false
    }
  }, [key, tries])

  return useMemo<ContentsState>(() => {
    if (loaded === 'loading') return { status: 'loading' }
    if (loaded === 'failed') {
      return {
        status: 'failed',
        retry: () => {
          setLoaded('loading')
          setTries((count) => count + 1)
        },
      }
    }
    return { status: 'ready', contents: loaded }
  }, [loaded])
}
