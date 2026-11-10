// Learner events (ADR-0008, docs/specs/data-model.md "events"). Every
// meaningful action becomes one row of the append-only events table.
import type { Database, Json } from '../supabase/database.types.ts'

export type EventType =
  | 'lesson_view'
  | 'answer'
  | 'code_run'
  | 'code_check'
  | 'explain_submit'
  | 'hint'
  | 'review'
  /** A finished placement run (ADR-0021): what it found. */
  | 'placement'

/**
 * Where an event happened. Answers given during the placement test carry
 * 'placement': they aren't practice and don't start a topic (ADR-0021).
 */
export type EventContext =
  'learn' | 'practice' | 'prove' | 'review' | 'placement'

/** Details for one event type, saved as the row's `data` (at most 16 KB). */
export type EventData = { [key: string]: Json | undefined }

/** What a page reports. The event log adds who, when, and which session. */
export type NewEvent = {
  type: EventType
  topic_id: string
  context: EventContext
  /** The item's ID within its topic; leave out for topic-level events. */
  item_id?: string
  /** The item's `rev` when it was answered. */
  item_rev?: number
  /** For graded events. */
  correct?: boolean
  duration_ms?: number | null
  hints_used?: number
  data?: EventData
}

type EventsInsert = Database['public']['Tables']['events']['Insert']

/**
 * One row of the events table, exactly as it's sent: every column except
 * received_at, which only the server sets. Built from the generated database
 * types, so a renamed column fails type-checking here.
 */
export type EventRow = Required<
  Omit<EventsInsert, 'received_at' | 'type' | 'context'>
> & { type: EventType; context: EventContext }
