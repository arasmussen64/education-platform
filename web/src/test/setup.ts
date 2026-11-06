// Runs before every test file.
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Adds DOM checks like toBeInTheDocument() to Vitest's expect().
import '@testing-library/jest-dom/vitest'

// Remove whatever a test rendered, so tests can't affect each other.
afterEach(() => {
  cleanup()
})
