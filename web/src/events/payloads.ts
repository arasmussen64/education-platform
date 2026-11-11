// The `data` saved with code events (docs/specs/data-model.md, event types).
// Long code and output are cut short, so every event fits the database's
// 16 KB limit.
import type {
  CheckOutcome,
  RunOutcome,
  TraceOutcome,
} from '../python/runner.ts'
import type { EventData } from './types.ts'

export const MAX_CODE_CHARS = 6_000
export const MAX_TEXT_CHARS = 2_000

const CUT_MARKER = '…(cut)'

/**
 * Shortens long text to at most `max` characters, marking where it was cut.
 * The marker counts towards `max`, so the result is never longer.
 */
export function clip(text: string, max: number): string {
  if (text.length <= max) return text
  if (max < CUT_MARKER.length) return text.slice(0, max)
  let end = max - CUT_MARKER.length
  // An emoji is two halves in JavaScript (a "surrogate pair"). Cutting
  // between them leaves half a character, which Postgres refuses, so the
  // whole event would be lost: cut before the pair instead.
  const last = text.charCodeAt(end - 1)
  if (last >= 0xd800 && last <= 0xdbff) end -= 1
  return `${text.slice(0, end)}${CUT_MARKER}`
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

/** A press of Step through (ADR-0022): a run, plus how far it was recorded. */
export function traceEventData(code: string, outcome: TraceOutcome): EventData {
  const data: EventData = {
    code: clip(code, MAX_CODE_CHARS),
    outcome: outcome.kind,
    stepped: true,
  }
  if (outcome.kind === 'failed') {
    data.message = clip(outcome.message, MAX_TEXT_CHARS)
  }
  if (outcome.kind === 'done') {
    const { output, error, waiting_for_input, steps, truncated } = outcome.trace
    data.output = clip(output, MAX_TEXT_CHARS)
    data.error = error === null ? null : clip(error, MAX_TEXT_CHARS)
    data.waiting_for_input = waiting_for_input
    data.steps = steps.length
    data.truncated = truncated
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
