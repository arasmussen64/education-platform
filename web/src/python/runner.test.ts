import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { WorkerRequest, WorkerResponse } from './protocol.ts'
import { PythonRunner, type WorkerLike } from './runner.ts'

/** A stand-in for the real Python worker that each test controls by hand. */
class FakeWorker implements WorkerLike {
  onmessage: ((event: MessageEvent<WorkerResponse>) => void) | null = null
  onerror: ((event: ErrorEvent) => void) | null = null
  received: WorkerRequest[] = []
  terminated = false

  postMessage(message: WorkerRequest): void {
    this.received.push(message)
  }

  terminate(): void {
    this.terminated = true
  }

  /** Pretend the worker sent this message to the app. */
  reply(message: WorkerResponse): void {
    this.onmessage?.({ data: message } as MessageEvent<WorkerResponse>)
  }

  /** The id of the most recent request, for replying to it. */
  get lastId(): number {
    const last = this.received.at(-1)
    if (!last) throw new Error('No request received yet')
    return last.id
  }
}

function setup() {
  const workers: FakeWorker[] = []
  const runner = new PythonRunner(() => {
    const worker = new FakeWorker()
    workers.push(worker)
    return worker
  })
  return { runner, workers }
}

/** Let pending promises and zero-delay timers run. */
const flush = () => vi.advanceTimersByTimeAsync(0)

/** Track whether a promise has settled yet. */
function watch(promise: Promise<unknown>) {
  const state = { settled: false }
  void promise.then(() => {
    state.settled = true
  })
  return state
}

beforeEach(() => {
  vi.useFakeTimers()
})

afterEach(() => {
  vi.useRealTimers()
})

describe('PythonRunner', () => {
  it('waits until Python is ready before sending code', async () => {
    const { runner, workers } = setup()
    const outcome = runner.run('print(1)')
    await flush()
    expect(workers).toHaveLength(1)
    expect(workers[0].received).toHaveLength(0)

    workers[0].reply({ type: 'ready' })
    await flush()
    expect(workers[0].received).toEqual([
      { id: 1, type: 'run', code: 'print(1)', stdin: '', seed: null },
    ])

    const result = { output: '1\n', error: null, waiting_for_input: false }
    workers[0].reply({ id: 1, type: 'run-result', result })
    await expect(outcome).resolves.toEqual({ kind: 'done', result })
  })

  it('passes the typed input and the random seed to Python', async () => {
    const { runner, workers } = setup()
    void runner.run('code', { stdin: 'Ada\n', seed: 7 })
    await flush()
    workers[0].reply({ type: 'ready' })
    await flush()
    expect(workers[0].received).toEqual([
      { id: 1, type: 'run', code: 'code', stdin: 'Ada\n', seed: 7 },
    ])
  })

  it('returns check reports', async () => {
    const { runner, workers } = setup()
    const outcome = runner.check('code', 'tests')
    await flush()
    workers[0].reply({ type: 'ready' })
    await flush()
    const report = {
      status: 'ok' as const,
      message: '',
      passed: 1,
      total: 1,
      results: [],
    }
    workers[0].reply({
      id: workers[0].lastId,
      type: 'check-result',
      report,
    })
    await expect(outcome).resolves.toEqual({ kind: 'done', report })
  })

  it('stops code that runs too long and starts a fresh worker', async () => {
    const { runner, workers } = setup()
    const outcome = runner.run('while True: pass', { timeLimitMs: 5000 })
    const state = watch(outcome)
    await flush()
    workers[0].reply({ type: 'ready' })
    await flush()

    await vi.advanceTimersByTimeAsync(4999)
    expect(state.settled).toBe(false)

    await vi.advanceTimersByTimeAsync(1)
    await expect(outcome).resolves.toEqual({ kind: 'timeout' })
    expect(workers[0].terminated).toBe(true)
    expect(workers).toHaveLength(2)
  })

  it('runs requests one at a time, each with its own time limit', async () => {
    const { runner, workers } = setup()
    const first = runner.run('first', { timeLimitMs: 5000 })
    const second = runner.run('second', { timeLimitMs: 5000 })
    const secondState = watch(second)
    await flush()
    workers[0].reply({ type: 'ready' })
    await flush()
    expect(workers[0].received.map((request) => request.code)).toEqual([
      'first',
    ])

    await vi.advanceTimersByTimeAsync(4000)
    workers[0].reply({
      id: workers[0].lastId,
      type: 'run-result',
      result: { output: '', error: null, waiting_for_input: false },
    })
    await expect(first).resolves.toMatchObject({ kind: 'done' })
    await flush()
    expect(workers[0].received.map((request) => request.code)).toEqual([
      'first',
      'second',
    ])

    // The second request started at 4s, so it isn't out of time at 8s.
    await vi.advanceTimersByTimeAsync(4000)
    expect(secondState.settled).toBe(false)
    workers[0].reply({
      id: workers[0].lastId,
      type: 'run-result',
      result: { output: 'ok\n', error: null, waiting_for_input: false },
    })
    await expect(second).resolves.toEqual({
      kind: 'done',
      result: { output: 'ok\n', error: null, waiting_for_input: false },
    })
  })

  it('reports when Python fails to load, then tries again', async () => {
    const { runner, workers } = setup()
    const outcome = runner.run('x')
    await flush()
    workers[0].reply({ type: 'load-error', message: 'You seem to be offline.' })
    await expect(outcome).resolves.toEqual({
      kind: 'failed',
      message: 'You seem to be offline.',
    })
    expect(workers[0].terminated).toBe(true)

    void runner.run('x')
    await flush()
    expect(workers).toHaveLength(2)
  })

  it('fails the current request if the worker crashes', async () => {
    const { runner, workers } = setup()
    await flush()
    const outcome = runner.run('x')
    await flush()
    workers[0].reply({ type: 'ready' })
    await flush()
    workers[0].onerror?.({ message: 'Out of memory' } as ErrorEvent)
    await expect(outcome).resolves.toEqual({
      kind: 'failed',
      message: 'Out of memory',
    })
    expect(workers[0].terminated).toBe(true)
    expect(workers).toHaveLength(2)
  })

  it('passes internal errors through as failures', async () => {
    const { runner, workers } = setup()
    const outcome = runner.run('x')
    await flush()
    workers[0].reply({ type: 'ready' })
    await flush()
    workers[0].reply({
      id: workers[0].lastId,
      type: 'internal-error',
      message: 'Something broke',
    })
    await expect(outcome).resolves.toEqual({
      kind: 'failed',
      message: 'Something broke',
    })
  })
})
