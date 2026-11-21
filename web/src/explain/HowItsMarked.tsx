import type { Explain } from '../content/types.ts'
import { pointsSentence } from './marking.ts'

/**
 * How an explanation is marked, shown before the learner writes it
 * (ADR-0013, amended 2026-11-16): how many points it's checked against, how
 * many of them a pass needs, and what happens when one is missing.
 *
 * Not the points' wording. Every rubric in the content is written as the
 * answer itself ("append adds the item to the end … it returns None"), so
 * showing it would turn the explanation into copying, and an explanation
 * only proves something when it comes from memory (ADR-0002). The question
 * above already names what to cover; this says how it will be judged.
 */
export function HowItsMarked({ explain }: { explain: Explain }) {
  const required = explain.rubric.filter((point) => point.required).length
  const extra = explain.rubric.length - required
  if (explain.rubric.length === 0) return null
  return (
    <details className="text-sm text-ink">
      <summary className="cursor-pointer font-medium">How it's marked</summary>
      <ul className="mt-2 list-disc space-y-1 pl-6">
        <li>{pointsSentence(explain.rubric.length, required, extra)}</li>
        <li>
          The ideas count, not the wording: plain words, your own order or an
          example are fine. An idea that's only hinted at, or stated wrongly,
          doesn't count.
        </li>
        <li>
          If one is missing or wrong, you get up to three questions about it,
          never the answer, and you can try again as often as you like.
        </li>
      </ul>
    </details>
  )
}
