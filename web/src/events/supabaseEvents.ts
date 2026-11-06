import { getSupabase } from '../supabase/client.ts'
import type { EventsClient } from './sync.ts'

/**
 * HTTP status codes that mean "try again later": 0 is no connection at all,
 * 401 an expired sign-in (it refreshes itself), 408 and 429 a slow or busy
 * server, 5xx a server fault. Anything else means the server refused the
 * data itself.
 */
export function isTemporaryFailure(status: number): boolean {
  return (
    status === 0 ||
    status === 401 ||
    status === 408 ||
    status === 429 ||
    status >= 500
  )
}

/** Stores events in the Supabase events table. */
export function supabaseEventsClient(): EventsClient {
  return {
    async send(events) {
      // "Upsert, ignoring duplicates" is INSERT ... ON CONFLICT DO NOTHING:
      // an event the server already has (a retried upload) is skipped.
      const { error, status } = await getSupabase()
        .from('events')
        .upsert(events, { onConflict: 'id', ignoreDuplicates: true })
      if (!error) return { ok: true }
      return {
        ok: false,
        retryLater: isTemporaryFailure(status),
        message: `${status} ${error.code}: ${error.message}`,
      }
    },
  }
}
