import { evaluate } from '@mdx-js/mdx'
import * as runtime from 'react/jsx-runtime'
import { describe, expect, it } from 'vitest'
import { type LessonShape, remarkLessonShape } from './remarkLessonShape.ts'

/** Compiles and runs a lesson the way the build does, and returns its shape. */
async function shapeOfLesson(source: string): Promise<LessonShape> {
  const lesson = (await evaluate(source, {
    ...runtime,
    remarkPlugins: [remarkLessonShape],
  })) as unknown as { shape: LessonShape }
  return lesson.shape
}

describe("a lesson's shape, measured while it's compiled", () => {
  it('cuts the intro into sections, each ending at a question', async () => {
    const shape = await shapeOfLesson(
      [
        '<Intro>',
        '',
        'One two three.',
        '',
        '- four',
        '- five',
        '',
        '<Check item="mcq-a" />',
        '',
        'Six seven.',
        '',
        '<Check item="mcq-b" />',
        '',
        'Eight.',
        '',
        '</Intro>',
        '',
        '<Resource index={0} />',
        '',
        '<Recap>',
        '',
        'Nine ten eleven twelve.',
        '',
        '</Recap>',
      ].join('\n'),
    )
    expect(shape).toEqual({
      sections: [
        // A paragraph, a list and the question.
        { words: 5, blocks: 3, check: 'mcq-a' },
        { words: 2, blocks: 2, check: 'mcq-b' },
        // What follows the last question.
        { words: 1, blocks: 1, check: null },
      ],
      recapWords: 4,
    })
  })

  it('counts the words in code, in a puzzle and in a story', async () => {
    const shape = await shapeOfLesson(
      [
        '<Intro>',
        '',
        '<Puzzle question="Why is it so?">',
        '',
        'Because it is.',
        '',
        '</Puzzle>',
        '',
        '```',
        'print("hello there")',
        '```',
        '',
        '<Story title="A bad day" source="https://example.com/a/long/address">',
        '',
        'It broke.',
        '',
        '</Story>',
        '',
        '</Intro>',
      ].join('\n'),
    )
    // 4 + 3 in the puzzle, 2 of code, 3 + 2 in the story; not the address.
    expect(shape.sections).toEqual([{ words: 14, blocks: 3, check: null }])
    // The puzzle's question, for asking before the lesson is opened.
    expect(shape.puzzle).toBe('Why is it so?')
  })

  it('names no puzzle for a lesson without one', async () => {
    const shape = await shapeOfLesson('<Intro>\n\nJust text.\n\n</Intro>')
    expect(shape).not.toHaveProperty('puzzle')
  })

  it("doesn't end a section at a question inside a list, or count a comment", async () => {
    const shape = await shapeOfLesson(
      [
        '<Intro>',
        '',
        '{/* a note to authors */}',
        '',
        '- A point. <Check item="mcq-inline" />',
        '',
        'More.',
        '',
        '</Intro>',
      ].join('\n'),
    )
    expect(shape.sections).toEqual([{ words: 3, blocks: 2, check: null }])
  })

  it('has no sections for a lesson without an intro', async () => {
    expect(await shapeOfLesson('Just text.')).toEqual({
      sections: [],
      recapWords: 0,
    })
  })
})
