// Starting a track over (ADR-0029). A learner who wants a clean start on a
// track records one `track_reset` event naming the track. Nothing is ever
// deleted (ADR-0008): the progress derivation just stops counting that
// track's events from before the newest reset, so every topic in it is back
// to not started. The full history stays in the log for the ML capstone.
//
// Starting everything over (ADR-0029, amended 2026-11-22) is the same event
// with EVERYTHING where the track's id would be. Nothing at all from before
// it counts: every track, and what describes the learner too (practice
// hours, weeks, the forgetting curve, how sure they are).
import { placeOf } from '../content/content.ts'
import type { EventRow, NewEvent } from '../events/types.ts'
import { getSupabase } from '../supabase/client.ts'

/** The event type that starts a track over. */
export const TRACK_RESET = 'track_reset'

/** One time the learner started a track over. */
export type TrackReset = {
  /** The track's id, like `python-foundations`. */
  track: string
  /** In ISO format, UTC, so comparing the text compares the times. */
  occurred_at: string
}

/**
 * What stands in the track's place when the learner starts everything over.
 * No track may have this id (a test checks).
 */
export const EVERYTHING = 'everything'

/**
 * The newest reset of each track, by track id. The newest time everything
 * was started over, if it ever was, is under EVERYTHING.
 */
export type Resets = Map<string, string>

/** No track has been started over. */
export const NO_RESETS: Resets = new Map()

/** The event recorded when the learner starts this track over. */
export function trackResetEvent(trackId: string): NewEvent {
  // The track's id stands in the topic column, the way a placement's does
  // (ADR-0021). The context is 'learn': a reset isn't practice, a proof or
  // a review, and no new context is needed for it.
  return { type: TRACK_RESET, topic_id: trackId, context: 'learn' }
}

/** The event recorded when the learner starts everything over. */
export function everythingResetEvent(): NewEvent {
  return trackResetEvent(EVERYTHING)
}

/** When the learner last started everything over, if they ever did. */
export function freshStart(resets: Resets): string | undefined {
  return resets.get(EVERYTHING)
}

/**
 * The events since the learner last started everything over, whatever
 * their track. Returns the same list when they never did.
 */
export function sinceFreshStart<T extends { occurred_at: string }>(
  events: T[],
  resets: Resets,
): T[] {
  const start = freshStart(resets)
  if (start === undefined) return events
  return events.filter((event) => event.occurred_at >= start)
}

type Row = { type: string; topic_id: string; occurred_at: string }

/** The reset this event records, if it records one. */
export function toReset(row: Row): TrackReset | null {
  if (row.type !== TRACK_RESET) return null
  return {
    track: row.topic_id,
    // The server writes "+00:00" where the browser writes "Z": make them the
    // same, so comparing the text compares the times.
    occurred_at: new Date(row.occurred_at).toISOString(),
  }
}

/** The resets among events this device recorded. */
export function localResets(rows: EventRow[]): TrackReset[] {
  return rows.map(toReset).filter((reset) => reset !== null)
}

/** The newest reset of each track, from any number of lists. */
export function latestResets(...lists: TrackReset[][]): Resets {
  const latest: Resets = new Map()
  for (const reset of lists.flat()) {
    const current = latest.get(reset.track)
    if (!current || reset.occurred_at > current) {
      latest.set(reset.track, reset.occurred_at)
    }
  }
  return latest
}

/**
 * Whether something that happened at `occurred_at` on this track was
 * before the track's newest reset, and so no longer counts. A topic that
 * belongs to no track (an id the content doesn't know) is never reset by a
 * track's reset. Starting everything over resets it all, track or no track.
 */
export function wasReset(
  trackId: string | undefined,
  occurred_at: string,
  resets: Resets,
): boolean {
  const start = freshStart(resets)
  if (start !== undefined && occurred_at < start) return true
  if (trackId === undefined) return false
  const reset = resets.get(trackId)
  return reset !== undefined && occurred_at < reset
}

/** The track a topic belongs to, if the content knows it. */
export function trackOfTopic(topicId: string): string | undefined {
  return placeOf(topicId)?.track.id
}

/**
 * The events that still count: every one whose topic's track hasn't been
 * started over since. Attempts, checkpoint steps opened, anything with a
 * topic and a time. Returns the same list when there are no resets, so
 * nothing downstream has to work anything out again.
 */
export function afterResets<
  T extends { topic_id: string; occurred_at: string },
>(
  events: T[],
  resets: Resets,
  trackOf: (topicId: string) => string | undefined = trackOfTopic,
): T[] {
  if (resets.size === 0) return events
  return events.filter(
    (event) => !wasReset(trackOf(event.topic_id), event.occurred_at, resets),
  )
}

/**
 * Every time the signed-in learner started a track over, from the server.
 * There are only ever a handful, so one page is enough. Row-level security
 * means it can only ever read their own events.
 */
export async function fetchResets(): Promise<TrackReset[]> {
  const { data, error } = await getSupabase()
    .from('events')
    .select('type, topic_id, occurred_at')
    .eq('type', TRACK_RESET)
    .order('occurred_at')
    .limit(1000)
  if (error) throw new Error(error.message)
  return data.map(toReset).filter((reset) => reset !== null)
}

/**
 * The track a placement subject belongs to: a track's own id, or the track
 * of a module's foundations list. A diagnostic, like math, measures the
 * learner rather than a track, so no track's reset clears it (ADR-0029).
 * Only starting everything over does.
 */
export function trackOfPlacement(record: {
  subject: string
  kind: 'track' | 'diagnostic' | 'foundations'
  list?: { track: string }
}): string | undefined {
  if (record.kind === 'track') return record.subject
  if (record.kind === 'foundations') return record.list?.track
  return undefined
}
