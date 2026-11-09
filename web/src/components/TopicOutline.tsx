import type { TopicContent } from '../content/types.ts'
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

/** One rung of the practice ladder, in page order. */
export type LadderItem = { itemId: string; content: TopicContent }

type Props = {
  content: TopicContent
  /** The practice ladder as the page shows it, an earlier topic's question included. */
  items: LadderItem[]
  /** Each attempted item's state, or null while unknown (signed out, loading). */
  states: Map<string, ItemState> | null
  /** When each proof check passed, or null while unknown. */
  passed: Partial<Record<Proof, string>> | null
  /** The place the learner is looking at, if the page can tell. */
  current: string | null
  /** How many parts the lesson has, once the page has counted them. */
  lessonParts: number
  /** The place remembered from the last visit, if any. */
  resume: string | null
  /** Which sections the page is showing. */
  sections: { learn: boolean; practice: boolean; prove: boolean }
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
 * lesson's parts, every practice item with whether it's done, the three
 * proof checks, and a way to continue where the last visit stopped. The
 * states come from the learner's saved answers, never from a tick they set
 * themselves.
 */
export function TopicOutline({
  content,
  items,
  states,
  passed,
  current,
  lessonParts,
  resume,
  sections,
}: Props) {
  const stateOf = (item: LadderItem) =>
    states?.get(itemKey(item.content.topic.id, item.itemId))
  const done = items.filter((item) => stateOf(item) === 'done').length
  const nextNotDone = states
    ? items.findIndex((item) => stateOf(item) !== 'done')
    : -1
  const lessonPart = current?.startsWith(LESSON_PLACE_PREFIX)
    ? Number(current.slice(LESSON_PLACE_PREFIX.length))
    : null
  const resumeLabel = resume ? describePlace(resume, items) : null

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
          className="block rounded-md border border-lime-600 px-3 py-2 font-medium text-lime-800 hover:bg-lime-50 dark:border-lime-500 dark:text-lime-300 dark:hover:bg-lime-950"
        >
          Continue where you left off: {resumeLabel}
        </a>
      )}
      {sections.learn && (
        <div className="space-y-1">
          <p className="font-semibold">Learn</p>
          <ul className="space-y-0.5">
            {LEARN_PLACES.map((place) => {
              const isCurrent =
                current === place.id ||
                (place.id === `${LESSON_PLACE_PREFIX}1` && lessonPart !== null)
              return (
                <li key={place.id}>
                  <a
                    href={`#${place.id}`}
                    aria-current={isCurrent ? 'location' : undefined}
                    className={isCurrent ? 'font-semibold' : 'hover:underline'}
                  >
                    {isCurrent && (
                      <span aria-hidden="true">{CURRENT_MARK}</span>
                    )}
                    {place.label}
                    {place.id === `${LESSON_PLACE_PREFIX}1` &&
                      lessonPart !== null &&
                      lessonParts > 0 &&
                      ` (part ${lessonPart} of ${lessonParts})`}
                  </a>
                </li>
              )
            })}
          </ul>
        </div>
      )}
      {sections.practice && items.length > 0 && (
        <div className="space-y-2">
          <p className="font-semibold">
            Practice
            {states && (
              <span className="font-normal text-slate-600 dark:text-slate-400">
                {' '}
                · {done} of {items.length} done
              </span>
            )}
          </p>
          {nextNotDone >= 0 && (
            <a
              href={`#${itemPlace(items[nextNotDone]!.content.topic.id, items[nextNotDone]!.itemId)}`}
              className="block underline"
            >
              Next not done: Practice {nextNotDone + 1}
            </a>
          )}
          <ol className="grid grid-cols-6 gap-1" aria-label="Practice items">
            {items.map((item, index) => {
              const id = itemPlace(item.content.topic.id, item.itemId)
              const state = stateOf(item)
              const isCurrent = current === id
              return (
                <li key={id}>
                  <a
                    href={`#${id}`}
                    aria-label={`Practice ${index + 1}: ${
                      state ? ITEM_STATE_LABELS[state] : 'not done yet'
                    }`}
                    aria-current={isCurrent ? 'location' : undefined}
                    className={`flex h-8 items-center justify-center gap-0.5 rounded border text-xs font-medium ${
                      state === 'done'
                        ? 'border-lime-600 bg-lime-100 text-lime-900 dark:border-lime-500 dark:bg-lime-950 dark:text-lime-200'
                        : state === 'tried'
                          ? 'border-amber-500 bg-amber-50 text-amber-900 dark:bg-amber-950 dark:text-amber-200'
                          : 'border-slate-300 text-slate-700 dark:border-slate-700 dark:text-slate-300'
                    } ${isCurrent ? 'ring-2 ring-slate-900 ring-offset-1 dark:ring-white dark:ring-offset-slate-900' : ''}`}
                  >
                    {index + 1}
                    {/* A mark as well as a color, never color alone (F9). */}
                    {state === 'done' && <span aria-hidden="true">✓</span>}
                    {state === 'tried' && <span aria-hidden="true">◐</span>}
                  </a>
                </li>
              )
            })}
          </ol>
        </div>
      )}
      {sections.prove && (
        <div className="space-y-1">
          <p className="font-semibold">
            Prove it
            {passed && (
              <span className="font-normal text-slate-600 dark:text-slate-400">
                {' '}
                · {PROOFS.filter((proof) => passed[proof]).length} of{' '}
                {PROOFS.length} passed
              </span>
            )}
          </p>
          <ul className="space-y-0.5">
            {PROOFS.filter((proof) => content.topic.prove[proof]).map(
              (proof) => {
                const id = provePlace(proof)
                const isCurrent = current === id
                return (
                  <li key={proof}>
                    <a
                      href={`#${id}`}
                      aria-current={isCurrent ? 'location' : undefined}
                      className={
                        isCurrent ? 'font-semibold' : 'hover:underline'
                      }
                    >
                      {isCurrent && (
                        <span aria-hidden="true">{CURRENT_MARK}</span>
                      )}
                      <span aria-hidden="true">
                        {passed?.[proof] ? '✓ ' : '○ '}
                      </span>
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
              },
            )}
          </ul>
        </div>
      )}
    </nav>
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
