// Runs before every test file.
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

// Adds DOM checks like toBeInTheDocument() to Vitest's expect().
import '@testing-library/jest-dom/vitest'

// jsdom lays nothing out, so it has no scrollIntoView. This stand-in lets
// pages call it in tests, and tests spy on it.
if (typeof window !== 'undefined') {
  Element.prototype.scrollIntoView = function scrollIntoView() {}
}

// No track has been started over (ADR-0029), unless a test says otherwise.
// The progress and placement hooks read the resets from the server; this
// keeps every test that renders them off the network.
vi.mock('../resets/resets.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../resets/resets.ts')>()),
  fetchResets: vi.fn(async () => []),
}))

// Remove whatever a test rendered or saved (the event outbox lives in
// localStorage), so tests can't affect each other.
afterEach(() => {
  cleanup()
  // Only the browser-like test environment (jsdom) has localStorage; the
  // Pyodide tests run in plain Node.
  if (typeof window !== 'undefined') localStorage.clear()
})
