// CodeMirror needs a real browser to lay itself out, so component tests swap
// the editor for a plain text box with the same name. In a test file:
//
//   vi.mock('../components/CodeEditor.tsx', () => import('../test/FakeCodeEditor.tsx'))

type Props = {
  initialCode: string
  onChange: (code: string) => void
  label: string
}

export function CodeEditor({ initialCode, onChange, label }: Props) {
  return (
    <textarea
      aria-label={label}
      defaultValue={initialCode}
      onChange={(event) => onChange(event.target.value)}
    />
  )
}
