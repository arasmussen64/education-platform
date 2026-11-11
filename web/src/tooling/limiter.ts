/**
 * A waiting line for work that mustn't all happen at once.
 *
 * `limiter(3)` gives back a function. Hand it jobs (functions that return a
 * promise) and it runs at most three of them at a time; the rest wait their
 * turn, first come first served. Each call resolves or rejects exactly as its
 * job does.
 *
 * The build uses it to read files a few at a time (see vite.config.ts).
 */
export function limiter(max: number) {
  if (!Number.isInteger(max) || max < 1) {
    throw new Error(`limiter needs a whole number of at least 1, got ${max}`)
  }

  // How many more jobs may start right now.
  let free = max
  // Jobs that arrived while none were free. Calling an entry lets that job go.
  const waiting: (() => void)[] = []

  return async function run<T>(job: () => Promise<T>): Promise<T> {
    if (free > 0) {
      free -= 1
    } else {
      await new Promise<void>((go) => waiting.push(go))
    }
    try {
      return await job()
    } finally {
      // A finished job hands its place straight to the next in line. Giving
      // the place back first (free += 1) would let a newcomer take it in the
      // moment before the waiting job wakes, and one job too many would run.
      const next = waiting.shift()
      if (next) next()
      else free += 1
    }
  }
}
