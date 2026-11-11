import index from 'virtual:skill-index'
import { describe, expect, it } from 'vitest'
import {
  getTopic,
  loadTopicContent,
  loadTrackOf,
  topicIdsOf,
  tracks,
} from '../content/content.ts'
import type { TopicContent } from '../content/types.ts'
import { loadSkillIndex, openItemsOf, type SkillIndex } from './skillIndex.ts'

// The skill index is built from the content files while building
// (vite.config.ts). This checks it against the content as a topic page loads
// it, for every topic, so a change to either that makes them disagree shows
// up here.

/** What the index should hold for a topic, from its full content. */
function expectedFor(content: TopicContent) {
  const expected: Record<string, unknown> = {}
  for (const exercise of Object.values(content.exercises)) {
    const tests = exercise.test_skills
    expected[exercise.id] = {
      skills: exercise.skills,
      stage: exercise.stage,
      ...(Object.keys(tests).length > 0 ? { test_skills: tests } : {}),
    }
  }
  for (const item of Object.values(content.recall)) {
    expected[item.id] = { skills: item.skills }
  }
  return expected
}

// The topics bundled with the app, and any other the index names (say, a
// lazy track's topic being written).
const topicIds = [
  ...new Set([
    ...tracks()
      .flatMap(topicIdsOf)
      .filter((id) => getTopic(id) !== undefined),
    ...Object.keys(index),
  ]),
].sort()

describe.each(topicIds)('%s', (topicId) => {
  // Loading a topic's thirty-odd files can pass the default 5 s on a busy
  // machine, especially for the first topic, which waits for the set-up.
  it(
    'is in the skill index as in its content',
    { timeout: 20_000 },
    async () => {
      await loadTrackOf(topicId)
      const content = await loadTopicContent(topicId)
      if (!content) throw new Error(`${topicId} has items but no topic.yaml`)
      expect(index[topicId] ?? {}).toEqual(expectedFor(content))
    },
  )
})

describe('the skill index', () => {
  it('covers the topics with questions', () => {
    expect(index['py.programs-and-print']?.['predict-four-lines']).toEqual({
      skills: ['print-commas'],
    })
    expect(index['py.programs-and-print']?.['write-recipe-card']).toMatchObject(
      { stage: 'write' },
    )
  })

  it('downloads once, and is shared after that', async () => {
    const first = loadSkillIndex()
    expect(loadSkillIndex()).toBe(first)
    expect(await first).toBe(index)
  })
})

describe('openItemsOf', () => {
  const planned = tracks()
    .flatMap(topicIdsOf)
    .find((id) => getTopic(id)?.status === 'planned')
  const fake: SkillIndex = {
    'py.programs-and-print': { 'mcq-print': { skills: ['print-text'] } },
    [planned ?? '']: { 'mcq-later': { skills: ['later'] } },
  }

  it("gives an open topic's items", () => {
    expect(openItemsOf(fake)('py.programs-and-print')).toEqual({
      'mcq-print': { skills: ['print-text'] },
    })
  })

  it("gives nothing for a topic that can't be opened, or isn't known", () => {
    expect(planned).toBeDefined()
    expect(openItemsOf(fake)(planned ?? '')).toBeUndefined()
    expect(openItemsOf(fake)('py.nothing')).toBeUndefined()
    expect(openItemsOf(fake)('constructor')).toBeUndefined()
  })
})
