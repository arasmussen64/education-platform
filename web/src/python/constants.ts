/**
 * The Pyodide release the worker loads from the CDN. Keep it in sync with
 * "pyodide" in package.json; session.pyodide.test.ts checks that they match.
 */
export const PYODIDE_VERSION = '314.0.7'

export const PYODIDE_INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`

/** How long learner code may run before it's stopped (v1 spec, F4). */
export const DEFAULT_TIME_LIMIT_MS = 5000
