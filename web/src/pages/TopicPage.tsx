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
import { stepsOpenedEvent } from '../checkpoints/stepsOpened.ts'
import {
  type LoadAttempts,
  ProveOnAFreshVersion,
  SuggestSteps,
  Unstuck,
} from '../checkpoints/Unstuck.tsx'
import { SUGGEST_STEPS_AFTER } from '../checkpoints/versions.ts'
import { getTopic, placeOf, tracks } from '../content/content.ts'
import type { Explain, Topic, TopicContent } from '../content/types.ts'
import { LessonView } from '../components/LessonView.tsx'
import { Markdown } from '../components/Markdown.tsx'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { CARD, PROSE, SECONDARY_BUTTON } from '../components/styles.ts'
import { type LadderItem, TopicOutline } from '../components/TopicOutline.tsx'
import { useRecordEvent } from '../events/useEvents.ts'
import { ExplainCheck, ExplainClosed } from '../explain/ExplainCheck.tsx'
import { fetchAttempts, mergeAttempts } from '../followups/history.ts'
import { recallPlace } from '../place/placeMemory.ts'
import {
  itemPlace,
  PLACE_ATTRIBUTE,
  provePlace,
  START_PLACE,
  useCurrentPlace,
} from '../place/useCurrentPlace.ts'
import type { Interleaved } from '../practice/interleave.ts'
import { ReportProblem } from '../reports/ReportProblem.tsx'
import { type ItemState, itemKey, itemStates } from '../progress/itemStates.ts'
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
  const isTopic = content?.topic.kind === 'topic'

  // The learner's place in a long topic: the practice ladder as the page
  // shows it, where they stand on each item, and which part they're at.
  const items = useMemo(
    () => (content && isTopic ? ladderOf(content, interleaved) : []),
    [content, interleaved, isTopic],
  )
  const states = useMemo(
    () => (progress.status === 'ready' ? itemStates(progress.attempts) : null),
    [progress],
  )
  // Items done before this visit are folded away; one done during it stays
  // open, so an answer doesn't make the question vanish. The set is taken
  // once, the first time the progress is known (setting state during the
  // render is how React keeps a value from an earlier render).
  const [doneAtLoad, setDoneAtLoad] = useState<Set<string> | null>(null)
  if (doneAtLoad === null && states !== null) {
    setDoneAtLoad(
      new Set(
        [...states].filter(([, state]) => state === 'done').map(([key]) => key),
      ),
    )
  }
  const article = useRef<HTMLElement>(null)
  const { current, lessonParts } = useCurrentPlace(
    topic.id,
    article,
    `${progress.status} ${proveNow} ${locked}`,
  )
  // Read once, before this visit starts remembering places of its own.
  const [resume] = useState(() => recallPlace(topic.id))
  const passed =
    progress.status === 'ready'
      ? (progress.progress.get(topic.id)?.passed ?? {})
      : null
  const showOutline = Boolean(content) && isTopic

  return (
    <article
      ref={article}
      className="lg:grid lg:grid-cols-[minmax(0,1fr)_15rem] lg:gap-x-10"
    >
      <div className="mb-8 lg:col-span-2">
        <TopicHeader topic={topic} state={state} progress={progress} />
      </div>
      {content && showOutline && (
        <aside className="mb-8 lg:sticky lg:top-6 lg:col-start-2 lg:row-start-2 lg:mb-0 lg:max-h-[calc(100vh-3rem)] lg:self-start lg:overflow-y-auto">
          <TopicOutline
            content={content}
            items={items}
            states={states}
            passed={passed}
            current={current}
            lessonParts={lessonParts}
            resume={resume}
            sections={{
              learn: !proveNow,
              practice: !locked && !proveNow,
              prove: !locked,
            }}
          />
        </aside>
      )}
      <div
        className={`space-y-10 ${showOutline ? 'lg:col-start-1 lg:row-start-2' : 'lg:col-span-2'}`}
      >
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
        {content && isTopic && (
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
              <Practice
                content={content}
                items={items}
                states={states}
                doneAtLoad={doneAtLoad}
              />
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
      </div>
    </article>
  )
}

/**
 * The practice ladder as the page shows it: the topic's own items, with the
 * earlier topic's question after this topic's own recall questions, before
 * the exercises (F5).
 */
function ladderOf(
  content: TopicContent,
  interleaved: Interleaved | null,
): LadderItem[] {
  const own = content.topic.practice.map((itemId) => ({ itemId, content }))
  if (own.length === 0 || !interleaved) return own
  const lastRecall = own.findLastIndex(({ itemId }) => itemId in content.recall)
  return own.toSpliced(lastRecall + 1, 0, interleaved)
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
  const recordEvent = useRecordEvent()
  const [failedChecks, setFailedChecks] = useState(0)
  const [buildPassed, setBuildPassed] = useState(false)
  const [stepsOpen, setStepsOpen] = useState(false)
  // Whether the steps have been opened at all on this visit.
  const [openedHere, setOpenedHere] = useState(false)
  const stepsHeading = useRef<HTMLHeadingElement>(null)
  const own =
    progress.status === 'ready'
      ? progress.progress.get(content.topic.id)
      : undefined
  // The steps show most of the build's program, so once they've been opened
  // (on this visit or an earlier one), a pass of the build no longer proves
  // it; a fresh version does (ADR-0012, amended 2026-11-11). A build proved
  // already stays proved. Without a fresh version the build still counts,
  // as progress/progress.ts says.
  const freshVersionNeeded =
    unstuck !== undefined &&
    unstuck.versions.length > 0 &&
    (openedHere || own?.stepsOpenedAt !== undefined) &&
    !own?.passed.build
  const suggest =
    unstuck !== undefined &&
    failedChecks >= SUGGEST_STEPS_AFTER &&
    !buildPassed &&
    !stepsOpen &&
    // Already pointing at the steps, for a better reason.
    !freshVersionNeeded

  /**
   * Opens or closes the steps. The first opening on each visit is saved, so
   * progress knows from when the build's own passes stop counting.
   */
  function showSteps(open: boolean) {
    setStepsOpen(open)
    if (open && !openedHere) {
      setOpenedHere(true)
      recordEvent(stepsOpenedEvent(content))
    }
  }

  /** Opens the steps and moves there, keyboard focus and all. */
  function goToSteps() {
    // Show the steps straight away, so the page is long enough to scroll
    // them to the top of the screen.
    flushSync(() => showSteps(true))
    stepsHeading.current?.scrollIntoView({ block: 'start' })
    stepsHeading.current?.focus({ preventScroll: true })
  }

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
        explainWaitsForBuild
        onBuildCheck={(passed) => {
          if (passed) setBuildPassed(true)
          else setFailedChecks((count) => count + 1)
        }}
        beforeBuild={
          freshVersionNeeded && <ProveOnAFreshVersion onGoToSteps={goToSteps} />
        }
        afterBuild={
          <>
            {/* <output> is announced by screen readers when its text changes. */}
            <output className="sr-only">
              {suggest ? 'Stuck on the build? You can try it in steps.' : ''}
            </output>
            {suggest && <SuggestSteps onOpen={goToSteps} />}
          </>
        }
      />
      {unstuck && (
        <Unstuck
          content={content}
          unstuck={unstuck}
          open={stepsOpen}
          onToggle={() => showSteps(!stepsOpen)}
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
      <div
        id={START_PLACE}
        {...{ [PLACE_ATTRIBUTE]: START_PLACE }}
        className={PROSE}
      >
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
  items,
  states,
  doneAtLoad,
}: {
  content: TopicContent
  items: LadderItem[]
  /** Each attempted item's state, by itemKey, once known. */
  states: Map<string, ItemState> | null
  /** The items already done when the page opened, by itemKey, once known. */
  doneAtLoad: Set<string> | null
}) {
  if (items.length === 0) return null
  const interleaved = items.some((item) => item.content !== content)
  return (
    <section aria-labelledby="practice" className="space-y-4">
      <SectionHeading id="practice">Practice</SectionHeading>
      <p className="text-slate-600 dark:text-slate-400">
        Work through these in order. Each one asks a little more of you.
        {interleaved &&
          ' One question is from an earlier topic, to keep it fresh.'}
      </p>
      {items.map((item, index) => {
        const key = itemKey(item.content.topic.id, item.itemId)
        return (
          <PracticeItem
            key={key}
            itemId={item.itemId}
            content={item.content}
            context="practice"
            position={
              item.content === content
                ? `Practice ${index + 1} of ${items.length}`
                : `Practice ${index + 1} of ${items.length} · from ${item.content.topic.title}`
            }
            status={states?.get(key)}
            collapsed={doneAtLoad?.has(key) ?? false}
            placeId={itemPlace(item.content.topic.id, item.itemId)}
          />
        )
      })}
    </section>
  )
}

const TOPIC_PROOF_INTRO =
  'Three checks show you can use this on your own: build something from a blank editor, fix broken code, and explain the idea in your own words. No hints here. Passing all three marks the topic as learned.'

/** The three proof checks: build, debug and explain (F7). */
function ProveIt({
  content,
  intro = TOPIC_PROOF_INTRO,
  explainWaitsForBuild = false,
  onBuildCheck,
  beforeBuild,
  afterBuild,
  progress,
}: {
  content: TopicContent
  intro?: string
  /**
   * On a checkpoint: keep the explain check closed until the build has
   * passed (see ExplainAfterBuild). A regular topic shows all three at once.
   */
  explainWaitsForBuild?: boolean
  /** Called after each Check of the build, with whether it passed. */
  onBuildCheck?: (passed: boolean) => void
  /** Shown right before the build. */
  beforeBuild?: ReactNode
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
      {beforeBuild}
      {build && (
        <PracticeItem
          itemId={build}
          content={content}
          context="prove"
          placeId={provePlace('build')}
          onCheck={onBuildCheck}
        />
      )}
      {afterBuild}
      {debug && (
        <PracticeItem
          itemId={debug}
          content={content}
          context="prove"
          placeId={provePlace('debug')}
        />
      )}
      {explain && (
        <div
          id={provePlace('explain')}
          {...{ [PLACE_ATTRIBUTE]: provePlace('explain') }}
        >
          {explainWaitsForBuild ? (
            <ExplainAfterBuild
              topic={content.topic}
              explain={explain}
              progress={progress}
            />
          ) : (
            <ExplainCheck topic={content.topic} explain={explain} />
          )}
        </div>
      )}
    </section>
  )
}

/**
 * A checkpoint's explain check, which opens only once the build has passed
 * (ADR-0012, amended 2026-11-10). Its prompt often walks through a working
 * program much like the one the build asks for, so showing it any sooner
 * would hand over part of the "blank editor" answer.
 *
 * "Passed" is what the proof list above says: any fresh version, or the main
 * build from before the steps were first opened, on any day (ADR-0012,
 * amended 2026-11-11). A Check passed during this visit counts straight
 * away, because the progress includes it. Until the page knows, the check
 * stays closed and says why.
 */
function ExplainAfterBuild({
  topic,
  explain,
  progress,
}: {
  topic: Topic
  explain: Explain
  progress: ProgressState
}) {
  switch (progress.status) {
    case 'ready': {
      const own = progress.progress.get(topic.id)
      if (own?.passed.build) {
        return <ExplainCheck topic={topic} explain={explain} />
      }
      return (
        <ExplainClosed>
          <p>
            Explain it back opens once your build passes.
            {/* The main build stops counting once the steps are opened. */}
            {own?.stepsOpenedAt &&
              " Since you've opened the steps, that means a fresh version, at the end of them."}
          </p>
        </ExplainClosed>
      )
    }
    case 'loading':
      return (
        <ExplainClosed>
          <p>
            Explain it back opens once your build passes. Checking whether it
            has…
          </p>
        </ExplainClosed>
      )
    case 'failed':
      return (
        <ExplainClosed>
          <p>
            Explain it back opens once your build passes. Your progress here
            couldn't load, so the page can't tell whether it has.
          </p>
          <button
            type="button"
            onClick={progress.retry}
            className={SECONDARY_BUTTON}
          >
            Try again
          </button>
        </ExplainClosed>
      )
    case 'signed-out':
      // Nothing a signed-out visitor does is saved, so the page never
      // learns that their build passed. They couldn't have an explanation
      // checked anyway.
      return (
        <ExplainClosed>
          <p>
            Explain it back opens once your build passes.{' '}
            <Link to="/sign-in" className="underline">
              Sign in
            </Link>{' '}
            first, so the page can save your build and tell when it has.
          </p>
        </ExplainClosed>
      )
  }
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
