// How sure the learner said they were before a quick question was checked
// (ADR-0028), and how well that matches how often they were right. It's
// saved in the answer event's data as `confidence`, and changes no grade.
import type { EventRow } from '../events/types.ts'
import { getSupabase } from '../supabase/client.ts'

export type Confidence = 'guess' | 'fair' | 'sure'

/** Least sure first: the order of the buttons and of the summary. */
export const CONFIDENCES: readonly Confidence[] = ['guess', 'fair', 'sure']

/** What each button says. */
export const CONFIDENCE_LABELS: Record<Confidence, string> = {
  guess: 'Guessing',
  fair: 'Fairly sure',
  sure: 'Certain',
}

export function isConfidence(value: unknown): value is Confidence {
  return value === 'guess' || value === 'fair' || value === 'sure'
}

/** One answer given with a confidence: what's needed to summarise it. */
export type RatedAnswer = {
  id: string
  confidence: Confidence
  correct: boolean
}

/** How often the learner was right at one level. */
export type Level = { confidence: Confidence; answers: number; right: number }

/**
 * How many answers a level needs before its share is shown: below this, one
 * answer more or less swings it by 20 points or more.
 */
export const FEWEST_ANSWERS = 5

/** Each level's answers and how many were right, least sure first. */
export function calibration(answers: RatedAnswer[]): Level[] {
  return CONFIDENCES.map((confidence) => {
    const at = answers.filter((answer) => answer.confidence === confidence)
    return {
      confidence,
      answers: at.length,
      right: at.filter((answer) => answer.correct).length,
    }
  })
}

/** "When you're certain", "when you're fairly sure", "when you guess". */
const WHEN: Record<Confidence, string> = {
  guess: 'When you guess',
  fair: "When you're fairly sure",
  sure: "When you're certain",
}

/**
 * The sentence for one level: "When you're certain, you're right 92% of
 * the time (25 answers)." Null while it has too few answers to say.
 */
export function levelSentence(level: Level): string | null {
  if (level.answers < FEWEST_ANSWERS) return null
  const percent = Math.round((100 * level.right) / level.answers)
  return `${WHEN[level.confidence]}, you're right ${percent}% of the time (${level.answers} answers).`
}

/** An answer event's confidence and result, if it has both. */
function rated(
  id: string,
  correct: boolean | null,
  confidence: unknown,
): RatedAnswer | null {
  if (correct === null || !isConfidence(confidence)) return null
  return { id, confidence, correct }
}

/**
 * The rated answers among events this browser holds (not yet saved). With
 * `since`, only those from that time on: the learner started everything
 * over then (ADR-0029).
 */
export function localRatedAnswers(
  rows: EventRow[],
  since?: string,
): RatedAnswer[] {
  return rows.flatMap((row) => {
    if (row.type !== 'answer') return []
    if (since !== undefined && row.occurred_at < since) return []
    const data =
      row.data !== null &&
      typeof row.data === 'object' &&
      !Array.isArray(row.data)
        ? row.data
        : {}
    const answer = rated(row.id, row.correct, data.confidence)
    return answer ? [answer] : []
  })
}

/** Supabase returns at most 1,000 rows per request, so read in pages. */
const PAGE_SIZE = 1000

/**
 * Every answer the signed-in learner gave with a confidence, from the
 * server. With `since`, only those from that time on. Row-level security
 * means it can only read their own events.
 */
export async function fetchRatedAnswers(
  since?: string,
): Promise<RatedAnswer[]> {
  const answers: RatedAnswer[] = []
  for (let from = 0; ; from += PAGE_SIZE) {
    let query = getSupabase()
      .from('events')
      .select('id, correct, confidence:data->>confidence')
      .eq('type', 'answer')
      .not('correct', 'is', null)
      .not('data->>confidence', 'is', null)
    if (since !== undefined) query = query.gte('occurred_at', since)
    const { data, error } = await query
      .order('occurred_at')
      .order('id')
      .range(from, from + PAGE_SIZE - 1)
    if (error) throw new Error(error.message)
    for (const row of data) {
      const answer = rated(row.id, row.correct, row.confidence)
      if (answer) answers.push(answer)
    }
    if (data.length < PAGE_SIZE) return answers
  }
}

/** Joins the server's answers and this browser's, each event once. */
export function mergeRated(...lists: RatedAnswer[][]): RatedAnswer[] {
  const byId = new Map<string, RatedAnswer>()
  for (const list of lists)
    for (const answer of list) byId.set(answer.id, answer)
  return [...byId.values()]
}
