import { describe, expect, it } from 'vitest'
import type { TopicContent } from '../content/types.ts'
import type { Attempt } from '../followups/followUps.ts'
import { nextTimeFor } from './nextTime.ts'

/** A topic with one lesson question, two practice items and two proofs. */
function content(over: { puzzle?: string; objectives?: string[] } = {}) {
  return {
    topic: {
      id: 'py.print',
      title: 'Programs and print',
      objectives: over.objectives ?? ['Print text to the screen.'],
      practice: ['mcq-lesson', 'predict-1', 'write-1'],
      prove: { build: 'build-1', debug: 'debug-1' },
    },
    lessonChecks: ['mcq-lesson'],
    lessonShape: { sections: [], recapWords: 0, puzzle: over.puzzle },
    recall: {
      'mcq-lesson': { type: 'mcq', prompt: 'What does `print` do?' },
      'predict-1': {
        type: 'predict_output',
        prompt: 'What does this print?',
        code: 'print("a", "b")',
      },
    },
    exercises: {
      'write-1': { title: 'Greet twice', prompt: 'Print two lines.\n\nMore.' },
      'build-1': { title: 'A receipt', prompt: 'Print a receipt.' },
      'debug-1': { title: 'Fix it', prompt: 'It prints the wrong thing.' },
    },
  } as unknown as TopicContent
}

let lastId = 0
function right(item: string, type: Attempt['type'] = 'answer'): Attempt {
  return {
    id: `a-${++lastId}`,
    type,
    topic_id: 'py.print',
    item_id: item,
    correct: true,
    occurred_at: '2026-11-20T12:00:00.000Z',
  }
}

describe('the question a session ends on', () => {
  it("asks the next topic's opening puzzle, to guess at", () => {
    const next = nextTimeFor(content({ puzzle: 'Why a new line?' }), false, [])
    expect(next).toMatchObject({
      kind: 'guess',
      question: 'Why a new line?',
      source: 'puzzle',
    })
  })

  it("asks about the topic's first goal when its lesson has no puzzle", () => {
    const next = nextTimeFor(content(), false, [])
    expect(next).toMatchObject({ kind: 'guess', source: 'goal' })
    expect(next?.kind === 'guess' && next.question).toContain(
      '**Print text to the screen.**',
    )
  })

  it('asks nothing of a topic with neither', () => {
    expect(nextTimeFor(content({ objectives: [] }), false, [])).toBeNull()
  })

  it('shows the next unanswered question of a topic in progress', () => {
    expect(nextTimeFor(content(), true, [])).toMatchObject({
      kind: 'question',
      prompt: 'What does `print` do?',
      code: null,
      proof: null,
    })
    // With the code a prediction is about.
    expect(nextTimeFor(content(), true, [right('mcq-lesson')])).toMatchObject({
      prompt: 'What does this print?',
      code: 'print("a", "b")',
    })
  })

  it("gives an exercise's title and the first paragraph of its prompt", () => {
    const done = [right('mcq-lesson'), right('predict-1')]
    expect(nextTimeFor(content(), true, done)).toMatchObject({
      prompt: '**Greet twice.** Print two lines.',
      proof: null,
    })
  })

  it('says when the next thing is a proof', () => {
    const done = [
      right('mcq-lesson'),
      right('predict-1'),
      right('write-1', 'code_check'),
    ]
    expect(nextTimeFor(content(), true, done)).toMatchObject({
      prompt: '**A receipt.** Print a receipt.',
      proof: 'build',
    })
    expect(
      nextTimeFor(content(), true, [...done, right('build-1', 'code_check')]),
    ).toMatchObject({ proof: 'debug' })
  })

  it('has nothing to show once every item is right', () => {
    const all = [
      right('mcq-lesson'),
      right('predict-1'),
      right('write-1', 'code_check'),
      right('build-1', 'code_check'),
      right('debug-1', 'code_check'),
    ]
    expect(nextTimeFor(content(), true, all)).toBeNull()
  })

  it("doesn't count an answer given in the placement test", () => {
    const placed = { ...right('mcq-lesson'), context: 'placement' as const }
    expect(nextTimeFor(content(), true, [placed])).toMatchObject({
      prompt: 'What does `print` do?',
    })
  })
})
