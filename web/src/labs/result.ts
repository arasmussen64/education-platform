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

/**
 * Reads a pasted result for this lab and this revision, or says what's wrong
 * with it. The counts are worked out from the checks, not trusted.
 */
export function parseLabResult(
  text: string,
  lab: string,
  rev: number,
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
  if (raw.rev !== rev) {
    return {
      error:
        `That result is for revision ${raw.rev} of this lab, and this page ` +
        `is revision ${rev}. Start the lab again and rerun the checks.`,
    }
  }
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
