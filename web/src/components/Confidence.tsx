import type { Ref } from 'react'
import {
  type Confidence,
  CONFIDENCE_LABELS,
  CONFIDENCES,
} from '../confidence/confidence.ts'
import { BUTTON } from './styles.ts'

type ButtonsProps = {
  /** Called with the level the learner pressed: that press checks the answer. */
  onPick: (confidence: Confidence) => void
  /** True until there's an answer to check. */
  disabled?: boolean
  /** The first button, for a box whose Enter moves focus here. */
  firstRef?: Ref<HTMLButtonElement>
}

/**
 * The Check of a quick question, split in three (ADR-0028): the learner
 * says how sure they are, and that press checks the answer. Plain buttons
 * in the tab order, so Tab reaches each and Enter or Space presses it.
 * They never submit a form: a form's Enter would otherwise press the first
 * of them, "Guessing", for the learner.
 */
export function ConfidenceButtons({
  onPick,
  disabled = false,
  firstRef,
}: ButtonsProps) {
  return (
    // A fieldset, so a screen reader names the three buttons' group by its
    // legend: "How sure are you? Pick one to check."
    <fieldset className="m-0 min-w-0 space-y-1 border-0 p-0">
      <legend className="mb-1 p-0 text-sm font-medium">
        How sure are you? Pick one to check.
      </legend>
      <div className="flex flex-wrap gap-2">
        {CONFIDENCES.map((confidence, index) => (
          <button
            key={confidence}
            ref={index === 0 ? firstRef : undefined}
            type="button"
            disabled={disabled}
            onClick={() => onPick(confidence)}
            className={BUTTON}
          >
            {CONFIDENCE_LABELS[confidence]}
          </button>
        ))}
      </div>
    </fieldset>
  )
}

/**
 * One line after the answer that uses how sure the learner said they were
 * (ADR-0028), or nothing. Being certain and wrong is the mistake that sticks
 * best once it's corrected (hypercorrection), if the learner reads why. A
 * right guess isn't known yet, so it's worth reading why too.
 */
export function ConfidenceNote({
  confidence,
  correct,
}: {
  confidence: Confidence | null
  correct: boolean
}) {
  if (confidence === 'sure' && !correct) {
    return (
      <p className="rounded-md border-l-4 border-sky-500 bg-card px-3 py-2 text-sm">
        You were certain, and it's wrong. That's the kind of mistake that sticks
        once it's corrected, so read why below.
      </p>
    )
  }
  if (confidence === 'guess' && correct) {
    return (
      <p className="text-sm text-muted">
        Right, though you were guessing: read why, so next time you know.
      </p>
    )
  }
  return null
}
