import { Link } from 'react-router'
import { Markdown } from '../components/Markdown.tsx'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { INLINE_CODE } from '../components/styles.ts'
import type { Day } from '../days.ts'
import { type Card, keyOf, skillName, whenDue } from './cards.ts'
import { CORRECT_DAYS_NEEDED, type FollowUp } from './followUps.ts'

// A mistake coming back as a fresh question (ADR-0011), as the Today page
// and the guided session (pages/SessionPage.tsx) both show it.

/** What happened to a follow-up after today's answer, if anything yet. */
function progressOf(live: FollowUp | undefined, today: Day): string {
  if (!live) {
    return `Relearned: you've got this right on ${CORRECT_DAYS_NEEDED} different days.`
  }
  if (live.due <= today) return ''
  return live.missedOn === today
    ? `Not quite. It comes back ${whenDue(live.due, today)}.`
    : `Right! It comes back ${whenDue(live.due, today)}, to make sure it sticks.`
}

export function FollowUpCard({
  card,
  live,
  today,
}: {
  card: Card
  /** Every open follow-up as it stands now; a relearned one is missing. */
  live: Map<string, FollowUp>
  today: Day
}) {
  const { content, followUps } = card
  const names = followUps.map((followUp) => skillName(followUp))
  const results = followUps.map((followUp) =>
    progressOf(live.get(keyOf(followUp)), today),
  )
  // One line, unless the skills on this card ended up in different places
  // (say, one relearned and the other due again in 3 days).
  const progress =
    new Set(results).size <= 1
      ? (results[0] ?? '')
      : results
          .map((result, index) => (result ? `${names[index]}: ${result}` : ''))
          .filter(Boolean)
          .join(' ')

  return (
    <div className="space-y-2">
      <p
        className={`text-sm text-slate-600 dark:text-slate-400 ${INLINE_CODE}`}
      >
        <span className="font-medium">
          {names.length === 1 ? 'Skill:' : 'Skills:'}
        </span>{' '}
        {names.map((name, index) => (
          <span key={name}>
            {index > 0 && '; '}
            <Markdown inline>{name}</Markdown>
          </span>
        ))}
        {' · from '}
        <Link to={`/topic/${content.topic.id}`} className="underline">
          {content.topic.title}
        </Link>
      </p>
      <PracticeItem itemId={card.itemId} content={content} context="review" />
      {/* <output> is announced by screen readers when its text changes. */}
      <output className="block font-medium">{progress}</output>
    </div>
  )
}
