// Opening a checkpoint's step-by-step help (ADR-0012, amended 2026-11-11).
// The steps hand over most of the build's own program, so once a learner has
// opened them, only a fresh version proves the build (progress/progress.ts).
// To know when that was, opening them is saved as an event: a `hint` event,
// since the steps are help with the build, whose data says it was the steps.
import type { TopicContent } from '../content/types.ts'
import type { EventRow, NewEvent } from '../events/types.ts'
import { PAGE_SIZE } from '../followups/history.ts'
import type { StepsOpened } from '../progress/progress.ts'
import { getSupabase } from '../supabase/client.ts'

/** The `source` in a hint event's data that says it was the steps. */
export const STEPS_SOURCE = 'steps'

/** The event saved when the learner opens a checkpoint's steps. */
export function stepsOpenedEvent(content: TopicContent): NewEvent {
  const build = content.topic.prove.build
  return {
    type: 'hint',
    topic_id: content.topic.id,
    // The steps are help with the build, so the event names the build. The
    // build is a proof check, which is why the context is "prove".
    item_id: build,
    item_rev: build ? content.exercises[build]?.rev : undefined,
    context: 'prove',
    data: { source: STEPS_SOURCE },
  }
}

/** What reading an opening needs from an event. */
type Row = {
  type: string
  topic_id: string
  occurred_at: string
  /** The hint's source, from the event's data. */
  source?: unknown
}

/** The opening this event records, if it records one. */
export function toStepsOpened(row: Row): StepsOpened | null {
  if (row.type !== 'hint' || row.source !== STEPS_SOURCE) return null
  return {
    topic_id: row.topic_id,
    // The server writes "+00:00" where the browser writes "Z": make them the
    // same, so comparing the text compares the times.
    occurred_at: new Date(row.occurred_at).toISOString(),
  }
}

/** The opening an event this device recorded saves, if it saves one. */
export function localStepsOpened(row: EventRow): StepsOpened | null {
  const data =
    row.data !== null &&
    typeof row.data === 'object' &&
    !Array.isArray(row.data)
      ? row.data
      : {}
  return toStepsOpened({ ...row, source: data.source })
}

/**
 * Every time the signed-in learner opened a checkpoint's steps, from the
 * server, oldest first. Row-level security means it can only ever read
 * their own events.
 */
export async function fetchStepsOpened(): Promise<StepsOpened[]> {
  const found: StepsOpened[] = []
  for (let from = 0; ; from += PAGE_SIZE) {
    const { data, error } = await getSupabase()
      .from('events')
      .select('type, topic_id, occurred_at, source:data->>source')
      .eq('type', 'hint')
      .eq('data->>source', STEPS_SOURCE)
      .order('occurred_at')
      .order('id')
      .range(from, from + PAGE_SIZE - 1)
    if (error) throw new Error(error.message)
    for (const row of data) {
      const opened = toStepsOpened(row)
      if (opened) found.push(opened)
    }
    if (data.length < PAGE_SIZE) return found
  }
}
