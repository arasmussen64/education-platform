import { savedCheckCouldNotRun } from '../events/checkGrade.ts'
import type { EventContext, EventRow } from '../events/types.ts'
import { getSupabase } from '../supabase/client.ts'
import type { Attempt } from './followUps.ts'

/** Supabase returns at most 1,000 rows per request, so read in pages. */
export const PAGE_SIZE = 1000

/** What an attempt needs from an event: its columns, and some of its data. */
type Row = {
  id: string
  type: string
  topic_id: string
  item_id: string | null
  correct: boolean | null
  occurred_at: string
  duration_ms?: number | null
  context?: string
  /** A Check's status: "ok" when its tests ran. */
  status?: unknown
  /** The names of a Check's tests that didn't pass. */
  failing?: unknown
  /** A review session's rating: "again", "hard" or "good". */
  rating?: unknown
  /** How a Check went: "done", or "failed" when it couldn't run. */
  outcome?: unknown
  /** A Check's message, when its tests or the learner's code couldn't load. */
  message?: unknown
  /** How many tests a Check ran. */
  total?: unknown
  /** The learner's own calendar day, recorded since 2026-11-11. */
  local_day?: unknown
}

function isTextList(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string')
}

function isRating(value: unknown): value is 'again' | 'hard' | 'good' {
  return value === 'again' || value === 'hard' || value === 'good'
}

const CONTEXTS: readonly string[] = [
  'learn',
  'practice',
  'prove',
  'review',
  'placement',
] satisfies EventContext[]

function isContext(value: unknown): value is EventContext {
  return typeof value === 'string' && CONTEXTS.includes(value)
}

/** The event types that count as graded attempts. */
export const ATTEMPT_TYPES = [
  'answer',
  'code_check',
  'explain_submit',
  'review',
] as const

/**
 * A graded attempt, if this event is one: an answer, a Check of code, a
 * graded explanation, or a finished review session.
 */
export function toAttempt(row: Row): Attempt | null {
  if (!(ATTEMPT_TYPES as readonly string[]).includes(row.type)) return null
  if (row.item_id === null || row.correct === null) return null
  // A review session without a rating can't be used, so it's left out.
  if (row.type === 'review' && !isRating(row.rating)) return null
  // A Check that couldn't run says nothing about the learner's code. Those
  // saved before 2026-11-11 were marked wrong; the log keeps them as they
  // are, and here they're left out (ADR-0008, amended 2026-11-11).
  if (row.type === 'code_check' && savedCheckCouldNotRun(row)) return null
  const attempt: Attempt = {
    id: row.id,
    type: row.type as Attempt['type'],
    topic_id: row.topic_id,
    item_id: row.item_id,
    correct: row.correct,
    // The server writes "+00:00" where the browser writes "Z": make them
    // the same, so comparing the text compares the times.
    occurred_at: new Date(row.occurred_at).toISOString(),
  }
  if (typeof row.duration_ms === 'number') attempt.duration_ms = row.duration_ms
  if (isContext(row.context)) attempt.context = row.context
  if (typeof row.local_day === 'string') attempt.local_day = row.local_day
  if (row.type === 'review' && isRating(row.rating)) {
    attempt.rating = row.rating
  }
  // Checkpoint tests name the skills they check, so which tests failed says
  // which skills were missed (ADR-0012). Only when the tests ran.
  if (
    row.type === 'code_check' &&
    row.status === 'ok' &&
    isTextList(row.failing)
  ) {
    attempt.failing = row.failing
  }
  return attempt
}

/** An attempt from an event this device recorded, which has all its data. */
export function localAttempt(row: EventRow): Attempt | null {
  const data =
    row.data !== null &&
    typeof row.data === 'object' &&
    !Array.isArray(row.data)
      ? row.data
      : {}
  return toAttempt({
    ...row,
    status: data.status,
    failing: data.failing,
    rating: data.rating,
    outcome: data.outcome,
    message: data.message,
    total: data.total,
    local_day: data.local_day,
  })
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
 * Every graded attempt the signed-in learner has made, from the server: all
 * of them, or only those in one topic. Row-level security means it can only
 * ever read their own events.
 */
export async function fetchAttempts(topicId?: string): Promise<Attempt[]> {
  const attempts: Attempt[] = []
  for (let from = 0; ; from += PAGE_SIZE) {
    let query = getSupabase()
      .from('events')
      .select(
        'id, type, topic_id, item_id, correct, occurred_at, duration_ms, context, status:data->>status, failing:data->failing, rating:data->>rating, outcome:data->>outcome, message:data->>message, total:data->total, local_day:data->>local_day',
      )
      .in('type', [...ATTEMPT_TYPES])
      .not('correct', 'is', null)
    if (topicId !== undefined) query = query.eq('topic_id', topicId)
    const { data, error } = await query
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
