import { formatTime, youtubeEmbedUrl } from '../content/resources.ts'
import type { Resource } from '../content/types.ts'

/**
 * A lesson's main resource (v1 spec, F3): an embedded video segment, or a
 * link to a reading. Always credits the source and shows its license.
 */
export function ResourceView({ resource }: { resource: Resource }) {
  const embed =
    resource.type === 'video' && resource.use === 'embed'
      ? youtubeEmbedUrl(resource)
      : null
  const segment =
    resource.start !== undefined && resource.end !== undefined
      ? ` (${formatTime(resource.start)}–${formatTime(resource.end)})`
      : ''

  return (
    <figure className="space-y-2">
      {embed ? (
        <div className="aspect-video overflow-hidden rounded-md bg-black">
          <iframe
            src={embed}
            title={resource.title}
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
        {resource.title}
        {segment}.{' '}
        <a
          href={resource.url}
          target="_blank"
          rel="noreferrer"
          className="underline"
        >
          Open the original
        </a>
        . License: {resource.license}.
      </figcaption>
    </figure>
  )
}
