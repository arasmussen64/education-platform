import { describe, expect, it } from 'vitest'
import { eventRow } from '../test/fakeEvents.ts'
import {
  calibration,
  levelSentence,
  localRatedAnswers,
  mergeRated,
  type RatedAnswer,
} from './confidence.ts'

const answers = (
  confidence: RatedAnswer['confidence'],
  right: number,
  wrong: number,
): RatedAnswer[] =>
  Array.from({ length: right + wrong }, (_, index) => ({
    id: `${confidence}-${index}`,
    confidence,
    correct: index < right,
  }))

describe('calibration (ADR-0028)', () => {
  it('counts each level, least sure first', () => {
    const levels = calibration([
      ...answers('sure', 11, 1),
      ...answers('guess', 2, 3),
    ])
    expect(levels).toEqual([
      { confidence: 'guess', answers: 5, right: 2 },
      { confidence: 'fair', answers: 0, right: 0 },
      { confidence: 'sure', answers: 12, right: 11 },
    ])
  })

  it('says how often a level is right, once it has five answers', () => {
    expect(levelSentence({ confidence: 'sure', answers: 12, right: 11 })).toBe(
      "When you're certain, you're right 92% of the time (12 answers).",
    )
    expect(levelSentence({ confidence: 'guess', answers: 5, right: 2 })).toBe(
      "When you guess, you're right 40% of the time (5 answers).",
    )
    expect(
      levelSentence({ confidence: 'fair', answers: 4, right: 4 }),
    ).toBeNull()
  })

  it("reads this browser's answers that carry a confidence, and only those", () => {
    const rows = [
      eventRow({
        id: 'a',
        type: 'answer',
        correct: true,
        data: { confidence: 'sure' },
      }),
      eventRow({ id: 'b', type: 'answer', correct: false, data: {} }),
      eventRow({
        id: 'c',
        type: 'answer',
        correct: false,
        data: { confidence: 'maybe' },
      }),
      eventRow({
        id: 'd',
        type: 'code_check',
        correct: true,
        data: { confidence: 'sure' },
      }),
    ]
    expect(localRatedAnswers(rows)).toEqual([
      { id: 'a', confidence: 'sure', correct: true },
    ])
  })

  it('counts an answer saved and still on this device once', () => {
    const saved = answers('fair', 1, 0)
    expect(mergeRated(saved, saved)).toHaveLength(1)
  })
})
