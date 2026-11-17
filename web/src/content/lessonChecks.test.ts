import { describe, expect, it } from 'vitest'
import { fakeContent } from '../test/fakeContent.tsx'
import { loadTopicContent } from './content.ts'
import { practiceOutsideLesson } from './lessonChecks.ts'

describe('the practice ladder and the lesson (ADR-0026)', () => {
  it('leaves out the questions the lesson asks itself', () => {
    const content = {
      ...fakeContent(),
      lessonChecks: ['mcq-print', 'predict-print'],
    }
    expect(practiceOutsideLesson(content)).toEqual([
      'example-hello',
      'fill-hello',
      'write-hello',
    ])
  })

  it('keeps the whole ladder when the lesson asks none', () => {
    const content = fakeContent()
    expect(practiceOutsideLesson(content)).toEqual(content.topic.practice)
  })

  it("reads a real lesson's questions while loading its topic", async () => {
    // Every compiled lesson says which questions it asks, if only none.
    const content = await loadTopicContent('csa.linux.memory')
    expect(content?.Lesson).toBeTypeOf('function')
    expect(Array.isArray(content?.lessonChecks)).toBe(true)
  })
})
