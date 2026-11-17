// A topic in parts (ADR-0025): the lesson, then the practice ladder cut into
// parts of about half an hour, then the proof checks. The page shows one
// part at a time, so a topic of four or five hours reads as a few sittings
// rather than one endless page. Parts never gate anything: a learner can
// open any part at any time, and nothing about the proofs or mastery
// changes (ADR-0002). Whether a part is done is worked out from the saved
// answers, like everything else in progress; nothing new is stored.
import { STAGES } from '../content/stages.ts'
import type { TopicContent } from '../content/types.ts'
import {
  itemPlace,
  LESSON_PLACE_PREFIX,
  provePlace,
  START_PLACE,
} from '../place/useCurrentPlace.ts'
import { type ItemState, itemKey } from '../progress/itemStates.ts'
import { type Proof, PROOFS } from '../progress/progress.ts'
import { itemMinutes, proofMinutes } from './estimates.ts'

/** One rung of the practice ladder, in page order. */
export type LadderItem = { itemId: string; content: TopicContent }

export type TopicPart =
  | { id: 'learn'; kind: 'learn'; title: string; minutes: number }
  | {
      id: string
      kind: 'practice'
      title: string
      minutes: number
      /** Its items, in ladder order. */
      items: LadderItem[]
      /** Where its first item is in the whole ladder, counting from 0. */
      start: number
    }
  | { id: 'prove'; kind: 'prove'; title: string; minutes: number }

/** A practice part should come out at about this many minutes… */
const TARGET_MINUTES = 30
/** …and at most about this many, where the items allow it. */
const LONGEST_MINUTES = 40
/**
 * The lesson is at least this share of the topic's total. Where the guesses
 * for the practice and the proofs leave less than that (short Python topics,
 * whose exercises are quicker than the figures assume), those guesses are
 * scaled down to fit instead.
 */
const LESSON_SHARE = 0.25
/**
 * What it costs, in squared minutes, to cut between two quick questions
 * rather than where the kind of work changes (a question, then an exercise).
 * About as bad as a part five minutes off its target: enough to move a cut
 * to a natural break nearby, never enough to make a part much too long.
 */
const CUT_IN_QUESTIONS = 25

/**
 * The parts of a regular topic, in order. A Locked topic has its lesson
 * only, since its practice and proofs wait (F8). Checkpoints aren't cut into
 * parts: they have no lesson or practice, only their proof checks.
 */
export function topicParts(
  content: TopicContent,
  items: LadderItem[],
  { locked = false }: { locked?: boolean } = {},
): TopicPart[] {
  const total = content.topic.estimated_minutes
  const practiceRaw = items.map((item) =>
    itemMinutes(item.content, item.itemId),
  )
  const practiceTotal = sum(practiceRaw)
  const hasProofs = PROOFS.some((proof) => content.topic.prove[proof])
  const proveRaw = hasProofs ? proofMinutes(content) : 0
  // Scale the guesses so the parts add up to the topic's own total.
  const rest = practiceTotal + proveRaw
  const lessonFloor = total * LESSON_SHARE
  const scale =
    rest === 0 || total - rest >= lessonFloor
      ? 1
      : Math.max(total - lessonFloor, 0) / rest
  const lesson = total - rest * scale

  const parts: TopicPart[] = [
    { id: 'learn', kind: 'learn', title: 'Learn', minutes: lesson },
  ]
  if (locked) return parts

  const minutes = practiceRaw.map((each) => each * scale)
  const groups = splitLadder(
    minutes,
    items.map((item) => kindOf(item)),
  )
  for (const [index, group] of groups.entries()) {
    const start = group[0] ?? 0
    const partItems = group.map((at) => items[at]!)
    parts.push({
      id: `practice-${index + 1}`,
      kind: 'practice',
      title:
        groups.length === 1
          ? 'Practice'
          : `Practice: ${describeItems(partItems)}`,
      minutes: sum(group.map((at) => minutes[at] ?? 0)),
      items: partItems,
      start,
    })
  }
  if (hasProofs) {
    parts.push({
      id: 'prove',
      kind: 'prove',
      title: 'Prove it',
      minutes: proveRaw * scale,
    })
  }
  return parts
}

/** "about 30 min": to the nearest 5 minutes, and never less than 5. */
export function aboutMinutes(minutes: number): string {
  return `about ${Math.max(5, Math.round(minutes / 5) * 5)} min`
}

type Kind = 'question' | 'exercise'

function kindOf(item: LadderItem): Kind {
  return item.content.exercises[item.itemId] ? 'exercise' : 'question'
}

function sum(values: number[]): number {
  return values.reduce((total, value) => total + value, 0)
}

/** How many practice parts a ladder of this many minutes makes. */
export function practicePartCount(minutes: number, items: number): number {
  if (items === 0) return 0
  if (minutes <= LONGEST_MINUTES) return 1
  const count = Math.max(
    Math.round(minutes / TARGET_MINUTES),
    Math.ceil(minutes / LONGEST_MINUTES),
  )
  return Math.min(count, items)
}

/**
 * Cuts the ladder into parts of about equal length, keeping its order, and
 * returns each part's item positions. It tries every way to cut and keeps
 * the one whose parts are closest to equal (the sum of each part's squared
 * distance from the average), with a small extra cost for cutting in the
 * middle of a run of quick questions, so cuts fall where the kind of work
 * changes when that costs little.
 */
export function splitLadder(minutes: number[], kinds: Kind[]): number[][] {
  const count = minutes.length
  const parts = practicePartCount(sum(minutes), count)
  if (parts === 0) return []
  if (parts === 1) return [minutes.map((_, index) => index)]
  const target = sum(minutes) / parts
  // before[i] is the time of the first i items, so any run's time is one
  // subtraction.
  const before = [0]
  for (const each of minutes) before.push(before.at(-1)! + each)
  const runCost = (from: number, to: number) =>
    (before[to]! - before[from]! - target) ** 2
  const cutCost = (at: number) =>
    kinds[at - 1] === 'question' && kinds[at] === 'question'
      ? CUT_IN_QUESTIONS
      : 0

  // best[p][i]: the cheapest way to make the first i items into p parts,
  // and where its last part starts.
  const best: { cost: number; from: number }[][] = [
    [{ cost: 0, from: 0 }, ...minutes.map(() => ({ cost: Infinity, from: 0 }))],
  ]
  for (let p = 1; p <= parts; p += 1) {
    const row = [{ cost: Infinity, from: 0 }]
    for (let i = 1; i <= count; i += 1) {
      let cheapest = { cost: Infinity, from: 0 }
      for (let from = p - 1; from < i; from += 1) {
        const earlier = best[p - 1]![from]!.cost
        if (earlier === Infinity) continue
        const cost = earlier + runCost(from, i) + (from > 0 ? cutCost(from) : 0)
        if (cost < cheapest.cost) cheapest = { cost, from }
      }
      row.push(cheapest)
    }
    best.push(row)
  }
  // Walk back from the end to find the cuts.
  const groups: number[][] = []
  let end = count
  for (let p = parts; p >= 1; p -= 1) {
    const from = best[p]![end]!.from
    groups.unshift(range(from, end))
    end = from
  }
  return groups
}

function range(from: number, to: number): number[] {
  return Array.from({ length: to - from }, (_, index) => from + index)
}

/**
 * What a practice part holds, in a few words: "worked example and 12
 * questions", "13 questions", "fill in the gaps, write it and 1 question".
 */
export function describeItems(items: LadderItem[]): string {
  // In the order they come, with the questions counted where the first is.
  const pieces: string[] = []
  let questions = 0
  let questionsAt = -1
  for (const item of items) {
    const exercise = item.content.exercises[item.itemId]
    if (exercise) {
      pieces.push(STAGES[exercise.stage].label.toLowerCase())
    } else {
      if (questionsAt < 0) questionsAt = pieces.push('') - 1
      questions += 1
    }
  }
  if (questionsAt >= 0) {
    pieces[questionsAt] =
      `${questions} ${questions === 1 ? 'question' : 'questions'}`
  }
  const text =
    pieces.length <= 1
      ? (pieces[0] ?? '')
      : `${pieces.slice(0, -1).join(', ')} and ${pieces.at(-1)}`
  return text.charAt(0).toUpperCase() + text.slice(1)
}

/**
 * Whether each part is done, by its id, or null while that can't be known
 * (signed out, or the progress still loading). A practice part is done once
 * every item in it has been got right; the proofs, once every proof check
 * has passed. The lesson has no answers of its own, so it counts as done
 * once the learner has tried anything in this topic's practice or proofs:
 * moving on is the only sign the page has, and nothing is stored for it.
 */
export function partsDone(
  parts: TopicPart[],
  content: TopicContent,
  states: Map<string, ItemState> | null,
  passed: Partial<Record<Proof, string>> | null,
  /**
   * Items made optional by the quick check, by itemKey: they don't hold a
   * practice part back (ADR-0025, amended 2026-11-16).
   */
  optional: Set<string> = new Set(),
): Map<string, boolean> | null {
  if (!states || !passed) return null
  const topicId = content.topic.id
  const proofs = PROOFS.filter((proof) => content.topic.prove[proof])
  const ownItems = [
    ...parts.flatMap((part) =>
      part.kind === 'practice'
        ? part.items
            .filter((item) => item.content.topic.id === topicId)
            .map((item) => item.itemId)
        : [],
    ),
    ...[content.topic.prove.build, content.topic.prove.debug].filter(
      (id) => id !== undefined,
    ),
  ]
  const startedHere =
    ownItems.some((itemId) => states.has(itemKey(topicId, itemId))) ||
    proofs.some((proof) => passed[proof])
  const done = new Map<string, boolean>()
  for (const part of parts) {
    if (part.kind === 'learn') done.set(part.id, startedHere)
    else if (part.kind === 'practice') {
      done.set(
        part.id,
        part.items.every((item) => {
          const key = itemKey(item.content.topic.id, item.itemId)
          return states.get(key) === 'done' || optional.has(key)
        }),
      )
    } else {
      done.set(
        part.id,
        proofs.every((proof) => passed[proof]),
      )
    }
  }
  return done
}

/**
 * The part to open the page at: the part last viewed on this device if it
 * isn't done yet (the learner was in the middle of it), otherwise the first
 * part that isn't done, otherwise the last one viewed, otherwise the first.
 */
export function resumePart(
  parts: TopicPart[],
  done: Map<string, boolean> | null,
  lastViewed: string | null,
): string {
  const viewed = parts.some((part) => part.id === lastViewed)
    ? lastViewed
    : null
  const first = parts[0]?.id ?? 'learn'
  if (!done) return viewed ?? first
  if (viewed && !done.get(viewed)) return viewed
  return parts.find((part) => !done.get(part.id))?.id ?? viewed ?? first
}

/**
 * The id of a part's heading, which a link to the part points at: "learn",
 * "practice" (the first practice part), "practice-2" and so on, and
 * "prove-it".
 */
export function partAnchor(part: TopicPart): string {
  if (part.kind === 'learn') return 'learn'
  if (part.kind === 'prove') return 'prove-it'
  return part.id === 'practice-1' ? 'practice' : part.id
}

/** The ids on the page that belong to the lesson (see useCurrentPlace.ts). */
function isLessonAnchor(anchor: string): boolean {
  return (
    anchor === 'learn' ||
    anchor === START_PLACE ||
    anchor.startsWith(LESSON_PLACE_PREFIX) ||
    anchor === 'place-resource' ||
    anchor === 'place-recap'
  )
}

/**
 * The part that holds an element of the page, from its id (a link's
 * "#place-recap", say), so a link to anything opens the right part. An id
 * the page doesn't know comes from the lesson's own text, so it opens the
 * lesson.
 */
export function partOfAnchor(
  parts: TopicPart[],
  content: TopicContent,
  anchor: string,
): TopicPart | undefined {
  const learn = parts.find((part) => part.kind === 'learn')
  if (isLessonAnchor(anchor)) return learn
  const headed = parts.find((part) => partAnchor(part) === anchor)
  if (headed) return headed
  for (const part of parts) {
    if (part.kind !== 'practice') continue
    const holds = part.items.some(
      (item) =>
        anchor === itemPlace(item.content.topic.id, item.itemId) ||
        anchor === `item-${item.itemId}`,
    )
    if (holds) return part
  }
  const prove = parts.find((part) => part.kind === 'prove')
  const { build, debug } = content.topic.prove
  const proveAnchors = [
    'prove-it',
    ...PROOFS.map((proof) => provePlace(proof)),
    ...[build, debug]
      .filter((id) => id !== undefined)
      .map((id) => `item-${id}`),
  ]
  if (proveAnchors.includes(anchor)) return prove ?? learn
  return learn
}
