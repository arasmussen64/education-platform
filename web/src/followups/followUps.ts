// Mistakes come back as fresh questions until relearned (ADR-0011).
//
// Everything here is worked out from the learner's history of graded
// attempts, so it needs no table of its own, and misses from before this
// feature existed count too.
import { STAGES } from '../content/stages.ts'
import type { Stage, TopicContent } from '../content/types.ts'
import { addDays, type Day, dayOf } from '../days.ts'
import type { EventContext } from '../events/types.ts'

/**
 * One graded attempt: an answer to a question, a Check of some code, a
 * graded explanation, or a finished review session.
 */
export type Attempt = {
  id: string
  /**
   * A graded explanation has the item ID "explain", and a review session
   * "review". Neither names skills, so neither brings a mistake back
   * (ADR-0013, ADR-0009).
   */
  type: 'answer' | 'code_check' | 'explain_submit' | 'review'
  topic_id: string
  item_id: string
  correct: boolean
  /** In ISO format, UTC, so comparing the text compares the times. */
  occurred_at: string
  /**
   * How long the attempt took, when known: from the learner's first touch
   * of the item, or their previous attempt, to this one. The practice-hours
   * tracker adds these up (progress/practiceTime.ts).
   */
  duration_ms?: number | null
  /**
   * For a Check whose tests ran: the names of those that didn't pass.
   * Checkpoint tests name the skills they check (ADR-0012), so this says
   * which skills a Check missed.
   */
  failing?: string[]
  /** For a review session: how it was rated (ADR-0009). */
  rating?: 'again' | 'hard' | 'good'
  /**
   * Where it happened, when known. An answer given during the placement
   * test isn't practice: it never opens a follow-up or starts a topic
   * (ADR-0021).
   */
  context?: EventContext
}

/** A skill the learner missed and is relearning. */
export type FollowUp = {
  topicId: string
  skillId: string
  /** The day of the most recent miss. */
  missedOn: Day
  /**
   * The items missed that day. Getting one of them right later doesn't
   * count, unless the skill has no other question.
   */
  missedItems: string[]
  /** The days that counted towards relearning it, oldest first. */
  correctOn: Day[]
  /** When it should come back. A right answer before then doesn't count. */
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

/**
 * What follow-ups need to know about a question or exercise: the skills it
 * tests and, for an exercise, its stage. A checkpoint's builds and debug
 * also name the skills each of their tests checks, as "topic/skill", by
 * test name (ADR-0012). A loaded question or exercise has all of these, and
 * so has each entry of the skill index (skillIndex.ts).
 */
export type ItemFacts = {
  skills: string[]
  /** Exercises only: a question has no stage. */
  stage?: Stage
  test_skills?: Record<string, string[]>
}

/** A topic's questions and exercises, by item ID. */
export type TopicItems = Readonly<Record<string, ItemFacts>>

/** Looks up a topic's items; undefined for a topic that isn't known. */
export type ItemsOf = (topicId: string) => TopicItems | undefined

/** One topic's questions and exercises together. */
function itemsOfContent(content: TopicContent): TopicItems {
  return { ...content.exercises, ...content.recall }
}

/** The questions and exercises of loaded topics. */
export function itemsIn(contents: Map<string, TopicContent>): ItemsOf {
  const byTopic = new Map(
    [...contents].map(([topicId, content]) => [
      topicId,
      itemsOfContent(content),
    ]),
  )
  return (topicId) => byTopic.get(topicId)
}

/**
 * An item, if what happens on it says something about its skills. A worked
 * example shows its answer as it goes, so getting it right, or wrong, says
 * nothing about what the learner remembers (ADR-0011, amended 2026-11-11).
 */
function evidenceFrom(
  itemsOf: ItemsOf,
  topicId: string,
  itemId: string,
): ItemFacts | undefined {
  const items = itemsOf(topicId)
  // Object.hasOwn: an item ID like "constructor" isn't one of the items.
  const item = items && Object.hasOwn(items, itemId) ? items[itemId] : undefined
  return item?.stage === 'worked_example' ? undefined : item
}

/**
 * Whether an item can be asked as a follow-up: any question, and fill-in,
 * write and review exercises. Proof checks and worked examples never are.
 */
function canComeBack(item: ItemFacts): boolean {
  return item.stage === undefined || STAGES[item.stage].followUp
}

/** The items a follow-up on a skill can ask, by ID, in order. */
export function candidatesFor(
  items: TopicItems | undefined,
  skillId: string,
): string[] {
  return Object.entries(items ?? {})
    .filter(([, item]) => canComeBack(item) && item.skills.includes(skillId))
    .map(([id]) => id)
    .sort()
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
  // Answers given during the placement test are about topics the learner
  // hasn't studied: they place, they don't open follow-ups (ADR-0021).
  attempts = attempts.filter((attempt) => attempt.context !== 'placement')
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

type TestDay = {
  topicId: string
  itemId: string
  /** The skills the test checks, as "topic/skill". */
  skills: string[]
  test: string
  day: Day
  outcome: 'miss' | 'correct'
}

/**
 * How each test of a checkpoint's builds and debug went on each day
 * (ADR-0012). Like code in itemDays: a test that failed counts as a miss
 * only if no Check passed it that day. A Check whose tests couldn't run
 * says nothing about them.
 */
function testDays(attempts: Attempt[], itemsOf: ItemsOf): TestDay[] {
  const byKey = new Map<string, TestDay>()
  for (const attempt of attempts) {
    const { failing } = attempt
    if (attempt.type !== 'code_check' || failing === undefined) continue
    const tests =
      evidenceFrom(itemsOf, attempt.topic_id, attempt.item_id)?.test_skills ??
      {}
    const day = dayOf(attempt.occurred_at)
    for (const [test, skills] of Object.entries(tests)) {
      const key = [attempt.topic_id, attempt.item_id, test, day].join('\n')
      const passed =
        !failing.includes(test) || byKey.get(key)?.outcome === 'correct'
      byKey.set(key, {
        topicId: attempt.topic_id,
        itemId: attempt.item_id,
        skills,
        test,
        day,
        outcome: passed ? 'correct' : 'miss',
      })
    }
  }
  return [...byKey.values()]
}

/** How a skill went on a day, on one item. */
type SkillEvidence = {
  topicId: string
  skillId: string
  day: Day
  /** The item, named in full ("topic/item") when it's in another topic. */
  item: string
  outcome: 'miss' | 'correct'
}

/**
 * Everything the history says about each skill: from the items that name it,
 * and from the checkpoint tests that name it (ADR-0012).
 */
function skillEvidence(attempts: Attempt[], itemsOf: ItemsOf): SkillEvidence[] {
  const found: SkillEvidence[] = []
  for (const { topicId, itemId, day, outcome } of itemDays(attempts)) {
    const skills = evidenceFrom(itemsOf, topicId, itemId)?.skills ?? []
    for (const skillId of skills) {
      found.push({ topicId, skillId, day, item: itemId, outcome })
    }
  }
  for (const { topicId, itemId, skills, day, outcome } of testDays(
    attempts,
    itemsOf,
  )) {
    for (const ref of skills) {
      const [skillTopic = '', skillId = ''] = ref.split('/')
      found.push({
        topicId: skillTopic,
        skillId,
        day,
        item: `${topicId}/${itemId}`,
        outcome,
      })
    }
  }
  return found
}

/**
 * Whether a day of right answers on a skill moves its follow-up on
 * (ADR-0011, amended 2026-11-11). The day must be on or after the one the
 * follow-up is due, so the growing gaps of 1, 3 and 7 days are kept:
 * otherwise three right days in a row would close it in three days. And a
 * right answer must be on an item other than the ones missed, because
 * answering the same question again can be remembering its answer rather
 * than the rule. A missed item counts only when the skill has no other.
 */
function movesOn(
  followUp: FollowUp,
  day: Day,
  rightOn: Set<string>,
  candidates: string[],
): boolean {
  if (day < followUp.due) return false
  const missed = new Set(followUp.missedItems)
  const nothingElseToAsk = candidates.every((id) => missed.has(id))
  return [...rightOn].some((item) => nothingElseToAsk || !missed.has(item))
}

/**
 * Every skill that's currently being relearned. Day by day, for each skill:
 * a miss opens it (due the next day, and any earlier progress starts over);
 * a right day on another item, once it's due, counts towards closing it
 * (due again 3 days later, then 7); 3 such days close it. Checkpoint tests
 * count for the skills they name (ADR-0012).
 */
export function openFollowUps(
  attempts: Attempt[],
  itemsOf: ItemsOf,
): FollowUp[] {
  type SkillDay = { missed: Set<string>; right: Set<string> }
  const bySkill = new Map<string, Map<Day, SkillDay>>()
  for (const { topicId, skillId, day, item, outcome } of skillEvidence(
    attempts,
    itemsOf,
  )) {
    const key = `${topicId}\n${skillId}`
    const days = bySkill.get(key) ?? new Map<Day, SkillDay>()
    bySkill.set(key, days)
    const skillDay = days.get(day) ?? { missed: new Set(), right: new Set() }
    days.set(day, skillDay)
    if (outcome === 'miss') skillDay.missed.add(item)
    else skillDay.right.add(item)
  }

  const open: FollowUp[] = []
  for (const [key, days] of bySkill) {
    const [topicId = '', skillId = ''] = key.split('\n')
    const candidates = candidatesFor(itemsOf(topicId), skillId)
    let state: FollowUp | null = null
    for (const [day, { missed, right }] of [...days].sort(([a], [b]) =>
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
      } else if (state && movesOn(state, day, right, candidates)) {
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

/** When each item of a topic was last answered or Checked. */
export function lastAttempted(
  attempts: Attempt[],
  topicId: string,
): Map<string, string> {
  const last = new Map<string, string>()
  for (const attempt of attempts) {
    if (attempt.topic_id !== topicId) continue
    if (attempt.occurred_at > (last.get(attempt.item_id) ?? '')) {
      last.set(attempt.item_id, attempt.occurred_at)
    }
  }
  return last
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
  const candidates = candidatesFor(itemsOfContent(content), followUp.skillId)
  const fresh = candidates.filter((id) => !followUp.missedItems.includes(id))
  const pool = fresh.length > 0 ? fresh : candidates

  const lastAnswered = lastAttempted(attempts, followUp.topicId)
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

/** The topics whose full content the cards for these follow-ups need. */
export function topicsToLoad(due: FollowUp[]): string[] {
  return [...new Set(due.map((followUp) => followUp.topicId))].sort()
}
