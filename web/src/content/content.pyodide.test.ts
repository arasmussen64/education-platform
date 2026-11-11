// @vitest-environment node

// Every ready exercise's reference solution must pass its own tests in the
// browser's Python (Pyodide), not only in the Python that CI installs. The
// validator proves the same under CPython in CI (tools/validate_content.py);
// this proves the browser's Python agrees, so a learner is never shown an
// exercise whose own solution fails in the app. Only the reference solutions
// run here: a known-wrong solution may loop forever on purpose, and Pyodide
// in Node has no way to stop it, so the validator keeps those.
//
// It also proves each solution is fast enough. The app stops a Run or a
// Check after the exercise's time limit (time_limit_ms in its exercise.yaml,
// 5 seconds when it doesn't say), so a correct solution that runs longer
// can never pass in the app. The validator can't see that: CPython is
// faster than Pyodide. So every Check is timed here, and so is the Run of
// every worked example (Run is the button a worked example is read with).
//
// How the two numbers relate: authors keep each solution under 40% of its
// limit on their own machine ("npm run time:content" in web/ measures it),
// and this test fails only at 100%. That leaves a machine two and a half
// times slower than the author's before the test fails, which is what keeps
// it from failing by chance on CI's slower, busier machines.
import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadPyodide, type PyodideAPI } from 'pyodide'
import { afterAll, beforeAll, describe, expect, it } from 'vitest'
import { parse as parseYaml } from 'yaml'
import { DEFAULT_TIME_LIMIT_MS } from '../python/constants.ts'
import { installHarness, runChecks, runProgram } from '../python/session.ts'

const TOPICS = fileURLToPath(
  new URL('../../../content/topics', import.meta.url),
)

type Case = {
  topic: string
  exercise: string
  folder: string
  /** How long the app lets this exercise's Run or Check take. */
  limitMs: number
  isWorkedExample: boolean
}

/** One timed Run or Check, kept for the report at the end. */
type Timing = {
  name: string
  button: 'Run' | 'Check'
  ms: number
  limitMs: number
}

/** The packages ready topics declare (ADR-0023), loaded once for all cases. */
const PACKAGES = new Set<string>()

function readyCases(): Case[] {
  const cases: Case[] = []
  for (const topic of readdirSync(TOPICS).sort()) {
    const topicFile = join(TOPICS, topic, 'topic.yaml')
    if (!existsSync(topicFile)) continue
    const meta = parseYaml(readFileSync(topicFile, 'utf8')) as {
      status?: string
      packages?: string[]
    }
    if (meta.status !== 'ready') continue
    for (const name of meta.packages ?? []) PACKAGES.add(name)
    const exercises = join(TOPICS, topic, 'exercises')
    if (!existsSync(exercises)) continue
    for (const exercise of readdirSync(exercises).sort()) {
      const folder = join(exercises, exercise)
      if (!existsSync(join(folder, 'test_exercise.py'))) continue
      const settings = parseYaml(
        readFileSync(join(folder, 'exercise.yaml'), 'utf8'),
      ) as { stage?: string; time_limit_ms?: number }
      cases.push({
        topic,
        exercise,
        folder,
        limitMs: settings.time_limit_ms ?? DEFAULT_TIME_LIMIT_MS,
        isWorkedExample: settings.stage === 'worked_example',
      })
    }
  }
  return cases
}

let pyodide: PyodideAPI

const cases = readyCases()
const timings: Timing[] = []

/** Run one step and return what it gave back and how long it took. */
function timed<T>(work: () => T): { result: T; ms: number } {
  const start = performance.now()
  const result = work()
  return { result, ms: performance.now() - start }
}

const seconds = (ms: number) => `${(ms / 1000).toFixed(1)} s`

/** Record a time, and fail when the app would have stopped the solution. */
function expectInTime(timing: Timing): void {
  timings.push(timing)
  const { name, button, ms, limitMs } = timing
  const topic = name.split('/')[0]
  expect(
    ms,
    `${name}: ${button} took ${seconds(ms)}, over its time limit of ` +
      `${seconds(limitMs)}, so the app would stop a correct answer. ` +
      `Make the tests lighter or raise time_limit_ms in its exercise.yaml; ` +
      `"npm run time:content -- ${topic}" times it.`,
  ).toBeLessThanOrEqual(limitMs)
}

beforeAll(async () => {
  pyodide = await loadPyodide()
  installHarness(pyodide)
  // In Node the packages come from the CDN on first use, then from a cache
  // in node_modules.
  if (PACKAGES.size > 0) {
    await pyodide.loadPackage([...PACKAGES], {
      messageCallback: () => undefined,
    })
    // Import each package once now, so no exercise is timed doing it. The
    // first "import numpy" takes about half a second on a quiet machine and
    // a few seconds while other test files are running, and it would all
    // land on whichever exercise happens to come first. (A learner's first
    // Run on a page pays it too; the margin described above covers that.)
    for (const name of PACKAGES) pyodide.runPython(`import ${name}`)
  }
}, 180_000)

// The ten times closest to their limits, so CI's log shows how much room
// is left before this test would start failing.
afterAll(() => {
  const share = (timing: Timing) => timing.ms / timing.limitMs
  const closest = [...timings].sort((a, b) => share(b) - share(a)).slice(0, 10)
  const lines = closest.map(
    (timing) =>
      `${String(Math.round(share(timing) * 100)).padStart(4)}%  ` +
      `${seconds(timing.ms).padStart(6)} of ${seconds(timing.limitMs).padStart(6)}  ` +
      `${timing.button.padEnd(5)}  ${timing.name}`,
  )
  // Written straight to the output: Vitest didn't show a console.log from
  // here in a run where every test passed.
  process.stdout.write(
    ['', 'The ten times closest to their limits:', ...lines, ''].join('\n'),
  )
})

// Only the reference solutions: a known-wrong solution may loop forever on
// purpose, and Pyodide in Node has no way to stop it. CPython proves those
// fail, in the validator.
describe(`every ready exercise's solution under Pyodide (${cases.length})`, () => {
  for (const { topic, exercise, folder, limitMs, isWorkedExample } of cases) {
    const name = `${topic}/${exercise}`

    it(`${name}: the solution passes its tests, within its time limit`, () => {
      const tests = readFileSync(join(folder, 'test_exercise.py'), 'utf8')
      const solution = readFileSync(join(folder, 'solution.py'), 'utf8')
      const check = timed(() => runChecks(pyodide, solution, tests))
      const report = check.result
      expect(report.status, report.message).toBe('ok')
      const failed = report.results.filter((r) => r.outcome !== 'pass')
      expect(failed, JSON.stringify(failed, null, 2)).toEqual([])
      expectInTime({ name, button: 'Check', ms: check.ms, limitMs })
    }, 60_000)

    if (!isWorkedExample) continue

    it(`${name}: the program runs within its time limit`, () => {
      const solution = readFileSync(join(folder, 'solution.py'), 'utf8')
      const run = timed(() => runProgram(pyodide, solution, '', null))
      expectInTime({ name, button: 'Run', ms: run.ms, limitMs })
    }, 60_000)
  }
})
