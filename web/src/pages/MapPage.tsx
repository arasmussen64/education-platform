import { useMemo } from 'react'
import { Link } from 'react-router'
import { SECONDARY_BUTTON } from '../components/styles.ts'
import { getTopic, isOpen, mainTrack } from '../content/content.ts'
import type { Topic } from '../content/types.ts'
import { PROOFS, type TopicProgress } from '../progress/progress.ts'
import { type ProgressState, useProgress } from '../progress/useProgress.ts'

// The topic map: every topic in the track, by module (v1 spec, F9), with the
// signed-in learner's progress on each. Topic states (Locked, Learned...)
// and the graph arrive once explanations are graded (Milestone B).
export function MapPage() {
  const track = mainTrack()
  const topics = useMemo(
    () =>
      track.modules
        .flatMap((module) => [...module.topics, module.checkpoint])
        .map((id) => getTopic(id))
        .filter((topic) => topic !== undefined),
    [track],
  )
  const progress = useProgress(topics)

  return (
    <section className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-bold">Topic map</h1>
        <p className="text-slate-600 dark:text-slate-400">
          <span className="font-medium">{track.title}:</span> {track.summary}
        </p>
        <ProgressStatus state={progress} />
      </header>
      <ol className="space-y-8">
        {track.modules.map((module, index) => (
          <li key={module.id} className="space-y-3">
            <h2 className="text-xl font-semibold">
              Module {index + 1}: {module.title}
            </h2>
            <ol className="space-y-2">
              {[...module.topics, module.checkpoint].map((topicId) => {
                const topic = getTopic(topicId)
                return topic ? (
                  <TopicRow
                    key={topicId}
                    topic={topic}
                    progress={
                      progress.status === 'ready'
                        ? progress.progress.get(topicId)
                        : undefined
                    }
                  />
                ) : null
              })}
            </ol>
          </li>
        ))}
      </ol>
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

/** What the learner has done on a topic they've started. */
function progressNote(topic: Topic, progress: TopicProgress): string {
  if (progress.learnedAt) {
    return topic.kind === 'checkpoint' ? '✓ Passed' : '✓ Learned'
  }
  const passed = PROOFS.filter((proof) => progress.passed[proof])
  return passed.length === 0
    ? 'In progress'
    : `In progress · Proof checks passed: ${listOf(passed)}`
}

function TopicRow({
  topic,
  progress,
}: {
  topic: Topic
  /** The learner's progress, once it has loaded. */
  progress?: TopicProgress
}) {
  const state = availability(topic)
  const open = state !== AVAILABILITY.soon
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
          <span aria-hidden="true">{state.icon} </span>
          {state.label}
        </span>
      </div>
      <p className="text-sm text-slate-600 dark:text-slate-400">
        {topic.summary}
      </p>
      {progress?.started && (
        <p className="mt-1 text-sm font-medium text-slate-800 dark:text-slate-200">
          {progressNote(topic, progress)}
        </p>
      )}
    </li>
  )
}
