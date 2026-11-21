import type { MouseEvent } from 'react'
import type { TopicContent } from '../content/types.ts'
import {
  aboutMinutes,
  type LadderItem,
  partAnchor,
  type TopicPart,
} from '../parts/topicParts.ts'
import {
  itemPlace,
  LESSON_PLACE_PREFIX,
  provePlace,
  START_PLACE,
} from '../place/useCurrentPlace.ts'
import {
  type ItemState,
  ITEM_STATE_LABELS,
  itemKey,
} from '../progress/itemStates.ts'
import { type Proof, PROOFS } from '../progress/progress.ts'
import { PROGRESS_FILL } from './styles.ts'

export type { LadderItem }

type Props = {
  content: TopicContent
  /** The topic's parts, in order (ADR-0025). */
  parts: TopicPart[]
  /** The part on screen. */
  currentPart: string
  /** Whether each part is done, by its id, or null while unknown. */
  done: Map<string, boolean> | null
  /** The practice ladder as the page shows it, an earlier topic's question included. */
  items: LadderItem[]
  /** Each attempted item's state, or null while unknown (signed out, loading). */
  states: Map<string, ItemState> | null
  /** Practice the quick check made optional, by itemKey (ADR-0025, amended). */
  optional?: Set<string>
  /** When each proof check passed, or null while unknown. */
  passed: Partial<Record<Proof, string>> | null
  /** The place the learner is looking at, if the page can tell. */
  current: string | null
  /** How many parts the lesson has, once the page has counted them. */
  lessonParts: number
  /** The place remembered from the last visit, if any. */
  resume: string | null
  /** Opens the part that holds this place, and goes to it. */
  onGoTo: (anchor: string) => void
}

const PROOF_NAMES: Record<Proof, string> = {
  build: 'Build',
  debug: 'Debug',
  explain: 'Explain',
}

const LEARN_PLACES: { id: string; label: string }[] = [
  { id: START_PLACE, label: 'What you can do after' },
  { id: `${LESSON_PLACE_PREFIX}1`, label: 'The lesson' },
  { id: 'place-resource', label: 'The main resource' },
  { id: 'place-recap', label: 'Recap' },
]

const CURRENT_MARK = '▸ '

/**
 * The learner's place in a topic (v1 spec, F3 and F5, for long topics): the
 * topic's parts with whether each is done (ADR-0025), and inside them the
 * lesson's places, every practice item with whether it's done, and the
 * three proof checks, plus a way to continue where the last visit stopped.
 * The states come from the learner's saved answers, never from a tick they
 * set themselves. Every link opens the part it points into.
 */
export function TopicOutline({
  content,
  parts,
  currentPart,
  done,
  items,
  states,
  optional = new Set(),
  passed,
  current,
  lessonParts,
  resume,
  onGoTo,
}: Props) {
  const stateOf = (item: LadderItem) =>
    states?.get(itemKey(item.content.topic.id, item.itemId))
  const isOptional = (item: LadderItem) =>
    optional.has(itemKey(item.content.topic.id, item.itemId))
  const practiceShown = parts.some((part) => part.kind === 'practice')
  // Optional practice isn't "not done": the quick check showed it's known.
  const nextNotDone =
    states && practiceShown
      ? items.findIndex((item) => stateOf(item) !== 'done' && !isOptional(item))
      : -1
  const lessonPart = current?.startsWith(LESSON_PLACE_PREFIX)
    ? Number(current.slice(LESSON_PLACE_PREFIX.length))
    : null
  const resumeLabel = resume ? describePlace(resume, items) : null

  /** A link to a place on the page, which opens its part first. */
  const follow = (anchor: string) => (event: MouseEvent) => {
    event.preventDefault()
    onGoTo(anchor)
  }

  return (
    <nav aria-labelledby="outline" className="space-y-4 text-sm">
      <h2
        id="outline"
        className="text-xs font-semibold tracking-wide text-slate-500 uppercase dark:text-slate-400"
      >
        Your place in this topic
      </h2>
      {resume && resumeLabel && (
        <a
          href={`#${resume}`}
          onClick={follow(resume)}
          // Not lime: the page's one lime button is "Next: Part…", and lime is
          // never a text colour.
          className="block rounded-md border border-slate-500 px-3 py-2 font-medium text-slate-900 hover:bg-slate-100 dark:border-slate-400 dark:text-slate-100 dark:hover:bg-slate-800"
        >
          Continue where you left off: {resumeLabel}
        </a>
      )}
      {nextNotDone >= 0 && (
        <a
          href={`#${itemPlace(items[nextNotDone]!.content.topic.id, items[nextNotDone]!.itemId)}`}
          onClick={follow(
            itemPlace(
              items[nextNotDone]!.content.topic.id,
              items[nextNotDone]!.itemId,
            ),
          )}
          className="block underline"
        >
          Next not done: Practice {nextNotDone + 1}
        </a>
      )}
      <ol className="space-y-4" aria-label="Parts">
        {parts.map((part, index) => {
          const isCurrent = part.id === currentPart
          const isDone = done?.get(part.id)
          const anchor = partAnchor(part)
          return (
            <li key={part.id} className="space-y-1">
              <a
                href={`#${anchor}`}
                onClick={follow(anchor)}
                aria-current={isCurrent ? 'step' : undefined}
                className={`block ${isCurrent ? 'font-semibold' : 'hover:underline'}`}
              >
                {isCurrent && <span aria-hidden="true">{CURRENT_MARK}</span>}
                {done && (
                  // A mark as well as words, never color alone (F9).
                  <span aria-hidden="true">{isDone ? '✓ ' : '○ '}</span>
                )}
                {parts.length > 1 && `Part ${index + 1} · `}
                {part.title}
                <span className="sr-only">
                  {done ? (isDone ? ': done' : ': not done yet') : ''}
                </span>
              </a>
              {parts.length > 1 && (
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {aboutMinutes(part.minutes)}
                  {part.kind === 'practice' &&
                    states &&
                    ` · ${part.items.filter((item) => stateOf(item) === 'done').length} of ${part.items.length} done`}
                </p>
              )}
              {part.kind === 'learn' && (
                <ul className="space-y-0.5">
                  {LEARN_PLACES.map((place) => {
                    const here =
                      isCurrent &&
                      (current === place.id ||
                        (place.id === `${LESSON_PLACE_PREFIX}1` &&
                          lessonPart !== null))
                    return (
                      <li key={place.id}>
                        <a
                          href={`#${place.id}`}
                          onClick={follow(place.id)}
                          aria-current={here ? 'location' : undefined}
                          className={here ? 'font-semibold' : 'hover:underline'}
                        >
                          {here && (
                            <span aria-hidden="true">{CURRENT_MARK}</span>
                          )}
                          {place.label}
                          {place.id === `${LESSON_PLACE_PREFIX}1` &&
                            here &&
                            lessonPart !== null &&
                            lessonParts > 0 &&
                            ` (part ${lessonPart} of ${lessonParts})`}
                        </a>
                      </li>
                    )
                  })}
                </ul>
              )}
              {part.kind === 'practice' && (
                <PracticeSquares
                  part={part}
                  stateOf={stateOf}
                  isOptional={isOptional}
                  current={isCurrent ? current : null}
                  follow={follow}
                />
              )}
              {part.kind === 'prove' && (
                <ProofList
                  content={content}
                  passed={passed}
                  current={isCurrent ? current : null}
                  follow={follow}
                />
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

/** A practice part's items, as a grid of numbered squares with their states. */
function PracticeSquares({
  part,
  stateOf,
  isOptional,
  current,
  follow,
}: {
  part: Extract<TopicPart, { kind: 'practice' }>
  stateOf: (item: LadderItem) => ItemState | undefined
  isOptional: (item: LadderItem) => boolean
  current: string | null
  follow: (anchor: string) => (event: MouseEvent) => void
}) {
  return (
    <ol
      className="grid grid-cols-6 gap-1"
      aria-label={`Practice items, part ${part.id.slice('practice-'.length)}`}
    >
      {part.items.map((item, offset) => {
        const number = part.start + offset + 1
        const id = itemPlace(item.content.topic.id, item.itemId)
        const state = stateOf(item)
        // Optional once the quick check showed its skills, unless done.
        const optional = state !== 'done' && isOptional(item)
        const isCurrent = current === id
        return (
          <li key={id}>
            <a
              href={`#${id}`}
              onClick={follow(id)}
              aria-label={`Practice ${number}: ${
                optional
                  ? 'optional, from your quick check'
                  : state
                    ? ITEM_STATE_LABELS[state]
                    : 'not done yet'
              }`}
              aria-current={isCurrent ? 'location' : undefined}
              className={`flex h-8 items-center justify-center gap-0.5 rounded border text-xs font-medium ${
                state === 'done'
                  ? PROGRESS_FILL
                  : optional
                    ? 'border-dashed border-slate-300 text-slate-400 dark:border-slate-700 dark:text-slate-500'
                    : state === 'tried'
                      ? 'border-amber-500 bg-amber-50 text-amber-900 dark:bg-amber-950 dark:text-amber-200'
                      : 'border-slate-300 text-slate-700 dark:border-slate-700 dark:text-slate-300'
              } ${isCurrent ? 'ring-2 ring-slate-900 ring-offset-1 dark:ring-white dark:ring-offset-slate-900' : ''}`}
            >
              {number}
              {/* A mark as well as a color, never color alone (F9). */}
              {state === 'done' && <span aria-hidden="true">✓</span>}
              {state === 'tried' && !optional && (
                <span aria-hidden="true">◐</span>
              )}
            </a>
          </li>
        )
      })}
    </ol>
  )
}

/** The proof checks, with whether each has passed. */
function ProofList({
  content,
  passed,
  current,
  follow,
}: {
  content: TopicContent
  passed: Partial<Record<Proof, string>> | null
  current: string | null
  follow: (anchor: string) => (event: MouseEvent) => void
}) {
  const proofs = PROOFS.filter((proof) => content.topic.prove[proof])
  return (
    <>
      {passed && (
        <p className="text-xs text-slate-500 dark:text-slate-400">
          {proofs.filter((proof) => passed[proof]).length} of {proofs.length}{' '}
          passed
        </p>
      )}
      <ul className="space-y-0.5">
        {proofs.map((proof) => {
          const id = provePlace(proof)
          const isCurrent = current === id
          return (
            <li key={proof}>
              <a
                href={`#${id}`}
                onClick={follow(id)}
                aria-current={isCurrent ? 'location' : undefined}
                className={isCurrent ? 'font-semibold' : 'hover:underline'}
              >
                {isCurrent && <span aria-hidden="true">{CURRENT_MARK}</span>}
                <span aria-hidden="true">{passed?.[proof] ? '✓ ' : '○ '}</span>
                {PROOF_NAMES[proof]}
                <span className="sr-only">
                  {passed
                    ? passed[proof]
                      ? ': passed'
                      : ': not passed yet'
                    : ''}
                </span>
              </a>
            </li>
          )
        })}
      </ul>
    </>
  )
}

/** How a remembered place reads: "Practice 8", "the lesson, part 4", … */
function describePlace(placeId: string, items: LadderItem[]): string | null {
  if (placeId === START_PLACE) return null
  if (placeId.startsWith(LESSON_PLACE_PREFIX)) {
    return `the lesson, part ${placeId.slice(LESSON_PLACE_PREFIX.length)}`
  }
  if (placeId === 'place-resource') return 'the main resource'
  if (placeId === 'place-recap') return 'the recap'
  for (const proof of PROOFS) {
    if (placeId === provePlace(proof)) return `the ${PROOF_NAMES[proof]} check`
  }
  const index = items.findIndex(
    (item) => itemPlace(item.content.topic.id, item.itemId) === placeId,
  )
  return index >= 0 ? `Practice ${index + 1}` : null
}
