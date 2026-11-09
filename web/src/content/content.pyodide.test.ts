// @vitest-environment node
//
// Runs every ready topic's exercises inside real Pyodide, the way the Check
// button does: each reference solution must pass all its tests. The content
// validator proves the same under CPython in CI (tools/validate_content.py);
// this proves the browser's Python agrees, so a learner is never shown an
// exercise whose own solution fails in the app. Only the reference solutions
// run here: a known-wrong solution may loop forever on purpose, and Pyodide
// in Node has no way to stop it, so the validator keeps those.
import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadPyodide, type PyodideAPI } from 'pyodide'
import { beforeAll, describe, expect, it } from 'vitest'
import { parse as parseYaml } from 'yaml'
import { installHarness, runChecks } from '../python/session.ts'

const TOPICS = fileURLToPath(
  new URL('../../../content/topics', import.meta.url),
)

type Case = { topic: string; exercise: string; folder: string }

function readyCases(): Case[] {
  const cases: Case[] = []
  for (const topic of readdirSync(TOPICS).sort()) {
    const topicFile = join(TOPICS, topic, 'topic.yaml')
    if (!existsSync(topicFile)) continue
    const meta = parseYaml(readFileSync(topicFile, 'utf8')) as {
      status?: string
    }
    if (meta.status !== 'ready') continue
    const exercises = join(TOPICS, topic, 'exercises')
    if (!existsSync(exercises)) continue
    for (const exercise of readdirSync(exercises).sort()) {
      const folder = join(exercises, exercise)
      if (!existsSync(join(folder, 'test_exercise.py'))) continue
      cases.push({ topic, exercise, folder })
    }
  }
  return cases
}

let pyodide: PyodideAPI

beforeAll(async () => {
  pyodide = await loadPyodide()
  installHarness(pyodide)
}, 120_000)

const cases = readyCases()

// Only the reference solutions: a known-wrong solution may loop forever on
// purpose, and Pyodide in Node has no way to stop it. CPython proves those
// fail, in the validator.
describe(`every ready exercise's solution under Pyodide (${cases.length})`, () => {
  for (const { topic, exercise, folder } of cases) {
    it(`${topic}/${exercise}: the solution passes its tests`, () => {
      const tests = readFileSync(join(folder, 'test_exercise.py'), 'utf8')
      const solution = readFileSync(join(folder, 'solution.py'), 'utf8')
      const report = runChecks(pyodide, solution, tests)
      expect(report.status, report.message).toBe('ok')
      const failed = report.results.filter((r) => r.outcome !== 'pass')
      expect(failed, JSON.stringify(failed, null, 2)).toEqual([])
    }, 60_000)
  }
})
