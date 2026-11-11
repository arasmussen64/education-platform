import { indentWithTab } from '@codemirror/commands'
import { python } from '@codemirror/lang-python'
import { EditorView, keymap } from '@codemirror/view'
import { basicSetup } from 'codemirror'
import { useEffect, useRef } from 'react'

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
    const view = new EditorView({
      parent: host,
      doc: firstPropsRef.current.initialCode,
      extensions: [
        basicSetup,
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
    return () => view.destroy()
  }, [])

  return (
    <div
      ref={hostRef}
      className="overflow-hidden rounded-md border border-slate-300 bg-white text-sm text-slate-900 dark:border-slate-700"
    />
  )
}
