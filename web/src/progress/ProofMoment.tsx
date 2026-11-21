import { useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router'
import { PROGRESS_FILL } from '../components/styles.ts'
import { getTopic, isOpen, placeOf, tracks } from '../content/content.ts'
import type { Topic } from '../content/types.ts'
import type { Attempt } from '../followups/followUps.ts'
import { useTopicContents } from '../followups/useTopicContents.ts'
import { forgetGuess } from '../nexttime/guesses.ts'
import { NextTimeCard } from '../nexttime/NextTimeCard.tsx'
import { nextTimeFor } from '../nexttime/nextTime.ts'
import { describeGap } from '../reviews/reviews.ts'
import { bundledTopics, nextNewTopic } from '../session/sessionPlan.ts'
import { describeModule } from './modules.ts'
import type { TopicProgress } from './progress.ts'
import { type ModuleStep, moduleStep, openedBy } from './proofMoment.ts'

/** The moment's id, so a link or a test can find it. */
export const PROOF_MOMENT_ID = 'proven'

/** Whether a topic, by ID, is bundled and can be opened. */
function canOpen(topicId: string): boolean {
  const topic = getTopic(topicId)
  return topic !== undefined && isOpen(topic)
}

/**
 * The moment a topic is proven (ADR-0030): shown on its page when the last
 * proof passes during the visit, never on a later one. It says what the
 * proof earned, all of it true of the learner's own progress: the module's
 * bar moving on by one, the topics this one opened, when its first review
 * comes, and then a question about the topic that's next, so the best
 * moment of a topic is also a reason to come back.
 *
 * The lime bar is the only movement, it runs once, and it stays still for a
 * learner whose system asks for reduced motion. No points and no confetti:
 * the proof is the reward (docs/learning-science.md, "Myths we avoid").
 */
export function ProofMoment({
  topic,
  progress,
  attempts,
  now,
}: {
  topic: Topic
  /** Everyone's progress, this topic's proof included. */
  progress: Map<string, TopicProgress>
  attempts: Attempt[]
  /** When the page opened, in ISO format. */
  now: string
}) {
  const heading = useRef<HTMLHeadingElement>(null)
  // Take the learner (and a screen reader) to it once, when it appears. A
  // guess kept about this topic has nothing left to wait for.
  useEffect(() => {
    heading.current?.focus()
    forgetGuess(topic.id)
  }, [topic.id])

  const open = useMemo(() => bundledTopics().filter(isOpen), [])
  const opened = openedBy(topic.id, open, progress)
  const place = placeOf(topic.id)
  const step =
    place && place.role !== 'capstone'
      ? moduleStep(place.number, place.module, progress, canOpen)
      : null
  const card = progress.get(topic.id)?.card ?? null
  const isCheckpoint = topic.kind === 'checkpoint'

  // The topic that's next, fixed when the moment appears, and its content
  // for the question to end on.
  const [next] = useState(() =>
    nextNewTopic(tracks(), open, progress, attempts),
  )
  const nextIds = useMemo(() => (next ? [next.topic.id] : []), [next])
  const loaded = useTopicContents(nextIds)
  const nextContent =
    next && loaded.status === 'ready'
      ? loaded.contents.get(next.topic.id)
      : undefined
  const nextTime =
    next && nextContent
      ? nextTimeFor(nextContent, next.state === 'in-progress', attempts)
      : null

  return (
    <section
      id={PROOF_MOMENT_ID}
      aria-labelledby={`${PROOF_MOMENT_ID}-heading`}
      className="space-y-4 rounded-lg border-2 border-line-strong bg-card p-5"
    >
      <div>
        <p className="text-sm font-semibold tracking-wide text-muted uppercase">
          {isCheckpoint ? 'Checkpoint passed' : 'Topic proven'}
        </p>
        <h2
          id={`${PROOF_MOMENT_ID}-heading`}
          ref={heading}
          tabIndex={-1}
          className="text-2xl font-bold outline-none"
        >
          {/* Green for "proven", as passed tests are; lime means forward. */}
          <span
            aria-hidden="true"
            className="text-emerald-700 dark:text-emerald-400"
          >
            ✓{' '}
          </span>
          {isCheckpoint ? "You've passed" : "You've proven"} {topic.title}
        </h2>
      </div>
      <p>
        {isCheckpoint
          ? 'Every part passed, from a blank editor, with no hints. Nobody ticked this for you: you built it.'
          : 'You built with it from a blank editor, fixed code you had never seen, and explained it in your own words, with no hints. Nobody ticked this for you: you showed it.'}
        {topic.objectives.length > 0 &&
          ' The goals of this topic, below, are now things you can do.'}
      </p>
      {step && <ModuleBar step={step} />}
      {opened.length > 0 && (
        <div className="space-y-1">
          <p className="font-semibold">
            {opened.length === 1
              ? 'It opened a topic that was locked:'
              : `It opened ${opened.length} topics that were locked:`}
          </p>
          <ul className="list-disc space-y-1 pl-6">
            {opened.map((each) => (
              <li key={each.id}>
                <Link to={`/topic/${each.id}`} className="underline">
                  {each.title}
                </Link>
                <span className="text-muted"> · {each.summary}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      {card && (
        <p className="text-muted">
          To keep it, its first review comes {describeGap(now, card.due)}: two
          short questions on the Today page. A topic becomes Mastered once it
          has survived a review at least a week after today.
        </p>
      )}
      {nextTime && <NextTimeCard nextTime={nextTime} />}
    </section>
  )
}

/**
 * The module's progress, moving on by the topic just proven: the bar starts
 * where it stood before and grows to where it stands now. The sentence
 * under it says the same, so the bar is hidden from screen readers.
 */
function ModuleBar({ step }: { step: ModuleStep }) {
  const { count, before, complete, number, module } = step
  const share = (proven: number) =>
    count.open === 0 ? 0 : Math.min(100, (100 * proven) / count.open)
  // Drawn at the old width first, then moved to the new one, so the
  // browser animates the difference.
  const [width, setWidth] = useState(() => share(before))
  const target = share(count.proven)
  useEffect(() => {
    const frame = requestAnimationFrame(() => setWidth(target))
    return () => cancelAnimationFrame(frame)
  }, [target])
  return (
    <div className="space-y-1">
      <div
        aria-hidden="true"
        data-testid="module-bar"
        className="h-3 overflow-hidden rounded-full border border-line-strong bg-sunken"
      >
        <div
          className={`h-full rounded-full border ${PROGRESS_FILL} transition-[width] duration-700 ease-out motion-reduce:transition-none`}
          style={{ width: `${width}%` }}
        />
      </div>
      <p className="font-medium">
        {describeModule(number, module, count)}
        {complete && ' That is the whole module.'}
      </p>
    </div>
  )
}
