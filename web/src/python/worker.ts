// Runs in a Web Worker: a background thread, so long-running Python never
// freezes the page. The app talks to it only through messages (protocol.ts).
import type { PyodideAPI } from 'pyodide'
import { PYODIDE_INDEX_URL } from './constants.ts'
import type { WorkerRequest, WorkerResponse } from './protocol.ts'
import { installHarness, runChecks, runProgram } from './session.ts'

// A typed view of the worker's global scope.
const scope = self as unknown as {
  postMessage(message: WorkerResponse): void
  onmessage: ((event: MessageEvent<WorkerRequest>) => void) | null
}

function describe(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}

async function boot(): Promise<PyodideAPI> {
  // Pyodide itself comes from the CDN, pinned to the version in constants.ts.
  const pyodideModule = (await import(
    /* @vite-ignore */ `${PYODIDE_INDEX_URL}pyodide.mjs`
  )) as typeof import('pyodide')
  const pyodide = await pyodideModule.loadPyodide({
    indexURL: PYODIDE_INDEX_URL,
  })
  installHarness(pyodide)
  return pyodide
}

const ready = boot()

ready.then(
  () => scope.postMessage({ type: 'ready' }),
  (error: unknown) =>
    scope.postMessage({ type: 'load-error', message: describe(error) }),
)

scope.onmessage = async (event) => {
  const request = event.data
  try {
    const pyodide = await ready
    if (request.type === 'run') {
      const result = runProgram(
        pyodide,
        request.code,
        request.stdin,
        request.seed,
      )
      scope.postMessage({ id: request.id, type: 'run-result', result })
    } else {
      const report = runChecks(pyodide, request.code, request.tests)
      scope.postMessage({ id: request.id, type: 'check-result', report })
    }
  } catch (error) {
    scope.postMessage({
      id: request.id,
      type: 'internal-error',
      message: describe(error),
    })
  }
}
