// A lab's result (ADR-0018): what tools/labcheck.py prints after `check`,
// which the learner pastes into the lab's box. Only which checks passed
// travels; the reasons stay on the learner's machine.
import type { EventData } from '../events/types.ts'

export type LabResult = {
  /** "topic/exercise". */
  lab: string
  rev: number
  checker: string
  checked_at: string
  passed: number
  total: number
  checks: { id: string; passed: boolean }[]
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value)

const NOT_A_RESULT =
  "That isn't the checker's result. Copy the whole line that starts with " +
  '{"lab", exactly as the checker printed it.'

// A result made before the lab's checks changed, most likely. The second
// sentence is for the case where running check again gives the same line:
// the checker reads the checks from the learner's copy of the repository,
// which can be older than the site.
const OTHER_CHECKS =
  "That result doesn't list the same checks as this lab has now, so it " +
  "can't be recorded. The lab's checks have probably changed since the " +
  'result was made: run the check command again and paste the new line. ' +
  'If the new line is refused too, your copy of the repository is older ' +
  'than this page: update it (git pull) and run the check command again.'

/** What to say about a result made for another revision of the lab. */
function otherRevision(pasted: number, rev: number): string {
  const start = `That result is for revision ${pasted} of this lab, and this page is revision ${rev}. `
  if (pasted > rev) {
    return (
      start +
      'Your copy of the repository is newer than this page. Reload the ' +
      "page; if it still shows the older revision, the site hasn't been " +
      'updated yet.'
    )
  }
  return (
    start +
    'The lab has changed since the result was made. Update your copy of ' +
    'the repository (git pull), begin the lab again by running the start ' +
    'command with --fresh added, and run the checks again.'
  )
}

/**
 * Reads a pasted result for this lab and this revision, or says what's wrong
 * with it. The counts are worked out from the checks, not trusted, and the
 * checks must be exactly the lab's own (`checkIds`, in any order): a result
 * with other checks, or with some missing, records nothing.
 */
export function parseLabResult(
  text: string,
  lab: string,
  rev: number,
  checkIds: string[],
): { result: LabResult } | { error: string } {
  let raw: unknown
  try {
    raw = JSON.parse(text.trim())
  } catch {
    return { error: NOT_A_RESULT }
  }
  if (
    !isRecord(raw) ||
    typeof raw.lab !== 'string' ||
    typeof raw.rev !== 'number' ||
    typeof raw.checker !== 'string' ||
    typeof raw.checked_at !== 'string' ||
    !Array.isArray(raw.checks)
  ) {
    return { error: NOT_A_RESULT }
  }
  if (raw.lab !== lab) {
    return { error: `That result is for another lab (${raw.lab}).` }
  }
  if (raw.rev !== rev) return { error: otherRevision(raw.rev, rev) }
  const checks: LabResult['checks'] = []
  for (const check of raw.checks) {
    if (
      !isRecord(check) ||
      typeof check.id !== 'string' ||
      typeof check.passed !== 'boolean'
    ) {
      return { error: NOT_A_RESULT }
    }
    checks.push({ id: check.id, passed: check.passed })
  }
  if (checks.length === 0) return { error: NOT_A_RESULT }
  // Each of the lab's checks once, and nothing else. Without this, one
  // made-up check that passed would count as the whole lab passing, and a
  // result from before the checks changed would tick the wrong boxes.
  const pasted = new Set(checks.map((check) => check.id))
  const sameChecks =
    checks.length === checkIds.length &&
    pasted.size === checks.length &&
    checkIds.every((id) => pasted.has(id))
  if (!sameChecks) return { error: OTHER_CHECKS }
  return {
    result: {
      lab,
      rev,
      checker: raw.checker,
      checked_at: raw.checked_at,
      passed: checks.filter((check) => check.passed).length,
      total: checks.length,
      checks,
    },
  }
}

/** What a recorded lab result saves with its code_check event. */
export function labEventData(result: LabResult): EventData {
  return {
    runtime: 'lab',
    checker: result.checker,
    checked_at: result.checked_at,
    passed: result.passed,
    total: result.total,
    failing: result.checks.filter((check) => !check.passed).map((c) => c.id),
  }
}
