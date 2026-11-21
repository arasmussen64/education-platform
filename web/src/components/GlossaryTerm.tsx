import {
  type ReactNode,
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
} from 'react'
import { Link } from 'react-router'
import { Markdown } from './Markdown.tsx'

type Props = {
  /** The term as its glossary writes it, e.g. "source NAT". */
  term: string
  /** One line of Markdown. */
  definition: string
  /** The topic that teaches the term. */
  topicId: string
  topicTitle: string
  /** The word as the lesson wrote it, e.g. "SNAT". */
  children?: ReactNode
}

/** The gap kept between the definition and the edge of the screen, in px. */
const EDGE = 12

/**
 * A word the glossary defines, where a lesson first uses it (ADR-0026). It
 * reads like the rest of the sentence, with a dotted underline; pressing it
 * (a tap, a click, Enter or Space) shows the definition and the topic that
 * teaches it, and so does hovering with a mouse. Escape, or a press
 * anywhere else, puts it away. The build adds these to lessons
 * (src/tooling/remarkGlossary.ts); writers never write one.
 */
export function GlossaryTerm({
  term,
  definition,
  topicId,
  topicTitle,
  children,
}: Props) {
  // Shown after a press until the next one; or while a mouse is over it.
  const [pinned, setPinned] = useState(false)
  const [hovered, setHovered] = useState(false)
  const open = pinned || hovered
  // How far left the definition moves to stay on a narrow screen.
  const [shift, setShift] = useState(0)
  const wrapper = useRef<HTMLSpanElement>(null)
  const button = useRef<HTMLButtonElement>(null)
  const panel = useRef<HTMLSpanElement>(null)
  const panelId = `${useId()}-definition`

  useEffect(() => {
    if (!pinned) return
    const away = (event: PointerEvent) => {
      if (!wrapper.current?.contains(event.target as Node)) {
        setPinned(false)
        setHovered(false)
      }
    }
    document.addEventListener('pointerdown', away)
    return () => document.removeEventListener('pointerdown', away)
  }, [pinned])

  // A term near the right edge of a phone would push its definition off the
  // screen; this moves it back, measured once it's on the page.
  useLayoutEffect(() => {
    if (!open || !panel.current) {
      setShift(0)
      return
    }
    const { left, right } = panel.current.getBoundingClientRect()
    const over = right - (window.innerWidth - EDGE)
    setShift(over > 0 ? Math.min(over, left - EDGE) : 0)
  }, [open])

  return (
    // The button is the control. These handlers only add to it: a mouse
    // hovering shows the definition too, and Escape anywhere inside (the
    // button or the definition's links) puts it away.
    // oxlint-disable-next-line jsx-a11y/no-static-element-interactions
    <span
      ref={wrapper}
      className="relative"
      onPointerEnter={(event) => {
        if (event.pointerType === 'mouse') setHovered(true)
      }}
      onPointerLeave={(event) => {
        if (event.pointerType === 'mouse') setHovered(false)
      }}
      onKeyDown={(event) => {
        if (event.key === 'Escape' && open) {
          setPinned(false)
          setHovered(false)
          button.current?.focus()
        }
      }}
    >
      <button
        ref={button}
        type="button"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => {
          // A press keeps it open (even after a mouse moves away); a second
          // press closes it, though the mouse is still over the word.
          setPinned(!pinned)
          setHovered(false)
        }}
        className="cursor-help underline decoration-muted decoration-dotted decoration-2 underline-offset-4 hover:decoration-ink"
      >
        {children}
        <span className="sr-only">{' (show its definition)'}</span>
      </button>
      {open && (
        <span
          ref={panel}
          id={panelId}
          style={shift ? { transform: `translateX(-${shift}px)` } : undefined}
          className="absolute top-full left-0 z-30 mt-1 block w-72 max-w-[calc(100vw-2rem)] space-y-1 rounded-md border border-line-strong bg-card p-3 text-left text-sm leading-normal font-normal text-ink not-italic shadow-lg"
        >
          <span className="block font-semibold">{term}</span>
          <span className="block">
            <Markdown inline>{definition}</Markdown>
          </span>
          <span className="block text-muted">
            Taught in:{' '}
            <Link to={`/topic/${topicId}`} className="underline">
              {topicTitle}
            </Link>
            {' · '}
            <Link to="/glossary" className="underline">
              All terms
            </Link>
          </span>
        </span>
      )}
    </span>
  )
}
