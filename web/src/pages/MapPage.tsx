import { type ReactNode, useEffect, useMemo, useState } from 'react'
import { Link, NavLink, useParams } from 'react-router'
import { SECONDARY_BUTTON } from '../components/styles.ts'
import {
  getTopic,
  getTrack,
  isOpen,
  loadTrackTopics,
  mainTrack,
  topicIdsOf,
  tracks,
  trackTopicsLoaded,
} from '../content/content.ts'
import type { Module, Topic, Track } from '../content/types.ts'
import {
  PROOFS,
  STATE_LABELS,
  stateOf,
  type TopicProgress,
  type TopicState,
} from '../progress/progress.ts'
import { type ProgressState, useProgress } from '../progress/useProgress.ts'
import { memoryPercent } from '../reviews/reviews.ts'

// The topic map: every topic in a track, by module (v1 spec, F9), each with
// its state for the signed-in learner (F8). /map shows the first track, and
// /map/<track id> another. The graph view arrives later; the list is what
// narrow screens get anyway.
export function MapPage() {
  const { trackId } = useParams()
  const track = trackId ? getTrack(trackId) : mainTrack()
  if (!track) return <UnknownTrack />
  return <TrackMap key={track.id} track={track} />
}

type OutlinesState = 'loading' | 'ready' | 'failed'

/**
 * Whether the track's topic outlines are here. The main track's are bundled
 * with the app; another track's download the first time its map is shown
 * (content.ts), so this says "loading" until they arrive.
 */
function useTrackOutlines(track: Track): [OutlinesState, () => void] {
  const [state, setState] = useState<OutlinesState>(() =>
    trackTopicsLoaded(track.id) ? 'ready' : 'loading',
  )
  useEffect(() => {
    if (state !== 'loading') return
    let current = true
    loadTrackTopics(track.id).then(
      () => current && setState('ready'),
      () => current && setState('failed'),
    )
    return () => {
      current = false
    }
  }, [track.id, state])
  return [state, () => setState('loading')]
}

function TrackMap({ track }: { track: Track }) {
  const [outlines, retryOutlines] = useTrackOutlines(track)
  if (outlines !== 'ready') {
    return (
      <section className="space-y-8">
        <TrackHeader track={track} />
        {outlines === 'loading' ? (
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Loading this track's map…
          </p>
        ) : (
          <p className="flex flex-wrap items-center gap-2 text-sm">
            This track's map couldn't load. Check your connection, then try
            again.
            <button
              type="button"
              onClick={retryOutlines}
              className={SECONDARY_BUTTON}
            >
              Try again
            </button>
          </p>
        )}
      </section>
    )
  }
  return <LoadedTrackMap track={track} />
}

/** The title, the links to the other tracks, and the track's summary. */
function TrackHeader({
  track,
  children,
}: {
  track: Track
  children?: ReactNode
}) {
  return (
    <header className="space-y-2">
      <h1 className="text-2xl font-bold">Topic map</h1>
      <TrackSwitcher current={track} />
      <p className="text-slate-600 dark:text-slate-400">
        <span className="font-medium">{track.title}:</span> {track.summary}
      </p>
      <p className="text-sm">
        Know some of this already?{' '}
        <Link to="/placement" className="underline">
          Take the placement test
        </Link>
        .
      </p>
      {children}
    </header>
  )
}

function LoadedTrackMap({ track }: { track: Track }) {
  const topics = useMemo(
    () =>
      topicIdsOf(track)
        .map((id) => getTopic(id))
        .filter((topic) => topic !== undefined),
    [track],
  )
  // A topic may build on another track's topic (the ML track's math on
  // Python Foundations). Its state needs that topic's progress too.
  const withPrerequisites = useMemo(() => {
    const own = new Set(topics.map((topic) => topic.id))
    const borrowed = topics
      .flatMap((topic) => topic.prerequisites)
      .filter((id) => !own.has(id))
      .map((id) => getTopic(id))
      .filter((topic) => topic !== undefined)
    return [...topics, ...borrowed]
  }, [topics])
  const progress = useProgress(withPrerequisites)
  // Drafts count as "still being written": the dev server can open them,
  // but the note is about what a learner can do.
  const anythingReady = topics.some((topic) => topic.status === 'ready')
  // Read the clock once, when the map opens, for the memory percentages.
  const [now] = useState(() => new Date().toISOString())

  return (
    <section className="space-y-8">
      <TrackHeader track={track}>
        {!anythingReady && (
          <p className="text-sm text-slate-500 dark:text-slate-400">
            This track is an outline so far: every topic is still being written.
            It's on the map so you can see where everything fits.
          </p>
        )}
        <ProgressStatus state={progress} />
      </TrackHeader>
      <ol className="space-y-8">
        {track.modules.map((module, index) => (
          <ModuleSection
            key={module.id}
            module={module}
            number={index + 1}
            progress={progress}
            now={now}
          />
        ))}
      </ol>
    </section>
  )
}

/** Links to the other tracks, once there's more than one. */
function TrackSwitcher({ current }: { current: Track }) {
  const all = tracks()
  if (all.length < 2) return null
  return (
    <nav aria-label="Tracks">
      <ul className="flex flex-wrap gap-2">
        {all.map((track, index) => (
          <li key={track.id}>
            <NavLink
              // The first track lives at /map itself. NavLink marks the
              // current one with aria-current="page".
              to={index === 0 ? '/map' : `/map/${track.id}`}
              end
              className={`inline-block rounded-full border px-3 py-1 text-sm ${
                track.id === current.id
                  ? 'border-lime-600 bg-lime-50 font-medium dark:bg-lime-950'
                  : 'border-slate-300 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800'
              }`}
            >
              {track.title}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}

/** A module's topics and checkpoint, then its capstone if it has one. */
function ModuleSection({
  module,
  number,
  progress,
  now,
}: {
  module: Module
  number: number
  progress: ProgressState
  now: string
}) {
  const rows = (ids: string[]) =>
    ids.map((topicId) => {
      const topic = getTopic(topicId)
      if (!topic) return null
      // A state needs the learner's progress, and a topic that can be opened.
      const known = progress.status === 'ready' && isOpen(topic)
      return (
        <TopicRow
          key={topicId}
          topic={topic}
          progress={known ? progress.progress.get(topicId) : undefined}
          state={known ? stateOf(topic, progress.progress) : undefined}
          now={now}
        />
      )
    })
  const capstone = module.capstone ? getTopic(module.capstone) : undefined

  return (
    <>
      <li className="space-y-3">
        <h2 className="text-xl font-semibold">
          Module {number}: {module.title}
        </h2>
        <ol className="space-y-2">
          {rows([...module.topics, module.checkpoint])}
        </ol>
      </li>
      {capstone && (
        <li className="space-y-3">
          <h2 className="text-xl font-semibold">Capstone</h2>
          <ol className="space-y-2">{rows([capstone.id])}</ol>
        </li>
      )}
    </>
  )
}

function UnknownTrack() {
  return (
    <section className="space-y-3">
      <h1 className="text-2xl font-bold">No such track</h1>
      <p>
        There's no track at this address.{' '}
        <Link to="/map" className="underline">
          See the topic map
        </Link>
        .
      </p>
    </section>
  )
}

/** Says while the learner's progress loads, or if it couldn't. */
function ProgressStatus({ state }: { state: ProgressState }) {
  if (state.status === 'loading') {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400">
        Loading your progress…
      </p>
    )
  }
  if (state.status === 'failed') {
    return (
      <p className="flex flex-wrap items-center gap-2 text-sm">
        Your progress couldn't load. Check your connection, then try again.
        <button
          type="button"
          onClick={state.retry}
          className={SECONDARY_BUTTON}
        >
          Try again
        </button>
      </p>
    )
  }
  return null
}

// Never color alone: each state has an icon and a word (F9).
const AVAILABILITY = {
  ready: { icon: '●', label: 'Ready' },
  draft: { icon: '✎', label: 'Draft' },
  soon: { icon: '○', label: 'Coming soon' },
} as const

function availability(topic: Topic) {
  if (!isOpen(topic)) return AVAILABILITY.soon
  return topic.status === 'draft' ? AVAILABILITY.draft : AVAILABILITY.ready
}

/** "build", "build and debug", "build, debug and explain". */
function listOf(words: string[]): string {
  if (words.length < 2) return words.join('')
  return `${words.slice(0, -1).join(', ')} and ${words.at(-1)}`
}

/** The proof checks passed on a topic that isn't Learned yet, if any. */
function passedNote(progress: TopicProgress): string | null {
  if (progress.learnedAt) return null
  const passed = PROOFS.filter((proof) => progress.passed[proof])
  return passed.length === 0 ? null : `Proof checks passed: ${listOf(passed)}`
}

function TopicRow({
  topic,
  progress,
  state,
  now,
}: {
  topic: Topic
  /** The learner's progress, once it has loaded. */
  progress?: TopicProgress
  /** The topic's state for the learner, once known (F8). */
  state?: TopicState
  now: string
}) {
  // A signed-in learner sees the topic's state; everyone else, whether it
  // can be opened.
  const shown = state ? STATE_LABELS[state] : availability(topic)
  const open = isOpen(topic)
  const note = progress ? passedNote(progress) : null
  // The living map: a Learned topic shows how well it's predicted to be
  // remembered right now, so the spacing is something the learner can see.
  const memory = progress?.card ? memoryPercent(progress.card, now) : null
  return (
    <li
      className={`rounded-lg border p-3 ${
        open
          ? 'border-lime-500 bg-white dark:bg-slate-900'
          : 'border-slate-200 dark:border-slate-800'
      }`}
    >
      <div className="flex flex-wrap items-baseline justify-between gap-x-4">
        <Link
          to={`/topic/${topic.id}`}
          className="font-medium underline-offset-2 hover:underline"
        >
          {topic.title}
        </Link>
        <span className="text-sm text-slate-500 dark:text-slate-400">
          <span aria-hidden="true">{shown.icon} </span>
          {shown.label}
        </span>
      </div>
      <p className="text-sm text-slate-600 dark:text-slate-400">
        {topic.summary}
      </p>
      {note && (
        <p className="mt-1 text-sm font-medium text-slate-800 dark:text-slate-200">
          {note}
        </p>
      )}
      {memory !== null && (
        <p className="mt-1 flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
          <span>Memory: {memory}%</span>
          {/* The words carry the meaning; the bar only shows it at a glance. */}
          <meter
            className="h-2 w-24"
            min={0}
            max={100}
            low={90}
            value={memory}
            aria-hidden="true"
          />
        </p>
      )}
    </li>
  )
}
