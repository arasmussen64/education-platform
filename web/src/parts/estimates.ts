// How long each step of a topic takes, roughly, so the topic page can cut a
// long topic into parts of about half an hour and say how long each part is
// (ADR-0025).
//
// Why guesses, and why these: the page knows each topic's total
// (`estimated_minutes`, which its author worked out), but not how that total
// splits between the lesson, the practice and the proofs. These figures are
// the ones authors use when they work the total out (content/README.md, and
// the "Worked out" notes in many topic.yaml files): about a minute and a half
// for a quick question, and a fixed figure for each kind of exercise. A lab,
// which runs in a container and is checked by tools/labcheck.py, takes far
// longer than a short Python exercise, so labs have figures of their own.
//
// They're only ever used for "about N min" and for where to cut the practice,
// so a guess that's a few minutes out does no harm. topicParts.ts then
// scales them to fit the topic's own total, so the parts always add up to
// the number at the top of the page.
import type { Stage, TopicContent } from '../content/types.ts'

/** A quick question: multiple choice, predict the output, Parsons, estimate. */
export const QUESTION_MINUTES = 1.5

/**
 * How fast a lesson is read, in words a minute: the speed authors use when
 * they work a topic's total out (content/README.md). It's slower than
 * ordinary reading, because a lesson is studied, not skimmed.
 */
export const READING_WORDS_A_MINUTE = 130

/** A Python exercise, run in the browser, by its stage. */
const PYTHON_MINUTES: Record<Stage, number> = {
  worked_example: 5,
  fill_in: 6,
  write: 10,
  review_code: 8,
  build: 12,
  debug: 8,
}

/** A lab, a container on the learner's machine (ADR-0018), by its stage. */
const LAB_MINUTES: Record<Stage, number> = {
  worked_example: 25,
  fill_in: 20,
  write: 30,
  review_code: 20,
  build: 50,
  debug: 40,
}

/** Writing an explanation and reading the feedback on it. */
export const EXPLAIN_MINUTES = 15

/**
 * About how long one practice or proof item takes, in minutes. An item the
 * content doesn't have (a draft being written) counts as a quick question.
 */
export function itemMinutes(content: TopicContent, itemId: string): number {
  const exercise = content.exercises[itemId]
  if (!exercise) return QUESTION_MINUTES
  const table = exercise.runtime === 'lab' ? LAB_MINUTES : PYTHON_MINUTES
  return table[exercise.stage]
}

/** About how long the proof checks take together, in minutes. */
export function proofMinutes(content: TopicContent): number {
  const { build, debug, explain } = content.topic.prove
  return (
    (build ? itemMinutes(content, build) : 0) +
    (debug ? itemMinutes(content, debug) : 0) +
    (explain ? EXPLAIN_MINUTES : 0)
  )
}
