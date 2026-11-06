// @vitest-environment node
//
// Runs every harness scenario (harness/scenarios) inside real Pyodide and
// checks it gives exactly the result CPython gives in CI. This is what makes
// "the same verdict in the browser and on GitHub" true (v1 spec, F4).
import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadPyodide, type PyodideAPI, version } from 'pyodide'
import { beforeAll, describe, expect, it } from 'vitest'
import { PYODIDE_VERSION } from './constants.ts'
import { installHarness, runChecks, runProgram } from './session.ts'

const SCENARIOS = fileURLToPath(
  new URL('../../../harness/scenarios', import.meta.url),
)

let pyodide: PyodideAPI

beforeAll(async () => {
  pyodide = await loadPyodide()
  installHarness(pyodide)
}, 120_000)

describe('the Python harness under Pyodide', () => {
  it('uses the same Pyodide version the browser loads', () => {
    expect(version).toBe(PYODIDE_VERSION)
  })

  for (const name of readdirSync(SCENARIOS).sort()) {
    it(`matches the expected result for ${name}`, () => {
      const folder = join(SCENARIOS, name)
      const read = (file: string) => readFileSync(join(folder, file), 'utf8')
      const has = (file: string) => existsSync(join(folder, file))

      const expected: unknown = JSON.parse(read('expected.json'))
      const actual = has('test_exercise.py')
        ? runChecks(pyodide, read('solution.py'), read('test_exercise.py'))
        : runProgram(
            pyodide,
            read('solution.py'),
            has('stdin.txt') ? read('stdin.txt') : '',
            has('seed.txt') ? Number(read('seed.txt')) : null,
          )
      expect(actual).toEqual(expected)
    })
  }
})
