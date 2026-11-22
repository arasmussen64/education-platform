import { useEffect, useMemo, useState } from 'react'
import { readingToReact } from '../content/readingHtml.tsx'
import type { Resource } from '../content/types.ts'
import { READING } from './styles.ts'

type Loaded =
  | { status: 'loading' }
  | { status: 'ready'; html: string }
  | { status: 'failed' }

/**
 * A reading's own words, shown inside the lesson (ADR-0031), so the learner
 * doesn't have to leave the page to read it. It is somebody else's text,
 * copied under its licence, so it sits in a box of its own with its credit:
 * whose it is, the licence, what was changed, and a link to the original.
 */
export function ReadingText({
  resource,
  load,
}: {
  resource: Resource
  /** Fetches the copy: it's downloaded only when it's shown. */
  load: () => Promise<string>
}) {
  const [loaded, setLoaded] = useState<Loaded>({ status: 'loading' })
  useEffect(() => {
    let current = true
    load().then(
      (html) => current && setLoaded({ status: 'ready', html }),
      () => current && setLoaded({ status: 'failed' }),
    )
    return () => {
      current = false
    }
  }, [load])
  const body = useMemo(
    () => (loaded.status === 'ready' ? readingToReact(loaded.html) : null),
    [loaded],
  )
  const text = resource.text
  if (!text) return null

  return (
    <figure className="space-y-2">
      <figcaption className="text-sm">
        <span className="font-semibold">The reading:</span> {resource.title}.{' '}
        <a
          href={resource.url}
          target="_blank"
          rel="noreferrer"
          className="underline"
        >
          Open the original ↗
        </a>
      </figcaption>
      <div className="rounded-md border border-line-strong bg-card p-4">
        {loaded.status === 'loading' && <p>Loading the reading…</p>}
        {loaded.status === 'failed' && (
          <p role="alert">
            The reading didn't load. Use "Open the original", above.
          </p>
        )}
        {body && <div className={READING}>{body}</div>}
      </div>
      <p className="text-xs text-muted">
        These are the source's words, not ours: by {text.by}.{' '}
        {text.notice && <>{text.notice} </>}
        License:{' '}
        <a
          href={text.license_url}
          target="_blank"
          rel="noreferrer"
          className="underline"
        >
          {resource.license}
        </a>
        . Changes: {text.changes} Copied on {text.retrieved}.
      </p>
    </figure>
  )
}
