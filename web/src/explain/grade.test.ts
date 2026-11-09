import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { Explain } from '../content/types.ts'
import { gradeExplanation } from './grade.ts'

// A stand-in for Supabase's functions client: each test says what the
// proxy answers.
const proxy = vi.hoisted(() => ({ invoke: vi.fn() }))
vi.mock('../supabase/client.ts', () => ({
  getSupabase: () => ({ functions: { invoke: proxy.invoke } }),
}))

const EXPLAIN: Explain = {
  prompt: 'Why does it print 12?',
  rubric: [
    { id: 'input-is-text', required: true, description: 'Input is text.' },
  ],
  model_answer: 'SECRET MODEL ANSWER',
}

const GRADED = {
  status: 'graded',
  grading: {
    verdict: 'pass',
    rubric: [{ id: 'input-is-text', met: true }],
    questions: [],
  },
  ai_call_id: 'call-1',
  model: 'claude-haiku-5-5',
}

describe('gradeExplanation', () => {
  beforeEach(() => {
    proxy.invoke.mockReset()
  })

  it('sends the explanation to the proxy, with what it needs to grade it', async () => {
    proxy.invoke.mockResolvedValue({ data: GRADED, error: null })
    const outcome = await gradeExplanation(
      'py.values-and-types',
      EXPLAIN,
      'Typed input is text.',
    )
    expect(proxy.invoke).toHaveBeenCalledWith('ai', {
      body: {
        action: 'grade_explanation',
        topic_id: 'py.values-and-types',
        prompt: 'Why does it print 12?',
        rubric: EXPLAIN.rubric,
        model_answer: 'SECRET MODEL ANSWER',
        explanation: 'Typed input is text.',
      },
    })
    expect(outcome).toEqual(GRADED)
  })

  it('passes on the answers that mean "not graded this time"', async () => {
    for (const status of ['not_allowed', 'paused', 'unavailable'] as const) {
      proxy.invoke.mockResolvedValueOnce({ data: { status }, error: null })
      expect(await gradeExplanation('t', EXPLAIN, 'x')).toEqual({ status })
    }
  })

  it('says it failed when the proxy errs, throws, or answers strangely', async () => {
    proxy.invoke.mockResolvedValueOnce({
      data: null,
      error: new Error('Failed to send a request to the Edge Function'),
    })
    expect(await gradeExplanation('t', EXPLAIN, 'x')).toEqual({
      status: 'failed',
    })

    proxy.invoke.mockRejectedValueOnce(new Error('offline'))
    expect(await gradeExplanation('t', EXPLAIN, 'x')).toEqual({
      status: 'failed',
    })

    proxy.invoke.mockResolvedValueOnce({
      data: { status: 'graded', grading: { verdict: 'maybe' } },
      error: null,
    })
    expect(await gradeExplanation('t', EXPLAIN, 'x')).toEqual({
      status: 'failed',
    })
  })
})
