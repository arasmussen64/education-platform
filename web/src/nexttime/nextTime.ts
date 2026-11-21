// What to leave the learner with when they stop for the day (ADR-0030): one
// open question about what comes next. People remember an unfinished thing
// better than a finished one and want to get back to it (the Zeigarnik
// effect; Ovsiankina, 1928, on the urge to resume), so a session ends on a
// question, not on "done".
//
// - A topic not yet started: its lesson's opening puzzle, to guess at now.
//   The answer waits in the lesson. A lesson without a puzzle asks how the
//   learner would do the topic's first goal today.
// - A topic in progress: its next unanswered question, shown without a way
//   to answer it here. Answering belongs on the topic's page, where it's
//   graded and saved.
import type { Topic, TopicContent } from '../content/types.ts'
import type { Attempt } from '../followups/followUps.ts'
import { itemKey, itemStates } from '../progress/itemStates.ts'

/** The question a session ends on. */
export type NextTime =
  | {
      kind: 'guess'
      topic: Topic
      /** The question, as Markdown. */
      question: string
      source: 'puzzle' | 'goal'
    }
  | {
      kind: 'question'
      topic: Topic
      /** The next unanswered question or exercise, as Markdown. */
      prompt: string
      /** Code the question is about, when it has some. */
      code: string | null
      /** "the build, from a blank editor", for a proof; null otherwise. */
      proof: 'build' | 'debug' | null
    }

/** A lesson without a puzzle: ask how the learner would do its first goal. */
function goalQuestion(objective: string): string {
  return `One thing this topic teaches: **${objective.trim()}** How would you go about that today?`
}

/** The items a topic's page asks, in its order: lesson, practice, proofs. */
function itemsInOrder(content: TopicContent): string[] {
  const { practice, prove } = content.topic
  const ids = [
    ...(content.lessonChecks ?? []),
    ...practice,
    ...(prove.build ? [prove.build] : []),
    ...(prove.debug ? [prove.debug] : []),
  ]
  return [...new Set(ids)]
}

/** The first paragraph of some Markdown: enough of a long prompt to chew on. */
function firstParagraph(markdown: string): string {
  return markdown.trim().split(/\n\s*\n/)[0] ?? ''
}

/**
 * The next question of a topic the learner hasn't got right yet, or null
 * when there's none left (or the content has none).
 */
function nextQuestion(
  content: TopicContent,
  attempts: Attempt[],
): Extract<NextTime, { kind: 'question' }> | null {
  const states = itemStates(attempts)
  const topic = content.topic
  for (const id of itemsInOrder(content)) {
    if (states.get(itemKey(topic.id, id)) === 'done') continue
    const recall = content.recall[id]
    if (recall) {
      // What the question is about, when the prompt alone wouldn't say:
      // the program to predict, or the command.
      const code =
        recall.type === 'predict_output'
          ? recall.code
          : recall.type === 'predict_shell'
            ? `$ ${recall.command}`
            : null
      return {
        kind: 'question',
        topic,
        prompt: recall.prompt,
        code,
        proof: null,
      }
    }
    const exercise = content.exercises[id]
    if (exercise) {
      const proof =
        id === topic.prove.build
          ? 'build'
          : id === topic.prove.debug
            ? 'debug'
            : null
      return {
        kind: 'question',
        topic,
        prompt: `**${exercise.title}.** ${firstParagraph(exercise.prompt)}`,
        code: null,
        proof,
      }
    }
  }
  return null
}

/**
 * The question to end on, for the topic that's next: `started` says whether
 * the learner has begun it. Null when there's nothing to ask.
 */
export function nextTimeFor(
  content: TopicContent,
  started: boolean,
  attempts: Attempt[],
): NextTime | null {
  const topic = content.topic
  if (started) return nextQuestion(content, attempts)
  const puzzle = content.lessonShape?.puzzle
  if (puzzle)
    return { kind: 'guess', topic, question: puzzle, source: 'puzzle' }
  const goal = topic.objectives[0]
  if (goal) {
    return {
      kind: 'guess',
      topic,
      question: goalQuestion(goal),
      source: 'goal',
    }
  }
  return null
}
