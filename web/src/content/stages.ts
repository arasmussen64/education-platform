import type { Stage } from './types.ts'

/**
 * How each exercise stage behaves (docs/specs/data-model.md, "How each stage
 * behaves"). Hidden tests show what they check but not why they failed.
 * Hints stand in for the tutor until it exists (Milestone D), so they're only
 * offered where the tutor will be on.
 */
export const STAGES: Record<
  Stage,
  { label: string; hiddenTests: boolean; hints: boolean }
> = {
  worked_example: { label: 'Worked example', hiddenTests: false, hints: true },
  fill_in: { label: 'Fill in the gaps', hiddenTests: false, hints: true },
  write: { label: 'Write it', hiddenTests: false, hints: true },
  build: { label: 'Build', hiddenTests: true, hints: false },
  debug: { label: 'Debug', hiddenTests: false, hints: false },
  review_code: { label: 'Review', hiddenTests: true, hints: false },
}
