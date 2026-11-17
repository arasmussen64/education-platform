import { evaluate } from '@mdx-js/mdx'
import * as runtime from 'react/jsx-runtime'
import { describe, expect, it } from 'vitest'
import { remarkLessonChecks } from './remarkLessonChecks.ts'

/** Compiles and runs a lesson the way the build does, and returns its module. */
async function compileLesson(source: string) {
  return (await evaluate(source, {
    ...runtime,
    remarkPlugins: [remarkLessonChecks],
  })) as { checks?: string[] }
}

describe('the questions a lesson places (ADR-0026)', () => {
  it('exports the item of every <Check>, in lesson order', async () => {
    const lesson = await compileLesson(
      [
        '<Intro>',
        '',
        'Some text.',
        '',
        '<Check item="mcq-b" />',
        '',
        '</Intro>',
        '',
        'Inline <Check item="mcq-a" /> works too.',
      ].join('\n'),
    )
    expect(lesson.checks).toEqual(['mcq-b', 'mcq-a'])
  })

  it('exports an empty list from a lesson without one', async () => {
    const lesson = await compileLesson('<Intro>Just text.</Intro>')
    expect(lesson.checks).toEqual([])
  })

  it('leaves out a <Check> in code, and one without a plain item', async () => {
    const lesson = await compileLesson(
      [
        'Write `<Check item="in-code" />` to place one.',
        '',
        '```mdx',
        '<Check item="in-a-block" />',
        '```',
        '',
        "<Check item={'an-expression'} />",
      ].join('\n'),
    )
    expect(lesson.checks).toEqual([])
  })
})
