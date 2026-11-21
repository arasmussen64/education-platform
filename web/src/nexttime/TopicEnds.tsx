import { useState } from 'react'
import { Markdown } from '../components/Markdown.tsx'
import { SECONDARY_BUTTON } from '../components/styles.ts'
import type { Topic, TopicContent } from '../content/types.ts'
import type { Attempt } from '../followups/followUps.ts'
import { forgetGuess, recallGuess } from './guesses.ts'
import { NextTimeCard } from './NextTimeCard.tsx'
import { nextTimeFor } from './nextTime.ts'

/**
 * On a topic's page, below the part on screen: "Stopping here for today?"
 * (ADR-0030). Opened, it shows the topic's next unanswered question to
 * sleep on, so a sitting that stops mid-topic ends on an open question too.
 * Folded by default: a learner who's carrying on never needs it.
 */
export function StoppingHere({
  content,
  attempts,
}: {
  content: TopicContent
  attempts: Attempt[]
}) {
  const [open, setOpen] = useState(false)
  // Worked out only when asked for, from the answers saved so far.
  const nextTime = open ? nextTimeFor(content, true, attempts) : null
  return (
    <details
      className="text-sm"
      onToggle={(event) => setOpen(event.currentTarget.open)}
    >
      <summary className="cursor-pointer text-muted underline">
        Stopping here for today?
      </summary>
      <div className="mt-3 space-y-3 text-base">
        <p className="text-muted">
          Everything you've answered is saved, and the page will open where you
          stopped.
        </p>
        {nextTime && <NextTimeCard nextTime={nextTime} />}
      </div>
    </details>
  )
}

/**
 * At the start of a lesson that has no opening puzzle: the guess the
 * learner made about this topic at the end of an earlier session (a guess
 * at a puzzle shows in the puzzle itself). Put away with one click.
 */
export function SavedGuessNote({ topic }: { topic: Topic }) {
  const [saved, setSaved] = useState(() => {
    const found = recallGuess(topic.id)
    return found?.source === 'goal' ? found : null
  })
  if (!saved) return null
  return (
    <aside
      aria-label="Your guess from last time"
      className="space-y-2 rounded-lg border border-line-strong bg-card p-4"
    >
      <p className="text-sm font-semibold tracking-wide text-muted uppercase">
        Your guess from last time
      </p>
      <div className="font-medium">
        <Markdown>{saved.question}</Markdown>
      </div>
      <p>
        <span className="font-semibold">You guessed:</span> {saved.guess}
      </p>
      <p className="text-sm text-muted">
        Keep it in mind as you read, and see where the lesson agrees with you
        and where it doesn't.
      </p>
      <button
        type="button"
        className={SECONDARY_BUTTON}
        onClick={() => {
          forgetGuess(topic.id)
          setSaved(null)
        }}
      >
        Put it away
      </button>
    </aside>
  )
}
