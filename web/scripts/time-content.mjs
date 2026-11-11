// Times exercises' reference solutions in the browser's Python (Pyodide),
// the way the Run and Check buttons run them, and compares each time with
// the exercise's time limit.
//
// Why: the app stops a Run or a Check after the exercise's time_limit_ms
// (5 seconds unless its exercise.yaml says otherwise). A solution that is
// correct but slower than that can never pass in the app, and the content
// validator can't see it, because it runs ordinary Python, which is faster.
//
// Usage, from web/:
//   npm run time:content                    every topic that has exercises
//   npm run time:content -- ml.nn. py.loops only topics whose id starts so
//
// Read the "share" column: keep every exercise under 40% of its limit on
// your own machine before marking a topic ready. The machines that run CI,
// and a learner's laptop, may be a good deal slower than yours, and CI
// fails once a time passes 100% (src/content/content.pyodide.test.ts), so
// the gap between 40% and 100% is the room they get. Rows over 40% are
// marked, and the script then exits with an error. Close other programs
// first: a busy machine reads high.
//
// To bring a time down: load the learner's file once per test file instead
// of once per test, shrink the tests' data or step counts (every known-wrong
// solution must still fail), or, for a program that honestly needs longer,
// set time_limit_ms in its exercise.yaml (30000 at most).
import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadPyodide } from 'pyodide'
import { parse as parseYaml } from 'yaml'
// Node 24 reads this TypeScript file directly; it only holds constants.
import { DEFAULT_TIME_LIMIT_MS } from '../src/python/constants.ts'

/** The share of its time limit a solution may use on an author's machine. */
const ADVISED_SHARE = 0.4

const REPO = fileURLToPath(new URL('../..', import.meta.url))
const TOPICS = join(REPO, 'content', 'topics')
const HARNESS = join(REPO, 'harness')

/** The folder Python works in, as in the app (src/python/session.ts). */
const WORKDIR = '/home/pyodide'
const HARNESS_FILES = [
  'checks.py',
  'errors.py',
  'program.py',
  'testrunner.py',
  'tracer.py',
]

const prefixes = process.argv.slice(2)

/** The topics to time, and every package they declare (ADR-0023). */
function findExercises() {
  const exercises = []
  const packages = new Set()
  for (const topic of readdirSync(TOPICS).sort()) {
    if (prefixes.length > 0 && !prefixes.some((p) => topic.startsWith(p))) {
      continue
    }
    const topicFile = join(TOPICS, topic, 'topic.yaml')
    const folder = join(TOPICS, topic, 'exercises')
    if (!existsSync(topicFile) || !existsSync(folder)) continue
    const meta = parseYaml(readFileSync(topicFile, 'utf8'))
    for (const name of meta.packages ?? []) packages.add(name)
    for (const exercise of readdirSync(folder).sort()) {
      const files = ['exercise.yaml', 'solution.py', 'test_exercise.py']
      if (!files.every((file) => existsSync(join(folder, exercise, file)))) {
        continue
      }
      exercises.push({ topic, exercise, folder: join(folder, exercise) })
    }
  }
  return { exercises, packages: [...packages] }
}

/** Start Python with the harness in place, as the app's worker does. */
async function startPython(packages) {
  const pyodide = await loadPyodide()
  if (packages.length > 0) {
    await pyodide.loadPackage(packages, { messageCallback: () => undefined })
  }
  for (const name of HARNESS_FILES) {
    const source = readFileSync(join(HARNESS, name), 'utf8')
    pyodide.FS.writeFile(`${WORKDIR}/${name}`, source)
  }
  pyodide.runPython(`
import os, sys
os.chdir(${JSON.stringify(WORKDIR)})
if ${JSON.stringify(WORKDIR)} not in sys.path:
    sys.path.insert(0, ${JSON.stringify(WORKDIR)})
import program, testrunner, tracer
`)
  return pyodide
}

/** Run one step and return what it gave back and how long it took. */
function timed(work) {
  const start = performance.now()
  const result = work()
  return { result, ms: performance.now() - start }
}

/** Time the Run button's work, then the Check button's, for one exercise. */
function timeExercise(pyodide, { topic, exercise, folder }) {
  const meta = parseYaml(readFileSync(join(folder, 'exercise.yaml'), 'utf8'))
  const limitMs = meta.time_limit_ms ?? DEFAULT_TIME_LIMIT_MS
  const solution = readFileSync(join(folder, 'solution.py'), 'utf8')
  const tests = readFileSync(join(folder, 'test_exercise.py'), 'utf8')
  pyodide.FS.writeFile(`${WORKDIR}/solution.py`, solution)
  pyodide.FS.writeFile(`${WORKDIR}/test_exercise.py`, tests)
  pyodide.globals.set('_learner_stdin', '')
  pyodide.globals.set('_learner_seed', undefined)
  const run = timed(() =>
    pyodide.runPython(
      'import json, program; json.dumps(program.run_program(_learner_stdin, _learner_seed))',
    ),
  )
  const check = timed(() =>
    pyodide.runPython(
      'import json, testrunner; json.dumps(testrunner.run_tests())',
    ),
  )
  const report = JSON.parse(check.result)
  const passed =
    report.status === 'ok' &&
    report.results.every((result) => result.outcome === 'pass')
  const slowerMs = Math.max(run.ms, check.ms)
  return {
    name: `${topic}/${exercise}`,
    runMs: run.ms,
    checkMs: check.ms,
    limitMs,
    share: slowerMs / limitMs,
    passed,
  }
}

const seconds = (ms) => `${(ms / 1000).toFixed(2)} s`.padStart(8)

function printRow(row) {
  const share = `${Math.round(row.share * 100)}%`.padStart(5)
  let note = ''
  if (!row.passed) note = '  THE SOLUTION FAILS ITS TESTS'
  else if (row.share > 1) note = '  OVER ITS LIMIT'
  else if (row.share > ADVISED_SHARE) note = '  over 40% of its limit'
  console.log(
    `run ${seconds(row.runMs)}  check ${seconds(row.checkMs)}  ` +
      `limit ${seconds(row.limitMs)}  share ${share}  ${row.name}${note}`,
  )
}

const { exercises, packages } = findExercises()
if (exercises.length === 0) {
  console.error(`No exercises found for: ${prefixes.join(' ')}`)
  process.exit(1)
}
const pyodide = await startPython(packages)
const rows = []
for (const exercise of exercises) {
  const row = timeExercise(pyodide, exercise)
  rows.push(row)
  printRow(row)
}

const tooSlow = rows.filter((row) => !row.passed || row.share > ADVISED_SHARE)
console.log(
  `\nTimed ${rows.length} exercises. ` +
    (tooSlow.length === 0
      ? 'Every solution passes and uses under 40% of its time limit.'
      : `${tooSlow.length} need attention:`),
)
for (const row of tooSlow) printRow(row)
process.exit(tooSlow.length === 0 ? 0 : 1)
