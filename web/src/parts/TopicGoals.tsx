import { Markdown } from '../components/Markdown.tsx'
import { CARD } from '../components/styles.ts'
import { PLACE_ATTRIBUTE, START_PLACE } from '../place/useCurrentPlace.ts'

/**
 * What the learner will be able to do, at the top of a topic (the topic's
 * `objectives`), ticked once the topic is Learned: all three proofs passed
 * (ADR-0002). They're ticked together, because the content doesn't say
 * which proof shows which goal, and a tick has to be earned, never guessed.
 * Open on the lesson's part; folded on the others, a click away.
 */
export function TopicGoals({
  objectives,
  learnedOn,
  open,
}: {
  objectives: string[]
  /** "Nov 6": when the topic became Learned, or null while it isn't. */
  learnedOn: string | null
  /** Whether it starts unfolded. */
  open: boolean
}) {
  if (objectives.length === 0) return null
  return (
    <details
      id={START_PLACE}
      {...{ [PLACE_ATTRIBUTE]: START_PLACE }}
      open={open}
      className={CARD}
    >
      <summary className="cursor-pointer font-semibold">
        {learnedOn ? 'You can now…' : "You'll be able to…"}
      </summary>
      <ul aria-label="Goals of this topic" className="space-y-2">
        {objectives.map((objective) => (
          <li key={objective} className="flex gap-2">
            {/* A mark and words, never color alone (F9). */}
            <span
              aria-hidden="true"
              className={
                learnedOn
                  ? 'text-lime-700 dark:text-lime-400'
                  : 'text-slate-400'
              }
            >
              {learnedOn ? '✓' : '○'}
            </span>
            <span>
              <Markdown inline>{objective}</Markdown>
              <span className="sr-only">
                {learnedOn ? ' (proven)' : ' (not proven yet)'}
              </span>
            </span>
          </li>
        ))}
      </ul>
      <p className="text-sm text-slate-600 dark:text-slate-400">
        {learnedOn
          ? `Ticked on ${learnedOn}, when you passed all three proofs.`
          : 'These are ticked once you pass all three proofs at the end.'}
      </p>
    </details>
  )
}
