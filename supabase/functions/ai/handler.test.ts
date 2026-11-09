import assert from 'node:assert/strict'
import { costOf, isPricedModel } from './cost.ts'
import type { Grading } from './grading.ts'
import {
  type CallLog,
  createHandler,
  type Graded,
  type Hinted,
  readGradeRequest,
  readHintRequest,
  type Services,
} from './handler.ts'

const BODY = {
  action: 'grade_explanation',
  topic_id: 'py.values-and-types',
  prompt: 'Why does it print 12?',
  rubric: [{ id: 'input-is-text', required: true, description: 'Input is text.' }],
  model_answer: 'Typed input is text.',
  explanation: 'Because input() gives a string.',
}

const PASS: Grading = {
  verdict: 'pass',
  rubric: [{ id: 'input-is-text', met: true }],
  questions: [],
}

const GRADED: Graded = {
  model: 'claude-haiku-5-5',
  usage: { input_tokens: 1500, output_tokens: 1000 },
  cost_usd: 0.00065,
  grading: PASS,
}

const HINT_BODY = {
  action: 'tutor_hint',
  topic_id: 'py.while-loops',
  item_id: 'fill-count-up',
  exercise: {
    title: 'Count to n',
    prompt: 'Count from 1 up to the number typed.',
    hints: ['The first number printed is 1.'],
    solution: 'i = 1\nwhile i <= n:\n    print(i)\n    i += 1\n',
  },
  code: 'i = ...\nwhile i <= n:\n    print(i)\n',
  check: {
    passed: 0,
    total: 1,
    results: [{ description: 'Typing 3 prints 1, 2, 3.', outcome: 'fail', message: '' }],
  },
  question: 'Why does it print nothing?',
  earlier: [],
}

const HINTED: Hinted = {
  model: 'claude-haiku-5-5',
  usage: { input_tokens: 2000, output_tokens: 150 },
  cost_usd: 0.000275,
  hint: { text: 'What is i before the loop starts?', level: 'nudge', replaced: false },
}

/** Fake services, all saying yes, that note what was called. */
function fakes(overrides: Partial<Services> = {}) {
  const calls: string[] = []
  const logged: CallLog[] = []
  const services: Services = {
    userFor: (authorization) => {
      calls.push('userFor')
      return Promise.resolve(authorization === 'Bearer good' ? 'ada' : null)
    },
    isAllowed: () => {
      calls.push('isAllowed')
      return Promise.resolve(true)
    },
    spentThisMonth: () => {
      calls.push('spentThisMonth')
      return Promise.resolve(1.25)
    },
    grade: () => {
      calls.push('grade')
      return Promise.resolve(GRADED)
    },
    hint: () => {
      calls.push('hint')
      return Promise.resolve(HINTED)
    },
    logCall: (call) => {
      calls.push('logCall')
      logged.push(call)
      return Promise.resolve('call-1')
    },
    capUsd: 10,
    promptVersion: 1,
    tutorPromptVersion: 1,
    ...overrides,
  }
  return { handle: createHandler(services), calls, logged }
}

function post(body: unknown = BODY, token = 'good') {
  return new Request('http://localhost/ai', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(body),
  })
}

async function send(handle: (r: Request) => Promise<Response>, request: Request) {
  const response = await handle(request)
  return { status: response.status, body: await response.json() }
}

Deno.test('grades, logs the cost, and returns the verdict', async () => {
  const { handle, calls, logged } = fakes()
  const { status, body } = await send(handle, post())
  assert.equal(status, 200)
  assert.deepEqual(body, {
    status: 'graded',
    grading: PASS,
    ai_call_id: 'call-1',
    model: 'claude-haiku-5-5',
  })
  assert.deepEqual(calls, ['userFor', 'isAllowed', 'spentThisMonth', 'grade', 'logCall'])
  assert.deepEqual(logged[0], {
    user_id: 'ada',
    action: 'grade_explanation',
    model: 'claude-haiku-5-5',
    input_tokens: 1500,
    output_tokens: 1000,
    cost_usd: 0.00065,
    request: {
      topic_id: 'py.values-and-types',
      explanation: 'Because input() gives a string.',
      prompt_version: 1,
    },
    response: PASS,
  })
})

Deno.test('a stranger gets nothing, and nothing else runs', async () => {
  const { handle, calls } = fakes()
  assert.equal((await send(handle, post(BODY, 'forged'))).status, 401)
  assert.deepEqual(calls, ['userFor'])
})

Deno.test('a learner who is not allowed is told so, before any spending', async () => {
  const { handle, calls } = fakes({ isAllowed: () => Promise.resolve(false) })
  assert.deepEqual((await send(handle, post())).body, { status: 'not_allowed' })
  assert.ok(!calls.includes('grade'))
})

Deno.test('the budget cap pauses grading once the month reaches it', async () => {
  const { handle, calls } = fakes({ spentThisMonth: () => Promise.resolve(10) })
  assert.deepEqual((await send(handle, post())).body, { status: 'paused' })
  assert.ok(!calls.includes('grade'))
})

Deno.test('without an API key, grading is unavailable', async () => {
  const { handle } = fakes({ grade: null })
  assert.deepEqual((await send(handle, post())).body, { status: 'unavailable' })
})

Deno.test('a failed call to Claude costs nothing to log', async () => {
  const { handle, calls } = fakes({
    grade: () => Promise.reject(new Error('529 overloaded')),
  })
  assert.deepEqual((await send(handle, post())).body, { status: 'unavailable' })
  assert.ok(!calls.includes('logCall'))
})

Deno.test('an answer that cannot be used is still logged, with its cost', async () => {
  const { handle, logged } = fakes({
    grade: () =>
      Promise.resolve({ ...GRADED, grading: null, problem: 'Claude stopped early: refusal' }),
  })
  assert.deepEqual((await send(handle, post())).body, { status: 'unavailable' })
  assert.equal(logged[0]?.cost_usd, 0.00065)
  assert.deepEqual(logged[0]?.response, { problem: 'Claude stopped early: refusal' })
})

Deno.test('the learner keeps their grading if logging fails', async () => {
  const { handle } = fakes({ logCall: () => Promise.reject(new Error('db down')) })
  const { body } = await send(handle, post())
  assert.equal(body.status, 'graded')
  assert.equal(body.ai_call_id, null)
})

Deno.test('turns away bad requests before calling anything costly', async () => {
  const { handle, calls } = fakes()
  assert.equal((await send(handle, post({ ...BODY, explanation: '   ' }))).status, 400)
  assert.equal((await send(handle, post({ ...BODY, action: 'tutor' }))).status, 400)
  assert.ok(!calls.includes('isAllowed'))
  assert.match(
    readGradeRequest({ ...BODY, explanation: 'x'.repeat(4001) }) as string,
    /4,000 characters/,
  )
  assert.equal(readGradeRequest({ ...BODY, rubric: [] }), 'rubric must have 1 to 12 items.')
})

Deno.test('answers the browser\'s CORS check, and only takes POST', async () => {
  const { handle } = fakes()
  const options = await handle(new Request('http://localhost/ai', { method: 'OPTIONS' }))
  assert.equal(options.status, 204)
  assert.equal(options.headers.get('Access-Control-Allow-Origin'), '*')
  assert.equal((await handle(new Request('http://localhost/ai'))).status, 405)
})

Deno.test('a broken service is a 500 the browser can read', async () => {
  const { handle } = fakes({ spentThisMonth: () => Promise.reject(new Error('db down')) })
  const response = await handle(post())
  assert.equal(response.status, 500)
  assert.equal(response.headers.get('Access-Control-Allow-Origin'), '*')
})

Deno.test('cost: tokens times the price per million', () => {
  assert.equal(isPricedModel('claude-haiku-5-5'), true)
  assert.equal(isPricedModel('claude-unknown'), false)
  assert.equal(
    costOf('claude-haiku-5-5', { input_tokens: 1500, output_tokens: 1000 }),
    0.00065,
  )
  assert.equal(
    costOf('claude-opus-5-5', { input_tokens: 1_000_000, output_tokens: 0 }),
    4,
  )
})

Deno.test('a hint: the same checks, then the rung, the code and the question are logged', async () => {
  const { handle, calls, logged } = fakes()
  const { status, body } = await send(handle, post(HINT_BODY))
  assert.equal(status, 200)
  assert.deepEqual(body, {
    status: 'hinted',
    hint: { text: 'What is i before the loop starts?', level: 'nudge', replaced: false },
    ai_call_id: 'call-1',
    model: 'claude-haiku-5-5',
  })
  assert.deepEqual(calls, ['userFor', 'isAllowed', 'spentThisMonth', 'hint', 'logCall'])
  assert.deepEqual(logged[0], {
    user_id: 'ada',
    action: 'tutor_hint',
    model: 'claude-haiku-5-5',
    input_tokens: 2000,
    output_tokens: 150,
    cost_usd: 0.000275,
    request: {
      topic_id: 'py.while-loops',
      item_id: 'fill-count-up',
      level: 'nudge',
      hints_so_far: 0,
      question: 'Why does it print nothing?',
      code: 'i = ...\nwhile i <= n:\n    print(i)\n',
      prompt_version: 1,
    },
    response: { text: 'What is i before the loop starts?', level: 'nudge', replaced: false },
  })
})

Deno.test('the budget cap and the allowed flag guard hints too, before any spending', async () => {
  const paused = fakes({ spentThisMonth: () => Promise.resolve(10) })
  assert.deepEqual((await send(paused.handle, post(HINT_BODY))).body, { status: 'paused' })
  assert.ok(!paused.calls.includes('hint'))
  const notAllowed = fakes({ isAllowed: () => Promise.resolve(false) })
  assert.deepEqual((await send(notAllowed.handle, post(HINT_BODY))).body, {
    status: 'not_allowed',
  })
})

Deno.test('without an API key, the tutor is unavailable, and a reply that cannot be used is still logged', async () => {
  const { handle } = fakes({ hint: null })
  assert.deepEqual((await send(handle, post(HINT_BODY))).body, { status: 'unavailable' })

  const refused = fakes({
    hint: () => Promise.resolve({ ...HINTED, hint: null, problem: 'Claude stopped early: refusal' }),
  })
  assert.deepEqual((await send(refused.handle, post(HINT_BODY))).body, { status: 'unavailable' })
  assert.deepEqual(refused.logged[0]?.response, { problem: 'Claude stopped early: refusal' })
  assert.equal(refused.logged[0]?.cost_usd, 0.000275)
})

Deno.test('a replaced hint is returned and logged as replaced, with the reason', async () => {
  const replaced = {
    text: 'The first number printed is 1.',
    level: 'nudge' as const,
    replaced: true,
    reason: '5 lines of code',
  }
  const { handle, logged } = fakes({ hint: () => Promise.resolve({ ...HINTED, hint: replaced }) })
  const { body } = await send(handle, post(HINT_BODY))
  assert.deepEqual(body.hint, replaced)
  assert.deepEqual(logged[0]?.response, replaced)
})

Deno.test('a hint request is checked before anything costly: sizes, shapes, defaults', async () => {
  const { handle, calls } = fakes()
  assert.equal(
    (await send(handle, post({ ...HINT_BODY, code: 'x'.repeat(6001) }))).status,
    400,
  )
  assert.equal((await send(handle, post({ ...HINT_BODY, exercise: {} }))).status, 400)
  assert.ok(!calls.includes('isAllowed'))
  assert.match(
    readHintRequest({ ...HINT_BODY, question: 'x'.repeat(501) }) as string,
    /500 characters/,
  )
  assert.match(
    readHintRequest({ ...HINT_BODY, check: { passed: 'no' } }) as string,
    /check needs passed/,
  )
  // A first ask can leave the code, question, check and earlier hints out.
  const minimal = readHintRequest({
    action: 'tutor_hint',
    topic_id: 'py.while-loops',
    item_id: 'fill-count-up',
    exercise: HINT_BODY.exercise,
  })
  assert.ok(typeof minimal !== 'string')
  assert.deepEqual(
    { code: minimal.code, question: minimal.question, check: minimal.check, earlier: minimal.earlier },
    { code: '', question: '', check: null, earlier: [] },
  )
})
