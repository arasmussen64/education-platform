import type { Explain } from '../content/types.ts'
import { getSupabase } from '../supabase/client.ts'

// Asking the AI proxy (supabase/functions/ai, ADR-0013) to grade an
// explanation. The proxy holds the Claude API key and checks the learner,
// the month's budget and the key before calling Claude.

/** Claude's grading, as the proxy returns it. */
export type Grading = {
  verdict: 'pass' | 'needs_work'
  /** Every rubric item: did the explanation show it? */
  rubric: { id: string; met: boolean }[]
  /** Only when it needs work: questions toward what's missing. */
  questions: string[]
}

/** What came back. Anything but "graded" means it wasn't graded this time. */
export type GradeOutcome =
  | {
      status: 'graded'
      grading: Grading
      ai_call_id: string | null
      model: string
    }
  /** The account can't use the AI (sign-ups are closed; see `allowed`). */
  | { status: 'not_allowed' }
  /** This month's AI budget is used up. */
  | { status: 'paused' }
  /** The proxy has no key, or Claude couldn't grade it. */
  | { status: 'unavailable' }
  /** The proxy couldn't be reached, or said something unexpected. */
  | { status: 'failed' }

export type GradeExplanation = (
  topicId: string,
  explain: Explain,
  explanation: string,
) => Promise<GradeOutcome>

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value)

const isStringList = (value: unknown): value is string[] =>
  Array.isArray(value) && value.every((item) => typeof item === 'string')

/** Checks the proxy's reply has the shape the page relies on. */
function readOutcome(data: unknown): GradeOutcome {
  if (!isRecord(data)) return { status: 'failed' }
  const { status } = data
  if (status === 'not_allowed' || status === 'paused') return { status }
  if (status === 'unavailable') return { status }
  if (status !== 'graded' || !isRecord(data.grading))
    return { status: 'failed' }
  const { verdict, rubric, questions } = data.grading
  if (
    (verdict !== 'pass' && verdict !== 'needs_work') ||
    !Array.isArray(rubric) ||
    !isStringList(questions)
  ) {
    return { status: 'failed' }
  }
  return {
    status: 'graded',
    grading: {
      verdict,
      rubric: rubric.filter(
        (item): item is { id: string; met: boolean } =>
          isRecord(item) &&
          typeof item.id === 'string' &&
          typeof item.met === 'boolean',
      ),
      questions,
    },
    ai_call_id: typeof data.ai_call_id === 'string' ? data.ai_call_id : null,
    model: typeof data.model === 'string' ? data.model : 'unknown',
  }
}

/**
 * Asks the proxy to grade an explanation. It never throws: a problem comes
 * back as "failed", so the page can say so and keep the learner's text.
 */
export const gradeExplanation: GradeExplanation = async (
  topicId,
  explain,
  explanation,
) => {
  try {
    const { data, error } = await getSupabase().functions.invoke('ai', {
      body: {
        action: 'grade_explanation',
        topic_id: topicId,
        prompt: explain.prompt,
        rubric: explain.rubric,
        // The grader needs it to judge correctness; the page never shows it.
        model_answer: explain.model_answer,
        explanation,
      },
    })
    return error ? { status: 'failed' } : readOutcome(data)
  } catch {
    return { status: 'failed' }
  }
}
