// Runs before every test file.
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Adds DOM checks like toBeInTheDocument() to Vitest's expect().
import '@testing-library/jest-dom/vitest'

// jsdom lays nothing out, so it has no scrollIntoView. This stand-in lets
// pages call it in tests, and tests spy on it.
if (typeof window !== 'undefined') {
  Element.prototype.scrollIntoView = function scrollIntoView() {}
}

// Remove whatever a test rendered or saved (the event outbox lives in
// localStorage), so tests can't affect each other.
afterEach(() => {
  cleanup()
  // Only the browser-like test environment (jsdom) has localStorage; the
  // Pyodide tests run in plain Node.
  if (typeof window !== 'undefined') localStorage.clear()
})
