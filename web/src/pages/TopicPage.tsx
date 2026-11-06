import { type ReactNode, useEffect, useRef, useState } from 'react'
import { flushSync } from 'react-dom'
import { Link, useLoaderData } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import {
  type LoadAttempts,
  SuggestSteps,
  Unstuck,
} from '../checkpoints/Unstuck.tsx'
import { SUGGEST_STEPS_AFTER } from '../checkpoints/versions.ts'
import { getTopic, moduleFor } from '../content/content.ts'
import type { Explain, Topic, TopicContent } from '../content/types.ts'
import { LessonView } from '../components/LessonView.tsx'
import { Markdown } from '../components/Markdown.tsx'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { CARD, PROSE } from '../components/styles.ts'
import { useRecordEvent } from '../events/useEvents.ts'
import type { topicLoader } from './topicLoader.ts'

// One topic: Learn, Practice and Prove it (v1 spec, F3, F5, F7).
export function TopicPage() {
  const { topic, content } = useLoaderData<typeof topicLoader>()
  if (!topic) return <UnknownTopic />
  // A new key for each topic, so nothing typed on one topic carries over to
  // the next.
  return <TopicView key={topic.id} topic={topic} content={content} />
}

export function TopicView({
  topic,
  content,
  loadAttempts,
}: {
  topic: Topic
  /** Null when the topic isn't open yet. */
  content: TopicContent | null
  /** For checkpoints: reads the learner's history. Tests pass a fake. */
  loadAttempts?: LoadAttempts
}) {
  useLessonView(content)
  return (
    <article className="space-y-10">
      <TopicHeader topic={topic} />
      {content && content.topic.kind === 'checkpoint' && (
        <>
          <SignInToSave />
          <CheckpointView content={content} loadAttempts={loadAttempts} />
        </>
      )}
      {content && content.topic.kind === 'topic' && (
        <>
          <SignInToSave />
          <Learn content={content} />
          <Practice content={content} />
          <ProveIt content={content} />
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
 * A module's checkpoint (F10): what it brings together, the three proof
 * checks, and a way through the build for a learner who's stuck (ADR-0012).
 */
function CheckpointView({
  content,
  loadAttempts,
}: {
  content: TopicContent
  loadAttempts?: LoadAttempts
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

  return (
    <>
      <CheckpointIntro content={content} />
      <ProveIt
        content={content}
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
  const topics = (moduleFor(content.topic.id)?.module.topics ?? [])
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

function TopicHeader({ topic }: { topic: Topic }) {
  const place = moduleFor(topic.id)
  const prerequisites = topic.prerequisites
    .map((id) => getTopic(id))
    .filter((found) => found !== undefined)

  return (
    <header className="space-y-2">
      {place && (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Module {place.number}: {place.module.title}
        </p>
      )}
      <h1 className="text-3xl font-bold">{topic.title}</h1>
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
    <h2 id={id} className="text-2xl font-bold">
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
function Practice({ content }: { content: TopicContent }) {
  const items = content.topic.practice
  if (items.length === 0) return null
  return (
    <section aria-labelledby="practice" className="space-y-4">
      <SectionHeading id="practice">Practice</SectionHeading>
      <p className="text-slate-600 dark:text-slate-400">
        Work through these in order. Each one asks a little more of you.
      </p>
      {items.map((itemId, index) => (
        <PracticeItem
          key={itemId}
          itemId={itemId}
          content={content}
          context="practice"
          position={`Practice ${index + 1} of ${items.length}`}
        />
      ))}
    </section>
  )
}

const TOPIC_PROOF_INTRO =
  "Three checks show you can use this on your own: build something from a blank editor, fix broken code, and explain the idea in your own words. No hints here. Once progress tracking arrives (Milestone B), passing all three marks the topic as learned; for now, they're extra practice."

/** The three proof checks: build, debug and explain (F7). */
function ProveIt({
  content,
  intro = TOPIC_PROOF_INTRO,
  onBuildCheck,
  afterBuild,
}: {
  content: TopicContent
  intro?: string
  /** Called after each Check of the build, with whether it passed. */
  onBuildCheck?: (passed: boolean) => void
  /** Shown right after the build. */
  afterBuild?: ReactNode
}) {
  const { build, debug, explain } = content.topic.prove
  if (!build && !debug && !explain) return null
  return (
    <section aria-labelledby="prove-it" className="space-y-4">
      <SectionHeading id="prove-it">Prove it</SectionHeading>
      <p className="text-slate-600 dark:text-slate-400">{intro}</p>
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
      {explain && <ExplainPrompt explain={explain} />}
    </section>
  )
}

/**
 * The explain-it-back check. AI grading arrives in Milestone B; the rubric
 * and model answer are never shown to the learner (F7).
 */
function ExplainPrompt({ explain }: { explain: Explain }) {
  return (
    <section aria-labelledby="explain" className={CARD}>
      <h3 id="explain" className="text-lg font-semibold">
        Explain it back
      </h3>
      <Markdown>{explain.prompt}</Markdown>
      <p className="text-sm text-slate-600 dark:text-slate-400">
        Soon you'll type your answer here and get feedback on it (Milestone B).
        Until then, explain it out loud or on paper, as if teaching a friend.
      </p>
    </section>
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
