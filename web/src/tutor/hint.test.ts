import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fakeExercise } from '../test/fakeContent.tsx'
import { oneFailed, report } from '../test/fakePython.ts'
import {
  askTutor,
  checkSummary,
  type HintRequest,
  MAX_TUTOR_CODE_CHARS,
} from './hint.ts'

// A stand-in for Supabase's functions client: each test says what the
// proxy answers.
const proxy = vi.hoisted(() => ({ invoke: vi.fn() }))
vi.mock('../supabase/client.ts', () => ({
  getSupabase: () => ({ functions: { invoke: proxy.invoke } }),
}))

const EXERCISE = fakeExercise({
  id: 'fill-hello',
  stage: 'fill_in',
  hints: ['Look at the quotes.'],
  solution: 'print("Hello!")\n',
})

const REQUEST: HintRequest = {
  topicId: 'py.values-and-types',
  itemId: 'fill-hello',
  exercise: EXERCISE,
  code: 'print(Hello!)',
  check: oneFailed('Prints Hello!', 'NameError: name Hello is not defined'),
  question: '  why the error?  ',
  earlier: [],
}

const HINTED = {
  status: 'hinted',
  hint: {
    text: 'What kind of value is Hello?',
    level: 'nudge',
    replaced: false,
  },
  ai_call_id: 'call-1',
  model: 'claude-haiku-5-5',
}

describe('askTutor', () => {
  beforeEach(() => {
    proxy.invoke.mockReset()
  })

  it('sends the proxy the exercise, the code, the latest Check and the question', async () => {
    proxy.invoke.mockResolvedValue({ data: HINTED, error: null })
    const outcome = await askTutor(REQUEST)
    expect(proxy.invoke).toHaveBeenCalledWith('ai', {
      body: {
        action: 'tutor_hint',
        topic_id: 'py.values-and-types',
        item_id: 'fill-hello',
        exercise: {
          title: 'Say hello',
          prompt: 'Print `Hello!`',
          hints: ['Look at the quotes.'],
          solution: 'print("Hello!")\n',
        },
        code: 'print(Hello!)',
        check: {
          passed: 0,
          total: 1,
          results: [
            {
              description: 'Prints Hello!',
              outcome: 'fail',
              message: 'NameError: name Hello is not defined',
            },
          ],
        },
        question: 'why the error?',
        earlier: [],
      },
    })
    expect(outcome).toEqual(HINTED)
  })

  it('passes on the answers that mean "no hint this time"', async () => {
    for (const status of ['not_allowed', 'paused', 'unavailable'] as const) {
      proxy.invoke.mockResolvedValueOnce({ data: { status }, error: null })
      expect(await askTutor(REQUEST)).toEqual({ status })
    }
  })

  it('says it failed when the proxy errs, throws, or answers strangely', async () => {
    proxy.invoke.mockResolvedValueOnce({
      data: null,
      error: new Error('Failed to send a request to the Edge Function'),
    })
    expect(await askTutor(REQUEST)).toEqual({ status: 'failed' })

    proxy.invoke.mockRejectedValueOnce(new Error('offline'))
    expect(await askTutor(REQUEST)).toEqual({ status: 'failed' })

    proxy.invoke.mockResolvedValueOnce({
      data: { status: 'hinted', hint: { text: 'x', level: 'shout' } },
      error: null,
    })
    expect(await askTutor(REQUEST)).toEqual({ status: 'failed' })
  })

  it('sends long programs whole: the longest in the track is 12,323 characters', async () => {
    proxy.invoke.mockResolvedValue({ data: HINTED, error: null })
    const program = 'x = 1\n'.repeat(2054) // 12,324 characters
    await askTutor({
      ...REQUEST,
      code: program,
      exercise: { ...EXERCISE, solution: program },
    })
    const body = proxy.invoke.mock.calls[0]?.[1]?.body as {
      code: string
      exercise: { solution: string }
    }
    expect(body.code).toBe(program)
    expect(body.exercise.solution).toBe(program)
  })

  it('says a program is too long for the tutor, without asking the proxy', async () => {
    const tooLong = 'x'.repeat(MAX_TUTOR_CODE_CHARS + 1)
    expect(await askTutor({ ...REQUEST, code: tooLong })).toEqual({
      status: 'too_long',
    })
    expect(
      await askTutor({
        ...REQUEST,
        exercise: { ...EXERCISE, solution: tooLong },
      }),
    ).toEqual({ status: 'too_long' })
    expect(proxy.invoke).not.toHaveBeenCalled()
  })

  it('passes on the proxy saying a program is too long', async () => {
    proxy.invoke.mockResolvedValueOnce({
      data: { status: 'too_long' },
      error: null,
    })
    expect(await askTutor(REQUEST)).toEqual({ status: 'too_long' })
  })

  it('sends only the last eight earlier hints', async () => {
    proxy.invoke.mockResolvedValue({ data: HINTED, error: null })
    const earlier = Array.from({ length: 10 }, (_, i) => `hint ${i + 1}`)
    await askTutor({ ...REQUEST, earlier })
    const body = proxy.invoke.mock.calls[0]?.[1]?.body as { earlier: string[] }
    expect(body.earlier).toEqual(earlier.slice(2))
  })
})

describe('checkSummary', () => {
  it('is nothing before the first Check', () => {
    expect(checkSummary(null)).toBeNull()
  })

  it('turns a time-out into one error the tutor can read', () => {
    expect(checkSummary({ kind: 'timeout' })).toEqual({
      passed: 0,
      total: 0,
      results: [
        {
          description:
            'The program ran past the time limit and was stopped (a loop that never ends?).',
          outcome: 'error',
          message: '',
        },
      ],
    })
  })

  it('passes on tests that could not run, and drops a runner failure', () => {
    expect(
      checkSummary(report({ status: 'error', message: 'SyntaxError: ...' })),
    ).toEqual({
      passed: 0,
      total: 0,
      results: [
        {
          description: "The checks couldn't run.",
          outcome: 'error',
          message: 'SyntaxError: ...',
        },
      ],
    })
    expect(checkSummary({ kind: 'failed', message: 'worker died' })).toBeNull()
  })
})
