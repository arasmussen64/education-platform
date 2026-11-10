import { describe, expect, it } from 'vitest'
import type { McqItem } from '../content/types.ts'
import { choiceOrder } from './scramble.ts'

function mcq(id: string, choices = 4): McqItem {
  return {
    id,
    type: 'mcq',
    rev: 1,
    prompt: 'Which?',
    choices: Array.from({ length: choices }, (_, i) => `choice ${i}`),
    answer: 0,
    explanation: 'Because.',
    skills: [],
  }
}

describe('choiceOrder', () => {
  it('is a permutation of every choice', () => {
    const order = choiceOrder(mcq('mcq-something'))
    expect([...order].sort()).toEqual([0, 1, 2, 3])
  })

  it('is the same every time for the same item', () => {
    expect(choiceOrder(mcq('mcq-stable'))).toEqual(
      choiceOrder(mcq('mcq-stable')),
    )
  })

  it('puts an answer written first in every position across items', () => {
    // Authors tend to write the right answer first; across many items the
    // shuffle must land it everywhere, or position still gives it away.
    const positions = new Set<number>()
    for (let n = 0; n < 40; n++) {
      positions.add(choiceOrder(mcq(`mcq-item-${n}`)).indexOf(0))
    }
    expect(positions).toEqual(new Set([0, 1, 2, 3]))
  })

  it('leaves a single choice alone', () => {
    expect(choiceOrder(mcq('mcq-one', 1))).toEqual([0])
  })
})
