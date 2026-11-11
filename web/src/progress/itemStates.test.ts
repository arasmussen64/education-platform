import { describe, expect, it } from 'vitest'
import type { Attempt } from '../followups/followUps.ts'
import { itemKey, itemStates } from './itemStates.ts'

function attempt(
  itemId: string,
  correct: boolean,
  type: Attempt['type'] = 'answer',
  topicId = 'py.values-and-types',
): Attempt {
  return {
    id: `${type}-${topicId}-${itemId}-${correct}`,
    type,
    topic_id: topicId,
    item_id: itemId,
    correct,
    occurred_at: '2026-11-09T12:00:00.000Z',
  }
}

describe('item states', () => {
  it('is done after a correct attempt, tried after only wrong ones', () => {
    const states = itemStates([
      attempt('mcq-print', false),
      attempt('mcq-print', true),
      attempt('predict-print', false),
      attempt('write-hello', true, 'code_check'),
    ])
    expect(states.get(itemKey('py.values-and-types', 'mcq-print'))).toBe('done')
    expect(states.get(itemKey('py.values-and-types', 'predict-print'))).toBe(
      'tried',
    )
    expect(states.get(itemKey('py.values-and-types', 'write-hello'))).toBe(
      'done',
    )
    expect(states.has(itemKey('py.values-and-types', 'fill-hello'))).toBe(false)
  })

  it('stays done however the attempts are ordered', () => {
    const states = itemStates([
      attempt('mcq-print', true),
      attempt('mcq-print', false),
    ])
    expect(states.get(itemKey('py.values-and-types', 'mcq-print'))).toBe('done')
  })

  it('keeps topics apart and ignores explanations and reviews', () => {
    const states = itemStates([
      attempt('mcq-print', true, 'answer', 'py.programs-and-print'),
      attempt('explain', true, 'explain_submit'),
      attempt('review', true, 'review'),
    ])
    expect([...states.keys()]).toEqual(['py.programs-and-print/mcq-print'])
  })

  // The placement test asks review questions of topics the learner may never
  // have opened. Its answers place them; they aren't practice (ADR-0021).
  it('ignores answers given in the placement test', () => {
    const placed = (itemId: string, correct: boolean): Attempt => ({
      ...attempt(itemId, correct),
      id: `placement-${itemId}`,
      context: 'placement',
    })
    expect(
      itemStates([placed('mcq-print', true), placed('predict-print', false)]),
    ).toEqual(new Map())
  })

  it('still marks an item done when it was also answered in the placement test', () => {
    const states = itemStates([
      { ...attempt('mcq-print', false), context: 'placement' },
      { ...attempt('mcq-print', true), id: 'later', context: 'practice' },
    ])
    expect(states.get(itemKey('py.values-and-types', 'mcq-print'))).toBe('done')
  })

  it('counts answers saved before contexts were read, which have none', () => {
    const states = itemStates([attempt('mcq-print', false)])
    expect(states.get(itemKey('py.values-and-types', 'mcq-print'))).toBe(
      'tried',
    )
  })
})
