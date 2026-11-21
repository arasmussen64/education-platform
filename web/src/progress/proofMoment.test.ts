import { describe, expect, it } from 'vitest'
import type { Module, Topic } from '../content/types.ts'
import type { TopicProgress } from './progress.ts'
import { moduleStep, openedBy } from './proofMoment.ts'

function topic(id: string, prerequisites: string[] = []): Topic {
  return { id, prerequisites, kind: 'topic' } as unknown as Topic
}

/** Progress in which exactly these topics are learned. */
function learned(...ids: string[]): Map<string, TopicProgress> {
  return new Map(
    ids.map((id) => [
      id,
      {
        started: true,
        passed: {},
        learnedAt: '2026-11-21T10:00:00.000Z',
        reviews: [],
        card: null,
      },
    ]),
  )
}

describe('what proving a topic opened', () => {
  const topics = [
    topic('a'),
    topic('b', ['a']),
    topic('c', ['a', 'x']),
    topic('d', ['b']),
  ]

  it('is the topics built on it whose other prerequisites are learned', () => {
    // b needs only a. c also needs x, which isn't learned. d needs b.
    expect(openedBy('a', topics, learned('a')).map((each) => each.id)).toEqual([
      'b',
    ])
    expect(
      openedBy('a', topics, learned('a', 'x')).map((each) => each.id),
    ).toEqual(['b', 'c'])
  })

  it('leaves out a topic already learned', () => {
    expect(openedBy('a', topics, learned('a', 'b'))).toEqual([])
  })

  it('is nothing for a topic that is not proven', () => {
    expect(openedBy('a', topics, learned())).toEqual([])
  })
})

describe("where a proof left the topic's module", () => {
  const module = {
    title: 'Basics',
    topics: ['a', 'b', 'c'],
    checkpoint: 'check',
  } as unknown as Module
  const all = () => true

  it('counts one more than before', () => {
    const step = moduleStep(2, module, learned('a', 'b'), all)
    expect(step).toMatchObject({ number: 2, before: 1, complete: false })
    expect(step.count).toEqual({ proven: 2, open: 4, total: 4 })
  })

  it('is complete when every topic that can be opened is proven', () => {
    // The checkpoint is still being written, so three are open.
    const step = moduleStep(
      2,
      module,
      learned('a', 'b', 'c'),
      (id) => id !== 'check',
    )
    expect(step).toMatchObject({ before: 2, complete: true })
  })
})
