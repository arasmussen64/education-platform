import { Link } from 'react-router'
import { getTopic, isOpen, mainTrack } from '../content/content.ts'
import type { Topic } from '../content/types.ts'

// The topic map: every topic in the track, by module (v1 spec, F9). For now
// it lists each topic with whether it's ready to learn; the graph and your
// own progress (learned, due for review) arrive in Milestone B.
export function MapPage() {
  const track = mainTrack()
  return (
    <section className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-bold">Topic map</h1>
        <p className="text-slate-600 dark:text-slate-400">
          <span className="font-medium">{track.title}:</span> {track.summary}
        </p>
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
                return topic ? <TopicRow key={topicId} topic={topic} /> : null
              })}
            </ol>
          </li>
        ))}
      </ol>
    </section>
  )
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

function TopicRow({ topic }: { topic: Topic }) {
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
    </li>
  )
}
