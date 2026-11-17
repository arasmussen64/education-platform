import { describe, expect, it } from 'vitest'
import cases from '../../../tools/tests/typed_cases.json?raw'
import { TYPED_COMMAND, TYPED_TERM } from '../test/fakeContent.tsx'
import { caseOf, gradeTyped, isSlip, normaliseTyped } from './typed.ts'
import type { TypedCase, TypedKind } from './types.ts'

/** The cases tools/tests/test_typed_answers.py checks the validator against. */
const shared = JSON.parse(cases) as {
  normalise: { kind: TypedKind; case: TypedCase; typed: string; read: string }[]
  slips: { typed: string; answer: string; slip: boolean }[]
}

describe('reading a typed answer, exactly as the validator does (ADR-0027)', () => {
  it.each(shared.normalise)(
    '$kind, case $case: $typed',
    ({ kind, case: textCase, typed, read }) => {
      expect(normaliseTyped(typed, kind, textCase)).toBe(read)
    },
  )

  it.each(shared.slips)(
    '$typed for $answer is a slip: $slip',
    ({ typed, answer, slip }) => {
      expect(isSlip(typed, answer)).toBe(slip)
    },
  )
})

describe('gradeTyped', () => {
  it("takes the item's own case rule, or its kind's", () => {
    expect(caseOf(TYPED_COMMAND)).toBe('sensitive')
    expect(caseOf(TYPED_TERM)).toBe('insensitive')
    expect(caseOf({ ...TYPED_COMMAND, case: 'insensitive' })).toBe(
      'insensitive',
    )
  })

  it('accepts any accepted answer, read forgivingly', () => {
    expect(gradeTyped(TYPED_COMMAND, '$ docker  container ls')).toEqual({
      correct: true,
      mistake: null,
      slip: false,
      matched: 'docker container ls',
    })
    expect(gradeTyped(TYPED_TERM, '"k8s"').correct).toBe(true)
  })

  it("minds a command's case", () => {
    expect(gradeTyped(TYPED_COMMAND, 'Docker PS').correct).toBe(false)
  })

  it('names the known mistake a wrong answer matches, dashes and all', () => {
    // A phone's smart punctuation turns -- into an em dash.
    expect(gradeTyped(TYPED_COMMAND, 'docker ps —all')).toEqual({
      correct: false,
      mistake: 'every-container',
      slip: false,
      matched: null,
    })
  })

  it('forgives a term one slip among its letters, and says which answer', () => {
    expect(gradeTyped(TYPED_TERM, 'kubernets')).toEqual({
      correct: true,
      mistake: null,
      slip: true,
      matched: 'Kubernetes',
    })
    // A command is never forgiven one: a shell would refuse it.
    expect(gradeTyped(TYPED_COMMAND, 'dokcer ps').correct).toBe(false)
  })

  it('catches a known mistake before forgiving a slip', () => {
    const item = {
      ...TYPED_TERM,
      mistakes: [{ id: 'one-off', answers: ['Kubernetis'], why: 'Close.' }],
    }
    expect(gradeTyped(item, 'kubernetis')).toMatchObject({
      correct: false,
      mistake: 'one-off',
    })
  })
})
