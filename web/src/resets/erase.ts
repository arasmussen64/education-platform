// Starting everything over deletes the learner's history for good
// (ADR-0029, amended 2026-11-22). The browser can't delete events itself:
// the database gives learners no right to. It asks the database's one
// function for this, which deletes the caller's own events and nothing
// else (supabase/migrations/20261122200000_erase_my_history.sql).
import { getSupabase } from '../supabase/client.ts'

/**
 * Deletes every saved event of the signed-in learner. Resolves with how
 * many were deleted; throws if the database refused or couldn't be reached,
 * in which case nothing was deleted.
 */
export async function eraseHistory(): Promise<number> {
  const { data, error } = await getSupabase().rpc('erase_my_history')
  if (error) throw new Error(error.message)
  return data ?? 0
}
