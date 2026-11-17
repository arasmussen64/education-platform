import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import {
  BUTTON,
  CARD,
  PRIMARY_BUTTON,
  SECONDARY_BUTTON,
} from '../components/styles.ts'
import { dayOf } from '../days.ts'
import { type Card, dueCards, keyOf } from '../followups/cards.ts'
import { FollowUpCard } from '../followups/FollowUpCard.tsx'
import type { TopicContent } from '../content/types.ts'
import { type Attempt, topicsToLoad } from '../followups/followUps.ts'
import { useTopicContents } from '../followups/useTopicContents.ts'
import { type Pace, paced, stretches, topicPace } from '../progress/pace.ts'
import type { TopicProgress } from '../progress/progress.ts'
import { type ProgressState, useProgress } from '../progress/useProgress.ts'
import { ReviewSession } from '../reviews/ReviewSession.tsx'
import type { DueReview } from '../reviews/reviews.ts'
import {
  bundledTopics,
  type NextTopic,
  planSession,
  quickCount,
  quickPlan,
  SESSION_PATH,
  type SessionPlan,
} from '../session/sessionPlan.ts'

// "Start today's session" (and "Just 5 minutes") from the Today page: the
// day's work one thing at a time, in the order session/sessionPlan.ts sets.
// The steps are the Today page's own pieces (a ReviewSession, a mistake's
// FollowUpCard), so everything is saved and graded exactly as it is there.
// The Today page keeps every section for browsing; this is the guided way.

export function SessionPage() {
  const auth = useAuth()
  const [params] = useSearchParams()
  const quick = params.get('minutes') === '5'
  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-bold">
          {quick ? 'Just 5 minutes' : "Today's session"}
        </h1>
        <p className="text-slate-600 dark:text-slate-400">
          {quick
            ? 'Only the reviews you are closest to forgetting. They count exactly like any other review.'
            : 'One thing at a time: reviews first, the most faded first, then the mistakes coming back today, then your next topic.'}
        </p>
      </header>
      {auth.status === 'signed-in' && (
        // Keyed by length, so following the link from the short session to
        // the full one plans afresh.
        <Session key={quick ? 'quick' : 'full'} quick={quick} />
      )}
      {auth.status === 'signed-out' && (
        <p>
          <Link to="/sign-in" className="underline">
            Sign in
          </Link>{' '}
          to start a session.
        </p>
      )}
      <p>
        <Link to="/" className="underline">
          Back to Today
        </Link>
      </p>
    </section>
  )
}

/** One step of the session. */
type Step =
  | {
      kind: 'review'
      key: string
      review: DueReview
      entry: TopicProgress
      content: TopicContent
    }
  | { kind: 'revisit'; key: string; card: Card }
  | { kind: 'new'; key: string; next: NextTopic }

const STEP_NAMES: Record<Step['kind'], string> = {
  review: 'Review',
  revisit: 'A mistake coming back',
  new: 'Your next topic',
}

/** The steps of a plan whose questions have loaded, in the plan's order. */
function stepsOf(
  plan: SessionPlan,
  entries: Map<string, TopicProgress>,
  cards: Card[],
  contents: Map<string, TopicContent>,
): Step[] {
  const steps: Step[] = []
  for (const review of plan.reviews) {
    const entry = entries.get(review.topic.id)
    const content = contents.get(review.topic.id)
    // A topic whose content didn't come back (renamed in an update) is left
    // out rather than shown empty.
    if (!entry || !content) continue
    steps.push({
      kind: 'review',
      key: `review/${review.topic.id}`,
      review,
      entry,
      content,
    })
  }
  for (const card of cards) {
    steps.push({ kind: 'revisit', key: `revisit/${card.key}`, card })
  }
  if (plan.next) {
    steps.push({
      kind: 'new',
      key: `new/${plan.next.topic.id}`,
      next: plan.next,
    })
  }
  return steps
}

function Session({ quick }: { quick: boolean }) {
  const topics = useMemo(() => bundledTopics(), [])
  const progress = useProgress(topics)
  // Read the clock once: the plan, and "today", stay fixed for the visit.
  const [now] = useState(() => new Date().toISOString())
  // The plan is fixed when the history first loads, so finishing a review
  // doesn't reshuffle the steps under the learner's feet.
  const [plan, setPlan] = useState<SessionPlan | null>(null)
  // The learner's pace (progress/pace.ts), for the new topic's time.
  const [pace, setPace] = useState<Pace | null>(null)
  if (progress.status === 'ready' && plan === null) {
    const full = planSession({
      topics,
      progress: progress.progress,
      attempts: progress.attempts,
      followUps: progress.followUps,
      now,
    })
    setPlan(quick ? quickPlan(full, quickCount(progress.attempts)) : full)
    setPace(topicPace(topics, progress.progress, progress.attempts))
  }
  // Each topic's progress as the plan saw it, for its review's card.
  const [entries, setEntries] = useState<Map<string, TopicProgress> | null>(
    null,
  )
  if (progress.status === 'ready' && entries === null) {
    setEntries(progress.progress)
  }
  const ids = useMemo(
    () =>
      plan === null
        ? null
        : [
            ...new Set([
              ...plan.reviews.map((review) => review.topic.id),
              ...topicsToLoad(plan.followUps),
            ]),
          ].sort(),
    [plan],
  )
  const loaded = useTopicContents(ids)
  const [steps, setSteps] = useState<Step[] | null>(null)
  if (
    progress.status === 'ready' &&
    plan !== null &&
    entries !== null &&
    loaded.status === 'ready' &&
    steps === null
  ) {
    const cards = dueCards(plan.followUps, loaded.contents, progress.attempts)
    setSteps(stepsOf(plan, entries, cards, loaded.contents))
  }

  if (progress.status === 'failed') {
    return <CouldNotLoad what="Your progress" retry={progress.retry} />
  }
  if (loaded.status === 'failed') {
    return <CouldNotLoad what="Today's questions" retry={loaded.retry} />
  }
  if (steps === null || progress.status !== 'ready') {
    return (
      <p className="text-slate-500 dark:text-slate-400">
        Getting your session ready…
      </p>
    )
  }
  if (steps.length === 0) return <NothingToDo quick={quick} />
  return <Steps steps={steps} progress={progress} now={now} pace={pace} />
}

function Steps({
  steps,
  progress,
  now,
  pace,
}: {
  steps: Step[]
  progress: Extract<ProgressState, { status: 'ready' }>
  now: string
  pace: Pace | null
}) {
  const [index, setIndex] = useState(0)
  const [today] = useState(() => dayOf(now))
  const heading = useRef<HTMLHeadingElement>(null)
  const moved = useRef(false)
  // After Next, move focus to the new step's heading, so a keyboard or
  // screen reader user starts at the top of it. Not on arrival.
  useEffect(() => {
    if (moved.current) heading.current?.focus()
  }, [index])
  const go = (to: number) => {
    moved.current = true
    setIndex(to)
  }

  if (index >= steps.length) {
    return <Finished steps={steps} attempts={progress.attempts} since={now} />
  }
  const step = steps[index]
  const last = index === steps.length - 1
  const live = new Map(
    progress.followUps.map((followUp) => [keyOf(followUp), followUp]),
  )

  return (
    <div className="space-y-4">
      <h2
        ref={heading}
        tabIndex={-1}
        className="text-sm font-semibold tracking-wide text-slate-500 uppercase outline-none dark:text-slate-400"
      >
        Step {index + 1} of {steps.length} · {STEP_NAMES[step.kind]}
      </h2>
      {step.kind === 'review' && (
        <ReviewSession
          key={step.key}
          content={step.content}
          progress={step.entry}
          attempts={progress.attempts}
          now={now}
        />
      )}
      {step.kind === 'revisit' && (
        <FollowUpCard
          key={step.key}
          card={step.card}
          live={live}
          today={today}
        />
      )}
      {step.kind === 'new' && <NewTopic next={step.next} pace={pace} />}
      <div className="flex flex-wrap items-center gap-3">
        {step.kind === 'new' ? (
          <button
            type="button"
            onClick={() => go(index + 1)}
            className={SECONDARY_BUTTON}
          >
            Done for today
          </button>
        ) : (
          <button
            type="button"
            onClick={() => go(index + 1)}
            className={PRIMARY_BUTTON}
          >
            {last ? 'Finish' : 'Next'}
          </button>
        )}
        <span className="text-sm text-slate-500 dark:text-slate-400">
          You can move on at any point. Whatever you answered is saved.
        </span>
      </div>
    </div>
  )
}

/** The last step: the topic to learn next, with the way into it. */
function NewTopic({ next, pace }: { next: NextTopic; pace: Pace | null }) {
  const verb = next.state === 'in-progress' ? 'Continue' : 'Start'
  return (
    <div className={CARD}>
      <h3 className="text-lg font-semibold">{next.topic.title}</h3>
      <p>{next.topic.summary}</p>
      <p className="text-sm text-slate-500 dark:text-slate-400">
        {next.track.title} · about {paced(next.topic.estimated_minutes, pace)}{' '}
        minutes{stretches(pace) && ' at your pace'}
      </p>
      <Link to={`/topic/${next.topic.id}`} className={PRIMARY_BUTTON}>
        {verb} {next.topic.title}
      </Link>
    </div>
  )
}

/** The end: what was done, counted from what was saved during the visit. */
function Finished({
  steps,
  attempts,
  since,
}: {
  steps: Step[]
  attempts: Attempt[]
  since: string
}) {
  const reviewed = new Set(
    steps.flatMap((step) =>
      step.kind === 'review' ? [step.review.topic.id] : [],
    ),
  )
  const asked = new Set(
    steps.flatMap((step) =>
      step.kind === 'revisit'
        ? [`${step.card.topicId}/${step.card.itemId}`]
        : [],
    ),
  )
  const recent = attempts.filter((attempt) => attempt.occurred_at >= since)
  const reviews = new Set(
    recent
      .filter(
        (attempt) =>
          attempt.type === 'review' && reviewed.has(attempt.topic_id),
      )
      .map((attempt) => attempt.topic_id),
  ).size
  const revisits = new Set(
    recent
      .filter(
        (attempt) =>
          attempt.type !== 'review' &&
          asked.has(`${attempt.topic_id}/${attempt.item_id}`),
      )
      .map((attempt) => `${attempt.topic_id}/${attempt.item_id}`),
  ).size
  const done = [
    reviews > 0 && `${reviews} ${reviews === 1 ? 'review' : 'reviews'}`,
    revisits > 0 &&
      `${revisits} ${revisits === 1 ? 'mistake' : 'mistakes'} coming back`,
  ].filter(Boolean)

  return (
    <div className="space-y-3">
      <h2 className="text-xl font-semibold">That's the session done</h2>
      <p>
        {done.length > 0
          ? `You finished ${done.join(' and ')}. Each one is saved and counts in full.`
          : 'Nothing was answered this time, and that is fine. Everything is still here when you come back.'}
      </p>
    </div>
  )
}

/** When there's nothing in the session at all. */
function NothingToDo({ quick }: { quick: boolean }) {
  if (quick) {
    return (
      <p>
        No reviews are due today, so there is nothing to fit into five minutes.{' '}
        <Link to={SESSION_PATH} className="underline">
          Today's session
        </Link>{' '}
        has whatever else is waiting.
      </p>
    )
  }
  return (
    <p>
      Nothing is due today, and no new topic is open right now. The{' '}
      <Link to="/map" className="underline">
        map
      </Link>{' '}
      shows what's coming.
    </p>
  )
}

/** Says what couldn't load, with a button to try again. */
function CouldNotLoad({ what, retry }: { what: string; retry: () => void }) {
  return (
    <div className="space-y-2">
      <p>{what} couldn't load. Check your connection, then try again.</p>
      <button type="button" onClick={retry} className={BUTTON}>
        Try again
      </button>
    </div>
  )
}
