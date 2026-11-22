import { type ReactNode, useEffect, useMemo, useState } from 'react'
import { Link, NavLink, useLocation, useParams } from 'react-router'
import { FoundationsList } from '../components/FoundationsList.tsx'
import {
  BAR_FILL,
  BAR_TRACK,
  CHIP,
  DONE_CHIP,
  SECONDARY_BUTTON,
  YOU_ARE_HERE,
} from '../components/styles.ts'
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
import {
  type ModuleFoundations,
  trackFoundations,
} from '../content/foundations.ts'
import type { Module, Topic, Track } from '../content/types.ts'
import {
  type PlacementRecord,
  subjectOfFoundations,
} from '../placement/history.ts'
import { usePlacements } from '../placement/usePlacements.ts'
import {
  furtherParts,
  PROOFS,
  STATE_LABELS,
  stateOf,
  type TopicProgress,
  type TopicState,
} from '../progress/progress.ts'
import { countModule } from '../progress/modules.ts'
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
          <p className="text-sm text-muted">Loading this track's map…</p>
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
    <header className="space-y-3">
      <h1 className="text-3xl font-bold sm:text-4xl">Topic map</h1>
      <TrackSwitcher current={track} />
      <p className="max-w-2xl text-muted">
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
  // A topic may build on another track's topics (the ML track's math on
  // Python Foundations). Each module lists the ones it needs, all the way
  // down, and their states need their progress too.
  const foundations = useMemo(() => trackFoundations(track), [track])
  const withPrerequisites = useMemo(
    () => [...topics, ...foundations.flatMap((each) => each.topics)],
    [topics, foundations],
  )
  const progress = useProgress(withPrerequisites)
  // Each foundations list shows its own placement result, if it has one.
  const placements = usePlacements()
  useScrollToHash()
  // Drafts count as "still being written": the dev server can open them,
  // but the note is about what a learner can do.
  const anythingReady = topics.some((topic) => topic.status === 'ready')
  // Read the clock once, when the map opens, for the memory percentages.
  const [now] = useState(() => new Date().toISOString())

  return (
    <section className="space-y-8">
      <TrackHeader track={track}>
        {!anythingReady && (
          <p className="text-sm text-muted">
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
            track={track}
            module={module}
            number={index + 1}
            foundations={foundations[index]}
            placement={
              placements.status === 'ready'
                ? placements.latest.get(subjectOfFoundations(module.id))
                : undefined
            }
            progress={progress}
            now={now}
          />
        ))}
      </ol>
    </section>
  )
}

/**
 * Scrolls to the part of the map a link names (/map/finance#foundations-…),
 * as a browser does for a page it loads, since moving within the app doesn't.
 */
function useScrollToHash() {
  const { hash } = useLocation()
  useEffect(() => {
    if (!hash) return
    document
      .getElementById(decodeURIComponent(hash.slice(1)))
      ?.scrollIntoView?.()
  }, [hash])
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
              className={`inline-block rounded-full border px-4 py-1.5 text-sm ${
                track.id === current.id
                  ? YOU_ARE_HERE
                  : 'border-line-strong bg-card font-medium hover:bg-sunken'
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
  track,
  module,
  number,
  foundations,
  placement,
  progress,
  now,
}: {
  track: Track
  module: Module
  number: number
  /** The other tracks' topics this module builds on. */
  foundations?: ModuleFoundations
  /** The latest placement test of that list alone (ADR-0021). */
  placement?: PlacementRecord
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
  // How far through the module the learner is (progress/modules.ts), once
  // anything in it can be opened.
  const count =
    progress.status === 'ready'
      ? countModule(module, progress.progress, (id) => {
          const topic = getTopic(id)
          return topic !== undefined && isOpen(topic)
        })
      : null

  return (
    <>
      <li className="space-y-3">
        <div className="flex flex-wrap items-baseline gap-x-3">
          <h2 className="text-xl font-semibold">
            Module {number}: {module.title}
          </h2>
          {count && count.open > 0 && (
            <p className="text-sm text-muted">
              {count.proven} of {count.open} proven
            </p>
          )}
        </div>
        {count && count.open > 0 && (
          // The count beside the heading says the same.
          <div aria-hidden="true" className={`max-w-xs ${BAR_TRACK}`}>
            {count.proven > 0 && (
              <div
                className={BAR_FILL}
                style={{ width: `${(100 * count.proven) / count.open}%` }}
              />
            )}
          </div>
        )}
        {foundations && foundations.topics.length > 0 && (
          <FoundationsList
            track={track}
            module={module}
            number={number}
            topics={foundations.topics}
            placement={placement}
            progress={
              progress.status === 'ready' ? progress.progress : undefined
            }
          />
        )}
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
      <h1 className="text-3xl font-bold sm:text-4xl">No such track</h1>
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
    return <p className="text-sm text-muted">Loading your progress…</p>
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

/** The states whose label is drawn as a progress fill: proven and kept. */
const DONE_STATES = new Set<TopicState>(['learned', 'mastered', 'passed'])

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

/**
 * The proof checks passed on a topic that isn't Learned yet, if any. A
 * checkpoint with further parts numbers its parts, as its own page does:
 * part 1 is the build, part 2 the debug, and part 3 on are prove.more
 * (ADR-0012, amended 2026-11-11), so a part still to do is never hidden
 * behind "build, debug and explain".
 */
function passedNote(topic: Topic, progress: TopicProgress): string | null {
  if (progress.learnedAt) return null
  const parts = furtherParts(topic)
  const passed =
    parts.length === 0
      ? PROOFS.filter((proof) => progress.passed[proof])
      : [
          ...(progress.passed.build ? ['part 1'] : []),
          ...(progress.passed.debug ? ['part 2'] : []),
          ...parts
            .filter((part) => progress.partsPassed?.[part.id])
            .map((part) => `part ${part.number}`),
          ...(progress.passed.explain ? ['explain'] : []),
        ]
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
  const note = progress ? passedNote(topic, progress) : null
  // The living map: a Learned topic shows how well it's predicted to be
  // remembered right now, so the spacing is something the learner can see.
  const memory = progress?.card ? memoryPercent(progress.card, now) : null
  return (
    <li
      // The whole row lifts under the pointer; the title is the link.
      className={`rounded-xl border px-4 py-3 ${
        open
          ? 'border-line bg-card shadow-card hover:border-line-strong'
          : 'border-dashed border-line-strong'
      }`}
    >
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1">
        <Link
          to={`/topic/${topic.id}`}
          className="font-display text-lg font-semibold underline-offset-2 hover:underline"
        >
          {topic.title}
        </Link>
        <span className={state && DONE_STATES.has(state) ? DONE_CHIP : CHIP}>
          <span aria-hidden="true">{shown.icon} </span>
          {shown.label}
        </span>
      </div>
      <p className="text-sm text-muted">{topic.summary}</p>
      {note && <p className="mt-1 text-sm font-medium text-ink">{note}</p>}
      {memory !== null && (
        <p className="mt-1 flex items-center gap-2 text-sm text-muted">
          <span>Memory: {memory}%</span>
          {/* The words carry the meaning; the bar only shows it at a glance. */}
          <meter
            className="h-2 w-24"
            min={0}
            max={100}
            low={90}
            // The best value is 100: without this the browser takes the
            // middle, 50, and colours a fading topic as the good one.
            optimum={100}
            value={memory}
            aria-hidden="true"
          />
        </p>
      )}
    </li>
  )
}
