import { useEffect, useState } from 'react'
import { SECONDARY_BUTTON } from '../components/styles.ts'

/** The card's id, so the page can move keyboard focus to it. */
export const BREAK_ID = 'part-break'

/** How long the suggested break is. */
export const BREAK_MS = 5 * 60 * 1000

/** "4:05": minutes and seconds left, rounded up to the next second. */
function clock(ms: number): string {
  const seconds = Math.ceil(ms / 1000)
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`
}

/**
 * A suggestion to rest for five minutes after finishing a part of a topic
 * (ADR-0025, amended 2026-11-16). A few minutes of quiet rest straight after
 * learning, eyes closed or looking out of a window rather than at a phone,
 * helps the brain keep what it just took in (Dewar et al., 2012). It's only
 * a suggestion: the part below it is open the whole time, the timer is
 * optional and runs on the page alone (no notifications), and Skip puts it
 * away.
 */
export function PartBreak({
  finished,
  onDismiss,
}: {
  /** The title of the part just finished, e.g. "Learn". */
  finished: string
  onDismiss: () => void
}) {
  // When the timer was started, by the clock; null until it is.
  const [startedAt, setStartedAt] = useState<number | null>(null)
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    if (startedAt === null) return
    // Ticks once a second; the time left is worked out from the clock, so
    // a tab left in the background shows the right time on its return.
    const timer = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(timer)
  }, [startedAt])

  const left =
    startedAt === null ? BREAK_MS : Math.max(0, startedAt + BREAK_MS - now)
  const over = startedAt !== null && left === 0

  return (
    <aside
      id={BREAK_ID}
      // Focusable, so moving on to the next part can put focus here first.
      tabIndex={-1}
      aria-label="A short break"
      className="space-y-3 rounded-lg border border-line bg-card p-4"
    >
      <p>
        <span className="font-medium">{finished}: done.</span> Time for a
        five-minute break? Rest quietly, with your eyes closed or looking out of
        a window rather than at your phone. A few minutes of quiet straight
        after learning helps your brain keep what you just did.
      </p>
      {startedAt !== null && (
        // The time left, for anyone who looks; not read out every second.
        <p
          role="timer"
          aria-label="Break time left"
          className="font-mono text-2xl"
        >
          {clock(left)}
        </p>
      )}
      {/* Announced by screen readers when it changes. */}
      <output className="block text-sm">
        {over ? "Break's over. Carry on whenever you're ready." : ''}
      </output>
      <div className="flex flex-wrap gap-2">
        {startedAt === null && (
          <button
            type="button"
            onClick={() => {
              const start = Date.now()
              setStartedAt(start)
              setNow(start)
            }}
            className={SECONDARY_BUTTON}
          >
            Start a 5-minute timer
          </button>
        )}
        <button type="button" onClick={onDismiss} className={SECONDARY_BUTTON}>
          {over
            ? 'Close'
            : startedAt === null
              ? 'Skip the break'
              : 'End the break'}
        </button>
      </div>
    </aside>
  )
}
