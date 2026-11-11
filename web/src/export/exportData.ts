import { APP_NAME } from '../config.ts'
import { dayOf } from '../days.ts'
import type { EventLog } from '../events/eventLog.ts'
import type { RefusedEvent } from '../events/outbox.ts'
import type { EventRow } from '../events/types.ts'
import { getSupabase } from '../supabase/client.ts'
import type { Tables } from '../supabase/database.types.ts'

// "Export my data" (v1 spec, F16): everything a learner has done here, as
// one JSON file, for backups and for the ML capstone. The file's layout is
// described in docs/specs/data-model.md ("The export file").

/**
 * The file's layout version. Adding a field doesn't change it. Change it
 * when an existing field changes meaning, so scripts reading older files can
 * tell them apart.
 */
export const EXPORT_FORMAT = 1

/** Rows to ask for at a time. Supabase sends at most 1,000 per request. */
export const PAGE_SIZE = 1000

/** One event as the server stores it. */
type SavedEvent = Tables<'events'>

/** One event in the file. */
export type ExportedEvent = Omit<SavedEvent, 'received_at'> & {
  /**
   * When the server received the event. Null if it hadn't yet: the event
   * came from this browser's outbox.
   */
  received_at: string | null
}

/**
 * An event the server refused, in the file. It's kept apart from `events`
 * because it isn't part of the saved history: it exists only in the browser
 * that made the file, which keeps trying to save it.
 */
export type ExportedRefusedEvent = {
  /** What the server said the last time the event was tried. */
  reason: string
  last_tried_at: string
  /** How many times the server has refused it. */
  attempts: number
  /** The event itself, exactly as it was sent. */
  event: EventRow
}

export type DataExport = {
  format: number
  exported_at: string
  /** The git commit the app that made this file was built from. */
  content_build: string
  user_id: string
  profile: Tables<'profiles'> | null
  /** Every event, oldest first. */
  events: ExportedEvent[]
  /** Events the server refused, which only this browser holds. */
  refused_events: ExportedRefusedEvent[]
}

/**
 * The learner's events that only this browser has: the ones waiting in its
 * outbox, and the ones the server refused. The event log supplies both.
 */
export type ThisBrowsersEvents = Pick<
  EventLog,
  'getPendingRows' | 'getRefusedEvents'
>

/** Gathers everything the signed-in learner has done. */
export async function collectExport(
  userId: string,
  browser: ThisBrowsersEvents,
  now = Date.now(),
): Promise<DataExport> {
  // This browser first, then the server. An event sent in between is on the
  // server by the time we ask, and an event sent later is still in our copy
  // of the outbox. Either way, none can fall through the gap.
  const pending = browser.getPendingRows()
  const refused = browser.getRefusedEvents()
  const [profile, saved] = await Promise.all([
    fetchProfile(userId),
    fetchEvents(userId),
  ])
  return {
    format: EXPORT_FORMAT,
    exported_at: new Date(now).toISOString(),
    content_build: __CONTENT_BUILD__,
    user_id: userId,
    profile,
    events: mergeEvents(saved, pending),
    refused_events: stillRefused(refused, saved),
  }
}

/**
 * The refused events for the file. One that the server has after all (it was
 * accepted on another try while we were reading) is left out here, because
 * it's already in `events`.
 */
function stillRefused(
  refused: RefusedEvent[],
  saved: SavedEvent[],
): ExportedRefusedEvent[] {
  const onServer = new Set(saved.map((event) => event.id))
  return refused
    .filter(({ event }) => !onServer.has(event.id))
    .map(({ event, reason, at, attempts }) => ({
      reason,
      last_tried_at: at,
      attempts,
      event,
    }))
}

async function fetchProfile(userId: string) {
  const { data, error } = await getSupabase()
    .from('profiles')
    .select('*')
    .eq('id', userId)
    .maybeSingle()
  if (error) throw new Error(error.message)
  return data
}

/**
 * Every event the server has for this learner, a page at a time.
 *
 * It stops at the first empty page, not the first short one, so it still
 * reads everything if the server sends fewer rows than asked for.
 *
 * If an event from another device arrives meanwhile with an earlier time,
 * the later pages shift along by one and an event is read twice.
 * mergeEvents keeps it once. None can be skipped, because events are never
 * deleted.
 */
async function fetchEvents(userId: string): Promise<SavedEvent[]> {
  const events: SavedEvent[] = []
  let page: SavedEvent[]
  do {
    const { data, error } = await getSupabase()
      .from('events')
      .select('*')
      // Row-level security already limits this to the learner's own events.
      .eq('user_id', userId)
      .order('occurred_at')
      .order('id')
      .range(events.length, events.length + PAGE_SIZE - 1)
    if (error) throw new Error(error.message)
    page = data
    events.push(...page)
  } while (page.length > 0)
  return events
}

/**
 * The server's events and the outbox's together, each once, oldest first.
 * An event that's only in the outbox has no received_at yet.
 */
export function mergeEvents(
  saved: SavedEvent[],
  pending: EventRow[],
): ExportedEvent[] {
  const byId = new Map<string, ExportedEvent>()
  for (const event of pending) {
    byId.set(event.id, { ...event, received_at: null })
  }
  // An event in both places keeps the server's copy, which has received_at.
  for (const event of saved) byId.set(event.id, event)
  return [...byId.values()].sort(
    // By time; events from the same moment by ID, so the order never varies.
    (a, b) =>
      Date.parse(a.occurred_at) - Date.parse(b.occurred_at) ||
      a.id.localeCompare(b.id),
  )
}

/** The app's name, "data" and the local date, like "<name>-data-2026-11-07.json". */
export function exportFileName(now = Date.now()): string {
  const name = APP_NAME.toLowerCase().replace(/[^a-z0-9]+/g, '-')
  return `${name}-data-${dayOf(now)}.json`
}
