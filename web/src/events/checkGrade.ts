// Whether a press of Check counts as right, as wrong, or not at all.
//
// A Check is saved as a graded attempt, and a wrong one opens a follow-up
// (ADR-0011) and lowers a review's rating (ADR-0009). So it may only count
// against the learner when it says something about their code. When it
// couldn't run for a reason of the platform's (Python didn't start, the
// network failed, the exercise itself is broken), it's saved with no
// verdict, the way an explanation that couldn't be graded is, and the
// learner can simply try again.
import { allChecksPassed, type CheckOutcome } from '../python/runner.ts'

/**
 * How the harness begins its message when an exercise's own tests couldn't
 * be loaded (harness/testrunner.py). That's a fault in the exercise, not in
 * the learner's code. A test checks the harness still says it.
 */
export const TESTS_NOT_LOADED = "The tests couldn't be loaded."

/** True when a Check couldn't say anything about the learner's code. */
export function checkCouldNotRun(outcome: CheckOutcome): boolean {
  // Python didn't start, the topic's packages didn't load (or took too
  // long), or the worker crashed: the runner reports all of these as
  // "failed". It's almost always the device or the network.
  if (outcome.kind === 'failed') return true
  // The code ran past its time limit. That's usually a loop that never
  // ends, which is the learner's own result, so it counts.
  if (outcome.kind === 'timeout') return false
  const { report } = outcome
  if (report.status === 'error') {
    // The tests couldn't be loaded: the exercise's fault. Otherwise the
    // learner's code couldn't be loaded, which is theirs.
    return report.message.startsWith(TESTS_NOT_LOADED)
  }
  // An exercise with no tests can't be passed or failed.
  return report.total === 0
}

/**
 * What to save as a Check's `correct`: whether every test passed, or
 * undefined (saved as no verdict) when the Check couldn't run.
 */
export function checkCorrect(outcome: CheckOutcome): boolean | undefined {
  return checkCouldNotRun(outcome) ? undefined : allChecksPassed(outcome)
}

/**
 * The parts of a saved Check's data (checkEventData in payloads.ts) that
 * say how it went. Data read back from storage could hold anything, so each
 * part is unknown until it's looked at.
 */
export type SavedCheck = {
  outcome?: unknown
  status?: unknown
  message?: unknown
  total?: unknown
}

/**
 * The same rule as checkCouldNotRun, for a Check that's already saved.
 * Checks saved before 2026-11-11 were marked wrong even when they couldn't
 * run, and the log is never rewritten, so the code that turns events into
 * attempts can ask this to leave them out instead. Data it can't read
 * counts as a Check that ran, as it always has.
 */
export function savedCheckCouldNotRun(data: SavedCheck): boolean {
  if (data.outcome === 'failed') return true
  if (data.outcome !== 'done') return false
  if (data.status === 'error') {
    return (
      typeof data.message === 'string' &&
      data.message.startsWith(TESTS_NOT_LOADED)
    )
  }
  return data.status === 'ok' && data.total === 0
}
