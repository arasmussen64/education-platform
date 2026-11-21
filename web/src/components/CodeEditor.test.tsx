import { act, render } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import { CodeEditor } from './CodeEditor.tsx'

/**
 * A stand-in for the browser's answer to "is the system in dark mode?",
 * which the test can change later, as the system would at sunset.
 */
function fakeColourScheme(dark: boolean) {
  type Listener = (event: { matches: boolean }) => void
  const listeners = new Set<Listener>()
  const scheme = {
    matches: dark,
    addEventListener: (_: string, listener: Listener) =>
      listeners.add(listener),
    removeEventListener: (_: string, listener: Listener) =>
      listeners.delete(listener),
  }
  // CodeMirror asks its own question ("print"); that one never changes.
  const never = {
    matches: false,
    addEventListener: () => {},
    removeEventListener: () => {},
  }
  vi.stubGlobal('matchMedia', (query: string) =>
    query === '(prefers-color-scheme: dark)' ? scheme : never,
  )
  return {
    listeners,
    change(nowDark: boolean) {
      scheme.matches = nowDark
      for (const listener of listeners) listener({ matches: nowDark })
    },
  }
}

const editor = (container: HTMLElement) => container.querySelector('.cm-editor')

function renderEditor() {
  return render(
    <CodeEditor initialCode="x = 1" onChange={() => {}} label="Your code" />,
  )
}

afterEach(() => {
  vi.unstubAllGlobals()
})

test('a light system gets the morning-trail theme', () => {
  fakeColourScheme(false)
  const { container } = renderEditor()
  expect(editor(container)).toHaveAttribute('data-theme', 'morning-trail')
})

test('a dark system gets the night-trail theme', () => {
  fakeColourScheme(true)
  const { container } = renderEditor()
  expect(editor(container)).toHaveAttribute('data-theme', 'night-trail')
})

test('the theme follows the system while the page is open, keeping the code', () => {
  const system = fakeColourScheme(false)
  const { container } = renderEditor()
  act(() => system.change(true))
  expect(editor(container)).toHaveAttribute('data-theme', 'night-trail')
  expect(container).toHaveTextContent('x = 1')
  act(() => system.change(false))
  expect(editor(container)).toHaveAttribute('data-theme', 'morning-trail')
})

test('it stops listening to the system when the editor goes away', () => {
  const system = fakeColourScheme(false)
  const { unmount } = renderEditor()
  expect(system.listeners.size).toBe(1)
  unmount()
  expect(system.listeners.size).toBe(0)
})

test('without matchMedia (some test browsers) the editor is light', () => {
  vi.stubGlobal('matchMedia', undefined)
  const { container } = renderEditor()
  expect(editor(container)).toHaveAttribute('data-theme', 'morning-trail')
})
