import { useId } from 'react'
import { formatTime, youtubeEmbedUrl } from '../content/resources.ts'
import type { Resource } from '../content/types.ts'

/** The part of a video to watch, when the resource names one. */
function clipOf(resource: Resource) {
  if (resource.start === undefined || resource.end === undefined) return null
  const minutes = Math.max(1, Math.round((resource.end - resource.start) / 60))
  return {
    from: formatTime(resource.start),
    to: formatTime(resource.end),
    length: `about ${minutes} ${minutes === 1 ? 'minute' : 'minutes'}`,
  }
}

/**
 * A lesson's main resource (v1 spec, F3): an embedded video segment, or a
 * link to a reading. Always credits the source and shows its license.
 */
export function ResourceView({ resource }: { resource: Resource }) {
  const clipNoteId = useId()
  const embed =
    resource.type === 'video' && resource.use === 'embed'
      ? youtubeEmbedUrl(resource)
      : null
  const clip = clipOf(resource)

  return (
    <figure className="space-y-2">
      {embed && clip && (
        // YouTube's player always shows the whole video's length, so a short
        // clip of a long lecture looks long. Say what to watch before it.
        <p id={clipNoteId} className="text-sm">
          <span className="font-semibold">
            This clip: {clip.from} to {clip.to} ({clip.length}).
          </span>{' '}
          The player shows the length of the whole video, but it stops by itself
          at {clip.to}.
        </p>
      )}
      {embed ? (
        <div className="aspect-video overflow-hidden rounded-md bg-black">
          <iframe
            src={embed}
            title={resource.title}
            aria-describedby={clip ? clipNoteId : undefined}
            className="h-full w-full"
            allow="encrypted-media; picture-in-picture; fullscreen"
            // YouTube's player needs to know which site embeds it.
            referrerPolicy="strict-origin-when-cross-origin"
            // Load the player only when it's about to scroll into view.
            loading="lazy"
            allowFullScreen
          />
        </div>
      ) : (
        <a
          href={resource.url}
          target="_blank"
          rel="noreferrer"
          className="block rounded-md border border-slate-300 p-4 font-medium hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
        >
          {resource.title} ↗
        </a>
      )}
      <figcaption className="text-xs text-slate-500 dark:text-slate-400">
        {embed ? (
          <>
            {resource.title}
            {clip && ` (${clip.from}–${clip.to})`}.{' '}
            <a
              href={resource.url}
              target="_blank"
              rel="noreferrer"
              className="underline"
            >
              Open the original
            </a>
            . License: {resource.license}.
          </>
        ) : (
          // The link above already shows the title and opens the original.
          <>License: {resource.license}.</>
        )}
      </figcaption>
    </figure>
  )
}
