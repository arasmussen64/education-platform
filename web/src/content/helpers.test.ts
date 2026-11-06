import { describe, expect, it } from 'vitest'
import { normalizeOutput } from './answers.ts'
import { formatTime, youtubeEmbedUrl } from './resources.ts'
import type { Resource } from './types.ts'

function video(url: string, times: Partial<Resource> = {}): Resource {
  return {
    title: 'A video',
    url,
    type: 'video',
    use: 'embed',
    license: 'CC BY 4.0',
    ...times,
  }
}

describe('youtubeEmbedUrl', () => {
  it('uses the privacy-enhanced player, starting and ending on time', () => {
    const embed = youtubeEmbedUrl(
      video('https://www.youtube.com/watch?v=abc123', { start: 65, end: 190 }),
    )
    expect(embed).toBe(
      'https://www.youtube-nocookie.com/embed/abc123?start=65&end=190&rel=0',
    )
  })

  it('understands short youtu.be links', () => {
    expect(youtubeEmbedUrl(video('https://youtu.be/abc123'))).toBe(
      'https://www.youtube-nocookie.com/embed/abc123?rel=0',
    )
  })

  it("gives nothing for videos that aren't on YouTube", () => {
    expect(youtubeEmbedUrl(video('https://example.com/watch?v=1'))).toBeNull()
    expect(youtubeEmbedUrl(video('not a url'))).toBeNull()
  })
})

describe('formatTime', () => {
  it('writes seconds the way video players do', () => {
    expect(formatTime(5)).toBe('0:05')
    expect(formatTime(754)).toBe('12:34')
    expect(formatTime(3725)).toBe('1:02:05')
  })
})

describe('normalizeOutput', () => {
  it('ignores line endings, trailing spaces and blank lines at the edges', () => {
    expect(normalizeOutput('\r\na  \r\nb\r\n\r\n')).toBe('a\nb')
  })

  it('keeps spaces at the start of a line and blank lines in the middle', () => {
    expect(normalizeOutput('  a\n\nb\n')).toBe('  a\n\nb')
  })
})
