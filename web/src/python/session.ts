import type { PyodideAPI } from 'pyodide'
import { HARNESS_FILES } from './harnessFiles.ts'
import type { CheckReport, ProgramResult, TraceResult } from './protocol.ts'

// Runs learner code with an already-loaded Pyodide. The Web Worker uses these
// functions, and so do the tests (in Node), so both exercise the same path.

/** The folder Python works in. Pyodide starts here by default. */
export const WORKDIR = '/home/pyodide'

/** Write the harness into Pyodide's file system and import it. */
export function installHarness(pyodide: PyodideAPI): void {
  for (const file of HARNESS_FILES) {
    pyodide.FS.writeFile(`${WORKDIR}/${file.name}`, file.source)
  }
  pyodide.runPython(`
import os, sys
os.chdir(${JSON.stringify(WORKDIR)})
if ${JSON.stringify(WORKDIR)} not in sys.path:
    sys.path.insert(0, ${JSON.stringify(WORKDIR)})
import program, testrunner, tracer
`)
}

/**
 * The Run button: run the learner's program with the input typed so far.
 * `seed` (null for none) makes Python's random module repeatable.
 */
export function runProgram(
  pyodide: PyodideAPI,
  code: string,
  stdin: string,
  seed: number | null,
): ProgramResult {
  pyodide.FS.writeFile(`${WORKDIR}/solution.py`, code)
  pyodide.globals.set('_learner_stdin', stdin)
  // JavaScript's undefined becomes Python's None. (null would arrive as a
  // special "JS null" object instead.)
  pyodide.globals.set('_learner_seed', seed ?? undefined)
  const json = pyodide.runPython(
    'import json, program; json.dumps(program.run_program(_learner_stdin, _learner_seed))',
  ) as string
  return JSON.parse(json) as ProgramResult
}

/**
 * The Step through button (ADR-0022): run the program like Run does, but
 * record every step, so the page can play it back.
 */
export function traceProgram(
  pyodide: PyodideAPI,
  code: string,
  stdin: string,
  seed: number | null,
): TraceResult {
  pyodide.FS.writeFile(`${WORKDIR}/solution.py`, code)
  pyodide.globals.set('_learner_stdin', stdin)
  pyodide.globals.set('_learner_seed', seed ?? undefined)
  const json = pyodide.runPython(
    'import json, tracer; json.dumps(tracer.trace_program(_learner_stdin, _learner_seed))',
  ) as string
  return JSON.parse(json) as TraceResult
}

/** The Check button: run the exercise's tests against the learner's code. */
export function runChecks(
  pyodide: PyodideAPI,
  code: string,
  tests: string,
): CheckReport {
  pyodide.FS.writeFile(`${WORKDIR}/solution.py`, code)
  pyodide.FS.writeFile(`${WORKDIR}/test_exercise.py`, tests)
  const json = pyodide.runPython(
    'import json, testrunner; json.dumps(testrunner.run_tests())',
  ) as string
  return JSON.parse(json) as CheckReport
}
