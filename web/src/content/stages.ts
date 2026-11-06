import type { Stage } from './types.ts'

/**
 * How each exercise stage behaves (docs/specs/data-model.md, "How each stage
 * behaves"). Hidden tests show what they check but not why they failed.
 * Hints stand in for the tutor until it exists (Milestone D), so they're only
 * offered where the tutor will be on. `followUp` stages can come back after a
 * miss (ADR-0011); proof checks and worked examples never do.
 */
export const STAGES: Record<
  Stage,
  { label: string; hiddenTests: boolean; hints: boolean; followUp: boolean }
> = {
  worked_example: {
    label: 'Worked example',
    hiddenTests: false,
    hints: true,
    followUp: false,
  },
  fill_in: {
    label: 'Fill in the gaps',
    hiddenTests: false,
    hints: true,
    followUp: true,
  },
  write: { label: 'Write it', hiddenTests: false, hints: true, followUp: true },
  build: { label: 'Build', hiddenTests: true, hints: false, followUp: false },
  debug: { label: 'Debug', hiddenTests: false, hints: false, followUp: false },
  review_code: {
    label: 'Review',
    hiddenTests: true,
    hints: false,
    followUp: true,
  },
}
