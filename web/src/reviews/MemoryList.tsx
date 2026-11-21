import { Link } from 'react-router'
import type { Topic } from '../content/types.ts'
import type { TopicProgress } from '../progress/progress.ts'
import {
  describeDrop,
  MEMORY_ROWS_SHOWN,
  type MemoryRow,
  memoryRows,
  memorySummary,
} from './memory.ts'
import { describeGap } from './reviews.ts'

/**
 * "Your memory" on the Today page (ADR-0030, reviews/memory.ts): the
 * learned topics remembered least well, each with the scheduler's own
 * estimate now and a day from now. It shows what studying today keeps, in
 * the learner's real numbers, where a streak would show an invented loss.
 */
export function MemoryList({
  topics,
  progress,
  now,
  minutesPerReview,
}: {
  /** The topics that can be opened. */
  topics: Topic[]
  progress: Map<string, TopicProgress>
  now: string
  /** About how long one review takes this learner, in minutes. */
  minutesPerReview: number
}) {
  const rows = memoryRows(topics, progress, now)
  // Nothing learned yet: nothing to keep, and nothing to say.
  if (rows.length === 0) return null
  const shown = rows.slice(0, MEMORY_ROWS_SHOWN)
  const more = rows.length - shown.length
  return (
    <section aria-labelledby="memory" className="space-y-3">
      <h2 id="memory" className="text-xl font-semibold">
        Your memory
      </h2>
      <p className="text-muted">{memorySummary(rows)}</p>
      <ul className="space-y-2">
        {shown.map((row) => (
          <Row
            key={row.topic.id}
            row={row}
            now={now}
            minutes={Math.max(1, Math.round(minutesPerReview))}
          />
        ))}
      </ul>
      {more > 0 && (
        <p className="text-sm text-muted">
          And {more} more, all remembered better than these.{' '}
          <Link to="/map" className="underline">
            The map
          </Link>{' '}
          shows every topic's memory.
        </p>
      )}
    </section>
  )
}

function Row({
  row,
  now,
  minutes,
}: {
  row: MemoryRow
  now: string
  minutes: number
}) {
  return (
    <li className="flex items-start gap-3">
      {/* The words carry the meaning; the bar only shows it at a glance.
          With the best value at 100 and "low" below 90, the browser draws a
          topic at or above the 90% target in its "good" colour and one
          under it in its "not so good" one. */}
      <meter
        className="mt-2 h-2 w-16 shrink-0 sm:w-24"
        min={0}
        max={100}
        low={90}
        optimum={100}
        value={row.percent}
        aria-hidden="true"
      />
      <span>
        <Link to={`/topic/${row.topic.id}`} className="font-medium underline">
          {row.topic.title}
        </Link>{' '}
        is {describeDrop(row)}.{' '}
        <span className="text-sm text-muted">
          {row.due
            ? `Its review is due: about ${minutes} ${minutes === 1 ? 'minute' : 'minutes'} to keep it.`
            : `Next review ${describeGap(now, row.dueAt)}.`}
        </span>
      </span>
    </li>
  )
}
