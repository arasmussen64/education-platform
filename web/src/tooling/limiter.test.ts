import { describe, expect, it } from 'vitest'
import { limiter } from './limiter'

/** A job the test finishes by hand, so it controls what is running. */
function manualJob<T>() {
  let finish!: (value: T) => void
  let fail!: (reason: Error) => void
  let started = false
  const done = new Promise<T>((resolve, reject) => {
    finish = resolve
    fail = reject
  })
  const job = () => {
    started = true
    return done
  }
  return { job, finish, fail, hasStarted: () => started }
}

/** Lets every promise callback that is ready to run, run. */
const settle = () => new Promise((resolve) => setTimeout(resolve, 0))

describe('limiter', () => {
  it('starts jobs straight away while there is room', async () => {
    const run = limiter(2)
    const a = manualJob<string>()
    const b = manualJob<string>()

    const resultA = run(a.job)
    const resultB = run(b.job)

    expect(a.hasStarted()).toBe(true)
    expect(b.hasStarted()).toBe(true)
    a.finish('a')
    b.finish('b')
    expect(await resultA).toBe('a')
    expect(await resultB).toBe('b')
  })

  it('makes the next job wait until one finishes', async () => {
    const run = limiter(2)
    const a = manualJob<void>()
    const b = manualJob<void>()
    const c = manualJob<void>()

    void run(a.job)
    void run(b.job)
    const resultC = run(c.job)
    await settle()
    expect(c.hasStarted()).toBe(false)

    a.finish()
    await settle()
    expect(c.hasStarted()).toBe(true)

    b.finish()
    c.finish()
    await resultC
  })

  it('never runs more than the limit, however many jobs arrive', async () => {
    const run = limiter(3)
    let running = 0
    let most = 0

    const job = async (value: number) => {
      running += 1
      most = Math.max(most, running)
      await settle()
      running -= 1
      return value
    }
    const results = await Promise.all(
      Array.from({ length: 50 }, (_, i) => run(() => job(i))),
    )

    expect(most).toBe(3)
    expect(results).toEqual(Array.from({ length: 50 }, (_, i) => i))
  })

  it("doesn't let a newcomer take the place of a job that was waiting", async () => {
    const run = limiter(1)
    const first = manualJob<void>()
    const waited = manualJob<void>()
    const newcomer = manualJob<void>()

    const firstResult = run(first.job)
    void run(waited.job)
    await settle()

    // The first job finishes, and in the same moment a new one arrives.
    first.finish()
    await firstResult
    void run(newcomer.job)
    await settle()

    expect(waited.hasStarted()).toBe(true)
    expect(newcomer.hasStarted()).toBe(false)

    waited.finish()
    await settle()
    expect(newcomer.hasStarted()).toBe(true)
    newcomer.finish()
  })

  it('passes a failure on, and still frees the place', async () => {
    const run = limiter(1)
    const broken = manualJob<void>()
    const after = manualJob<string>()

    const brokenResult = run(broken.job)
    const afterResult = run(after.job)
    broken.fail(new Error('could not read'))

    await expect(brokenResult).rejects.toThrow('could not read')
    await settle()
    expect(after.hasStarted()).toBe(true)
    after.finish('fine')
    expect(await afterResult).toBe('fine')
  })

  it('refuses a limit that makes no sense', () => {
    expect(() => limiter(0)).toThrow('at least 1')
    expect(() => limiter(1.5)).toThrow('at least 1')
  })
})
