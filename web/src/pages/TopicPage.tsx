import {
  type ReactNode,
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
} from 'react'
import { flushSync } from 'react-dom'
import { Link, useLoaderData } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import {
  type LoadAttempts,
  SuggestSteps,
  Unstuck,
} from '../checkpoints/Unstuck.tsx'
import { SUGGEST_STEPS_AFTER } from '../checkpoints/versions.ts'
import { getTopic, placeOf, tracks } from '../content/content.ts'
import type { Topic, TopicContent } from '../content/types.ts'
import { LessonView } from '../components/LessonView.tsx'
import { Markdown } from '../components/Markdown.tsx'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { CARD, PROSE, SECONDARY_BUTTON } from '../components/styles.ts'
import { useRecordEvent } from '../events/useEvents.ts'
import { ExplainCheck } from '../explain/ExplainCheck.tsx'
import { fetchAttempts, mergeAttempts } from '../followups/history.ts'
import type { Interleaved } from '../practice/interleave.ts'
import { ReportProblem } from '../reports/ReportProblem.tsx'
import {
  type Proof,
  PROOFS,
  STATE_LABELS,
  stateOf,
  type TopicState,
} from '../progress/progress.ts'
import { type ProgressState, useProgress } from '../progress/useProgress.ts'
import type { topicLoader } from './topicLoader.ts'

// One topic: Learn, Practice and Prove it (v1 spec, F3, F5, F7), gated by
// its state (F8): a Locked topic shows its lesson only.
export function TopicPage() {
  const { topic, content, interleaved } = useLoaderData<typeof topicLoader>()
  if (!topic) return <UnknownTopic />
  // A new key for each topic, so nothing typed on one topic carries over to
  // the next.
  return (
    <TopicView
      key={topic.id}
      topic={topic}
      content={content}
      interleaved={interleaved}
    />
  )
}

export function TopicView({
  topic,
  content,
  interleaved = null,
  loadAttempts,
}: {
  topic: Topic
  /** Null when the topic isn't open yet. */
  content: TopicContent | null
  /** A recall question from an earlier topic, mixed into the practice (F5). */
  interleaved?: Interleaved | null
  /** Reads the learner's history in a topic. Tests pass a fake. */
  loadAttempts?: LoadAttempts
}) {
  useLessonView(content)
  const progress = useTopicProgress(topic, loadAttempts)
  const state =
    progress.status === 'ready' ? stateOf(topic, progress.progress) : null
  // Gating applies to a signed-in learner once their progress is known.
  // Until then the page shows everything, rather than flashing in and out.
  const locked = state === 'locked'
  const [proveNow, setProveNow] = useState(false)

  return (
    <article className="space-y-10">
      <TopicHeader topic={topic} state={state} progress={progress} />
      {content && content.topic.kind === 'checkpoint' && (
        <>
          <SignInToSave />
          <CheckpointView
            content={content}
            loadAttempts={loadAttempts}
            progress={progress}
            locked={locked}
          />
        </>
      )}
      {content && content.topic.kind === 'topic' && (
        <>
          <SignInToSave />
          {locked && <LockedNotice topic={topic} progress={progress} />}
          {state === 'available' && !proveNow && (
            <ProveItNow
              onChoose={() => {
                // Show the checks straight away, then move focus to them.
                flushSync(() => setProveNow(true))
                document.getElementById('prove-it')?.focus()
              }}
            />
          )}
          {proveNow ? (
            <p className={CARD}>
              You skipped the lesson and practice to prove it now.{' '}
              <button
                type="button"
                onClick={() => setProveNow(false)}
                className="underline"
              >
                Show them anyway
              </button>
            </p>
          ) : (
            <Learn content={content} />
          )}
          {!locked && !proveNow && (
            <Practice content={content} interleaved={interleaved} />
          )}
          {!locked && <ProveIt content={content} progress={progress} />}
        </>
      )}
      {!content && (
        <p className={CARD}>
          This topic is still being written. It's on the map so you can see
          where it fits.
        </p>
      )}
    </article>
  )
}

/**
 * The learner's progress on a topic and on what it builds on, which is what
 * its state depends on. Reads each of those topics' history.
 */
function useTopicProgress(
  topic: Topic,
  loadAttempts?: LoadAttempts,
): ProgressState {
  const topics = useMemo(
    () => [
      topic,
      ...topic.prerequisites
        .map((id) => getTopic(id))
        .filter((found) => found !== undefined),
    ],
    [topic],
  )
  const load = useCallback(async () => {
    const read = loadAttempts ?? fetchAttempts
    const lists = await Promise.all(topics.map((each) => read(each.id)))
    return mergeAttempts(...lists)
  }, [loadAttempts, topics])
  return useProgress(topics, load)
}

/** Why a topic is Locked, and what opens it (F3, F8). */
function LockedNotice({
  topic,
  progress,
}: {
  topic: Topic
  progress: ProgressState
}) {
  const learned = (id: string) =>
    progress.status === 'ready' && Boolean(progress.progress.get(id)?.learnedAt)
  const waitingOn = topic.prerequisites
    .filter((id) => !learned(id))
    .map((id) => getTopic(id))
    .filter((found) => found !== undefined)
  return (
    <aside aria-labelledby="locked" className={`${CARD} space-y-2`}>
      <p id="locked" className="font-medium">
        <span aria-hidden="true">{STATE_LABELS.locked.icon} </span>
        {STATE_LABELS.locked.label}
      </p>
      <p>
        This {topic.kind === 'checkpoint' ? 'checkpoint' : 'topic'} opens once
        you've learned{' '}
        {waitingOn.map((prerequisite, index) => (
          <span key={prerequisite.id}>
            {index > 0 && (index === waitingOn.length - 1 ? ' and ' : ', ')}
            <Link to={`/topic/${prerequisite.id}`} className="underline">
              {prerequisite.title}
            </Link>
          </span>
        ))}
        . Until then you can read the lesson, but the practice and the proof
        checks wait.
      </p>
    </aside>
  )
}

/** On an Available topic: skip straight to the proof checks (F8). */
function ProveItNow({ onChoose }: { onChoose: () => void }) {
  return (
    <aside aria-label="Already know this?" className={`${CARD} space-y-2`}>
      <p>
        <span className="font-medium">Already know this?</span> Prove it now:
        skip the lesson and practice and go straight to the three checks.
        Passing them marks the topic as learned, just the same.
      </p>
      <button type="button" onClick={onChoose} className={SECONDARY_BUTTON}>
        Prove it now
      </button>
    </aside>
  )
}

/**
 * A module's checkpoint (F10): what it brings together, the three proof
 * checks, and a way through the build for a learner who's stuck (ADR-0012).
 * A Locked checkpoint shows only what it brings together.
 */
function CheckpointView({
  content,
  loadAttempts,
  progress,
  locked,
}: {
  content: TopicContent
  loadAttempts?: LoadAttempts
  progress: ProgressState
  locked: boolean
}) {
  const { unstuck } = content.topic
  const [failedChecks, setFailedChecks] = useState(0)
  const [buildPassed, setBuildPassed] = useState(false)
  const [stepsOpen, setStepsOpen] = useState(false)
  const stepsHeading = useRef<HTMLHeadingElement>(null)
  const suggest =
    unstuck !== undefined &&
    failedChecks >= SUGGEST_STEPS_AFTER &&
    !buildPassed &&
    !stepsOpen

  if (locked) {
    return (
      <>
        <CheckpointIntro content={content} />
        <LockedNotice topic={content.topic} progress={progress} />
      </>
    )
  }

  return (
    <>
      <CheckpointIntro content={content} />
      <ProveIt
        content={content}
        progress={progress}
        intro="Three checks show you can use everything in this module on your own: build a program from a blank editor, fix code with several bugs, and explain how it works. No hints here. If you get stuck on the build, there's a way through it below."
        onBuildCheck={(passed) => {
          if (passed) setBuildPassed(true)
          else setFailedChecks((count) => count + 1)
        }}
        afterBuild={
          <>
            {/* <output> is announced by screen readers when its text changes. */}
            <output className="sr-only">
              {suggest ? 'Stuck on the build? You can try it in steps.' : ''}
            </output>
            {suggest && (
              <SuggestSteps
                onOpen={() => {
                  // Show the steps straight away, so the page is long enough
                  // to scroll them to the top of the screen. Keyboard focus
                  // goes with them.
                  flushSync(() => setStepsOpen(true))
                  stepsHeading.current?.scrollIntoView({ block: 'start' })
                  stepsHeading.current?.focus({ preventScroll: true })
                }}
              />
            )}
          </>
        }
      />
      {unstuck && (
        <Unstuck
          content={content}
          unstuck={unstuck}
          open={stepsOpen}
          onToggle={() => setStepsOpen((open) => !open)}
          headingRef={stepsHeading}
          loadAttempts={loadAttempts}
        />
      )}
    </>
  )
}

/** In place of a lesson: what the checkpoint brings together. */
function CheckpointIntro({ content }: { content: TopicContent }) {
  const place = placeOf(content.topic.id)
  // A capstone brings a whole stage together, so there's no short list of
  // topics to go back to.
  const topics = (
    place?.role === 'capstone' ? [] : (place?.module.topics ?? [])
  )
    .map((id) => getTopic(id))
    .filter((topic) => topic !== undefined)

  return (
    <section aria-labelledby="about" className="space-y-4">
      <SectionHeading id="about">About this checkpoint</SectionHeading>
      <div className={PROSE}>
        <p>
          It brings together everything in this module. Passing it shows you
          can:
        </p>
        <ul>
          {content.topic.objectives.map((objective) => (
            <li key={objective}>
              <Markdown inline>{objective}</Markdown>
            </li>
          ))}
        </ul>
        {topics.length > 0 && (
          <p>
            To refresh something first, go back to{' '}
            {topics.map((topic, index) => (
              <span key={topic.id}>
                {index > 0 && (index === topics.length - 1 ? ' or ' : ', ')}
                <Link to={`/topic/${topic.id}`}>{topic.title}</Link>
              </span>
            ))}
            .
          </p>
        )}
      </div>
    </section>
  )
}

/** Saves a lesson_view event when an open topic's page opens (F3). */
function useLessonView(content: TopicContent | null) {
  const record = useRecordEvent()
  const recorded = useRef(false)
  useEffect(() => {
    // Once per visit, even though React runs effects twice in development.
    if (!content || recorded.current) return
    recorded.current = true
    record({
      type: 'lesson_view',
      topic_id: content.topic.id,
      context: 'learn',
      data: { resource: content.topic.resources[0]?.url ?? null },
    })
  }, [content, record])
}

/** Answers are saved only for a signed-in learner, so say so. */
function SignInToSave() {
  const auth = useAuth()
  if (auth.status !== 'signed-out') return null
  return (
    <p className="rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-100">
      You're not signed in, so your answers on this page won't be saved.{' '}
      <Link to="/sign-in" className="underline">
        Sign in
      </Link>
    </p>
  )
}

/** "Nov 6", as the page writes a date. */
function shortDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

function TopicHeader({
  topic,
  state,
  progress,
}: {
  topic: Topic
  /** Null until a signed-in learner's progress is known. */
  state: TopicState | null
  progress: ProgressState
}) {
  const place = placeOf(topic.id)
  const prerequisites = topic.prerequisites
    .map((id) => getTopic(id))
    .filter((found) => found !== undefined)
  const learnedAt =
    progress.status === 'ready'
      ? progress.progress.get(topic.id)?.learnedAt
      : null

  return (
    <header className="space-y-2">
      {place && (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          {/* The track's name matters once there's more than one. */}
          {tracks().length > 1 && `${place.track.title} · `}
          {place.role === 'capstone'
            ? `Capstone, after module ${place.number}: `
            : `Module ${place.number}: `}
          {place.module.title}
        </p>
      )}
      <h1 className="text-3xl font-bold">{topic.title}</h1>
      {state && (
        <p className="text-sm font-medium" data-testid="topic-state">
          {/* An icon and a word, never color alone (F9). */}
          <span aria-hidden="true">{STATE_LABELS[state].icon} </span>
          {STATE_LABELS[state].label}
          {learnedAt && ` on ${shortDate(learnedAt)}`}
        </p>
      )}
      {topic.status === 'draft' && (
        <p className="inline-block rounded bg-amber-100 px-2 py-0.5 text-sm font-medium text-amber-900 dark:bg-amber-900 dark:text-amber-100">
          Draft: only shown on the dev server
        </p>
      )}
      <p className="text-lg text-slate-600 dark:text-slate-400">
        {topic.summary}
      </p>
      <p className="text-sm text-slate-500 dark:text-slate-400">
        About {topic.estimated_minutes} minutes for the whole{' '}
        {topic.kind === 'checkpoint' ? 'checkpoint' : 'topic'}
        {prerequisites.length > 0 && (
          <>
            {' · Builds on '}
            {prerequisites.map((prerequisite, index) => (
              <span key={prerequisite.id}>
                {index > 0 && ', '}
                <Link to={`/topic/${prerequisite.id}`} className="underline">
                  {prerequisite.title}
                </Link>
              </span>
            ))}
          </>
        )}
      </p>
    </header>
  )
}

function SectionHeading({ id, children }: { id: string; children: string }) {
  return (
    // Focusable, so "Prove it now" can move focus to the checks.
    <h2 id={id} tabIndex={-1} className="text-2xl font-bold">
      {children}
    </h2>
  )
}

/** The lesson: what you'll be able to do, then intro, resource and recap. */
function Learn({ content }: { content: TopicContent }) {
  const { topic, Lesson } = content
  // The first resource is the main one, placed in the lesson; the rest are
  // listed after it (content/README.md).
  const moreResources = topic.resources.slice(1)

  return (
    <section aria-labelledby="learn" className="space-y-4">
      <SectionHeading id="learn">Learn</SectionHeading>
      <div className={PROSE}>
        <p className="font-medium">By the end of this topic, you can:</p>
        <ul>
          {topic.objectives.map((objective) => (
            <li key={objective}>
              <Markdown inline>{objective}</Markdown>
            </li>
          ))}
        </ul>
      </div>
      {Lesson ? (
        <LessonView Lesson={Lesson} resources={topic.resources} />
      ) : (
        <p>The lesson for this topic hasn't been written yet.</p>
      )}
      <ReportProblem
        about={{ topicId: topic.id, itemId: 'lesson', itemRev: topic.rev }}
      />
      {moreResources.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-semibold">More resources</h3>
          <ul className="list-disc space-y-1 pl-6">
            {moreResources.map((resource) => (
              <li key={resource.url}>
                <a
                  href={resource.url}
                  target="_blank"
                  rel="noreferrer"
                  className="underline"
                >
                  {resource.title}
                </a>{' '}
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  ({resource.type}; license: {resource.license})
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}

/** The practice ladder, in order: each step asks a little more (F5). */
function Practice({
  content,
  interleaved,
}: {
  content: TopicContent
  interleaved: Interleaved | null
}) {
  const own = content.topic.practice.map((itemId) => ({ itemId, content }))
  if (own.length === 0) return null
  // The earlier topic's question goes after this topic's own recall
  // questions, before the exercises (F5).
  const lastRecall = own.findLastIndex(({ itemId }) => itemId in content.recall)
  const items = interleaved
    ? own.toSpliced(lastRecall + 1, 0, interleaved)
    : own
  return (
    <section aria-labelledby="practice" className="space-y-4">
      <SectionHeading id="practice">Practice</SectionHeading>
      <p className="text-slate-600 dark:text-slate-400">
        Work through these in order. Each one asks a little more of you.
        {interleaved &&
          ' One question is from an earlier topic, to keep it fresh.'}
      </p>
      {items.map((item, index) => (
        <PracticeItem
          key={`${item.content.topic.id}/${item.itemId}`}
          itemId={item.itemId}
          content={item.content}
          context="practice"
          position={
            item.content === content
              ? `Practice ${index + 1} of ${items.length}`
              : `Practice ${index + 1} of ${items.length} · from ${item.content.topic.title}`
          }
        />
      ))}
    </section>
  )
}

const TOPIC_PROOF_INTRO =
  'Three checks show you can use this on your own: build something from a blank editor, fix broken code, and explain the idea in your own words. No hints here. Passing all three marks the topic as learned.'

/** The three proof checks: build, debug and explain (F7). */
function ProveIt({
  content,
  intro = TOPIC_PROOF_INTRO,
  onBuildCheck,
  afterBuild,
  progress,
}: {
  content: TopicContent
  intro?: string
  /** Called after each Check of the build, with whether it passed. */
  onBuildCheck?: (passed: boolean) => void
  /** Shown right after the build. */
  afterBuild?: ReactNode
  /** The learner's progress here, which the page loads once. */
  progress: ProgressState
}) {
  const { build, debug, explain } = content.topic.prove
  if (!build && !debug && !explain) return null
  return (
    <section aria-labelledby="prove-it" className="space-y-4">
      <SectionHeading id="prove-it">Prove it</SectionHeading>
      <p className="text-slate-600 dark:text-slate-400">{intro}</p>
      <ProofProgress topic={content.topic} state={progress} />
      {build && (
        <PracticeItem
          itemId={build}
          content={content}
          context="prove"
          onCheck={onBuildCheck}
        />
      )}
      {afterBuild}
      {debug && (
        <PracticeItem itemId={debug} content={content} context="prove" />
      )}
      {explain && <ExplainCheck topic={content.topic} explain={explain} />}
    </section>
  )
}

const PROOF_NAMES: Record<Proof, string> = {
  build: 'Build',
  debug: 'Debug',
  explain: 'Explain',
}

/**
 * Which of the three proof checks the signed-in learner has passed, and
 * when. A check passed on this page shows straight away.
 */
function ProofProgress({
  topic,
  state,
}: {
  topic: Topic
  state: ProgressState
}) {
  const labelId = useId()

  if (state.status === 'failed') {
    return (
      <p className="flex flex-wrap items-center gap-2 text-sm">
        Your progress here couldn't load.
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
  if (state.status !== 'ready') return null
  const passed = state.progress.get(topic.id)?.passed ?? {}

  return (
    <div className="text-sm">
      <p id={labelId} className="font-medium">
        Your proof so far:
      </p>
      <ul aria-labelledby={labelId} className="space-y-0.5">
        {PROOFS.map((proof) => {
          const when = passed[proof]
          return (
            <li key={proof}>
              {/* An icon and words, never color alone. */}
              <span aria-hidden="true">{when ? '✓ ' : '○ '}</span>
              {PROOF_NAMES[proof]}:{' '}
              {when ? `passed on ${shortDate(when)}` : 'not passed yet'}
            </li>
          )
        })}
      </ul>
    </div>
  )
}

function UnknownTopic() {
  return (
    <section>
      <h1 className="text-2xl font-bold">Topic not found</h1>
      <p className="mt-2 text-slate-600 dark:text-slate-400">
        There's no topic at this address.{' '}
        <Link to="/map" className="underline">
          See every topic on the map
        </Link>
      </p>
    </section>
  )
}
