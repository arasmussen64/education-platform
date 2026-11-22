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
import { Link, useLoaderData, useSearchParams } from 'react-router'
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
import {
  getTopic,
  getTrack,
  isOpen,
  placeOf,
  tracks,
} from '../content/content.ts'
import {
  aboutTime,
  foundationLink,
  foundationsAnchor,
  foundationsListing,
  type ModuleFoundations,
  prerequisitesInOrder,
  trackFoundations,
} from '../content/foundations.ts'
import { practiceOutsideLesson } from '../content/lessonChecks.ts'
import { playsInPage, readsInPage } from '../content/resources.ts'
import { STAGES } from '../content/stages.ts'
import type {
  Explain,
  Resource,
  Topic,
  TopicContent,
  Track,
} from '../content/types.ts'
import { LessonView } from '../components/LessonView.tsx'
import { Markdown } from '../components/Markdown.tsx'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { ResourceView } from '../components/ResourceView.tsx'
import {
  CARD,
  PRIMARY_BUTTON,
  PROSE,
  SECONDARY_BUTTON,
} from '../components/styles.ts'
import { TopicOutline } from '../components/TopicOutline.tsx'
import { useRecordEvent } from '../events/useEvents.ts'
import { ExplainCheck, ExplainClosed } from '../explain/ExplainCheck.tsx'
import { fetchAttempts, mergeAttempts } from '../followups/history.ts'
import { SavedGuessNote, StoppingHere } from '../nexttime/TopicEnds.tsx'
import { BREAK_ID, PartBreak } from '../parts/PartBreak.tsx'
import { recallPart, rememberPart } from '../parts/partMemory.ts'
import { QuickCheck, QuickCheckOffer } from '../parts/QuickCheck.tsx'
import {
  isOptional,
  quickCheckItems,
  quickCheckTaken,
  shownSkills,
} from '../parts/quickCheck.ts'
import { TopicGoals } from '../parts/TopicGoals.tsx'
import {
  aboutMinutes,
  type LadderItem,
  type LearnPart,
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
  useCurrentPlace,
} from '../place/useCurrentPlace.ts'
import type { Interleaved } from '../practice/interleave.ts'
import { ReportProblem } from '../reports/ReportProblem.tsx'
import { type ItemState, itemKey, itemStates } from '../progress/itemStates.ts'
import {
  formatRatio,
  type Pace,
  paced,
  stretches,
  topicPace,
} from '../progress/pace.ts'
import {
  furtherParts,
  nextUp,
  type Proof,
  PROOFS,
  STATE_LABELS,
  stateOf,
  type TopicProgress,
  type TopicState,
} from '../progress/progress.ts'
import { DifficultyNote } from '../progress/DifficultyParts.tsx'
import { ProofMoment } from '../progress/ProofMoment.tsx'
import { type ProgressState, useProgress } from '../progress/useProgress.ts'
import { bundledTopics } from '../session/sessionPlan.ts'
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
  const sentFor = useSentFor(topic)
  const progress = useTopicProgress(topic, loadAttempts, sentFor)
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

  // The learner's pace, from the topics they've proven (progress/pace.ts).
  // Fixed the first time the progress is known, so proving this topic
  // doesn't move the parts under the learner's feet. In tests that read one
  // topic's history at a time there is too little to measure, so it's null.
  const [pace, setPace] = useState<Pace | null | undefined>(undefined)
  if (pace === undefined && progress.status === 'ready') {
    setPace(topicPace(bundledTopics(), progress.progress, progress.attempts))
  }
  const stretch = stretches(pace ?? null) ? (pace?.ratio ?? 1) : 1

  // The topic in parts, one on screen at a time (ADR-0025), cut by the
  // learner's own pace so a part is about half an hour of their time.
  const parts = useMemo(
    () =>
      content && isTopic
        ? topicParts(content, items, { locked, pace: stretch })
        : [],
    [content, isTopic, items, locked, stretch],
  )
  // "Check what you know" (ADR-0025, amended 2026-11-16): its questions,
  // whether it's been taken, and the practice its right answers made
  // optional, by itemKey, all from the saved answers.
  const quickItems = useMemo(
    () => (content && isTopic ? quickCheckItems(content) : []),
    [content, isTopic],
  )
  const attempts = progress.status === 'ready' ? progress.attempts : null
  const optional = useMemo(() => {
    if (!content || !attempts) return new Set<string>()
    const shown = shownSkills(content, attempts)
    return new Set(
      items
        .filter(
          (item) =>
            item.content === content && isOptional(content, item.itemId, shown),
        )
        .map((item) => itemKey(content.topic.id, item.itemId)),
    )
  }, [attempts, content, items])
  const quickTaken =
    content && attempts ? quickCheckTaken(content, attempts) : false
  // The part the quick check is open on, if it is.
  const [quickOpenOn, setQuickOpenOn] = useState<string | null>(null)
  const done = content
    ? partsDone(parts, content, states, passed, optional)
    : null
  const { currentPart, openPart, goTo, breakAfter, endBreak } = usePartChoice(
    topic.id,
    content,
    parts,
    done,
    progress.status !== 'loading',
  )

  // Moving to another part puts the quick check away.
  if (quickOpenOn !== null && currentPart?.id !== quickOpenOn) {
    setQuickOpenOn(null)
  }

  const article = useRef<HTMLElement>(null)
  const { current, lessonParts } = useCurrentPlace(
    topic.id,
    article,
    `${progress.status} ${locked} ${currentPart?.id}`,
  )
  // Read once, before this visit starts remembering places of its own.
  const [resume] = useState(() => recallPlace(topic.id))
  const showOutline = Boolean(content) && isTopic
  // When all three proofs first passed (ADR-0002), which ticks the goals.
  const learnedAt =
    progress.status === 'ready'
      ? (progress.progress.get(topic.id)?.learnedAt ?? null)
      : null
  // Whether the topic was already proven when the page first knew: only a
  // proof finished during this visit gets its moment (ADR-0030).
  const [learnedAtLoad, setLearnedAtLoad] = useState<string | null | undefined>(
    undefined,
  )
  if (learnedAtLoad === undefined && progress.status === 'ready') {
    setLearnedAtLoad(learnedAt)
  }
  const justProven = learnedAtLoad === null && learnedAt !== null
  // Read the clock once, for "its first review comes in 3 days".
  const [now] = useState(() => new Date().toISOString())
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
        <TopicHeader
          topic={topic}
          state={state}
          progress={progress}
          pace={pace ?? null}
        />
        {sentFor && (
          <SentForNote topic={topic} sentFor={sentFor} progress={progress} />
        )}
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
            optional={optional}
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
        {justProven && progress.status === 'ready' && (
          <ProofMoment
            topic={topic}
            progress={progress.progress}
            attempts={progress.attempts}
            now={now}
          />
        )}
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
            <TopicGoals
              objectives={topic.objectives}
              learnedOn={learnedAt ? shortDate(learnedAt) : null}
              // Unfolded where the lesson starts, and when the topic has just
              // been proven, so the ticks are seen; folded otherwise.
              open={currentPart.id === 'learn' || justProven}
            />
            {locked && <LockedNotice topic={topic} progress={progress} />}
            {state === 'available' && currentPart.kind !== 'prove' && (
              // Moves to the proofs part, with focus on its heading.
              <ProveItNow onChoose={() => openPart('prove')} />
            )}
            {breakAfter && (
              <PartBreak finished={breakAfter} onDismiss={endBreak} />
            )}
            {currentPart.id === 'learn' && !learnedAt && (
              <SavedGuessNote topic={topic} />
            )}
            {currentPart.kind === 'learn' && (
              <Learn content={content} part={currentPart} eyebrow={eyebrow} />
            )}
            {currentPart.id === 'practice-1' &&
              quickItems.length > 0 &&
              progress.status === 'ready' &&
              !quickTaken &&
              !learnedAt &&
              quickOpenOn !== currentPart.id && (
                <QuickCheckOffer
                  count={quickItems.length}
                  onStart={() => {
                    flushSync(() => setQuickOpenOn(currentPart.id))
                    document.getElementById('quick-check')?.focus()
                  }}
                />
              )}
            {currentPart.kind === 'practice' &&
              quickOpenOn !== currentPart.id &&
              progress.status === 'ready' &&
              !learnedAt && (
                <DifficultyNote
                  topicId={topic.id}
                  attempts={progress.attempts}
                  onProve={() => openPart('prove')}
                  onLesson={() => openPart('learn')}
                />
              )}
            {currentPart.kind === 'practice' &&
              (quickOpenOn === currentPart.id ? (
                <QuickCheck
                  content={content}
                  itemIds={quickItems}
                  onDone={() => {
                    setQuickOpenOn(null)
                    openPart(currentPart.id)
                  }}
                />
              ) : (
                <Practice
                  content={content}
                  part={currentPart}
                  total={items.length}
                  states={states}
                  doneAtLoad={doneAtLoad}
                  optional={optional}
                  eyebrow={eyebrow}
                />
              ))}
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
                onNext={(next) =>
                  openPart(
                    next.id,
                    // A break is suggested on moving on from a finished part.
                    // The lesson has no answers, so reaching its end and
                    // going on is finishing it.
                    currentPart.kind === 'learn' || done?.get(currentPart.id)
                      ? currentPart.title
                      : null,
                  )
                }
              />
            )}
            {progress.status === 'ready' && !learnedAt && !locked && (
              <StoppingHere content={content} attempts={progress.attempts} />
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
  // The parts are cut again once the learner's pace is known, so the place
  // a link pointed at may now be in another part: look it up once more.
  const [lookedAgain, setLookedAgain] = useState(false)
  if (!lookedAgain && settled && parts.length > 0) {
    setLookedAgain(true)
    const part =
      initialAnchor && content
        ? partOfAnchor(parts, content, initialAnchor)
        : undefined
    if (part && part.id !== chosen) setChosen(part.id)
  }
  const currentId = chosen ?? resumePart(parts, null, lastViewed)
  const currentPart =
    parts.find((part) => part.id === currentId) ?? parts[0] ?? null

  useEffect(() => {
    if (chosen) rememberPart(topicId, chosen)
  }, [topicId, chosen])

  // The page opened from a link to a place in it: go there, now that its
  // part is on screen.
  const anchorPart = initialAnchor ? chosen : null
  useEffect(() => {
    if (initialAnchor) {
      document.getElementById(initialAnchor)?.scrollIntoView({ block: 'start' })
    }
    // Again if the link's place turned out to be in another part.
  }, [initialAnchor, anchorPart])

  // The part just finished, while a break is suggested after it (PartBreak).
  const [breakAfter, setBreakAfter] = useState<string | null>(null)

  /** Opens the part that holds an element, then scrolls to the element. */
  const goTo = useCallback(
    (anchor: string) => {
      const part = content ? partOfAnchor(parts, content, anchor) : undefined
      if (part) {
        flushSync(() => {
          setChosen(part.id)
          setBreakAfter(null)
        })
      }
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

  /**
   * Opens a part at its top, with keyboard focus on its heading, or on the
   * break suggested before it (`finished`: the title of the part just done).
   */
  const openPart = useCallback(
    (id: string, finished: string | null = null) => {
      const part = parts.find((each) => each.id === id)
      if (!part) return
      flushSync(() => {
        setChosen(part.id)
        setBreakAfter(finished)
      })
      const target = document.getElementById(
        finished ? BREAK_ID : partAnchor(part),
      )
      target?.scrollIntoView({ block: 'start' })
      target?.focus({ preventScroll: true })
      setHashAnchor(partAnchor(part))
    },
    [parts],
  )

  return {
    currentPart,
    openPart,
    goTo,
    breakAfter,
    endBreak: () => setBreakAfter(null),
  }
}

/** Back and on between a topic's parts, below the part on screen. */
function PartNav({
  parts,
  current,
  onOpen,
  onNext,
}: {
  parts: TopicPart[]
  current: TopicPart
  onOpen: (part: TopicPart) => void
  /** Moving on to the next part, which may suggest a break first. */
  onNext: (part: TopicPart) => void
}) {
  const index = parts.indexOf(current)
  const previous = parts[index - 1]
  const next = parts[index + 1]
  return (
    <nav
      aria-label="Parts of this topic"
      className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-6"
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
          onClick={() => onNext(next)}
          // Lime is for moving forward (the Momentum design).
          className={PRIMARY_BUTTON}
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
  const own = practiceOutsideLesson(content).map((itemId) => ({
    itemId,
    content,
  }))
  if (own.length === 0 || !interleaved) return own
  const lastRecall = own.findLastIndex(({ itemId }) => itemId in content.recall)
  return own.toSpliced(lastRecall + 1, 0, interleaved)
}

/**
 * The learner's progress on a topic and on what it builds on, which is what
 * its state depends on. Reads the whole history, as the map and the Today
 * page do: practice in the topics built on this one gives it implicit
 * review credit (ADR-0009, amended 2026-11-16), and a checkpoint's tests
 * can open follow-ups on its skills (ADR-0011), so its state depends on
 * events outside it. With `loadAttempts` (in tests), reads each topic's.
 */
function useTopicProgress(
  topic: Topic,
  loadAttempts?: LoadAttempts,
  sentFor?: SentFor | null,
): ProgressState {
  // Everything it builds on, all the way down, so a Locked topic can say
  // where to start; and the list the learner was sent from, so the page
  // can say what's next on it.
  const topics = useMemo(() => {
    const all = [
      topic,
      ...prerequisitesInOrder([topic.id]),
      ...(sentFor?.listing.topics ?? []),
    ]
    return [...new Map(all.map((each) => [each.id, each])).values()]
  }, [topic, sentFor])
  const load = useCallback(async () => {
    if (!loadAttempts) return fetchAttempts()
    const lists = await Promise.all(topics.map((each) => loadAttempts(each.id)))
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
  // Those may wait on others in turn: how many in all, and where to start.
  const toGo = prerequisitesInOrder([topic.id]).filter(
    (each) => !learned(each.id),
  )
  const start =
    progress.status === 'ready'
      ? nextUp(toGo.filter(isOpen), progress.progress)
      : null
  const deeper = toGo.length > waitingOn.length
  const place = placeOf(topic.id)
  const startPlace = start ? placeOf(start.topic.id) : undefined
  // The list on the map, when this topic's module builds on other tracks.
  const listing = place
    ? trackFoundations(place.track).find(
        (each) => each.module.id === place.module.id,
      )
    : undefined
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
      {deeper && (
        <p>
          Those build on others you haven't learned yet: {toGo.length} topics to
          go before this one, {aboutTime(toGo)}.
        </p>
      )}
      {start && deeper && (
        <p>
          <span className="font-medium">
            {start.state === 'in-progress' ? 'Continue with' : 'Start with'}:
          </span>{' '}
          <Link
            to={
              place && startPlace && startPlace.track.id !== place.track.id
                ? foundationLink(start.topic.id, place.track)
                : `/topic/${start.topic.id}`
            }
            className="underline"
          >
            {start.topic.title}
          </Link>
          {startPlace && (
            <span className="text-sm text-muted">
              {' '}
              ({startPlace.track.title}, Module {startPlace.number})
            </span>
          )}
        </p>
      )}
      {place && listing && listing.topics.length > 0 && (
        <p className="text-sm">
          <Link
            to={`/map/${place.track.id}#${foundationsAnchor(listing.module)}`}
            className="underline"
          >
            See everything Module {place.number} needs from other tracks
          </Link>
          , in order, on the {place.track.title} map.
        </p>
      )}
    </aside>
  )
}

/**
 * A track that sent the learner here from its list of foundations
 * (?for=finance), when this topic is on that list.
 */
type SentFor = { track: Track; listing: ModuleFoundations }

function useSentFor(topic: Topic): SentFor | null {
  const [params] = useSearchParams()
  const trackId = params.get('for')
  return useMemo(() => {
    const track = trackId ? getTrack(trackId) : undefined
    if (!track) return null
    const listing = foundationsListing(track, topic.id)
    return listing ? { track, listing } : null
  }, [trackId, topic.id])
}

/**
 * On a topic another track builds on, reached from that track's list:
 * which list, how far along it the learner is, and the way back. Without
 * it, a learner sent from Finance lands in Python Foundations with no sign
 * of how much of it they came for.
 */
function SentForNote({
  topic,
  sentFor,
  progress,
}: {
  topic: Topic
  sentFor: SentFor
  progress: ProgressState
}) {
  const { track, listing } = sentFor
  const number = track.modules.indexOf(listing.module) + 1
  const list = listing.topics
  const position = list.findIndex((each) => each.id === topic.id) + 1
  const ready = progress.status === 'ready' ? progress.progress : null
  const learned = ready
    ? list.filter((each) => ready.get(each.id)?.learnedAt).length
    : null
  // What's next on the list, once this one is learned.
  const next =
    ready && ready.get(topic.id)?.learnedAt
      ? nextUp(list.filter(isOpen), ready)
      : null
  return (
    <aside
      aria-label={`For ${track.title}`}
      className="mt-4 space-y-1 rounded-lg border-2 border-dashed border-line-strong p-3 text-sm"
    >
      <p>
        <span className="font-medium">For {track.title}:</span> this is{' '}
        {position} of the {list.length} topics its Module {number} builds on
        from other tracks
        {learned !== null && `, and you've learned ${learned} of them`}. You
        don't need the rest of this track for it.
      </p>
      <p className="flex flex-wrap gap-x-4">
        {next && (
          <Link to={foundationLink(next.topic.id, track)} className="underline">
            Next on the list: {next.topic.title}
          </Link>
        )}
        <Link
          to={`/map/${track.id}#${foundationsAnchor(listing.module)}`}
          className="underline"
        >
          Back to the list on the {track.title} map
        </Link>
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
  pace,
}: {
  topic: Topic
  /** Null until a signed-in learner's progress is known. */
  state: TopicState | null
  progress: ProgressState
  /** The learner's pace, which stretches the time shown (pace.ts). */
  pace: Pace | null
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
        <p className="text-sm text-muted">
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
      <p className="text-lg text-muted">{topic.summary}</p>
      <p className="text-sm text-muted">
        About {paced(topic.estimated_minutes, pace)} minutes for the whole{' '}
        {topic.kind === 'checkpoint' ? 'checkpoint' : 'topic'}
        {stretches(pace) &&
          ` at your pace (${formatRatio(pace.ratio)} the estimate of ${topic.estimated_minutes})`}
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
      <p className="text-xs font-semibold tracking-wide text-muted uppercase">
        {eyebrow}
      </p>
      {heading}
    </div>
  )
}

/** A further reading held as a copy: its title, and its text once opened. */
function FoldedReading({
  resource,
  loadText,
}: {
  resource: Resource
  loadText: (() => Promise<string>) | undefined
}) {
  const [opened, setOpened] = useState(false)
  return (
    <details onToggle={(event) => event.currentTarget.open && setOpened(true)}>
      <summary className="cursor-pointer underline">
        Read here: {resource.title}
      </summary>
      {opened && (
        <div className="mt-2">
          <ResourceView resource={resource} loadText={loadText} />
        </div>
      )}
    </details>
  )
}

/**
 * The lesson: the intro, the main resource and the recap. A long lesson
 * comes a part at a time (ADR-0025, amended 2026-11-21): some sections of
 * the intro, with the resource and the recap in the last part.
 */
function Learn({
  content,
  part,
  eyebrow,
}: {
  content: TopicContent
  part: LearnPart
  eyebrow?: string
}) {
  const { topic, Lesson } = content
  // The first resource is the main one, placed in the lesson; the rest are
  // listed after it (content/README.md), where the lesson ends.
  const moreResources = part.tail ? topic.resources.slice(1) : []
  // A video plays here too, like the main one, so nobody has to leave the
  // page to watch it. Readings and pages we can't embed stay links.
  const moreVideos = moreResources.filter(playsInPage)
  // A reading we hold a copy of opens here too (ADR-0031), folded until
  // asked for, so its text is only downloaded by someone who wants it.
  const loaderOf = (resource: Resource) =>
    resource.text && content.readings?.[resource.text.file]
  const moreReadings = moreResources.filter(
    (resource) => readsInPage(resource) && loaderOf(resource),
  )
  const moreLinks = moreResources.filter(
    (resource) => !playsInPage(resource) && !moreReadings.includes(resource),
  )
  const anchor = partAnchor(part)

  return (
    <section aria-labelledby={anchor} className="space-y-4">
      <SectionHeading id={anchor} eyebrow={eyebrow}>
        {part.title}
      </SectionHeading>
      {Lesson ? (
        <LessonView
          Lesson={Lesson}
          content={content}
          sections={part.sections}
          tail={part.tail}
        />
      ) : (
        <p>The lesson for this topic hasn't been written yet.</p>
      )}
      <ReportProblem
        about={{ topicId: topic.id, itemId: 'lesson', itemRev: topic.rev }}
      />
      {moreResources.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-semibold">More resources</h3>
          {moreVideos.map((resource) => (
            <ResourceView key={resource.url} resource={resource} />
          ))}
          {moreReadings.map((resource) => (
            <FoldedReading
              key={resource.url}
              resource={resource}
              loadText={loaderOf(resource)}
            />
          ))}
          {moreLinks.length > 0 && (
            <ul className="list-disc space-y-1 pl-6">
              {moreLinks.map((resource) => (
                <li key={resource.url}>
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noreferrer"
                    className="underline"
                  >
                    {resource.title}
                  </a>{' '}
                  <span className="text-sm text-muted">
                    ({resource.type}; license: {resource.license})
                  </span>
                </li>
              ))}
            </ul>
          )}
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
  optional,
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
  /** Items the quick check made optional, by itemKey. */
  optional: Set<string>
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
      <p className="text-muted">
        Work through these in order. Each one asks a little more of you.
        {interleaved &&
          ' One question is from an earlier topic, to keep it fresh.'}
      </p>
      {items.map((item, offset) => {
        const key = itemKey(item.content.topic.id, item.itemId)
        const number = part.start + offset + 1
        const card = (
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
        // Practice the quick check showed the learner knows: folded and
        // quieter, a click away (ADR-0025, amended 2026-11-16). One done
        // before this visit is folded away anyway. (Not one done during it,
        // so answering it doesn't move the card out of its fold.)
        if (!optional.has(key) || doneAtLoad?.has(key)) return card
        return (
          <details
            key={key}
            className="rounded-lg border border-dashed border-line-strong px-4 py-3"
          >
            <summary className="cursor-pointer text-sm text-muted">
              Practice {number} of {total} · Optional: you seem to know this,
              from your quick check
            </summary>
            <div className="mt-3">{card}</div>
          </details>
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
      <p className="text-muted">{intro}</p>
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
      <h1 className="text-3xl font-bold sm:text-4xl">Topic not found</h1>
      <p className="mt-2 text-muted">
        There's no topic at this address.{' '}
        <Link to="/map" className="underline">
          See every topic on the map
        </Link>
      </p>
    </section>
  )
}
