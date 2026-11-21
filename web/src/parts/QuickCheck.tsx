import { useState } from 'react'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { CARD, SECONDARY_BUTTON } from '../components/styles.ts'
import type { TopicContent } from '../content/types.ts'
import { QUESTION_MINUTES } from './estimates.ts'
import { QUICK_CHECK_DATA } from './quickCheck.ts'

/**
 * The offer of a quick check, at the top of a topic's first practice part:
 * a lighter way than "Prove it now" to skip what the learner already knows.
 */
export function QuickCheckOffer({
  count,
  onStart,
}: {
  /** How many questions the quick check asks. */
  count: number
  onStart: () => void
}) {
  const minutes = Math.max(1, Math.round(count * QUESTION_MINUTES))
  return (
    <aside aria-label="Check what you know" className={`${CARD} space-y-2`}>
      <p>
        <span className="font-medium">Know some of this already?</span> Check
        what you know: {count} quick questions from this topic's practice, about{' '}
        {minutes} minutes, on as many different skills as it has. Get one right
        and the practice on its skills is marked optional. The three proofs at
        the end stay required.
      </p>
      <button type="button" onClick={onStart} className={SECONDARY_BUTTON}>
        Check what you know
      </button>
    </aside>
  )
}

/**
 * "Check what you know" (ADR-0025, amended 2026-11-16): a few of the topic's
 * own quick questions, each on a different skill, in place of the practice
 * until the learner goes back to it. The answers are saved as ordinary
 * practice answers, marked `quick_check` in their data; the page works out
 * from them which practice is optional.
 */
export function QuickCheck({
  content,
  itemIds,
  onDone,
}: {
  content: TopicContent
  itemIds: string[]
  /** Back to the practice. */
  onDone: () => void
}) {
  // Each question's first answer on this visit, by item id: what the
  // summary counts, as the page's optional marks do.
  const [first, setFirst] = useState<Map<string, boolean>>(new Map())
  const answered = first.size
  const right = [...first.values()].filter(Boolean).length
  const finished = answered === itemIds.length

  return (
    <section aria-labelledby="quick-check" className="space-y-4">
      <h2 id="quick-check" tabIndex={-1} className="text-2xl font-bold">
        Check what you know
      </h2>
      <p className="text-muted">
        Answer from memory; only your first answer to each question counts. A
        skill you get right makes its practice optional. Nothing here counts
        against you.
      </p>
      {itemIds.map((itemId, index) => (
        <PracticeItem
          key={itemId}
          itemId={itemId}
          content={content}
          context="practice"
          eventData={QUICK_CHECK_DATA}
          position={`Question ${index + 1} of ${itemIds.length}`}
          onGraded={(correct) =>
            setFirst((before) =>
              before.has(itemId)
                ? before
                : new Map(before).set(itemId, correct),
            )
          }
        />
      ))}
      {/* <output> is announced by screen readers when its text changes. */}
      <output className="block">
        {finished &&
          `You got ${right} of ${itemIds.length} right. ${
            right > 0
              ? 'Practice on the skills you showed is now marked optional; the rest is as it was.'
              : 'The practice is all yours: every part of it is still worth doing.'
          } The proofs at the end are still required.`}
      </output>
      <button type="button" onClick={onDone} className={SECONDARY_BUTTON}>
        {finished ? 'Back to the practice' : 'Stop, and back to the practice'}
      </button>
    </section>
  )
}
