// Choices for a checkpoint's way through, for a learner who's stuck
// (ADR-0012).
import { type Attempt, lastAttempted } from '../followups/followUps.ts'

/**
 * After this many failing Checks on a checkpoint's build, the page suggests
 * trying it in steps. It never opens them by itself: some struggle helps,
 * and the learner decides.
 */
export const SUGGEST_STEPS_AFTER = 2

/**
 * The fresh version of a checkpoint's build to offer: one the learner hasn't
 * Checked yet, else the one Checked longest ago, so a second try is fresh
 * too. Ties keep their order in topic.yaml.
 */
export function chooseVersion(
  topicId: string,
  versions: string[],
  attempts: Attempt[],
): string | null {
  const last = lastAttempted(attempts, topicId)
  const sorted = [...versions].sort((a, b) =>
    (last.get(a) ?? '').localeCompare(last.get(b) ?? ''),
  )
  return sorted[0] ?? null
}
