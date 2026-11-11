import { describe, expect, it, vi } from 'vitest'
import type { LoaderFunctionArgs } from 'react-router'
import { loadTopicContent } from '../content/content.ts'
import { topicLoader } from './topicLoader.ts'

// The real content loads as usual, unless a test makes a download fail.
vi.mock('../content/content.ts', async (importOriginal) => {
  const content = await importOriginal<typeof import('../content/content.ts')>()
  return { ...content, loadTopicContent: vi.fn(content.loadTopicContent) }
})

/** Calls the loader the way the router would, with just the address. */
function load(topicId: string) {
  const args = {
    params: { topicId },
    request: new Request(`http://localhost/topic/${topicId}`),
  }
  return topicLoader(args as unknown as LoaderFunctionArgs)
}

describe('the topic loader', () => {
  it("loads a topic's content and a question from the topic before it", async () => {
    const { topic, content, interleaved } = await load('py.values-and-types')
    expect(topic?.id).toBe('py.values-and-types')
    expect(content?.topic.id).toBe('py.values-and-types')
    expect(interleaved?.content.topic.id).toBe('py.programs-and-print')
    expect(Object.keys(interleaved?.content.recall ?? {})).toContain(
      interleaved?.itemId,
    )
  })

  it("still opens the topic when the question to mix in can't download", async () => {
    // The topic's own content loads; the earlier topic's doesn't.
    const real = vi.mocked(loadTopicContent).getMockImplementation()
    vi.mocked(loadTopicContent).mockImplementation(async (topicId) => {
      if (topicId === 'py.programs-and-print') throw new Error('offline')
      return real ? real(topicId) : null
    })
    try {
      const { content, interleaved } = await load('py.values-and-types')
      expect(content?.topic.id).toBe('py.values-and-types')
      expect(interleaved).toBeNull()
    } finally {
      if (real) vi.mocked(loadTopicContent).mockImplementation(real)
    }
  })

  it("fails when the topic's own content can't download", async () => {
    vi.mocked(loadTopicContent).mockRejectedValueOnce(new Error('offline'))
    await expect(load('py.values-and-types')).rejects.toThrow('offline')
  })

  it('has nothing to mix in for the first topic', async () => {
    const { content, interleaved } = await load('py.programs-and-print')
    expect(content).not.toBeNull()
    expect(interleaved).toBeNull()
  })

  it('loads nothing for a topic that is still an outline, or unknown', async () => {
    // The cloud track's outlines aren't bundled in; the loader fetches them.
    // A Module 3 topic: Modules 1 and 2 have real content.
    expect(await load('csa.net.cidr')).toMatchObject({
      topic: { id: 'csa.net.cidr', status: 'planned' },
      content: null,
      interleaved: null,
    })
    expect(await load('py.nothing')).toEqual({
      topic: undefined,
      content: null,
      interleaved: null,
    })
  })
})
