import { useEffect, useId, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import { McqQuestion } from '../components/McqQuestion.tsx'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { BUTTON, CARD, SECONDARY_BUTTON } from '../components/styles.ts'
import { useAttemptTimer } from '../components/useAttemptTimer.ts'
import {
  diagnostics,
  getTopic,
  isOpen,
  loadTopicContent,
  topicIdsOf,
  tracks,
} from '../content/content.ts'
import {
  findFoundations,
  foundationLink,
  foundationsMapLink,
  foundationsTitle,
  type FoundationsScope,
} from '../content/foundations.ts'
import type {
  Diagnostic,
  DiagnosticLevel,
  McqItem,
  Topic,
  TopicContent,
  Track,
} from '../content/types.ts'
import { useRecordEvent } from '../events/useEvents.ts'
import {
  describeDiagnosticRecord,
  describeListRecord,
  describeTrackRecord,
} from '../placement/describe.ts'
import {
  type PlacementList,
  type PlacementRecord,
  subjectOfDiagnostic,
  subjectOfFoundations,
} from '../placement/history.ts'
import {
  afterProbe,
  chooseProbeItems,
  nextProbe,
  type Placement,
  type ProbeResult,
  probesNeeded,
  startWalk,
  summarize,
  verdict,
} from '../placement/placement.ts'
import { usePlacements } from '../placement/usePlacements.ts'
import { type ProgressState, useProgress } from '../progress/useProgress.ts'

// The placement test (ADR-0021): finds where a learner's knowledge runs out
// in a track, or in the math ladder, by asking a few questions from the
// middle and halving what's left. It marks nothing learned: what it finds
// becomes a short list of topics to prove with "Prove it now", in order, and
// a place to start.
//
// /placement?for=<track id>&module=<module id> is the test for one list
// only: what that module needs from other tracks (the amendment of
// 2026-11-21). It walks that list's topics and nothing else.
export function PlacementPage() {
  const auth = useAuth()
  const [params] = useSearchParams()
  const forTrack = params.get('for')
  const forModule = params.get('module')
  const asked = forTrack !== null && forModule !== null
  const scope = asked ? findFoundations(forTrack, forModule) : undefined
  return (
    <section className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-bold">Placement test</h1>
        <p className="text-slate-600 dark:text-slate-400">
          Already know some of this? The placement test finds where your
          knowledge runs out, so you can start there. It picks a topic in the
          middle of a track and asks a few of its questions; each answer rules
          out half of what's left, so a whole track takes about five topics'
          worth of questions, ten minutes or so. It doesn't say which answers
          were right until the end, and it ticks nothing off: the topics you
          seem to know become a short list to prove, in order, with "Prove it
          now". Every question has an "I don't know this" answer: use it rather
          than guess, because a lucky guess would place you past what you know
          and cost you time later.
        </p>
      </header>
      {asked && !scope && (
        <p>
          That link names a list this page can't find, so here is every
          placement test instead.
        </p>
      )}
      {auth.status === 'signed-in' && <Subjects scope={scope} />}
      {auth.status === 'signed-out' && (
        <p>
          <Link to="/sign-in" className="underline">
            Sign in
          </Link>{' '}
          to take the placement test.
        </p>
      )}
    </section>
  )
}

type Subject =
  | { kind: 'track'; track: Track }
  | { kind: 'foundations'; scope: FoundationsScope }
  | { kind: 'diagnostic'; diagnostic: Diagnostic }

/** Whether a placement can probe a topic: one a learner can open, no checkpoint. */
function canProbe(topic: Topic | undefined): topic is Topic {
  return topic !== undefined && topic.kind === 'topic' && isOpen(topic)
}

/** A track's topics a learner can open, in order: no checkpoints. */
function openTopicsOf(track: Track): Topic[] {
  return topicIdsOf(track)
    .map((id) => getTopic(id))
    .filter(canProbe)
}

/** The foundations lists that have a result, newest result first. */
function listsPlacedIn(
  latest: Map<string, PlacementRecord>,
): FoundationsScope[] {
  return [...latest.values()]
    .filter((record) => record.list !== undefined)
    .sort((a, b) => b.at.localeCompare(a.at))
    .map((record) =>
      record.list
        ? findFoundations(record.list.track, record.list.module)
        : undefined,
    )
    .filter((scope) => scope !== undefined)
}

/**
 * The tracks and diagnostics to place in, each with its last result. With a
 * `scope`, only that one foundations list.
 */
function Subjects({ scope }: { scope?: FoundationsScope }) {
  // The topics bundled with the app, like the Today page: an outline-only
  // track's topics can't be placed in, because they can't be opened.
  const topics = useMemo(
    () =>
      tracks()
        .flatMap(topicIdsOf)
        .map((id) => getTopic(id))
        .filter((topic) => topic !== undefined),
    [],
  )
  const progress = useProgress(topics)
  const placements = usePlacements()
  const [running, setRunning] = useState<Subject | null>(null)

  if (progress.status === 'failed') {
    return (
      <p className="flex flex-wrap items-center gap-2">
        Your progress couldn't load, and the test needs it to skip what you've
        learned.
        <button
          type="button"
          onClick={progress.retry}
          className={SECONDARY_BUTTON}
        >
          Try again
        </button>
      </p>
    )
  }
  if (progress.status !== 'ready' || placements.status === 'loading') {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400">
        Loading your progress…
      </p>
    )
  }
  const learned = (topicId: string) =>
    Boolean(progress.progress.get(topicId)?.learnedAt)
  const latest: Map<string, PlacementRecord> =
    placements.status === 'ready' ? placements.latest : new Map()

  if (running?.kind === 'track') {
    return (
      <TopicsRun
        title={running.track.title}
        subject={running.track.id}
        order={openTopicsOf(running.track).filter(
          (topic) => !learned(topic.id),
        )}
        learned={learned}
        onDone={() => setRunning(null)}
      />
    )
  }
  if (running?.kind === 'foundations') {
    return (
      <TopicsRun
        title={foundationsTitle(running.scope)}
        subject={subjectOfFoundations(running.scope.module.id)}
        scope={running.scope}
        // The list's own order: each topic after what it builds on.
        order={running.scope.topics
          .filter(canProbe)
          .filter((topic) => !learned(topic.id))}
        learned={learned}
        onDone={() => setRunning(null)}
      />
    )
  }
  if (running?.kind === 'diagnostic') {
    return (
      <DiagnosticRun
        diagnostic={running.diagnostic}
        onDone={() => setRunning(null)}
      />
    )
  }

  const listCard = (list: FoundationsScope) => (
    <ListCard
      key={list.module.id}
      scope={list}
      record={latest.get(subjectOfFoundations(list.module.id))}
      learned={learned}
      onStart={() => setRunning({ kind: 'foundations', scope: list })}
    />
  )
  if (scope) {
    return (
      <div className="space-y-4">
        {listCard(scope)}
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Or place yourself in a whole track, or in the math ladder:{' '}
          <Link to="/placement" className="underline">
            every placement test
          </Link>
          .
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {tracks().map((track) => {
        const open = openTopicsOf(track)
        const left = open.filter((topic) => !learned(topic.id))
        const record = latest.get(track.id)
        const headingId = `place-${track.id}`
        return (
          <section key={track.id} aria-labelledby={headingId} className={CARD}>
            <h2 id={headingId} className="text-lg font-semibold">
              {track.title}
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {open.length === 0
                ? 'Nothing written here yet.'
                : `${open.length} topics written so far, ${open.length - left.length} of them learned. About ${probesNeeded(left.length)} topics' worth of questions.`}
            </p>
            {record && <p>{describeTrackRecord(record, learned)}</p>}
            {open.length > 0 && left.length === 0 ? (
              <p>
                You've learned everything written here so far: nothing to place.
              </p>
            ) : (
              left.length > 0 && (
                <button
                  type="button"
                  onClick={() => setRunning({ kind: 'track', track })}
                  className={BUTTON}
                >
                  {record ? 'Take it again' : 'Start'}
                </button>
              )
            )}
          </section>
        )
      })}
      {
        // A list's test starts from the list on the map. Once taken, its
        // result is kept here too, beside the others.
        listsPlacedIn(latest).map(listCard)
      }
      {diagnostics().map((diagnostic) => {
        const record = latest.get(subjectOfDiagnostic(diagnostic.id))
        const headingId = `place-diagnostic-${diagnostic.id}`
        return (
          <section
            key={diagnostic.id}
            aria-labelledby={headingId}
            className={CARD}
          >
            <h2 id={headingId} className="text-lg font-semibold">
              {diagnostic.title}
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {diagnostic.summary} {diagnostic.levels.length} levels, about{' '}
              {probesNeeded(diagnostic.levels.length)} levels' worth of
              questions.
            </p>
            {record && <p>{describeDiagnosticRecord(record, diagnostic)}</p>}
            <button
              type="button"
              onClick={() => setRunning({ kind: 'diagnostic', diagnostic })}
              className={BUTTON}
            >
              {record ? 'Take it again' : 'Start'}
            </button>
          </section>
        )
      })}
    </div>
  )
}

/** One foundations list to place in, with its last result. */
function ListCard({
  scope,
  record,
  learned,
  onStart,
}: {
  scope: FoundationsScope
  record: PlacementRecord | undefined
  learned: (topicId: string) => boolean
  onStart: () => void
}) {
  const headingId = `place-foundations-${scope.module.id}`
  const open = scope.topics.filter(canProbe)
  const left = open.filter((topic) => !learned(topic.id))
  return (
    <section aria-labelledby={headingId} className={CARD}>
      <h2 id={headingId} className="text-lg font-semibold">
        {foundationsTitle(scope)}
      </h2>
      <p className="text-sm text-slate-600 dark:text-slate-400">
        {open.length === 0
          ? 'Nothing on this list is written yet.'
          : `Only the ${open.length} ${open.length === 1 ? 'topic' : 'topics'} from other tracks that Module ${scope.number} builds on, in the order to learn them; ${open.length - left.length} of them learned. About ${probesNeeded(left.length)} topics' worth of questions.`}{' '}
        <Link
          to={foundationsMapLink(scope.track, scope.module)}
          className="underline"
        >
          See the list on the map
        </Link>
        .
      </p>
      {record && <p>{describeListRecord(record, learned)}</p>}
      {open.length > 0 && left.length === 0 ? (
        <p>You've learned everything on this list: nothing to place.</p>
      ) : (
        left.length > 0 && (
          <button type="button" onClick={onStart} className={BUTTON}>
            {record ? 'Take it again' : 'Start'}
          </button>
        )
      )}
    </section>
  )
}

/** A run's progress line: how far the walk has got. */
function Progress({
  checked,
  outOf,
  asked,
  what,
}: {
  checked: number
  outOf: number
  asked: number
  what: string
}) {
  return (
    <p className="text-sm text-slate-500 dark:text-slate-400">
      Checked {checked} of up to {outOf} {what}; {asked}{' '}
      {asked === 1 ? 'question' : 'questions'} so far.
    </p>
  )
}

function StopButton({ onDone }: { onDone: () => void }) {
  return (
    <p className="flex flex-wrap items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
      <button type="button" onClick={onDone} className={SECONDARY_BUTTON}>
        Stop here
      </button>
      Stopping saves no result. You can start again any time.
    </p>
  )
}

// Topics: a track, or one foundations list ------------------------------------

function TopicsRun({
  title,
  subject,
  scope,
  order,
  learned,
  onDone,
}: {
  /** What's being walked, for the headings: a track's title, or a list's. */
  title: string
  /** The placement event's topic_id: a track's id, or the list's subject. */
  subject: string
  /** The foundations list, when the run walks one and not a whole track. */
  scope?: FoundationsScope
  /** The open topics the learner hasn't learned, in the order to walk. */
  order: Topic[]
  learned: (topicId: string) => boolean
  onDone: () => void
}) {
  const record = useRecordEvent()
  const headingId = useId()
  const [run] = useState(() => crypto.randomUUID())
  const [walk, setWalk] = useState(() => startWalk(order.length))
  const [probes, setProbes] = useState<ProbeResult[]>([])
  const [result, setResult] = useState<Placement | null>(null)
  const index = nextProbe(walk)

  function decided(probe: ProbeResult) {
    if (index === null) return
    const nextWalk = afterProbe(walk, index, probe.passed)
    const nextProbes = [...probes, probe]
    setWalk(nextWalk)
    setProbes(nextProbes)
    if (nextProbe(nextWalk) !== null) return
    const placement = summarize(
      order.map((topic) => topic.id),
      nextWalk,
      nextProbes,
    )
    // A list's run says which list, so its result is never read as the
    // whole track's (docs/specs/data-model.md).
    const list: PlacementList | undefined = scope && {
      track: scope.track.id,
      module: scope.module.id,
    }
    record({
      type: 'placement',
      topic_id: subject,
      item_id: 'placement',
      context: 'placement',
      data: {
        run,
        kind: list ? 'foundations' : 'track',
        ...(list ? { list } : {}),
        known: placement.known,
        next: placement.next,
        asked: placement.asked,
        correct: placement.correct,
        probes: placement.probes,
      },
    })
    setResult(placement)
  }

  if (result) {
    return (
      <TopicsResult
        title={title}
        scope={scope}
        result={result}
        learned={learned}
        onDone={onDone}
      />
    )
  }
  const topic = index === null ? undefined : order[index]
  if (!topic) return null
  const asked = probes.reduce((count, probe) => count + probe.asked.length, 0)
  return (
    <section aria-labelledby={headingId} className="space-y-4">
      <h2 id={headingId} className="text-xl font-semibold">
        {title}: placement
      </h2>
      <Progress
        checked={probes.length}
        outOf={probesNeeded(order.length)}
        asked={asked}
        what="topics"
      />
      <TopicProbe
        key={topic.id}
        topic={topic}
        run={run}
        askedBefore={asked}
        onDecided={decided}
      />
      <StopButton onDone={onDone} />
    </section>
  )
}

/** A few of one topic's review questions, one at a time, until decided. */
function TopicProbe({
  topic,
  run,
  askedBefore,
  onDecided,
}: {
  topic: Topic
  run: string
  askedBefore: number
  onDecided: (probe: ProbeResult) => void
}) {
  const [content, setContent] = useState<TopicContent | 'failed' | null>(null)
  const [items, setItems] = useState<string[]>([])
  const [tries, setTries] = useState(0)
  const [results, setResults] = useState<boolean[]>([])
  const [answered, setAnswered] = useState(false)

  useEffect(() => {
    let active = true
    loadTopicContent(topic.id).then(
      (loaded) => {
        if (!active) return
        if (!loaded) {
          setContent('failed')
          return
        }
        // Only recall questions: quick, and no code editor.
        const pool = loaded.topic.review_pool.filter(
          (id) => id in loaded.recall,
        )
        const chosen = chooseProbeItems(pool, (id) =>
          loaded.recall[id]?.type === 'mcq' ? 'choice' : 'other',
        )
        if (chosen.length === 0) {
          // Nothing to ask (a topic still being written): the benefit of the
          // doubt, as with a tie.
          onDecided({ id: topic.id, passed: true, asked: [] })
          return
        }
        setItems(chosen)
        setContent(loaded)
      },
      () => {
        if (active) setContent('failed')
      },
    )
    return () => {
      active = false
    }
    // onDecided is the parent's handler for this very probe.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [topic, tries])

  function graded(correct: boolean) {
    if (answered) return
    setResults([...results, correct])
    setAnswered(true)
  }

  function next() {
    if (verdict(results, items.length) === 'open') {
      setAnswered(false)
      return
    }
    onDecided({
      id: topic.id,
      passed: verdict(results, items.length) === 'pass',
      asked: items
        .slice(0, results.length)
        .map((item, at) => ({ item, correct: results[at] ?? false })),
    })
  }

  if (content === 'failed') {
    return (
      <p className="flex flex-wrap items-center gap-2">
        The questions for {topic.title} couldn't load.
        <button
          type="button"
          onClick={() => {
            setContent(null)
            setTries((count) => count + 1)
          }}
          className={SECONDARY_BUTTON}
        >
          Try again
        </button>
      </p>
    )
  }
  if (!content) {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400">
        Loading questions from {topic.title}…
      </p>
    )
  }
  const position = answered ? results.length - 1 : results.length
  const itemId = items[position]
  if (!itemId) return null
  return (
    <div className="space-y-3">
      <p className="text-sm text-slate-600 dark:text-slate-400">
        From the topic <span className="font-medium">{topic.title}</span>
      </p>
      <PracticeItem
        key={itemId}
        itemId={itemId}
        content={content}
        context="placement"
        eventData={{ run }}
        position={`Question ${askedBefore + position + 1}`}
        onGraded={graded}
      />
      {answered && (
        <button type="button" onClick={next} className={BUTTON}>
          Next question
        </button>
      )}
    </div>
  )
}

function TopicsResult({
  title,
  scope,
  result,
  learned,
  onDone,
}: {
  title: string
  /** The foundations list the run walked, if it wasn't a whole track. */
  scope?: FoundationsScope
  result: Placement
  learned: (topicId: string) => boolean
  onDone: () => void
}) {
  const headingId = useId()
  const toProve = result.known
    .map((id) => getTopic(id))
    .filter(
      (topic): topic is Topic => topic !== undefined && !learned(topic.id),
    )
  const next = result.next ? getTopic(result.next) : undefined
  // From a list, a topic's page keeps the way back to the track it's for.
  const linkTo = (topicId: string) =>
    scope ? foundationLink(topicId, scope.track) : `/topic/${topicId}`
  return (
    <section aria-labelledby={headingId} className="space-y-4">
      <h2 id={headingId} className="text-xl font-semibold">
        {title}: where to start
      </h2>
      <p>
        You answered {result.correct} of {result.asked} right.
      </p>
      {result.known.length === 0 ? (
        <p>
          Start at the beginning{scope && ' of the list'}
          {next && (
            <>
              :{' '}
              <Link to={linkTo(next.id)} className="underline">
                {next.title}
              </Link>
            </>
          )}
          . That's the right place for most people new to this, and the early
          topics go quickly when parts are familiar.
        </p>
      ) : (
        <>
          <p>
            {next ? (
              <>
                Your knowledge seems to run out at{' '}
                <Link to={linkTo(next.id)} className="underline">
                  {next.title}
                </Link>
                . That's where to start learning.
              </>
            ) : scope ? (
              <>
                You seem to know everything Module {scope.number} builds on from
                other tracks.
              </>
            ) : (
              <>You seem to know everything written here so far.</>
            )}
          </p>
          {toProve.length > 0 && (
            <>
              <p>
                {toProve.length === 1
                  ? 'One topic before it looks'
                  : `${toProve.length} topics before it look`}{' '}
                familiar. A test ticks nothing off: open each one and choose{' '}
                <strong>Prove it now</strong>, a short build, a debug and an
                explanation, about 10 to 15 minutes each. Do them in this order,
                because each one unlocks the next:
              </p>
              <ol className="list-decimal space-y-1 pl-6">
                {toProve.map((topic) => (
                  <li key={topic.id}>
                    <Link to={linkTo(topic.id)} className="underline">
                      {topic.title}
                    </Link>
                  </li>
                ))}
              </ol>
            </>
          )}
        </>
      )}
      <p className="flex flex-wrap items-center gap-3">
        <button type="button" onClick={onDone} className={SECONDARY_BUTTON}>
          Back to the placement test
        </button>
        {scope && (
          <Link
            to={foundationsMapLink(scope.track, scope.module)}
            className="underline"
          >
            Back to the list on the map
          </Link>
        )}
      </p>
    </section>
  )
}

// A diagnostic, such as math ------------------------------------------------

function DiagnosticRun({
  diagnostic,
  onDone,
}: {
  diagnostic: Diagnostic
  onDone: () => void
}) {
  const record = useRecordEvent()
  const headingId = useId()
  const [run] = useState(() => crypto.randomUUID())
  const levels = diagnostic.levels
  const [walk, setWalk] = useState(() => startWalk(levels.length))
  const [probes, setProbes] = useState<ProbeResult[]>([])
  const [result, setResult] = useState<Placement | null>(null)
  const index = nextProbe(walk)
  const subject = subjectOfDiagnostic(diagnostic.id)

  function decided(probe: ProbeResult) {
    if (index === null) return
    const nextWalk = afterProbe(walk, index, probe.passed)
    const nextProbes = [...probes, probe]
    setWalk(nextWalk)
    setProbes(nextProbes)
    if (nextProbe(nextWalk) !== null) return
    const placement = summarize(
      levels.map((level) => level.id),
      nextWalk,
      nextProbes,
    )
    record({
      type: 'placement',
      topic_id: subject,
      item_id: 'placement',
      context: 'placement',
      data: {
        run,
        kind: 'diagnostic',
        diagnostic: diagnostic.id,
        known: placement.known,
        next: placement.next,
        asked: placement.asked,
        correct: placement.correct,
        probes: placement.probes,
      },
    })
    setResult(placement)
  }

  if (result) {
    return (
      <DiagnosticResult
        diagnostic={diagnostic}
        result={result}
        onDone={onDone}
      />
    )
  }
  const level = index === null ? undefined : levels[index]
  if (!level) return null
  const asked = probes.reduce((count, probe) => count + probe.asked.length, 0)
  return (
    <section aria-labelledby={headingId} className="space-y-4">
      <h2 id={headingId} className="text-xl font-semibold">
        {diagnostic.title}: placement
      </h2>
      <Progress
        checked={probes.length}
        outOf={probesNeeded(levels.length)}
        asked={asked}
        what="levels"
      />
      <LevelProbe
        key={level.id}
        level={level}
        subject={subject}
        run={run}
        askedBefore={asked}
        onDecided={decided}
      />
      <StopButton onDone={onDone} />
    </section>
  )
}

/** A few of one level's questions, one at a time, until decided. */
function LevelProbe({
  level,
  subject,
  run,
  askedBefore,
  onDecided,
}: {
  level: DiagnosticLevel
  subject: string
  run: string
  askedBefore: number
  onDecided: (probe: ProbeResult) => void
}) {
  const record = useRecordEvent()
  const timer = useAttemptTimer()
  const headingId = useId()
  const [items] = useState<McqItem[]>(() =>
    chooseProbeItems(
      level.items.map((item) => item.id),
      () => 'choice',
    )
      .map((id) => level.items.find((item) => item.id === id))
      .filter((item) => item !== undefined),
  )
  const [results, setResults] = useState<boolean[]>([])
  const [answered, setAnswered] = useState(false)

  function graded(item: McqItem, correct: boolean, choice: number | null) {
    if (answered) return
    record({
      type: 'answer',
      topic_id: subject,
      item_id: item.id,
      item_rev: item.rev,
      context: 'placement',
      correct,
      duration_ms: timer.lap(),
      data: {
        run,
        level: level.id,
        choice,
        choice_text: choice === null ? null : (item.choices[choice] ?? null),
        // "I don't know this" is a wrong answer that was never a guess.
        ...(choice === null ? { dont_know: true } : {}),
      },
    })
    setResults([...results, correct])
    setAnswered(true)
  }

  function next() {
    if (verdict(results, items.length) === 'open') {
      setAnswered(false)
      return
    }
    onDecided({
      id: level.id,
      passed: verdict(results, items.length) === 'pass',
      asked: items
        .slice(0, results.length)
        .map((item, at) => ({ item: item.id, correct: results[at] ?? false })),
    })
  }

  const position = answered ? results.length - 1 : results.length
  const item = items[position]
  if (!item) return null
  return (
    // The attempt timer starts at the first focus or click inside, as in
    // PracticeItem. These handlers only time; they aren't controls.
    // oxlint-disable-next-line jsx-a11y/no-noninteractive-element-interactions
    <section
      aria-labelledby={headingId}
      className={CARD}
      onFocus={timer.start}
      onPointerDown={timer.start}
    >
      <p className="text-xs font-semibold tracking-wide text-slate-500 uppercase dark:text-slate-400">
        Question {askedBefore + position + 1} · {level.title}
      </p>
      <h3 id={headingId} className="text-lg font-semibold">
        Quick check
      </h3>
      <McqQuestion
        key={item.id}
        item={item}
        quiet
        onAnswer={(correct, choice) => graded(item, correct, choice)}
      />
      {answered && (
        <button type="button" onClick={next} className={BUTTON}>
          Next question
        </button>
      )}
    </section>
  )
}

function DiagnosticResult({
  diagnostic,
  result,
  onDone,
}: {
  diagnostic: Diagnostic
  result: Placement
  onDone: () => void
}) {
  const headingId = useId()
  const levels = diagnostic.levels
  const solidThrough = levels.find((level) => level.id === result.known.at(-1))
  const from = levels.findIndex((level) => level.id === result.next)
  const toRefresh = from === -1 ? [] : levels.slice(from)
  return (
    <section aria-labelledby={headingId} className="space-y-4">
      <h2 id={headingId} className="text-xl font-semibold">
        {diagnostic.title}: what it found
      </h2>
      <p>
        You answered {result.correct} of {result.asked} right.
      </p>
      {toRefresh.length === 0 ? (
        <p>
          Every level looks solid, through{' '}
          <strong>{levels.at(-1)?.title}</strong>. The math in the
          machine-learning track shouldn't get in your way.
        </p>
      ) : (
        <>
          <p>
            {solidThrough ? (
              <>
                Solid through <strong>{solidThrough.title}</strong>. From{' '}
              </>
            ) : (
              <>Start from the bottom of the ladder: from </>
            )}
            <strong>{toRefresh[0]?.title}</strong> on, a refresher before the
            machine-learning track will pay for itself. Each level is a topic of
            the Machine Learning Foundations track as it's written; until then,
            a free refresher:
          </p>
          <ul className="list-disc space-y-1 pl-6">
            {toRefresh.map((level) => {
              const topic = level.topic ? getTopic(level.topic) : undefined
              return (
                <li key={level.id}>
                  <strong>{level.title}</strong>: {level.summary}{' '}
                  {topic && isOpen(topic) ? (
                    <Link to={`/topic/${topic.id}`} className="underline">
                      {topic.title}, on this platform
                    </Link>
                  ) : (
                    <a
                      href={level.refresh.url}
                      target="_blank"
                      rel="noreferrer"
                      className="underline"
                    >
                      {level.refresh.title}
                    </a>
                  )}
                </li>
              )
            })}
          </ul>
        </>
      )}
      <p>
        <button type="button" onClick={onDone} className={SECONDARY_BUTTON}>
          Back to the placement test
        </button>
      </p>
    </section>
  )
}

export type { ProgressState }
