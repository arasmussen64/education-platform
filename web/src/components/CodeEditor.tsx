import { indentWithTab } from '@codemirror/commands'
import { python } from '@codemirror/lang-python'
import { Compartment } from '@codemirror/state'
import { EditorView, keymap } from '@codemirror/view'
import { basicSetup } from 'codemirror'
import { useEffect, useRef } from 'react'
import { editorTheme, paletteFor } from './editorThemes.ts'

type Props = {
  /**
   * The code shown when the editor first appears. Later changes are ignored:
   * to show other code, give the editor a new React `key`, which builds a
   * fresh one.
   */
  initialCode: string
  /** Called with the full code after every edit. */
  onChange: (code: string) => void
  /** The editor's accessible name, read out by screen readers. */
  label: string
  /** Put the cursor in the editor as soon as it appears (after Start over). */
  focusOnStart?: boolean
}

/** A Python code editor (CodeMirror 6) with highlighting and indentation. */
export function CodeEditor({
  initialCode,
  onChange,
  label,
  focusOnStart = false,
}: Props) {
  const hostRef = useRef<HTMLDivElement>(null)
  const onChangeRef = useRef(onChange)
  const firstPropsRef = useRef({ initialCode, label, focusOnStart })

  // Always call the latest onChange without rebuilding the editor.
  useEffect(() => {
    onChangeRef.current = onChange
  }, [onChange])

  // Build the editor once, when the component first appears.
  useEffect(() => {
    const host = hostRef.current
    if (!host) return
    // The app is light or dark by the system's colour scheme (Tailwind's
    // `dark:` classes read the same setting), and so is the editor. Some
    // test browsers have no matchMedia; no answer means light.
    const scheme = window.matchMedia?.('(prefers-color-scheme: dark)')
    // A compartment is a slot in the editor's setup whose contents can be
    // swapped later, here the theme, without rebuilding the editor.
    const theme = new Compartment()
    const view = new EditorView({
      parent: host,
      doc: firstPropsRef.current.initialCode,
      extensions: [
        basicSetup,
        theme.of(editorTheme(paletteFor(scheme?.matches ?? false))),
        python(),
        keymap.of([indentWithTab]),
        EditorView.contentAttributes.of({
          'aria-label': firstPropsRef.current.label,
        }),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            onChangeRef.current(update.state.doc.toString())
          }
        }),
      ],
    })
    if (firstPropsRef.current.focusOnStart) view.focus()
    // Follow the system if it changes while the page is open (at sunset,
    // say). The code, cursor and undo history are untouched.
    const followScheme = (event: MediaQueryListEvent) => {
      view.dispatch({
        effects: theme.reconfigure(editorTheme(paletteFor(event.matches))),
      })
    }
    scheme?.addEventListener('change', followScheme)
    return () => {
      scheme?.removeEventListener('change', followScheme)
      view.destroy()
    }
  }, [])

  return (
    <div
      ref={hostRef}
      // The colours inside come from the editor's theme (editorThemes.ts).
      className="overflow-hidden rounded-md border border-line-strong text-sm"
    />
  )
}
