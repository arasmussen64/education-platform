import type { Exercise } from '../content/types.ts'
import { clip, MAX_CODE_CHARS } from '../events/payloads.ts'
import type { CheckOutcome } from '../python/runner.ts'
import { getSupabase } from '../supabase/client.ts'

// Asking the AI proxy (supabase/functions/ai, ADR-0015) for a hint from the
// tutor. The proxy holds the Claude API key and checks the learner, the
// month's budget and the key before calling Claude. It gives hints one rung
// at a time and never the solution.

/** The rungs of the hint ladder (F13), in the order the tutor climbs them. */
export type HintLevel = 'nudge' | 'concept' | 'specific' | 'step'

/** How each rung is labelled on the page. */
export const LEVEL_LABELS: Record<HintLevel, string> = {
  nudge: 'A nudge',
  concept: 'The idea',
  specific: 'A closer look',
  step: 'The next step',
}

export type TutorHint = {
  text: string
  level: HintLevel
  /** True when the proxy swapped Claude's reply for a safer hint. */
  replaced: boolean
}

/** What came back. Anything but "hinted" means there's no hint this time. */
export type HintOutcome =
  | {
      status: 'hinted'
      hint: TutorHint
      ai_call_id: string | null
      model: string
    }
  /** The account can't use the AI (sign-ups are closed; see `allowed`). */
  | { status: 'not_allowed' }
  /** This month's AI budget is used up. */
  | { status: 'paused' }
  /** The proxy has no key, doesn't know the tutor yet, or Claude couldn't help. */
  | { status: 'unavailable' }
  /** The proxy couldn't be reached, or said something unexpected. */
  | { status: 'failed' }

/** One test of the latest Check, as the proxy wants it. */
export type TestSummary = {
  description: string
  outcome: 'pass' | 'fail' | 'error'
  message: string
}

export type CheckSummary = {
  passed: number
  total: number
  results: TestSummary[]
}

export type HintRequest = {
  topicId: string
  itemId: string
  exercise: Exercise
  /** The learner's code as it is now. */
  code: string
  /** Their latest Check, or null before the first one. */
  check: CheckOutcome | null
  /** What they typed, if anything. */
  question: string
  /** The tutor's earlier replies on this exercise, oldest first. */
  earlier: string[]
}

export type AskTutor = (request: HintRequest) => Promise<HintOutcome>

/** The longest question the proxy takes. */
export const MAX_QUESTION_CHARS = 500
/** The proxy reads at most this many earlier hints; the latest ones matter most. */
const MAX_EARLIER_HINTS = 8
const MAX_MESSAGE_CHARS = 1000

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value)

/**
 * The latest Check, boiled down to what the tutor can use: each test's
 * description and outcome, and its message (which the learner can see too).
 */
export function checkSummary(check: CheckOutcome | null): CheckSummary | null {
  if (!check) return null
  if (check.kind === 'timeout') {
    return {
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
    }
  }
  if (check.kind === 'failed') return null
  const { report } = check
  if (report.status === 'error') {
    return {
      passed: 0,
      total: 0,
      results: [
        {
          description: "The checks couldn't run.",
          outcome: 'error',
          message: clip(report.message, MAX_MESSAGE_CHARS),
        },
      ],
    }
  }
  return {
    passed: report.passed,
    total: report.total,
    results: report.results.map((result) => ({
      description: result.description,
      outcome: result.outcome,
      message: clip(result.message, MAX_MESSAGE_CHARS),
    })),
  }
}

const LEVELS = new Set<string>(['nudge', 'concept', 'specific', 'step'])

/** Checks the proxy's reply has the shape the page relies on. */
function readOutcome(data: unknown): HintOutcome {
  if (!isRecord(data)) return { status: 'failed' }
  const { status } = data
  if (status === 'not_allowed' || status === 'paused') return { status }
  if (status === 'unavailable') return { status }
  if (status !== 'hinted' || !isRecord(data.hint)) return { status: 'failed' }
  const { text, level, replaced } = data.hint
  if (
    typeof text !== 'string' ||
    text.trim() === '' ||
    typeof level !== 'string' ||
    !LEVELS.has(level) ||
    typeof replaced !== 'boolean'
  ) {
    return { status: 'failed' }
  }
  return {
    status: 'hinted',
    hint: { text, level: level as HintLevel, replaced },
    ai_call_id: typeof data.ai_call_id === 'string' ? data.ai_call_id : null,
    model: typeof data.model === 'string' ? data.model : 'unknown',
  }
}

/**
 * Asks the proxy for a hint. It never throws: a problem comes back as
 * "failed", so the page can say so and the written hints stay available.
 */
export const askTutor: AskTutor = async (request) => {
  try {
    const { data, error } = await getSupabase().functions.invoke('ai', {
      body: {
        action: 'tutor_hint',
        topic_id: request.topicId,
        item_id: request.itemId,
        exercise: {
          title: request.exercise.title,
          prompt: request.exercise.prompt,
          hints: request.exercise.hints,
          // The tutor needs it to judge the code; it never quotes it.
          solution: request.exercise.solution,
        },
        code: clip(request.code, MAX_CODE_CHARS),
        check: checkSummary(request.check),
        question: request.question.trim().slice(0, MAX_QUESTION_CHARS),
        earlier: request.earlier.slice(-MAX_EARLIER_HINTS),
      },
    })
    return error ? { status: 'failed' } : readOutcome(data)
  } catch {
    return { status: 'failed' }
  }
}
