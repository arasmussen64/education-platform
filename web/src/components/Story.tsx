import { type ReactNode, useId } from 'react'

type Props = {
  /** What happened, in a few words: "Cloudflare's regex outage, 2019". */
  title: string
  /** The public postmortem or report the story is drawn from (https). */
  source: string
  /** That page's own title, the link's text. */
  sourceTitle: string
  /** The source's licence, or "linked, not copied" (ADR-0004). */
  license: string
  /** The story, in the platform's own words. */
  children?: ReactNode
  /** A place on the page the outline can point at (LessonView sets it). */
  id?: string
  'data-place'?: string
}

/**
 * A real incident the topic explains (ADR-0026): a short account, in our own
 * words, of a public outage, with a link to the postmortem it's drawn from.
 * A real story gives an idea a reason to matter and something to hang it on.
 */
export function Story({
  title,
  source,
  sourceTitle,
  license,
  children,
  id,
  ...rest
}: Props) {
  const headingId = `${useId()}-story`
  // The validator only lets https links through; this keeps any other kind
  // (a javascript: link, say) off the page even if one slipped past.
  const safeSource = source.startsWith('https://') ? source : null
  return (
    <aside
      id={id}
      data-place={rest['data-place']}
      aria-labelledby={headingId}
      className="space-y-2 rounded-lg border border-l-4 border-line border-l-muted bg-card p-4"
    >
      <p className="text-xs font-semibold tracking-wide text-muted uppercase">
        A real incident
      </p>
      <p id={headingId} className="font-display text-lg font-semibold">
        {title}
      </p>
      {children}
      <p className="text-sm text-muted">
        Told in our own words, from{' '}
        {safeSource ? (
          <a
            href={safeSource}
            target="_blank"
            rel="noreferrer"
            className="wrap-anywhere underline"
          >
            {sourceTitle}
          </a>
        ) : (
          sourceTitle
        )}{' '}
        ({license}).
      </p>
    </aside>
  )
}
