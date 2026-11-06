// For tests of pages and components that contain a code runner: swaps the
// shared Python runner and the code editor for fakes. In a test file:
//
//   vi.mock('../python/runner.ts', () => import('../test/mockPython.ts').then((m) => m.mockRunnerModule()))
//   vi.mock('../components/CodeEditor.tsx', () => import('../test/FakeCodeEditor.tsx'))
//
// then call setFakeRunner() to choose what Run and Check return.
import { vi } from 'vitest'
import type * as RunnerModule from '../python/runner.ts'
import { fakeRunner } from './fakePython.ts'

let current = fakeRunner()

/** The runner module, with getPythonRunner() returning the current fake. */
export async function mockRunnerModule(): Promise<typeof RunnerModule> {
  const real = await vi.importActual<typeof RunnerModule>('../python/runner.ts')
  return {
    ...real,
    getPythonRunner: () => current as unknown as RunnerModule.PythonRunner,
  }
}

/** Makes the code runners in the next render use `runner`. */
export function setFakeRunner(runner = fakeRunner()) {
  current = runner
  return runner
}
