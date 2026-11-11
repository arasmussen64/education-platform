// The AI proxy's front door (ADR-0013, ADR-0015): who may call it, what they
// may send, and what happens, in order. It has two actions: grading an
// explanation, and a hint from the tutor. The real services are passed in
// (index.ts), so the tests can check every path with fakes.
import type { Usage } from './cost.ts'
import type { GradeInput, Grading } from './grading.ts'
import {
  type CheckSummary,
  type Hint,
  type HintInput,
  levelFor,
  type TestSummary,
} from './tutor.ts'

export type GradeRequest = GradeInput & {
  action: 'grade_explanation'
  topic_id: string
}

export type HintRequest = HintInput & {
  action: 'tutor_hint'
  topic_id: string
  item_id: string
}

export type ProxyRequest = GradeRequest | HintRequest

/** What one call to Claude cost, whatever it was for. */
type Called = {
  model: string
  usage: Usage
  cost_usd: number
  /** Why Claude's answer couldn't be used, when it couldn't. */
  problem?: string
}

/** A grading call. `grading` is null when the answer couldn't be used. */
export type Graded = Called & { grading: Grading | null }

/** A tutor call. `hint` is null when the reply couldn't be used. */
export type Hinted = Called & { hint: Hint | null }

/**
 * What one call cost, as the budget counts it: the smallest row of the
 * ai_calls table. Written on its own when the full row can't be.
 */
export type Spend = {
  user_id: string
  action: ProxyRequest['action']
  model: string
  input_tokens: number
  output_tokens: number
  cost_usd: number
}

/** One full row of the ai_calls table: the spend, and what was asked and answered. */
export type CallLog = Spend & {
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
  /** Hints with Claude (ADR-0015). Null when there's no API key. */
  hint: ((input: HintInput) => Promise<Hinted>) | null
  /** Saves one call, in full or just its spend, and returns its ID. */
  logCall(call: CallLog | Spend): Promise<string>
  /** Calls stop once the month's spending reaches this, in US dollars. */
  capUsd: number
  /** Which version of the grading instructions this proxy uses, for the log. */
  promptVersion: number
  /** The same for the tutor's instructions. */
  tutorPromptVersion: number
}

/** What the browser gets back. Anything but graded or hinted means: not now. */
export type Outcome =
  | {
      status: 'graded'
      grading: Grading
      ai_call_id: string | null
      model: string
    }
  | {
      status: 'hinted'
      hint: Hint
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

/** The learner's code is cut here, so a call stays small and the log fits. */
export const MAX_CODE_CHARS = 6000
export const MAX_QUESTION_CHARS = 500
const MAX_EARLIER_HINTS = 8
const MAX_TESTS = 20

/**
 * The ai_calls table refuses a request bigger than 16,384 bytes (its
 * migration, 20261108223826_ai_calls.sql), and a refused row would leave the
 * call's cost uncounted. So the logged request is cut to fit, by bytes, not
 * characters: "é" is one character and two bytes, "中" one and three, so
 * 6,000 characters can be 18,000 bytes. 1,024 bytes are kept back for
 * Postgres's own bookkeeping inside the column.
 */
export const MAX_LOGGED_REQUEST_BYTES = 16_384 - 1_024

/** Marks where logged text was cut, like clip() in the browser (web/src/events/payloads.ts). */
const CUT_MARKER = '…(cut)'

const encoder = new TextEncoder()

/** How many bytes `text` takes in UTF-8, as Postgres stores it. */
export const bytesOf = (text: string) => encoder.encode(text).length

/**
 * `text` cut to at most `maxBytes` bytes of UTF-8, its marker included.
 * It's cut between characters, never through one: `for...of` walks whole
 * characters, so an emoji (two halves in JavaScript) stays whole.
 */
export function clipBytes(text: string, maxBytes: number): string {
  if (bytesOf(text) <= maxBytes) return text
  const room = maxBytes - bytesOf(CUT_MARKER)
  if (room < 0) return ''
  let used = 0
  let end = 0
  for (const character of text) {
    const size = bytesOf(character)
    if (used + size > room) break
    used += size
    end += character.length
  }
  return `${text.slice(0, end)}${CUT_MARKER}`
}

/**
 * The request as it's logged: `field`, its one long text, cut by bytes so
 * the whole request fits its column. JSON measures the rest a little
 * generously (its quotes and commas), which only adds to the margin.
 */
export function requestForLog(
  request: Record<string, unknown>,
  field: string,
): Record<string, unknown> {
  const text = request[field]
  if (typeof text !== 'string') return request
  const rest = bytesOf(JSON.stringify({ ...request, [field]: '' }))
  return {
    ...request,
    [field]: clipBytes(text, Math.max(0, MAX_LOGGED_REQUEST_BYTES - rest)),
  }
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

const isStringList = (
  value: unknown,
  maxItems: number,
  maxChars: number,
): value is string[] =>
  Array.isArray(value) &&
  value.length <= maxItems &&
  value.every((item) => typeof item === 'string' && item.length <= maxChars)

const isCount = (value: unknown): value is number =>
  Number.isInteger(value) && (value as number) >= 0

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

/** The latest Check as the browser summarizes it, or what's wrong with it. */
function readCheck(value: unknown): CheckSummary | null | string {
  if (value === null || value === undefined) return null
  if (
    !isRecord(value) ||
    !isCount(value.passed) ||
    !isCount(value.total) ||
    !Array.isArray(value.results) ||
    value.results.length > MAX_TESTS
  ) {
    return `check needs passed, total and up to ${MAX_TESTS} results.`
  }
  const results: TestSummary[] = []
  for (const result of value.results) {
    if (
      !isRecord(result) ||
      !isText(result.description, 300, true) ||
      (result.outcome !== 'pass' &&
        result.outcome !== 'fail' &&
        result.outcome !== 'error') ||
      !isText(result.message, 1000, true)
    ) {
      return 'Each check result needs a description, an outcome and a message.'
    }
    results.push({
      description: result.description as string,
      outcome: result.outcome,
      message: result.message as string,
    })
  }
  return { passed: value.passed, total: value.total, results }
}

/** A tutor request, checked, or what's wrong with it. */
export function readHintRequest(body: unknown): HintRequest | string {
  if (!isRecord(body)) return 'Send a JSON object.'
  if (body.action !== 'tutor_hint') return 'Unknown action.'
  if (!isText(body.topic_id, 200)) return 'topic_id is missing or too long.'
  if (!isText(body.item_id, 200)) return 'item_id is missing or too long.'
  const exercise = body.exercise
  if (
    !isRecord(exercise) ||
    !isText(exercise.title, 200) ||
    !isText(exercise.prompt, 4000) ||
    !isText(exercise.solution, MAX_CODE_CHARS, true) ||
    !isStringList(exercise.hints, 10, 1000)
  ) {
    return 'exercise needs a title, a prompt, a solution and up to 10 hints.'
  }
  const code = body.code ?? ''
  if (!isText(code, MAX_CODE_CHARS, true)) {
    return `The code is longer than ${MAX_CODE_CHARS.toLocaleString('en-US')} characters.`
  }
  const question = body.question ?? ''
  if (!isText(question, MAX_QUESTION_CHARS, true)) {
    return `The question is longer than ${MAX_QUESTION_CHARS} characters.`
  }
  const earlier = body.earlier ?? []
  if (!isStringList(earlier, MAX_EARLIER_HINTS, 1000)) {
    return `earlier must be up to ${MAX_EARLIER_HINTS} earlier hints.`
  }
  const check = readCheck(body.check)
  if (typeof check === 'string') return check
  return {
    action: 'tutor_hint',
    topic_id: body.topic_id as string,
    item_id: body.item_id as string,
    exercise: {
      title: exercise.title as string,
      prompt: exercise.prompt as string,
      hints: exercise.hints,
      solution: exercise.solution as string,
    },
    code: code as string,
    check,
    question: question as string,
    earlier,
  }
}

/** Whichever action the browser asked for, checked. */
export function readRequest(body: unknown): ProxyRequest | string {
  if (!isRecord(body)) return 'Send a JSON object.'
  if (body.action === 'grade_explanation') return readGradeRequest(body)
  if (body.action === 'tutor_hint') return readHintRequest(body)
  return 'Unknown action.'
}

export function createHandler(services: Services) {
  // Calls Claude answered whose cost couldn't be written down at all, oldest
  // first. While any wait here, no new call is made: the cap can only stop
  // spending it can see (fail closed). Each new request tries to write them
  // again first. They live in this running copy of the function only; a
  // fresh copy starts empty, so at most one call per copy can go uncounted.
  const unrecorded: Spend[] = []

  /** Writes the waiting spends down. True once none are left. */
  async function recordUnrecorded(): Promise<boolean> {
    while (unrecorded.length > 0) {
      // Taken off the list first, so two requests at once can't write it twice.
      const spend = unrecorded.shift() as Spend
      try {
        await services.logCall(spend)
      } catch (error) {
        unrecorded.unshift(spend)
        console.error('An earlier call still could not be counted', error)
        return false
      }
    }
    return true
  }

  return async function handle(request: Request): Promise<Response> {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS })
    }
    if (request.method !== 'POST') return reply(405, { error: 'Use POST.' })
    try {
      return await respond(request)
    } catch (error) {
      console.error('The AI proxy failed', error)
      return reply(500, { error: 'Something went wrong.' })
    }
  }

  async function respond(request: Request): Promise<Response> {
    // 1. Who's asking. Nothing else happens for a stranger.
    const userId = await services.userFor(request.headers.get('Authorization'))
    if (!userId) return reply(401, { error: 'Sign in first.' })

    let body: unknown
    try {
      body = await request.json()
    } catch {
      return reply(400, { error: 'The request is not JSON.' })
    }
    const input = readRequest(body)
    if (typeof input === 'string') return reply(400, { error: input })

    // 2. May they use the AI? 3. Is every earlier call's cost written down,
    // and 4. is there budget left?
    const outcome = (status: Outcome['status']) => reply(200, { status })
    if (!(await services.isAllowed(userId))) return outcome('not_allowed')
    if (!(await recordUnrecorded())) return outcome('unavailable')
    if ((await services.spentThisMonth()) >= services.capUsd) {
      return outcome('paused')
    }

    // 5. Is there a key? Then 6. ask Claude, and 7. log the call.
    if (input.action === 'grade_explanation') {
      const grade = services.grade
      if (!grade) return outcome('unavailable')
      return completeCall(userId, () => grade(input), {
        action: 'grade_explanation',
        request: requestForLog(
          {
            topic_id: input.topic_id,
            explanation: input.explanation,
            prompt_version: services.promptVersion,
          },
          'explanation',
        ),
        response: (graded) => graded.grading,
        answer: (graded, ai_call_id) =>
          graded.grading && {
            status: 'graded',
            grading: graded.grading,
            ai_call_id,
            model: graded.model,
          },
      })
    }
    const hint = services.hint
    if (!hint) return outcome('unavailable')
    return completeCall(userId, () => hint(input), {
      action: 'tutor_hint',
      request: requestForLog(
        {
          topic_id: input.topic_id,
          item_id: input.item_id,
          level: levelFor(input.earlier.length),
          hints_so_far: input.earlier.length,
          question: input.question,
          code: input.code,
          prompt_version: services.tutorPromptVersion,
        },
        'code',
      ),
      response: (hinted) => hinted.hint,
      answer: (hinted, ai_call_id) =>
        hinted.hint && {
          status: 'hinted',
          hint: hinted.hint,
          ai_call_id,
          model: hinted.model,
        },
    })
  }

  /**
   * Steps 6 and 7, the same for both actions: ask Claude, log what it cost
   * (even when the answer couldn't be used), and answer the browser.
   */
  async function completeCall<Result extends Called>(
    userId: string,
    ask: () => Promise<Result>,
    call: {
      action: CallLog['action']
      request: Record<string, unknown>
      /** What to log as the response, or null when the answer was unusable. */
      response: (result: Result) => Record<string, unknown> | null
      /** What to tell the browser, or null when the answer was unusable. */
      answer: (result: Result, aiCallId: string | null) => Outcome | null
    },
  ): Promise<Response> {
    // A call that never reached Claude costs nothing to log.
    let result: Result
    try {
      result = await ask()
    } catch (error) {
      console.error('Claude could not be reached', error)
      return reply(200, { status: 'unavailable' })
    }

    // Claude has answered, so the call costs money: the budget must count it.
    const spend: Spend = {
      user_id: userId,
      action: call.action,
      model: result.model,
      input_tokens: result.usage.input_tokens,
      output_tokens: result.usage.output_tokens,
      cost_usd: result.cost_usd,
    }
    let aiCallId: string
    try {
      aiCallId = await services.logCall({
        ...spend,
        request: call.request,
        response: call.response(result) ?? {
          problem: result.problem ?? 'unknown',
        },
      })
    } catch (error) {
      console.error('The call could not be logged in full', error)
      try {
        // The spend alone, so the cap still counts it.
        aiCallId = await services.logCall(spend)
      } catch (error) {
        // Not even that: no more calls until it's written (see `unrecorded`),
        // and no answer this time, so a failure is never a silent success.
        console.error('The call could not be counted: calls stop', error)
        unrecorded.push(spend)
        return reply(200, { status: 'unavailable' })
      }
    }

    const answer = call.answer(result, aiCallId)
    return reply(200, answer ?? { status: 'unavailable' })
  }
}
