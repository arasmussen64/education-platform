// What the placement test found, read back from the event log (ADR-0021).
// A finished run is one `placement` event; nothing else is stored, so the
// Today page and the placement page both read the same thing.
import type { EventRow } from '../events/types.ts'
import { getSupabase } from '../supabase/client.ts'

export type PlacementKind = 'track' | 'diagnostic'

/** One finished placement run. */
export type PlacementRecord = {
  /** The event's id. */
  id: string
  /** The run's id, shared with the answers given during it. */
  run: string
  /** A track's id, or `diagnostic.<id>` for a diagnostic like math. */
  subject: string
  kind: PlacementKind
  /** When it finished, in ISO format, UTC. */
  at: string
  /** The topics or levels, in order, that count as known. */
  known: string[]
  /** The first that doesn't: where to start. Null when all are known. */
  next: string | null
  asked: number
  correct: number
}

/** The events' topic_id for a diagnostic, which has no topic of its own. */
export function subjectOfDiagnostic(diagnosticId: string): string {
  return `diagnostic.${diagnosticId}`
}

/** The diagnostic's id behind a subject, or null for a track's. */
export function diagnosticOfSubject(subject: string): string | null {
  return subject.startsWith('diagnostic.')
    ? subject.slice('diagnostic.'.length)
    : null
}

type Row = {
  id: string
  type: string
  topic_id: string
  occurred_at: string
  data: unknown
}

function isTextList(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string')
}

/** The record in a `placement` event, if the row is one and is whole. */
export function toPlacementRecord(row: Row): PlacementRecord | null {
  if (row.type !== 'placement') return null
  const data =
    row.data !== null &&
    typeof row.data === 'object' &&
    !Array.isArray(row.data)
      ? (row.data as Record<string, unknown>)
      : {}
  const { run, kind, known, next, asked, correct } = data
  if (typeof run !== 'string') return null
  if (kind !== 'track' && kind !== 'diagnostic') return null
  if (!isTextList(known)) return null
  if (next !== null && typeof next !== 'string') return null
  return {
    id: row.id,
    run,
    subject: row.topic_id,
    kind,
    at: new Date(row.occurred_at).toISOString(),
    known,
    next: next ?? null,
    asked: typeof asked === 'number' ? asked : 0,
    correct: typeof correct === 'number' ? correct : 0,
  }
}

/** The records among events this device recorded. */
export function localPlacements(rows: EventRow[]): PlacementRecord[] {
  return rows.map(toPlacementRecord).filter((record) => record !== null)
}

/** The newest record for each subject. */
export function latestBySubject(
  records: PlacementRecord[],
): Map<string, PlacementRecord> {
  const latest = new Map<string, PlacementRecord>()
  for (const record of records) {
    const current = latest.get(record.subject)
    if (!current || record.at > current.at) latest.set(record.subject, record)
  }
  return latest
}

/** Joins lists of records, keeping each event once, oldest first. */
export function mergePlacements(
  ...lists: PlacementRecord[][]
): PlacementRecord[] {
  const byId = new Map<string, PlacementRecord>()
  for (const list of lists) {
    for (const record of list) byId.set(record.id, record)
  }
  return [...byId.values()].sort((a, b) => a.at.localeCompare(b.at))
}

/**
 * Every finished placement of the signed-in learner, from the server. There
 * are only ever a handful, so one page is enough.
 */
export async function fetchPlacements(): Promise<PlacementRecord[]> {
  const { data, error } = await getSupabase()
    .from('events')
    .select('id, type, topic_id, occurred_at, data')
    .eq('type', 'placement')
    .order('occurred_at')
    .limit(1000)
  if (error) throw new Error(error.message)
  return data.map(toPlacementRecord).filter((record) => record !== null)
}
