// CodeMirror needs a real browser to lay itself out, so component tests swap
// the editor for a plain text box with the same name. In a test file:
//
//   vi.mock('../components/CodeEditor.tsx', () => import('../test/FakeCodeEditor.tsx'))

import { useEffect, useRef } from 'react'

type Props = {
  initialCode: string
  onChange: (code: string) => void
  label: string
  focusOnStart?: boolean
}

export function CodeEditor({
  initialCode,
  onChange,
  label,
  focusOnStart = false,
}: Props) {
  const boxRef = useRef<HTMLTextAreaElement>(null)
  const focusRef = useRef(focusOnStart)

  // Like the real editor: focused once, when it first appears, if asked.
  useEffect(() => {
    if (focusRef.current) boxRef.current?.focus()
  }, [])

  return (
    <textarea
      ref={boxRef}
      aria-label={label}
      defaultValue={initialCode}
      onChange={(event) => onChange(event.target.value)}
    />
  )
}
