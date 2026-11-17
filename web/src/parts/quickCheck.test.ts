import { describe, expect, it } from 'vitest'
import type { RecallItem, TopicContent } from '../content/types.ts'
import type { Attempt } from '../followups/followUps.ts'
import {
  ESTIMATE,
  fakeContent,
  fakeExercise,
  fakeTopic,
  MCQ,
  PARSONS,
  PREDICT,
  TYPED_TERM,
} from '../test/fakeContent.tsx'
import {
  isOptional,
  quickCheckItems,
  quickCheckTaken,
  shownSkills,
} from './quickCheck.ts'

/** A question of a kind, testing these skills. */
function question(id: string, skills: string[], base: RecallItem = MCQ) {
  return { ...base, id, skills } as RecallItem
}

/**
 * A topic with skills a, b, c and d, and a practice of questions and
 * exercises on them, in this order.
 */
function topicWith(recall: RecallItem[], extra: string[] = []): TopicContent {
  const base = fakeContent(
    fakeTopic({
      practice: ['example-hello', ...recall.map((item) => item.id), ...extra],
      skills: ['a', 'b', 'c', 'd'].map((id) => ({ id, description: id })),
    }),
  )
  return {
    ...base,
    recall: Object.fromEntries(recall.map((item) => [item.id, item])),
    exercises: {
      ...base.exercises,
      'write-a': fakeExercise({ id: 'write-a', stage: 'write', skills: ['a'] }),
      'write-ab': fakeExercise({
        id: 'write-ab',
        stage: 'write',
        skills: ['a', 'b'],
      }),
    },
  }
}

function quickAnswer(
  item: string,
  correct: boolean,
  minute = 0,
  topicId = 'py.values-and-types',
): Attempt {
  return {
    id: `${item}-${minute}`,
    type: 'answer',
    topic_id: topicId,
    item_id: item,
    correct,
    occurred_at: new Date(Date.UTC(2026, 10, 16, 10, minute)).toISOString(),
    context: 'practice',
    quick_check: true,
  }
}

describe('picking the quick check', () => {
  it('asks one quick question per skill, in ladder order', () => {
    const content = topicWith([
      question('q1', ['a']),
      question('q2', ['a']),
      question('q3', ['b'], PREDICT),
      question('q4', ['c'], ESTIMATE),
      question('q5', ['d']),
    ])
    expect(quickCheckItems(content)).toEqual(['q1', 'q3', 'q4', 'q5'])
  })

  it('counts a typed answer as quick (ADR-0027)', () => {
    const content = topicWith([
      question('q1', ['a']),
      question('t1', ['b'], TYPED_TERM),
      question('q2', ['c']),
    ])
    expect(quickCheckItems(content)).toEqual(['q1', 't1', 'q2'])
  })

  it('stops at five questions', () => {
    const content = topicWith(
      ['a', 'b', 'c', 'd', 'e', 'f'].map((skill) =>
        question(`q-${skill}`, [skill]),
      ),
    )
    expect(quickCheckItems(content)).toEqual([
      'q-a',
      'q-b',
      'q-c',
      'q-d',
      'q-e',
    ])
  })

  it('makes up three when the skills are fewer', () => {
    const content = topicWith([
      question('q1', ['a']),
      question('q2', ['a']),
      question('q3', ['a']),
    ])
    expect(quickCheckItems(content)).toEqual(['q1', 'q2', 'q3'])
  })

  it('leaves out Parsons problems, and offers nothing with under three quick questions', () => {
    const content = topicWith([
      question('q1', ['a']),
      question('p1', ['b'], PARSONS),
      question('q2', ['c']),
    ])
    expect(quickCheckItems(content)).toEqual([])
  })
})

describe('what the quick check shows', () => {
  const content = topicWith(
    [question('q1', ['a']), question('q2', ['b']), question('q3', ['c'])],
    ['write-a', 'write-ab'],
  )

  it('counts the skills of questions whose first answer was right', () => {
    const shown = shownSkills(content, [
      quickAnswer('q1', true),
      // Wrong first, then right after the feedback: not shown.
      quickAnswer('q2', false, 1),
      quickAnswer('q2', true, 2),
    ])
    expect([...shown]).toEqual(['a'])
  })

  it("ignores ordinary practice answers and another topic's", () => {
    const practice = { ...quickAnswer('q1', true), quick_check: undefined }
    expect(shownSkills(content, [practice]).size).toBe(0)
    expect(quickCheckTaken(content, [practice])).toBe(false)
    const elsewhere = quickAnswer('q1', true, 0, 'py.programs-and-print')
    expect(shownSkills(content, [elsewhere]).size).toBe(0)
    expect(quickCheckTaken(content, [quickAnswer('q2', false)])).toBe(true)
  })

  it('makes an item optional only when every skill it tests was shown', () => {
    const shown = new Set(['a'])
    expect(isOptional(content, 'write-a', shown)).toBe(true)
    expect(isOptional(content, 'write-ab', shown)).toBe(false)
    expect(isOptional(content, 'q1', shown)).toBe(true)
    expect(isOptional(content, 'q2', shown)).toBe(false)
    // An item that names no skills is never optional.
    expect(isOptional(content, 'missing', new Set(['a', 'b']))).toBe(false)
  })
})
