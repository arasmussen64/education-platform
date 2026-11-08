// The AI proxy's front door (ADR-0013): who may call it, what they may send,
// and what happens, in order. The real services are passed in (index.ts),
// so the tests can check every path with fakes.
import type { Usage } from './cost.ts'
import type { GradeInput, Grading } from './grading.ts'

export type GradeRequest = GradeInput & {
  action: 'grade_explanation'
  topic_id: string
}

/** What one call to Claude produced. */
export type Graded = {
  model: string
  usage: Usage
  cost_usd: number
  /** Null when Claude's answer couldn't be used, with the reason. */
  grading: Grading | null
  problem?: string
}

/** One row of the ai_calls table. */
export type CallLog = {
  user_id: string
  action: 'grade_explanation'
  model: string
  input_tokens: number
  output_tokens: number
  cost_usd: number
  request: Record<string, unknown>
  response: Record<string, unknown>
}

export type Services = {
  /** The signed-in user's ID for this Authorization header, or null. */
  userFor(authorization: string | null): Promise<string | null>
  isAllowed(userId: string): Promise<boolean>
  /** This calendar month's spending so far, in US dollars. */
  spentThisMonth(): Promise<number>
  /** Grades with Claude. Null when there's no API key. */
  grade: ((input: GradeInput) => Promise<Graded>) | null
  /** Saves one call and returns its ID. */
  logCall(call: CallLog): Promise<string>
  /** Calls stop once the month's spending reaches this, in US dollars. */
  capUsd: number
  promptVersion: number
}

/** What the browser gets back. Anything but "graded" means: not graded now. */
export type Outcome =
  | {
      status: 'graded'
      grading: Grading
      ai_call_id: string | null
      model: string
    }
  | { status: 'not_allowed' | 'paused' | 'unavailable' }

// Browsers ask first (OPTIONS) whether a page on another site may call this.
export const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers':
    'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}

function reply(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
  })
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value)

/** A string of at most `max` characters; empty only when allowed. */
const isText = (value: unknown, max: number, allowEmpty = false) =>
  typeof value === 'string' &&
  value.length <= max &&
  (allowEmpty || value.trim().length > 0)

/** The request, checked, or what's wrong with it. Limits keep each call small. */
export function readGradeRequest(body: unknown): GradeRequest | string {
  if (!isRecord(body)) return 'Send a JSON object.'
  if (body.action !== 'grade_explanation') return 'Unknown action.'
  if (!isText(body.topic_id, 200)) return 'topic_id is missing or too long.'
  if (!isText(body.prompt, 4000)) return 'prompt is missing or too long.'
  if (!isText(body.model_answer, 6000, true)) return 'model_answer is too long.'
  if (!isText(body.explanation, 4000)) {
    return 'The explanation is empty or longer than 4,000 characters.'
  }
  const rubric = body.rubric
  if (!Array.isArray(rubric) || rubric.length === 0 || rubric.length > 12) {
    return 'rubric must have 1 to 12 items.'
  }
  for (const item of rubric) {
    if (
      !isRecord(item) ||
      !isText(item.id, 100) ||
      typeof item.required !== 'boolean' ||
      !isText(item.description, 1000)
    ) {
      return 'Each rubric item needs an id, required and a description.'
    }
  }
  return {
    action: 'grade_explanation',
    topic_id: body.topic_id as string,
    prompt: body.prompt as string,
    rubric: rubric.map((item) => ({
      id: item.id as string,
      required: item.required as boolean,
      description: item.description as string,
    })),
    model_answer: body.model_answer as string,
    explanation: body.explanation as string,
  }
}

export function createHandler(services: Services) {
  return async function handle(request: Request): Promise<Response> {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS })
    }
    if (request.method !== 'POST') return reply(405, { error: 'Use POST.' })
    try {
      return await grade(request)
    } catch (error) {
      console.error('The AI proxy failed', error)
      return reply(500, { error: 'Something went wrong.' })
    }
  }

  async function grade(request: Request): Promise<Response> {
    // 1. Who's asking. Nothing else happens for a stranger.
    const userId = await services.userFor(request.headers.get('Authorization'))
    if (!userId) return reply(401, { error: 'Sign in first.' })

    let body: unknown
    try {
      body = await request.json()
    } catch {
      return reply(400, { error: 'The request is not JSON.' })
    }
    const input = readGradeRequest(body)
    if (typeof input === 'string') return reply(400, { error: input })

    // 2. May they use the AI, 3. is there budget left, 4. is there a key?
    const outcome = (status: Outcome['status']) => reply(200, { status })
    if (!(await services.isAllowed(userId))) return outcome('not_allowed')
    if ((await services.spentThisMonth()) >= services.capUsd) {
      return outcome('paused')
    }
    if (!services.grade) return outcome('unavailable')

    // 5. Ask Claude. A call that never reached it costs nothing to log.
    let graded: Graded
    try {
      graded = await services.grade(input)
    } catch (error) {
      console.error('Claude could not be reached', error)
      return outcome('unavailable')
    }

    // 6. Log what it cost, even when the answer couldn't be used.
    let aiCallId: string | null = null
    try {
      aiCallId = await services.logCall({
        user_id: userId,
        action: 'grade_explanation',
        model: graded.model,
        input_tokens: graded.usage.input_tokens,
        output_tokens: graded.usage.output_tokens,
        cost_usd: graded.cost_usd,
        request: {
          topic_id: input.topic_id,
          explanation: input.explanation,
          prompt_version: services.promptVersion,
        },
        response: graded.grading ?? { problem: graded.problem ?? 'unknown' },
      })
    } catch (error) {
      // The learner still gets their grading. The Anthropic Console's own
      // monthly limit stops spending if logging keeps failing.
      console.error('The call could not be logged', error)
    }

    if (!graded.grading) return outcome('unavailable')
    return reply(200, {
      status: 'graded',
      grading: graded.grading,
      ai_call_id: aiCallId,
      model: graded.model,
    } satisfies Outcome)
  }
}
