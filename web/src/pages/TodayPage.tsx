import { useState } from 'react'
import { Link } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import { Markdown } from '../components/Markdown.tsx'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { BUTTON, INLINE_CODE } from '../components/styles.ts'
import { getTopic } from '../content/content.ts'
import type { TopicContent } from '../content/types.ts'
import {
  addDays,
  chooseQuestion,
  type Day,
  dayOf,
  type FollowUp,
} from '../followups/followUps.ts'
import { type FollowUpsState, useFollowUps } from '../followups/useFollowUps.ts'

// The daily plan (v1 spec, F12). For now it holds one thing: mistakes coming
// back as fresh questions until they're relearned (ADR-0011). Topic reviews
// and the next topic join it in Milestone C.
export function TodayPage() {
  const auth = useAuth()
  return (
    <section className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-bold">Today</h1>
        <p className="text-slate-600 dark:text-slate-400">
          Skills you've missed come back here as different questions, until
          you've got them right on 2 different days.
        </p>
      </header>
      {auth.status === 'signed-in' && <Revisit />}
      {auth.status === 'signed-out' && (
        <p>
          <Link to="/sign-in" className="underline">
            Sign in
          </Link>{' '}
          to see what to revisit today.
        </p>
      )}
      <p>
        <Link to="/map" className="underline">
          See every topic on the map
        </Link>
      </p>
    </section>
  )
}

type Ready = Extract<FollowUpsState, { status: 'ready' }>

/** A follow-up that's due, with the question chosen to ask. */
type Card = {
  key: string
  followUp: FollowUp
  itemId: string
  content: TopicContent
}

const keyOf = (followUp: FollowUp) => `${followUp.topicId}/${followUp.skillId}`

function dueCards(state: Ready, today: Day): Card[] {
  const cards: Card[] = []
  for (const followUp of state.open) {
    if (followUp.due > today) continue
    const content = state.contents.get(followUp.topicId)
    const itemId = content && chooseQuestion(followUp, content, state.attempts)
    if (content && itemId) {
      cards.push({ key: keyOf(followUp), followUp, itemId, content })
    }
  }
  return cards
}

/** "today", "tomorrow", or "on Mon, Nov 9". */
function whenDue(day: Day, today: Day): string {
  if (day <= today) return 'today'
  if (day === addDays(today, 1)) return 'tomorrow'
  const [year = 0, month = 1, date = 1] = day.split('-').map(Number)
  const noon = new Date(year, month - 1, date, 12)
  return `on ${noon.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}`
}

function skillName(followUp: FollowUp, content: TopicContent | undefined) {
  const skill = content?.topic.skills.find(
    (candidate) => candidate.id === followUp.skillId,
  )
  return skill?.description ?? followUp.skillId
}

function Revisit() {
  const state = useFollowUps()
  // Read the clock once, when the page opens, so "today" stays the same
  // for the whole visit.
  const [today] = useState(() => dayOf(Date.now()))
  // The questions are chosen once, when the history first loads. Otherwise
  // answering one would change the card under the learner's eyes.
  const [cards, setCards] = useState<Card[] | null>(null)
  if (state.status === 'ready' && cards === null) {
    setCards(dueCards(state, today))
  }

  if (state.status === 'failed') {
    return (
      <div className="space-y-2">
        <p>
          Your history couldn't load. Check your connection, then try again.
        </p>
        <button type="button" onClick={state.retry} className={BUTTON}>
          Try again
        </button>
      </div>
    )
  }

  if (state.status === 'loading' || cards === null) {
    return (
      <p className="text-slate-500 dark:text-slate-400">
        Loading your history…
      </p>
    )
  }
  const live = new Map(
    state.open.map((followUp) => [keyOf(followUp), followUp]),
  )
  const shown = new Set(cards.map((card) => card.key))
  const later = state.open.filter(
    (followUp) => followUp.due > today && !shown.has(keyOf(followUp)),
  )

  return (
    <>
      <section aria-labelledby="revisit" className="space-y-4">
        <h2 id="revisit" className="text-xl font-semibold">
          Mistakes to revisit
        </h2>
        {cards.length === 0 ? (
          <p className="text-slate-600 dark:text-slate-400">
            Nothing to revisit today.
          </p>
        ) : (
          cards.map((card) => (
            <FollowUpCard
              key={card.key}
              card={card}
              live={live.get(card.key)}
              today={today}
            />
          ))
        )}
      </section>
      {later.length > 0 && (
        <section aria-labelledby="later" className="space-y-2">
          <h2 id="later" className="text-xl font-semibold">
            Coming back later
          </h2>
          <ul className={`list-disc space-y-1 pl-6 ${INLINE_CODE}`}>
            {later.map((followUp) => (
              <li key={keyOf(followUp)}>
                <Markdown inline>
                  {skillName(followUp, state.contents.get(followUp.topicId))}
                </Markdown>{' '}
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  ({getTopic(followUp.topicId)?.title}):{' '}
                  {whenDue(followUp.due, today)}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </>
  )
}

function FollowUpCard({
  card,
  live,
  today,
}: {
  card: Card
  /** The follow-up as it stands now, or undefined once it's relearned. */
  live: FollowUp | undefined
  today: Day
}) {
  const { content, followUp } = card
  let progress = ''
  if (!live) {
    progress = "Relearned: you've got this right on 2 different days."
  } else if (live.due > today) {
    progress =
      live.missedOn === today
        ? `Not quite. It comes back ${whenDue(live.due, today)}.`
        : `Right! It comes back ${whenDue(live.due, today)}, to make sure it sticks.`
  }

  return (
    <div className="space-y-2">
      <p
        className={`text-sm text-slate-600 dark:text-slate-400 ${INLINE_CODE}`}
      >
        <span className="font-medium">Skill:</span>{' '}
        <Markdown inline>{skillName(followUp, content)}</Markdown>
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
