// Mistakes come back as fresh questions until relearned (ADR-0011).
//
// Everything here is worked out from the learner's history of graded
// attempts, so it needs no table of its own, and misses from before this
// feature existed count too.
import { STAGES } from '../content/stages.ts'
import type { TopicContent } from '../content/types.ts'

/** A calendar day in the learner's own time zone, like "2026-11-06". */
export type Day = string

/** One graded attempt: an answer to a question, or a Check of some code. */
export type Attempt = {
  id: string
  type: 'answer' | 'code_check'
  topic_id: string
  item_id: string
  correct: boolean
  /** In ISO format, UTC, so comparing the text compares the times. */
  occurred_at: string
}

/** A skill the learner missed and is relearning. */
export type FollowUp = {
  topicId: string
  skillId: string
  /** The day of the most recent miss. */
  missedOn: Day
  /** The items missed that day. */
  missedItems: string[]
  /** Days since the miss with a correct answer on this skill. */
  correctOn: Day[]
  /** When it should come back. */
  due: Day
}

/**
 * After the 1st and 2nd correct days, the skill comes back this many days
 * later. Successive relearning works best with at least 3 relearning
 * sessions on growing gaps (Rawson & Dunlosky, 2011): together with the
 * first follow-up the next day, that's 1, 3 and 7 days.
 */
export const RELEARNING_GAPS = [3, 7]
/** A skill is relearned once it's answered correctly on this many days. */
export const CORRECT_DAYS_NEEDED = RELEARNING_GAPS.length + 1

/** The skills an item tests (empty for items that don't exist any more). */
export type SkillsOf = (topicId: string, itemId: string) => string[]

export function dayOf(time: string | number | Date): Day {
  const date = new Date(time)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

export function addDays(day: Day, days: number): Day {
  const [year = 0, month = 1, date = 1] = day.split('-').map(Number)
  // Noon, so a daylight-saving change can't tip it into another day.
  return dayOf(new Date(year, month - 1, date + days, 12))
}

type ItemDay = {
  topicId: string
  itemId: string
  day: Day
  outcome: 'miss' | 'correct'
}

/**
 * How each item went on each day. A question is missed if any answer to it
 * that day was wrong. Code is different: failing Checks while working
 * something out aren't mistakes, so a code exercise counts as correct if any
 * Check passed that day, and as a miss only if none did.
 */
function itemDays(attempts: Attempt[]): ItemDay[] {
  const byKey = new Map<string, ItemDay>()
  for (const attempt of attempts) {
    const day = dayOf(attempt.occurred_at)
    const key = `${attempt.topic_id}\n${attempt.item_id}\n${day}`
    const before = byKey.get(key)?.outcome
    const outcome =
      attempt.type === 'code_check'
        ? attempt.correct || before === 'correct'
          ? 'correct'
          : 'miss'
        : !attempt.correct || before === 'miss'
          ? 'miss'
          : 'correct'
    byKey.set(key, {
      topicId: attempt.topic_id,
      itemId: attempt.item_id,
      day,
      outcome,
    })
  }
  return [...byKey.values()]
}

/** Topics with at least one miss: only these can have follow-ups. */
export function topicsWithMisses(attempts: Attempt[]): string[] {
  const topics = itemDays(attempts)
    .filter((itemDay) => itemDay.outcome === 'miss')
    .map((itemDay) => itemDay.topicId)
  return [...new Set(topics)].sort()
}

/**
 * Every skill that's currently being relearned. Day by day, for each skill:
 * a miss opens it (due the next day, and any earlier progress starts over);
 * each correct day after the miss counts towards closing it (due again 3
 * days later, then 7); 3 correct days close it.
 */
export function openFollowUps(
  attempts: Attempt[],
  skillsOf: SkillsOf,
): FollowUp[] {
  type SkillDay = { missed: Set<string>; correct: boolean }
  const bySkill = new Map<string, Map<Day, SkillDay>>()
  for (const { topicId, itemId, day, outcome } of itemDays(attempts)) {
    for (const skillId of skillsOf(topicId, itemId)) {
      const key = `${topicId}\n${skillId}`
      const days = bySkill.get(key) ?? new Map<Day, SkillDay>()
      bySkill.set(key, days)
      const skillDay = days.get(day) ?? { missed: new Set(), correct: false }
      days.set(day, skillDay)
      if (outcome === 'miss') skillDay.missed.add(itemId)
      else skillDay.correct = true
    }
  }

  const open: FollowUp[] = []
  for (const [key, days] of bySkill) {
    const [topicId = '', skillId = ''] = key.split('\n')
    let state: FollowUp | null = null
    for (const [day, { missed, correct }] of [...days].sort(([a], [b]) =>
      a.localeCompare(b),
    )) {
      if (missed.size > 0) {
        state = {
          topicId,
          skillId,
          missedOn: day,
          missedItems: [...missed].sort(),
          correctOn: [],
          due: addDays(day, 1),
        }
      } else if (correct && state && day > state.missedOn) {
        state.correctOn.push(day)
        const gap = RELEARNING_GAPS[state.correctOn.length - 1]
        if (gap === undefined) state = null
        else state.due = addDays(day, gap)
      }
    }
    if (state) open.push(state)
  }
  return open.sort(
    (a, b) =>
      a.due.localeCompare(b.due) ||
      a.topicId.localeCompare(b.topicId) ||
      a.skillId.localeCompare(b.skillId),
  )
}

/** The skills each item tests, looked up in loaded topic content. */
export function skillsIn(contents: Map<string, TopicContent>): SkillsOf {
  return (topicId, itemId) => {
    const content = contents.get(topicId)
    return (
      content?.recall[itemId]?.skills ??
      content?.exercises[itemId]?.skills ??
      []
    )
  }
}

/**
 * The question to ask for a follow-up: a different one on the same skill
 * (the owner's choice), preferring one never answered, then the one answered
 * longest ago. Only if there's no other question does a missed one return.
 * Questions in `avoid` (already on the page) are used only as a last resort.
 */
export function chooseQuestion(
  followUp: FollowUp,
  content: TopicContent,
  attempts: Attempt[],
  avoid: ReadonlySet<string> = new Set(),
): string | null {
  const candidates = [
    ...Object.values(content.recall),
    ...Object.values(content.exercises).filter(
      (exercise) => STAGES[exercise.stage].followUp,
    ),
  ]
    .filter((item) => item.skills.includes(followUp.skillId))
    .map((item) => item.id)
  const fresh = candidates.filter((id) => !followUp.missedItems.includes(id))
  const pool = fresh.length > 0 ? fresh : candidates

  const lastAnswered = new Map<string, string>()
  for (const attempt of attempts) {
    if (attempt.topic_id !== followUp.topicId) continue
    const before = lastAnswered.get(attempt.item_id) ?? ''
    if (attempt.occurred_at > before) {
      lastAnswered.set(attempt.item_id, attempt.occurred_at)
    }
  }
  // Questions not already on the page first; then never answered (''),
  // then the oldest answer.
  const sorted = [...pool].sort((a, b) => {
    const whenA = lastAnswered.get(a) ?? ''
    const whenB = lastAnswered.get(b) ?? ''
    return (
      Number(avoid.has(a)) - Number(avoid.has(b)) ||
      whenA.localeCompare(whenB) ||
      a.localeCompare(b)
    )
  })
  return sorted[0] ?? null
}

/** A question to ask today, and the follow-ups it answers. */
export type PlannedCard = {
  topicId: string
  itemId: string
  content: TopicContent
  followUps: FollowUp[]
}

/**
 * Today's questions for the follow-ups that are due. One miss often opens
 * several follow-ups (an item can test several skills), so each gets a
 * different question where possible. When a skill's only remaining question
 * is already on the page, that question is asked once, for both.
 */
export function planCards(
  due: FollowUp[],
  contents: Map<string, TopicContent>,
  attempts: Attempt[],
): PlannedCard[] {
  const cards: PlannedCard[] = []
  for (const followUp of due) {
    const content = contents.get(followUp.topicId)
    if (!content) continue
    const sameTopic = cards.filter((card) => card.topicId === followUp.topicId)
    const used = new Set(sameTopic.map((card) => card.itemId))
    const itemId = chooseQuestion(followUp, content, attempts, used)
    if (!itemId) continue
    const shared = sameTopic.find((card) => card.itemId === itemId)
    if (shared) {
      shared.followUps.push(followUp)
    } else {
      cards.push({
        topicId: followUp.topicId,
        itemId,
        content,
        followUps: [followUp],
      })
    }
  }
  return cards
}
