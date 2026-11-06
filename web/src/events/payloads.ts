// The `data` saved with code events (docs/specs/data-model.md, event types).
// Long code and output are cut short, so every event fits the database's
// 16 KB limit.
import type { CheckOutcome, RunOutcome } from '../python/runner.ts'
import type { EventData } from './types.ts'

export const MAX_CODE_CHARS = 6_000
export const MAX_TEXT_CHARS = 2_000

/** Shortens long text, marking where it was cut. */
export function clip(text: string, max: number): string {
  return text.length <= max ? text : `${text.slice(0, max)}…(cut)`
}

/** A press of Run: the code and what it printed. */
export function runEventData(code: string, outcome: RunOutcome): EventData {
  const data: EventData = {
    code: clip(code, MAX_CODE_CHARS),
    outcome: outcome.kind,
  }
  if (outcome.kind === 'failed') {
    data.message = clip(outcome.message, MAX_TEXT_CHARS)
  }
  if (outcome.kind === 'done') {
    const { output, error, waiting_for_input } = outcome.result
    data.output = clip(output, MAX_TEXT_CHARS)
    data.error = error === null ? null : clip(error, MAX_TEXT_CHARS)
    data.waiting_for_input = waiting_for_input
  }
  return data
}

/** A press of Check: the code, how many tests passed, and which failed. */
export function checkEventData(code: string, outcome: CheckOutcome): EventData {
  const data: EventData = {
    code: clip(code, MAX_CODE_CHARS),
    outcome: outcome.kind,
  }
  if (outcome.kind === 'failed') {
    data.message = clip(outcome.message, MAX_TEXT_CHARS)
  }
  if (outcome.kind === 'done') {
    const { status, message, passed, total, results } = outcome.report
    data.status = status
    data.passed = passed
    data.total = total
    data.failing = results
      .filter((result) => result.outcome !== 'pass')
      .map((result) => result.name)
    if (status === 'error') data.message = clip(message, MAX_TEXT_CHARS)
  }
  return data
}
