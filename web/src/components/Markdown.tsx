import ReactMarkdown, { type Components } from 'react-markdown'
import { PROSE } from './styles.ts'

// Inline mode drops the paragraph around the text, for short Markdown inside
// another element, like a list item.
const INLINE: Components = { p: ({ children }) => <>{children}</> }

type Props = {
  children: string
  /** For one line inside another element; the parent supplies the styling. */
  inline?: boolean
}

/**
 * Renders the Markdown in content files (prompts, explanations). Raw HTML
 * is not allowed, so content can't inject anything into the page.
 */
export function Markdown({ children, inline = false }: Props) {
  if (inline) {
    return <ReactMarkdown components={INLINE}>{children}</ReactMarkdown>
  }
  return (
    <div className={PROSE}>
      <ReactMarkdown>{children}</ReactMarkdown>
    </div>
  )
}
