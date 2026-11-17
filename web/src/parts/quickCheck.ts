// "Check what you know" (ADR-0025, amended 2026-11-16): a few quick
// questions from a topic's own practice, before the practice, each on a
// different skill. A skill answered right there marks the practice items
// that test only skills the learner showed as optional. The proofs stay
// required, so nothing about Learned or Mastered changes (ADR-0002).
//
// The answers are ordinary practice answers, saved through the same events
// as any other (context "practice"), with `quick_check: true` in their data
// so they can be told apart. That needs no new event type, and so no
// database change. Which skills the learner showed is worked out from those
// saved answers on every visit, like the rest of progress.
import type { RecallItem, TopicContent } from '../content/types.ts'
import type { Attempt } from '../followups/followUps.ts'

/** The most questions a quick check asks, and the fewest worth offering. */
export const MOST_QUESTIONS = 5
export const FEWEST_QUESTIONS = 3

/** What each quick-check answer carries in its data. */
export const QUICK_CHECK_DATA = { quick_check: true } as const

/**
 * Quick to answer and graded on the spot: multiple choice, predict the
 * output (Python or shell), estimates and typed answers (ADR-0027). Parsons
 * problems take longer to do, so they stay in the practice.
 */
function isQuick(item: RecallItem | undefined): item is RecallItem {
  return (
    item?.type === 'mcq' ||
    item?.type === 'predict_output' ||
    item?.type === 'predict_shell' ||
    item?.type === 'estimate' ||
    item?.type === 'typed'
  )
}

/**
 * The quick check's questions, in ladder order: for each of the topic's
 * skills in turn, the first quick question in its practice that tests it
 * and isn't picked yet, up to five; then, if that's fewer than three, more
 * quick questions to make three. Empty when the practice has fewer than
 * three quick questions, since a check of one or two says little.
 */
export function quickCheckItems(content: TopicContent): string[] {
  const quick = content.topic.practice.filter((itemId) =>
    isQuick(content.recall[itemId]),
  )
  if (quick.length < FEWEST_QUESTIONS) return []
  const picked: string[] = []
  const covered = new Set<string>()
  // Skills the topic lists, then any an item names that the topic doesn't.
  const skills = [
    ...content.topic.skills.map((skill) => skill.id),
    ...quick.flatMap((itemId) => content.recall[itemId]?.skills ?? []),
  ]
  for (const skill of skills) {
    if (picked.length === MOST_QUESTIONS) break
    if (covered.has(skill)) continue
    const itemId = quick.find(
      (each) =>
        !picked.includes(each) &&
        (content.recall[each]?.skills ?? []).includes(skill),
    )
    if (!itemId) continue
    picked.push(itemId)
    for (const each of content.recall[itemId]?.skills ?? []) covered.add(each)
  }
  for (const itemId of quick) {
    if (picked.length >= FEWEST_QUESTIONS) break
    if (!picked.includes(itemId)) picked.push(itemId)
  }
  const order = content.topic.practice
  return picked.sort((a, b) => order.indexOf(a) - order.indexOf(b))
}

/** This topic's quick-check answers, oldest first. */
function quickAnswers(content: TopicContent, attempts: Attempt[]): Attempt[] {
  return attempts
    .filter(
      (attempt) => attempt.quick_check && attempt.topic_id === content.topic.id,
    )
    .toSorted((a, b) => a.occurred_at.localeCompare(b.occurred_at))
}

/** Whether the learner has answered anything in this topic's quick check. */
export function quickCheckTaken(
  content: TopicContent,
  attempts: Attempt[],
): boolean {
  return quickAnswers(content, attempts).length > 0
}

/**
 * The skills the learner showed in this topic's quick check: every skill of
 * a question whose first answer there was right. Only the first counts, as
 * in a review: a second try after seeing the feedback shows less. A wrong
 * answer later, in the practice, doesn't take a skill back; the follow-ups
 * (ADR-0011) bring a missed skill back on their own.
 */
export function shownSkills(
  content: TopicContent,
  attempts: Attempt[],
): Set<string> {
  const shown = new Set<string>()
  const seen = new Set<string>()
  for (const attempt of quickAnswers(content, attempts)) {
    if (seen.has(attempt.item_id)) continue
    seen.add(attempt.item_id)
    if (!attempt.correct) continue
    for (const skill of content.recall[attempt.item_id]?.skills ?? []) {
      shown.add(skill)
    }
  }
  return shown
}

/** The skills a practice item tests, whichever kind it is. */
function skillsOf(content: TopicContent, itemId: string): string[] {
  return (
    content.recall[itemId]?.skills ?? content.exercises[itemId]?.skills ?? []
  )
}

/**
 * Whether a practice item is optional: the learner showed every skill it
 * tests in the quick check. An item that names no skills is never optional.
 */
export function isOptional(
  content: TopicContent,
  itemId: string,
  shown: Set<string>,
): boolean {
  const skills = skillsOf(content, itemId)
  return skills.length > 0 && skills.every((skill) => shown.has(skill))
}
