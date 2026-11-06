import { getSupabase } from '../supabase/client.ts'
import type { Attempt } from './followUps.ts'

/** Supabase returns at most 1,000 rows per request, so read in pages. */
export const PAGE_SIZE = 1000

/** An event row as the server or this device stores it. */
type Row = {
  id: string
  type: string
  topic_id: string
  item_id: string | null
  correct: boolean | null
  occurred_at: string
}

/** A graded attempt, if this event is one (an answer, or a Check of code). */
export function toAttempt(row: Row): Attempt | null {
  if (row.type !== 'answer' && row.type !== 'code_check') return null
  if (row.item_id === null || row.correct === null) return null
  return {
    id: row.id,
    type: row.type,
    topic_id: row.topic_id,
    item_id: row.item_id,
    correct: row.correct,
    // The server writes "+00:00" where the browser writes "Z": make them
    // the same, so comparing the text compares the times.
    occurred_at: new Date(row.occurred_at).toISOString(),
  }
}

/** Joins lists of attempts, keeping each event once, oldest first. */
export function mergeAttempts(...lists: Attempt[][]): Attempt[] {
  const byId = new Map<string, Attempt>()
  for (const list of lists) {
    for (const attempt of list) byId.set(attempt.id, attempt)
  }
  return [...byId.values()].sort((a, b) =>
    a.occurred_at.localeCompare(b.occurred_at),
  )
}

/**
 * Every graded attempt the signed-in learner has made, from the server.
 * Row-level security means it can only ever read their own events.
 */
export async function fetchAttempts(): Promise<Attempt[]> {
  const attempts: Attempt[] = []
  for (let from = 0; ; from += PAGE_SIZE) {
    const { data, error } = await getSupabase()
      .from('events')
      .select('id, type, topic_id, item_id, correct, occurred_at')
      .in('type', ['answer', 'code_check'])
      .not('correct', 'is', null)
      .order('occurred_at')
      .order('id')
      .range(from, from + PAGE_SIZE - 1)
    if (error) throw new Error(error.message)
    for (const row of data) {
      const attempt = toAttempt(row)
      if (attempt) attempts.push(attempt)
    }
    if (data.length < PAGE_SIZE) return attempts
  }
}
