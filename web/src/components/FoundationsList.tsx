import { Link } from 'react-router'
import { isOpen, placeOf } from '../content/content.ts'
import {
  aboutTime,
  describeSources,
  foundationLink,
  foundationsAnchor,
  foundationsPlacementLink,
  groupByModule,
  type FoundationGroup,
} from '../content/foundations.ts'
import type { Module, Topic, Track } from '../content/types.ts'
import { describeListRecord } from '../placement/describe.ts'
import type { PlacementRecord } from '../placement/history.ts'
import { probesNeeded } from '../placement/placement.ts'
import {
  nextUp,
  STATE_LABELS,
  stateOf,
  type TopicProgress,
} from '../progress/progress.ts'

// "Before Module 1: from other tracks", on the map (v1 spec, F9). A track
// that builds on another track's topics lists exactly those, in an order to
// learn them, above the module that needs them. It answers the question a
// learner starting the track has: do I need the whole other track first,
// or which parts? Learning them here or there is the same: a topic is
// learned once, wherever it was opened from.

export function FoundationsList({
  track,
  module,
  number,
  topics,
  progress,
  placement,
}: {
  /** The track whose map this is. */
  track: Track
  module: Module
  number: number
  /** The other tracks' topics the module builds on, in learning order. */
  topics: Topic[]
  /** The learner's progress, once known; undefined when signed out. */
  progress?: Map<string, TopicProgress>
  /** The latest placement test taken for this list alone, if there is one. */
  placement?: PlacementRecord
}) {
  const learned = (topicId: string) =>
    Boolean(progress?.get(topicId)?.learnedAt)
  // The placement test for this list walks its topics by halving
  // (ADR-0021): this is how many of them it would probe at most. It skips
  // checkpoints, topics not written yet and topics already learned, so
  // there may be nothing left for it to walk.
  const probes = probesNeeded(
    topics.filter(
      (topic) => topic.kind === 'topic' && isOpen(topic) && !learned(topic.id),
    ).length,
  )
  const learnedCount = progress
    ? topics.filter((topic) => progress.get(topic.id)?.learnedAt).length
    : 0
  const allLearned = progress !== undefined && learnedCount === topics.length
  const next = progress ? nextUp(topics.filter(isOpen), progress) : null
  const groups = groupByModule(topics)
  const headingId = foundationsAnchor(module)
  const heading = `Before Module ${number}: from other tracks`

  // Once everything is learned it folds to one line, but stays on the map:
  // the list is still where to look when one of them fades.
  if (allLearned) {
    return (
      <details
        id={headingId}
        className="rounded-lg border border-slate-200 p-3 dark:border-slate-800"
      >
        <summary className="cursor-pointer text-sm">
          <span aria-hidden="true">✓ </span>
          {heading}: all {topics.length} learned
        </summary>
        <Groups groups={groups} track={track} progress={progress} next={null} />
      </details>
    )
  }

  return (
    <section
      id={headingId}
      aria-labelledby={`${headingId}-heading`}
      className="space-y-3 rounded-lg border-2 border-dashed border-slate-300 p-4 dark:border-slate-700"
    >
      <h3 id={`${headingId}-heading`} className="font-semibold">
        {heading}
      </h3>
      <p>
        This module builds on {topics.length}{' '}
        {topics.length === 1 ? 'topic' : 'topics'} from other tracks,{' '}
        {aboutTime(topics)} in all. You don't need the rest of those tracks:
      </p>
      <ul className="list-disc space-y-1 pl-6">
        {describeSources(topics).map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
      {progress && (
        <p className="text-sm text-slate-600 dark:text-slate-400">
          {learnedCount} of {topics.length} learned. Anything you learn from
          another track counts here too.
        </p>
      )}
      {next && (
        <p className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
          <Link
            to={foundationLink(next.topic.id, track)}
            className="inline-block rounded-md bg-lime-400 px-4 py-2 font-semibold text-slate-900 hover:bg-lime-300"
          >
            {next.state === 'in-progress' ? 'Continue' : 'Start'}:{' '}
            {next.topic.title}
          </Link>
          <PlaceNote topic={next.topic} />
        </p>
      )}
      <Groups
        groups={groups}
        track={track}
        progress={progress}
        next={next?.topic ?? null}
      />
      {placement && (
        <p className="text-sm text-slate-600 dark:text-slate-400">
          {describeListRecord(placement, learned)}
        </p>
      )}
      <p className="text-sm text-slate-600 dark:text-slate-400">
        Know some of this already?{' '}
        {probes > 0 && (
          <>
            <Link
              to={foundationsPlacementLink(track, module)}
              className="underline"
            >
              {placement
                ? "Take this list's placement test again"
                : 'Take a placement test of just this list'}
            </Link>
            : about {probes} topics' worth of questions find where in it to
            start.{' '}
          </>
        )}
        Any topic's "Prove it now" skips straight to its checks.
      </p>
    </section>
  )
}

/** "Python Foundations · Module 1: First programs". */
function PlaceNote({ topic }: { topic: Topic }) {
  const place = placeOf(topic.id)
  if (!place) return null
  return (
    <span className="text-sm text-slate-500 dark:text-slate-400">
      {place.track.title} · Module {place.number}: {place.module.title}
    </span>
  )
}

/**
 * The list, one fold per module it comes from. The fold holding the next
 * topic starts open, and so does the first one for a signed-out visitor,
 * so the list never opens as a wall of 30 rows.
 */
function Groups({
  groups,
  track,
  progress,
  next,
}: {
  groups: FoundationGroup[]
  track: Track
  progress?: Map<string, TopicProgress>
  next: Topic | null
}) {
  return (
    <div className="space-y-2">
      {groups.map((group, index) => {
        const { place, topics, whole } = group
        const learned = progress
          ? topics.filter((topic) => progress.get(topic.id)?.learnedAt).length
          : null
        const open = next
          ? topics.some((topic) => topic.id === next.id)
          : !progress && index === 0
        const size = whole
          ? 'the whole module'
          : `${topics.length} of its topics`
        return (
          <details
            key={`${place.module.id}-${index}`}
            open={open}
            className="rounded-md border border-slate-200 bg-white px-3 py-2 dark:border-slate-800 dark:bg-slate-900"
          >
            <summary className="cursor-pointer">
              <span className="font-medium">
                {place.track.title} · Module {place.number}:{' '}
                {place.module.title}
              </span>
              <span className="text-sm text-slate-500 dark:text-slate-400">
                {' · '}
                {size}
                {learned !== null && `, ${learned} of ${topics.length} learned`}
              </span>
            </summary>
            <ol className="mt-2 space-y-1">
              {topics.map((topic) => {
                const state =
                  progress && isOpen(topic) ? stateOf(topic, progress) : null
                const shown = state
                  ? STATE_LABELS[state]
                  : isOpen(topic)
                    ? { icon: '●', label: 'Ready' }
                    : { icon: '○', label: 'Coming soon' }
                return (
                  <li
                    key={topic.id}
                    className="flex flex-wrap items-baseline justify-between gap-x-4"
                  >
                    <Link
                      to={foundationLink(topic.id, track)}
                      className="underline-offset-2 hover:underline"
                    >
                      {topic.title}
                    </Link>
                    <span className="text-sm text-slate-500 dark:text-slate-400">
                      <span aria-hidden="true">{shown.icon} </span>
                      {shown.label}
                      {' · '}
                      {topic.estimated_minutes} min
                    </span>
                  </li>
                )
              })}
            </ol>
          </details>
        )
      })}
    </div>
  )
}
