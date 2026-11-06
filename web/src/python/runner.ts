import { DEFAULT_TIME_LIMIT_MS } from './constants.ts'
import type {
  CheckReport,
  ProgramResult,
  WorkerRequest,
  WorkerResponse,
} from './protocol.ts'

export type RunOutcome =
  | { kind: 'done'; result: ProgramResult }
  | { kind: 'timeout' }
  | { kind: 'failed'; message: string }

export type CheckOutcome =
  | { kind: 'done'; report: CheckReport }
  | { kind: 'timeout' }
  | { kind: 'failed'; message: string }

/** True when every test ran and passed. */
export function allChecksPassed(outcome: CheckOutcome): boolean {
  return (
    outcome.kind === 'done' &&
    outcome.report.status === 'ok' &&
    outcome.report.total > 0 &&
    outcome.report.passed === outcome.report.total
  )
}

export type RunOptions = {
  /** Every line typed so far, each ending with "\n". */
  stdin?: string
  /** Seeds Python's random module, so re-runs make the same choices. */
  seed?: number | null
  timeLimitMs?: number
}

/** The parts of a Web Worker the runner uses, so tests can pass a fake. */
export type WorkerLike = {
  postMessage(message: WorkerRequest): void
  terminate(): void
  onmessage: ((event: MessageEvent<WorkerResponse>) => void) | null
  onerror: ((event: ErrorEvent) => void) | null
}

export type CreateWorker = () => WorkerLike

const createBrowserWorker: CreateWorker = () =>
  new Worker(new URL('./worker.ts', import.meta.url), {
    type: 'module',
  }) as unknown as WorkerLike

type RequestBody =
  | { type: 'run'; code: string; stdin: string; seed: number | null }
  | { type: 'check'; code: string; tests: string }

type Reply =
  | { kind: 'done'; message: WorkerResponse }
  | { kind: 'timeout' }
  | { kind: 'failed'; message: string }

type Pending = {
  id: number
  resolve: (reply: Reply) => void
  timer: ReturnType<typeof setTimeout>
}

function describe(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}

/**
 * Runs learner Python in a background worker, one request at a time.
 *
 * Python running in a worker can't be interrupted from outside, so when code
 * runs past its time limit the runner throws the whole worker away and starts
 * a fresh one.
 */
export class PythonRunner {
  private readonly createWorker: CreateWorker
  private worker: WorkerLike | null = null
  private booting: Promise<WorkerLike> | null = null
  private pending: Pending | null = null
  private queue: Promise<unknown> = Promise.resolve()
  private nextId = 1

  constructor(createWorker: CreateWorker = createBrowserWorker) {
    this.createWorker = createWorker
  }

  /** Starts loading Python, if it isn't already. Resolves once it's ready. */
  start(): Promise<void> {
    return this.boot().then(() => undefined)
  }

  async run(
    code: string,
    {
      stdin = '',
      seed = null,
      timeLimitMs = DEFAULT_TIME_LIMIT_MS,
    }: RunOptions = {},
  ): Promise<RunOutcome> {
    const reply = await this.send(
      { type: 'run', code, stdin, seed },
      timeLimitMs,
    )
    if (reply.kind !== 'done') return reply
    if (reply.message.type === 'run-result') {
      return { kind: 'done', result: reply.message.result }
    }
    return { kind: 'failed', message: unexpected(reply.message) }
  }

  async check(
    code: string,
    tests: string,
    { timeLimitMs = DEFAULT_TIME_LIMIT_MS }: { timeLimitMs?: number } = {},
  ): Promise<CheckOutcome> {
    const reply = await this.send({ type: 'check', code, tests }, timeLimitMs)
    if (reply.kind !== 'done') return reply
    if (reply.message.type === 'check-result') {
      return { kind: 'done', report: reply.message.report }
    }
    return { kind: 'failed', message: unexpected(reply.message) }
  }

  private boot(): Promise<WorkerLike> {
    if (!this.booting) {
      const booting = new Promise<WorkerLike>((resolve, reject) => {
        const worker = this.createWorker()
        worker.onmessage = (event) => {
          const message = event.data
          if (message.type === 'ready') {
            this.worker = worker
            resolve(worker)
          } else if (message.type === 'load-error') {
            worker.terminate()
            reject(new Error(message.message))
          } else {
            this.settle(message)
          }
        }
        worker.onerror = (event) => {
          const message = event.message || 'Python stopped unexpectedly.'
          if (this.worker === worker) {
            this.fail(message)
          } else {
            worker.terminate()
            reject(new Error(message))
          }
        }
      })
      // After a failed start, the next request tries again from scratch.
      booting.catch(() => {
        if (this.booting === booting) this.booting = null
      })
      this.booting = booting
    }
    return this.booting
  }

  /** Requests wait their turn, so each one's time limit starts when it runs. */
  private send(body: RequestBody, timeLimitMs: number): Promise<Reply> {
    const task = this.queue.then(() => this.sendNow(body, timeLimitMs))
    this.queue = task.catch(() => undefined)
    return task
  }

  private async sendNow(
    body: RequestBody,
    timeLimitMs: number,
  ): Promise<Reply> {
    let worker: WorkerLike
    try {
      worker = await this.boot()
    } catch (error) {
      return { kind: 'failed', message: describe(error) }
    }
    const id = this.nextId++
    return new Promise<Reply>((resolve) => {
      const timer = setTimeout(() => {
        this.pending = null
        this.restart()
        resolve({ kind: 'timeout' })
      }, timeLimitMs)
      this.pending = { id, resolve, timer }
      worker.postMessage({ ...body, id })
    })
  }

  private settle(message: WorkerResponse): void {
    const pending = this.pending
    if (!pending || !('id' in message) || message.id !== pending.id) return
    clearTimeout(pending.timer)
    this.pending = null
    if (message.type === 'internal-error') {
      pending.resolve({ kind: 'failed', message: message.message })
    } else {
      pending.resolve({ kind: 'done', message })
    }
  }

  /** The worker crashed: fail the current request and start over. */
  private fail(message: string): void {
    const pending = this.pending
    if (pending) {
      clearTimeout(pending.timer)
      this.pending = null
      pending.resolve({ kind: 'failed', message })
    }
    this.restart()
  }

  /** Replace the worker with a fresh one, warming it up in the background. */
  private restart(): void {
    this.worker?.terminate()
    this.worker = null
    this.booting = null
    this.start().catch(() => undefined)
  }
}

function unexpected(message: WorkerResponse): string {
  return `Unexpected reply from Python: ${message.type}`
}

let shared: PythonRunner | null = null

/** The app's single Python runner, shared by every code editor. */
export function getPythonRunner(): PythonRunner {
  shared ??= new PythonRunner()
  return shared
}
