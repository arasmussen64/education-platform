import { describe, expect, it } from 'vitest'
import { getTopic } from '../content/content.ts'
import { fakeContent, fakeTopic } from '../test/fakeContent.tsx'
import { earlierTopicFor, interleavedItem } from './interleave.ts'

describe('earlierTopicFor', () => {
  it("is the topic's most recent prerequisite", () => {
    expect(earlierTopicFor(getTopic('py.values-and-types')!)?.id).toBe(
      'py.programs-and-print',
    )
    expect(earlierTopicFor(getTopic('py.strings-and-input')!)?.id).toBe(
      'py.variables',
    )
  })

  it('looks through a checkpoint to the last topic before it', () => {
    // Module 2's first topic builds on Checkpoint 1, which builds on Module
    // 1's last topics.
    expect(earlierTopicFor(getTopic('py.booleans-and-comparisons')!)?.id).toBe(
      'py.strings-and-input',
    )
  })

  it('is nothing for the first topic of a track', () => {
    expect(earlierTopicFor(getTopic('py.programs-and-print')!)).toBeNull()
  })

  it('gives up on a prerequisite that goes in a circle, or is missing', () => {
    const a = fakeTopic({ id: 'py.a', prerequisites: ['py.b'] })
    const b = fakeTopic({
      id: 'py.b',
      kind: 'checkpoint',
      prerequisites: ['py.a'],
    })
    const lookup = (id: string) => [a, b].find((topic) => topic.id === id)
    expect(earlierTopicFor(a, lookup)).toBeNull()
    expect(
      earlierTopicFor(fakeTopic({ prerequisites: ['py.gone'] }), lookup),
    ).toBeNull()
  })
})

describe('interleavedItem', () => {
  const content = fakeContent()

  it('picks one of the recall questions, the same one all day', () => {
    const today = interleavedItem(content, '2026-11-08')
    expect(Object.keys(content.recall)).toContain(today)
    expect(interleavedItem(content, '2026-11-08')).toBe(today)
  })

  it('rotates through the questions day by day', () => {
    const days = ['2026-11-08', '2026-11-09', '2026-11-10', '2026-11-11']
    const asked = new Set(days.map((day) => interleavedItem(content, day)))
    expect(asked.size).toBe(Object.keys(content.recall).length)
  })

  it('is nothing when the topic has no recall questions', () => {
    const empty = { ...content, recall: {} }
    expect(interleavedItem(empty, '2026-11-08')).toBeNull()
  })
})
