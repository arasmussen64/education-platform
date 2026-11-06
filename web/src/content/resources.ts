import type { Resource } from './types.ts'

/**
 * The privacy-enhanced YouTube player address for a video resource, starting
 * and ending where the topic says (v1 spec, F3). Null if it isn't YouTube.
 */
export function youtubeEmbedUrl(resource: Resource): string | null {
  let url: URL
  try {
    url = new URL(resource.url)
  } catch {
    return null
  }
  const host = url.hostname.replace(/^www\./, '')
  let videoId: string | null = null
  if (host === 'youtube.com' || host === 'm.youtube.com') {
    videoId = url.searchParams.get('v')
  } else if (host === 'youtu.be') {
    videoId = url.pathname.slice(1) || null
  }
  if (!videoId) return null

  const embed = new URL(`https://www.youtube-nocookie.com/embed/${videoId}`)
  if (resource.start !== undefined) {
    embed.searchParams.set('start', String(resource.start))
  }
  if (resource.end !== undefined) {
    embed.searchParams.set('end', String(resource.end))
  }
  // Suggest only videos from the same channel when the segment ends.
  embed.searchParams.set('rel', '0')
  return embed.toString()
}

/** 754 -> "12:34", 3725 -> "1:02:05". */
export function formatTime(totalSeconds: number): string {
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  const pad = (n: number) => String(n).padStart(2, '0')
  return hours > 0
    ? `${hours}:${pad(minutes)}:${pad(seconds)}`
    : `${minutes}:${pad(seconds)}`
}
