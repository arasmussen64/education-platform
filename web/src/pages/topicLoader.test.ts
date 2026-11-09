import { describe, expect, it } from 'vitest'
import type { LoaderFunctionArgs } from 'react-router'
import { topicLoader } from './topicLoader.ts'

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

  it('has nothing to mix in for the first topic', async () => {
    const { content, interleaved } = await load('py.programs-and-print')
    expect(content).not.toBeNull()
    expect(interleaved).toBeNull()
  })

  it('loads nothing for a topic that is still an outline, or unknown', async () => {
    // The cloud track's outlines aren't bundled in; the loader fetches them.
    expect(await load('csa.hw.hypervisors')).toMatchObject({
      topic: { id: 'csa.hw.hypervisors', status: 'planned' },
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
