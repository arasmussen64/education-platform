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
import { MoreParts } from '../checkpoints/MoreParts.tsx'
import { stepsOpenedEvent } from '../checkpoints/stepsOpened.ts'
import {
  type LoadAttempts,
  ProveOnAFreshVersion,
  SuggestSteps,
  Unstuck,
} from '../checkpoints/Unstuck.tsx'
import { SUGGEST_STEPS_AFTER } from '../checkpoints/versions.ts'
import { getTopic, placeOf, tracks } from '../content/content.ts'
import { STAGES } from '../content/stages.ts'
import type { Explain, Topic, TopicContent } from '../content/types.ts'
import { LessonView } from '../components/LessonView.tsx'
import { Markdown } from '../components/Markdown.tsx'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { CARD, PROSE, SECONDARY_BUTTON } from '../components/styles.ts'
import { TopicOutline } from '../components/TopicOutline.tsx'
import { useRecordEvent } from '../events/useEvents.ts'
import { ExplainCheck, ExplainClosed } from '../explain/ExplainCheck.tsx'
import { fetchAttempts, mergeAttempts } from '../followups/history.ts'
import { recallPart, rememberPart } from '../parts/partMemory.ts'
import {
  aboutMinutes,
  type LadderItem,
  partAnchor,
  partOfAnchor,
  partsDone,
  resumePart,
  topicParts,
  type TopicPart,
} from '../parts/topicParts.ts'
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
  furtherParts,
  type Proof,
  PROOFS,
  STATE_LABELS,
  stateOf,
  type TopicProgress,
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
  const passed =
    progress.status === 'ready'
      ? (progress.progress.get(topic.id)?.passed ?? {})
      : null

  // The topic in parts, one on screen at a time (ADR-0025).
  const parts = useMemo(
    () => (content && isTopic ? topicParts(content, items, { locked }) : []),
    [content, isTopic, items, locked],
  )
  const done = content ? partsDone(parts, content, states, passed) : null
  const { currentPart, openPart, goTo } = usePartChoice(
    topic.id,
    content,
    parts,
    done,
    progress.status !== 'loading',
  )

  const article = useRef<HTMLElement>(null)
  const { current, lessonParts } = useCurrentPlace(
    topic.id,
    article,
    `${progress.status} ${locked} ${currentPart?.id}`,
  )
  // Read once, before this visit starts remembering places of its own.
  const [resume] = useState(() => recallPlace(topic.id))
  const showOutline = Boolean(content) && isTopic
  const partNumber = currentPart ? parts.indexOf(currentPart) + 1 : 0
  // "Part 2 of 5 · about 30 min", above the part's heading, once there's
  // more than one part.
  const eyebrow =
    currentPart && parts.length > 1
      ? `Part ${partNumber} of ${parts.length} · ${aboutMinutes(currentPart.minutes)}`
      : undefined

  return (
    <article
      ref={article}
      className="lg:grid lg:grid-cols-[minmax(0,1fr)_15rem] lg:gap-x-10"
    >
      <div className="mb-8 lg:col-span-2">
        <TopicHeader topic={topic} state={state} progress={progress} />
      </div>
      {content && showOutline && currentPart && (
        <aside className="mb-8 lg:sticky lg:top-6 lg:col-start-2 lg:row-start-2 lg:mb-0 lg:max-h-[calc(100vh-3rem)] lg:self-start lg:overflow-y-auto">
          <TopicOutline
            content={content}
            parts={parts}
            currentPart={currentPart.id}
            done={done}
            items={items}
            states={states}
            passed={passed}
            current={current}
            lessonParts={lessonParts}
            resume={resume}
            onGoTo={goTo}
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
        {content && isTopic && currentPart && (
          <>
            <SignInToSave />
            {locked && <LockedNotice topic={topic} progress={progress} />}
            {state === 'available' && currentPart.kind !== 'prove' && (
              // Moves to the proofs part, with focus on its heading.
              <ProveItNow onChoose={() => openPart('prove')} />
            )}
            {currentPart.kind === 'learn' && (
              <Learn content={content} eyebrow={eyebrow} />
            )}
            {currentPart.kind === 'practice' && (
              <Practice
                content={content}
                part={currentPart}
                total={items.length}
                states={states}
                doneAtLoad={doneAtLoad}
                eyebrow={eyebrow}
              />
            )}
            {currentPart.kind === 'prove' && (
              <ProveIt
                content={content}
                progress={progress}
                eyebrow={eyebrow}
              />
            )}
            {parts.length > 1 && (
              <PartNav
                parts={parts}
                current={currentPart}
                onOpen={(part) => openPart(part.id)}
              />
            )}
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

/** The id in the address after "#", if any. */
function hashAnchor(): string | null {
  const hash = window.location.hash.slice(1)
  if (!hash) return null
  try {
    return decodeURIComponent(hash)
  } catch {
    return hash
  }
}

/** Puts an id in the address after "#", without a new history entry. */
function setHashAnchor(anchor: string) {
  // The router's own state is kept, so Back works as before.
  window.history.replaceState(window.history.state, '', `#${anchor}`)
}

/**
 * Which part of the topic is on screen (ADR-0025), and how to move. The page
 * opens at the part a link's "#…" points into; failing that, once the
 * progress is known, at the part last viewed on this device if it isn't
 * done, or else at the first part that isn't done. That choice is made once:
 * finishing a part never moves the learner on by itself. Any part can be
 * opened at any time; parts never gate anything.
 */
function usePartChoice(
  topicId: string,
  content: TopicContent | null,
  parts: TopicPart[],
  done: Map<string, boolean> | null,
  settled: boolean,
) {
  const [initialAnchor] = useState(hashAnchor)
  const [chosen, setChosen] = useState<string | null>(() => {
    if (!initialAnchor || !content || parts.length === 0) return null
    return partOfAnchor(parts, content, initialAnchor)?.id ?? null
  })
  // Read once, before this visit remembers parts of its own.
  const [lastViewed] = useState(() => recallPart(topicId))
  // Setting state during the render, as for doneAtLoad above.
  if (chosen === null && settled && parts.length > 0) {
    setChosen(resumePart(parts, done, lastViewed))
  }
  const currentId = chosen ?? resumePart(parts, null, lastViewed)
  const currentPart =
    parts.find((part) => part.id === currentId) ?? parts[0] ?? null

  useEffect(() => {
    if (chosen) rememberPart(topicId, chosen)
  }, [topicId, chosen])

  // The page opened from a link to a place in it: go there, now that its
  // part is on screen.
  useEffect(() => {
    if (initialAnchor) {
      document.getElementById(initialAnchor)?.scrollIntoView({ block: 'start' })
    }
  }, [initialAnchor])

  /** Opens the part that holds an element, then scrolls to the element. */
  const goTo = useCallback(
    (anchor: string) => {
      const part = content ? partOfAnchor(parts, content, anchor) : undefined
      if (part) flushSync(() => setChosen(part.id))
      document.getElementById(anchor)?.scrollIntoView({ block: 'start' })
      setHashAnchor(anchor)
    },
    [content, parts],
  )

  // A link in the lesson's own text, or an address changed by hand.
  useEffect(() => {
    function follow() {
      const anchor = hashAnchor()
      if (anchor) goTo(anchor)
    }
    window.addEventListener('hashchange', follow)
    return () => window.removeEventListener('hashchange', follow)
  }, [goTo])

  /** Opens a part at its top, with keyboard focus on its heading. */
  const openPart = useCallback(
    (id: string) => {
      const part = parts.find((each) => each.id === id)
      if (!part) return
      flushSync(() => setChosen(part.id))
      const heading = document.getElementById(partAnchor(part))
      heading?.scrollIntoView({ block: 'start' })
      heading?.focus({ preventScroll: true })
      setHashAnchor(partAnchor(part))
    },
    [parts],
  )

  return { currentPart, openPart, goTo }
}

/** Back and on between a topic's parts, below the part on screen. */
function PartNav({
  parts,
  current,
  onOpen,
}: {
  parts: TopicPart[]
  current: TopicPart
  onOpen: (part: TopicPart) => void
}) {
  const index = parts.indexOf(current)
  const previous = parts[index - 1]
  const next = parts[index + 1]
  return (
    <nav
      aria-label="Parts of this topic"
      className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-6 dark:border-slate-800"
    >
      {previous ? (
        <button
          type="button"
          onClick={() => onOpen(previous)}
          className={SECONDARY_BUTTON}
        >
          <span aria-hidden="true">← </span>
          Part {index}: {previous.title}
        </button>
      ) : (
        <span />
      )}
      {next && (
        <button
          type="button"
          onClick={() => onOpen(next)}
          // Lime is for moving forward (the Momentum design).
          className="rounded-md bg-lime-600 px-4 py-2 text-sm font-semibold text-white hover:bg-lime-700 dark:bg-lime-500 dark:text-slate-950 dark:hover:bg-lime-400"
        >
          Next: Part {index + 2}, {next.title}
          <span aria-hidden="true"> →</span>
        </button>
      )}
    </nav>
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
  // With further parts, the build is part 1 of several, and the notes about
  // the steps say so (ADR-0012, amended 2026-11-11).
  const numbered = furtherParts(content.topic).length > 0
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
        intro={checkpointProofIntro(content.topic)}
        explainWaitsForBuild
        onBuildCheck={(passed) => {
          if (passed) setBuildPassed(true)
          else setFailedChecks((count) => count + 1)
        }}
        beforeBuild={
          freshVersionNeeded && (
            <ProveOnAFreshVersion onGoToSteps={goToSteps} numbered={numbered} />
          )
        }
        afterBuild={
          <>
            {/* <output> is announced by screen readers when its text changes. */}
            <output className="sr-only">
              {suggest
                ? `Stuck on ${numbered ? 'part 1' : 'the build'}? You can try it in steps.`
                : ''}
            </output>
            {suggest && <SuggestSteps onOpen={goToSteps} numbered={numbered} />}
          </>
        }
        afterDebug={<MoreParts content={content} loadAttempts={loadAttempts} />}
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

const NUMBER_WORDS = [
  'zero',
  'one',
  'two',
  'three',
  'four',
  'five',
  'six',
  'seven',
  'eight',
  'nine',
]

/** "three" for 3, as a sentence writes a small number; digits past nine. */
function inWords(count: number): string {
  return NUMBER_WORDS[count] ?? String(count)
}

/**
 * What a checkpoint's proof checks are, above them. One with further parts
 * (ADR-0012, amended 2026-11-11) counts them all, since its build and debug
 * are parts 1 and 2 of several.
 */
function checkpointProofIntro(topic: Topic): string {
  const further = furtherParts(topic).length
  if (further === 0) {
    return "Three checks show you can use everything in this module on your own: build a program from a blank editor, fix code with several bugs, and explain how it works. No hints here. If you get stuck on the build, there's a way through it below."
  }
  const parts = 2 + further
  return `These ${inWords(parts + 1)} checks show you can use everything in this module on your own: ${inWords(parts)} parts to build or fix, and an explanation of how it all works. No hints here. If you get stuck on part 1, there's a way through it below.`
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

function SectionHeading({
  id,
  eyebrow,
  children,
}: {
  id: string
  /** A line above the heading: "Part 2 of 5 · about 30 min" (ADR-0025). */
  eyebrow?: string
  children: string
}) {
  const heading = (
    // Focusable, so "Prove it now" and the part buttons can move focus to it.
    <h2 id={id} tabIndex={-1} className="text-2xl font-bold">
      {children}
    </h2>
  )
  if (!eyebrow) return heading
  return (
    <div>
      <p className="text-xs font-semibold tracking-wide text-slate-500 uppercase dark:text-slate-400">
        {eyebrow}
      </p>
      {heading}
    </div>
  )
}

/** The lesson: what you'll be able to do, then intro, resource and recap. */
function Learn({
  content,
  eyebrow,
}: {
  content: TopicContent
  eyebrow?: string
}) {
  const { topic, Lesson } = content
  // The first resource is the main one, placed in the lesson; the rest are
  // listed after it (content/README.md).
  const moreResources = topic.resources.slice(1)

  return (
    <section aria-labelledby="learn" className="space-y-4">
      <SectionHeading id="learn" eyebrow={eyebrow}>
        Learn
      </SectionHeading>
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

/**
 * One part of the practice ladder, in order: each step asks a little more
 * (F5). Items are numbered across the whole ladder, as the outline numbers
 * them.
 */
function Practice({
  content,
  part,
  total,
  states,
  doneAtLoad,
  eyebrow,
}: {
  content: TopicContent
  part: Extract<TopicPart, { kind: 'practice' }>
  /** How many items the whole ladder has. */
  total: number
  /** Each attempted item's state, by itemKey, once known. */
  states: Map<string, ItemState> | null
  /** The items already done when the page opened, by itemKey, once known. */
  doneAtLoad: Set<string> | null
  eyebrow?: string
}) {
  const { items } = part
  if (items.length === 0) return null
  const interleaved = items.some((item) => item.content !== content)
  const anchor = partAnchor(part)
  return (
    <section aria-labelledby={anchor} className="space-y-4">
      <SectionHeading id={anchor} eyebrow={eyebrow}>
        {part.title}
      </SectionHeading>
      <p className="text-slate-600 dark:text-slate-400">
        Work through these in order. Each one asks a little more of you.
        {interleaved &&
          ' One question is from an earlier topic, to keep it fresh.'}
      </p>
      {items.map((item, offset) => {
        const key = itemKey(item.content.topic.id, item.itemId)
        const number = part.start + offset + 1
        return (
          <PracticeItem
            key={key}
            itemId={item.itemId}
            content={item.content}
            context="practice"
            position={
              item.content === content
                ? `Practice ${number} of ${total}`
                : `Practice ${number} of ${total} · from ${item.content.topic.title}`
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
  afterDebug,
  progress,
  eyebrow,
}: {
  content: TopicContent
  /** A line above the heading: "Part 5 of 5 · about 40 min" (ADR-0025). */
  eyebrow?: string
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
  /** Shown right after the debug: a checkpoint's further parts. */
  afterDebug?: ReactNode
  /** The learner's progress here, which the page loads once. */
  progress: ProgressState
}) {
  const { build, debug, explain } = content.topic.prove
  if (!build && !debug && !explain) return null
  // A checkpoint with further parts numbers them all, from its build as
  // part 1 and its debug as part 2 (ADR-0012, amended 2026-11-11).
  const numbered = furtherParts(content.topic).length > 0
  return (
    <section aria-labelledby="prove-it" className="space-y-4">
      <SectionHeading id="prove-it" eyebrow={eyebrow}>
        Prove it
      </SectionHeading>
      <p className="text-slate-600 dark:text-slate-400">{intro}</p>
      <ProofProgress content={content} state={progress} />
      {beforeBuild}
      {build && (
        <PracticeItem
          itemId={build}
          content={content}
          context="prove"
          position={numbered ? 'Part 1' : undefined}
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
          position={numbered ? 'Part 2' : undefined}
          placeId={provePlace('debug')}
        />
      )}
      {afterDebug}
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
 * stays closed and says why. A checkpoint's further parts don't hold it
 * back: it waits for the build, part 1, alone.
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
  // With further parts there's more than one build, so say which.
  const yourBuild =
    furtherParts(topic).length > 0 ? 'your part 1 build' : 'your build'
  switch (progress.status) {
    case 'ready': {
      const own = progress.progress.get(topic.id)
      if (own?.passed.build) {
        return <ExplainCheck topic={topic} explain={explain} />
      }
      return (
        <ExplainClosed>
          <p>
            Explain it back opens once {yourBuild} passes.
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
            Explain it back opens once {yourBuild} passes. Checking whether it
            has…
          </p>
        </ExplainClosed>
      )
    case 'failed':
      return (
        <ExplainClosed>
          <p>
            Explain it back opens once {yourBuild} passes. Your progress here
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
            Explain it back opens once {yourBuild} passes.{' '}
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

/** One line of "Your proof so far": a proof check, and when it first passed. */
type ProofRow = { key: string; name: string; passedAt?: string }

/**
 * The proof checks to list, in page order. On a checkpoint with further
 * parts, every part is listed by its number, its build and debug included,
 * as the page numbers them (ADR-0012, amended 2026-11-11).
 */
function proofRows(
  content: TopicContent,
  own: TopicProgress | undefined,
): ProofRow[] {
  const passed = own?.passed ?? {}
  const row = (proof: Proof, name = PROOF_NAMES[proof]): ProofRow => ({
    key: proof,
    name,
    passedAt: passed[proof],
  })
  const parts = furtherParts(content.topic)
  if (parts.length === 0) return PROOFS.map((proof) => row(proof))

  /** "Part 3, build": its number, and what kind of exercise it is. */
  const partName = (number: number, itemId: string) => {
    const stage = content.exercises[itemId]?.stage
    return stage
      ? `Part ${number}, ${STAGES[stage].label.toLowerCase()}`
      : `Part ${number}`
  }
  return [
    row('build', 'Part 1, build'),
    row('debug', 'Part 2, debug'),
    ...parts.map((part) => ({
      key: `part-${part.id}`,
      name: partName(part.number, part.id),
      passedAt: own?.partsPassed?.[part.id],
    })),
    row('explain'),
  ]
}

/**
 * Which proof checks the signed-in learner has passed, and when. A check
 * passed on this page shows straight away.
 */
function ProofProgress({
  content,
  state,
}: {
  content: TopicContent
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
  const rows = proofRows(content, state.progress.get(content.topic.id))

  return (
    <div className="text-sm">
      <p id={labelId} className="font-medium">
        Your proof so far:
      </p>
      <ul aria-labelledby={labelId} className="space-y-0.5">
        {rows.map(({ key, name, passedAt }) => (
          <li key={key}>
            {/* An icon and words, never color alone. */}
            <span aria-hidden="true">{passedAt ? '✓ ' : '○ '}</span>
            {name}:{' '}
            {passedAt ? `passed on ${shortDate(passedAt)}` : 'not passed yet'}
          </li>
        ))}
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
