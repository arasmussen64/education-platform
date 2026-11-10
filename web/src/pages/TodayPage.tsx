import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import { Markdown } from '../components/Markdown.tsx'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { BUTTON, INLINE_CODE } from '../components/styles.ts'
import {
  diagnostics,
  getTopic,
  getTrack,
  isOpen,
  loadTopicContent,
  placeOf,
  topicIdsOf,
  tracks,
} from '../content/content.ts'
import type { Topic, TopicContent } from '../content/types.ts'
import { addDays, type Day, dayOf } from '../days.ts'
import {
  CORRECT_DAYS_NEEDED,
  type FollowUp,
  type PlannedCard,
  planCards,
} from '../followups/followUps.ts'
import { type FollowUpsState, useFollowUps } from '../followups/useFollowUps.ts'
import {
  formatDuration,
  formatHours,
  nextMilestone,
  type PracticeTime,
  practiceTime,
  practiceTimeByTrack,
} from '../progress/practiceTime.ts'
import {
  describeDiagnosticRecord,
  describeTrackRecord,
} from '../placement/describe.ts'
import { subjectOfDiagnostic } from '../placement/history.ts'
import { usePlacements } from '../placement/usePlacements.ts'
import { nextUp, stateOf } from '../progress/progress.ts'
import { type ProgressState, useProgress } from '../progress/useProgress.ts'
import { ReviewSession } from '../reviews/ReviewSession.tsx'
import { type DueReview, dueReviews } from '../reviews/reviews.ts'

// The daily plan (v1 spec, F12), in this order: reviews that are due
// (ADR-0009), mistakes coming back as fresh questions until they're
// relearned (ADR-0011), then the topic to work on.
export function TodayPage() {
  const auth = useAuth()
  return (
    <section className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-bold">Today</h1>
        <p className="text-slate-600 dark:text-slate-400">
          First the topics due for a review, timed to how fast you forget. Then
          skills you've missed, back as different questions until you've got
          them right on {CORRECT_DAYS_NEEDED} different days. Then the topic
          you're on.
        </p>
      </header>
      {auth.status === 'signed-in' && <Plan />}
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

/** The signed-in learner's plan. The progress is read once, for all of it. */
function Plan() {
  // The topics bundled with the app. An outline-only track's topics aren't,
  // and don't need to be: nothing in them can be due or next (content.ts).
  const topics = useMemo(
    () =>
      tracks()
        .flatMap(topicIdsOf)
        .map((id) => getTopic(id))
        .filter((topic) => topic !== undefined),
    [],
  )
  const progress = useProgress(topics)
  // Read the clock once, when the page opens.
  const [now] = useState(() => new Date().toISOString())
  return (
    <>
      <Reviews topics={topics} progress={progress} now={now} />
      <Revisit />
      <NextUp topics={topics} progress={progress} />
      <PracticeHours progress={progress} now={now} />
    </>
  )
}

/**
 * Deliberate practice so far, on the way to 10,000 hours (the owner's idea;
 * roadmap, Phase 2). Only time spent on answers, Checks and reviews counts,
 * not time with the site open: see progress/practiceTime.ts. The total is
 * one sentence; the milestones are per track, because the 10,000 hours are
 * about mastering one domain (ADR-0019).
 */
function PracticeHours({
  progress,
  now,
}: {
  progress: ProgressState
  now: string
}) {
  if (progress.status !== 'ready') return null
  const all = practiceTime(progress.attempts, now)
  const split = practiceTimeByTrack(
    progress.attempts,
    now,
    tracks().map((track) => track.id),
    (topicId) => placeOf(topicId)?.track.id,
  )
  const recent =
    all.recentMs === 0
      ? 'none of it in the last 7 days'
      : `${formatDuration(all.recentMs)} of it in the last 7 days`

  return (
    <section aria-labelledby="practice-hours" className="space-y-3">
      <h2 id="practice-hours" className="text-xl font-semibold">
        Practice hours
      </h2>
      {all.attempts === 0 ? (
        <p className="text-slate-600 dark:text-slate-400">
          Nothing counted yet. Every answer, Check and review you finish adds
          its time here.
        </p>
      ) : (
        <>
          <p>
            <span className="font-medium">{formatDuration(all.totalMs)}</span>{' '}
            of deliberate practice so far, {recent}. Counting the time spent on
            answers, Checks and reviews, not time with the site open.
          </p>
          {split.tracks.map(({ trackId, time }) => (
            <TrackHours
              key={trackId}
              title={getTrack(trackId)?.title ?? trackId}
              time={time}
            />
          ))}
          {split.other.attempts > 0 && (
            <TrackHours title="Other" time={split.other} />
          )}
        </>
      )}
    </section>
  )
}

/** One track's practice time and its own next milestone (ADR-0019). */
function TrackHours({ title, time }: { title: string; time: PracticeTime }) {
  const milestone = nextMilestone(time.totalMs)
  const summary =
    time.attempts === 0
      ? 'nothing counted yet'
      : `${formatDuration(time.totalMs)} so far, ${
          time.recentMs === 0 ? 'none' : formatDuration(time.recentMs)
        } in the last 7 days`
  return (
    <div className="space-y-1">
      <h3 className="font-semibold">
        {title}
        <span className="ml-2 text-sm font-normal text-slate-500 dark:text-slate-400">
          {summary}
        </span>
      </h3>
      {milestone ? (
        <>
          <progress
            className="h-2 w-full"
            max={milestone.hours * 60}
            value={Math.floor(time.totalMs / 60_000)}
            aria-label={`${title}: progress toward ${formatHours(milestone.hours)}`}
          />
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Next milestone: {formatHours(milestone.hours)} (
            {formatDuration(milestone.remainingMs)} to go).
          </p>
        </>
      ) : (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Past {formatHours(10000)}. The milestones stop here; the practice
          doesn't have to.
        </p>
      )}
    </div>
  )
}

/**
 * The topics due for a review (ADR-0009, F11), most forgotten first, up to
 * the daily limit. Each gets a session; finishing one doesn't make it
 * disappear, because the list is fixed when it first loads.
 */
function Reviews({
  topics,
  progress,
  now,
}: {
  topics: Topic[]
  progress: ProgressState
  now: string
}) {
  const [due, setDue] = useState<DueReview[] | null>(null)
  if (progress.status === 'ready' && due === null) {
    setDue(dueReviews(topics.filter(isOpen), progress.progress, now))
  }
  const [contents, setContents] = useState<Map<string, TopicContent> | null>(
    null,
  )
  useEffect(() => {
    if (due === null) return
    let active = true
    Promise.all(due.map((review) => loadTopicContent(review.topic.id))).then(
      (loaded) => {
        if (!active) return
        const found = loaded.filter((content) => content !== null)
        setContents(
          new Map(found.map((content) => [content.topic.id, content])),
        )
      },
    )
    return () => {
      active = false
    }
  }, [due])

  if (progress.status === 'signed-out' || progress.status === 'failed') {
    return null
  }
  return (
    <section aria-labelledby="reviews" className="space-y-4">
      <h2 id="reviews" className="text-xl font-semibold">
        Reviews
      </h2>
      {due === null || contents === null || progress.status !== 'ready' ? (
        <p className="text-slate-500 dark:text-slate-400">
          Loading your reviews…
        </p>
      ) : due.length === 0 ? (
        <p className="text-slate-600 dark:text-slate-400">
          No reviews due today.
        </p>
      ) : (
        <>
          <p className="text-slate-600 dark:text-slate-400">
            {due.length === 1
              ? 'One topic is due for a review.'
              : `${due.length} topics are due for a review, the most forgotten first.`}{' '}
            Each asks two quick questions. No hints here.
          </p>
          {due.map((review) => {
            const content = contents.get(review.topic.id)
            const entry = progress.progress.get(review.topic.id)
            return content && entry ? (
              <ReviewSession
                key={review.topic.id}
                content={content}
                progress={entry}
                attempts={progress.attempts}
                now={now}
              />
            ) : null
          })}
        </>
      )}
    </section>
  )
}

/** The states in which a topic has been learned (ADR-0002), for the count. */
const LEARNED_STATES = new Set([
  'learned',
  'mastered',
  'fading',
  'relearning',
  'passed',
])

/**
 * The topic to work on in each track (F12, ADR-0019): the one in progress,
 * or the next Available, with how far along the track is, so a learner on
 * two tracks sees where they stand on both.
 */
function NextUp({
  topics,
  progress,
}: {
  topics: Topic[]
  progress: ProgressState
}) {
  if (progress.status !== 'ready') return null
  const open = new Set(topics.filter(isOpen).map((topic) => topic.id))

  return (
    <section aria-labelledby="next-up" className="space-y-4">
      <h2 id="next-up" className="text-xl font-semibold">
        Next up
      </h2>
      {tracks().map((track) => {
        const own = topicIdsOf(track)
          .map((id) => getTopic(id))
          .filter(
            (topic): topic is Topic =>
              topic !== undefined && open.has(topic.id),
          )
        const learned = own.filter((topic) =>
          LEARNED_STATES.has(stateOf(topic, progress.progress)),
        ).length
        const next = nextUp(own, progress.progress)
        return (
          <div key={track.id} className="space-y-1">
            <h3 className="font-semibold">
              {track.title}
              <span className="ml-2 text-sm font-normal text-slate-500 dark:text-slate-400">
                {learned} of {own.length} learned
              </span>
            </h3>
            {own.length === 0 ? (
              <p className="text-slate-600 dark:text-slate-400">
                Nothing written here yet.
              </p>
            ) : next ? (
              <p>
                <span className="font-medium">
                  {next.state === 'in-progress' ? 'Continue' : 'Start'}:
                </span>{' '}
                <Link to={`/topic/${next.topic.id}`} className="underline">
                  {next.topic.title}
                </Link>
                {' · '}
                {next.topic.summary}
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  {' · about '}
                  {next.topic.estimated_minutes} minutes
                </span>
              </p>
            ) : (
              <p className="text-slate-600 dark:text-slate-400">
                You've learned everything written here so far. More is on the
                way.
              </p>
            )}
          </div>
        )
      })}
      <PlacementNote progress={progress.progress} />
    </section>
  )
}

/**
 * Where the placement test said to start (ADR-0021), or the offer to take
 * it: it's how a learner who knows some of this skips to the right place.
 */
function PlacementNote({
  progress,
}: {
  progress: Map<string, { learnedAt: string | null }>
}) {
  const placements = usePlacements()
  if (placements.status !== 'ready') return null
  const learned = (topicId: string) => Boolean(progress.get(topicId)?.learnedAt)
  const notes = [
    ...tracks().map((track) => {
      const record = placements.latest.get(track.id)
      return record && `${track.title}. ${describeTrackRecord(record, learned)}`
    }),
    ...diagnostics().map((diagnostic) => {
      const record = placements.latest.get(subjectOfDiagnostic(diagnostic.id))
      return (
        record &&
        `${diagnostic.title}. ${describeDiagnosticRecord(record, diagnostic)}`
      )
    }),
  ].filter((note) => note !== undefined)
  if (notes.length === 0) {
    return (
      <p className="text-sm text-slate-600 dark:text-slate-400">
        New here, or know some of this already?{' '}
        <Link to="/placement" className="underline">
          Take the placement test
        </Link>
        : it finds where to start.
      </p>
    )
  }
  return (
    <div className="space-y-1 text-sm text-slate-600 dark:text-slate-400">
      {notes.map((note) => (
        <p key={note}>{note}</p>
      ))}
      <p>
        <Link to="/placement" className="underline">
          Placement test
        </Link>
      </p>
    </div>
  )
}

type Ready = Extract<FollowUpsState, { status: 'ready' }>

/** A question to ask today, with the follow-ups it answers. */
type Card = PlannedCard & { key: string }

const keyOf = (followUp: FollowUp) => `${followUp.topicId}/${followUp.skillId}`

function dueCards(state: Ready, today: Day): Card[] {
  const due = state.open.filter((followUp) => followUp.due <= today)
  return planCards(due, state.contents, state.attempts).map((card) => ({
    ...card,
    key: `${card.topicId}/${card.itemId}`,
  }))
}

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
  const shown = new Set(
    cards.flatMap((card) => card.followUps.map((followUp) => keyOf(followUp))),
  )
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
              live={live}
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
  /** Every open follow-up as it stands now; a relearned one is missing. */
  live: Map<string, FollowUp>
  today: Day
}) {
  const { content, followUps } = card
  const names = followUps.map((followUp) => skillName(followUp, content))
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
