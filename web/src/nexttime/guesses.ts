// A guess made before a topic is opened (ADR-0030): at the end of a session
// the page asks the next topic's opening question, and keeps the learner's
// guess here until they open the topic and see the answer. An unanswered
// question is a reason to come back, and a guess made first helps the answer
// stick, even a wrong one (Richland, Kornell & Kao 2009).
//
// Like the remembered part (parts/partMemory.ts), it's kept on this device
// only, in localStorage, which can be empty or missing. Nothing is graded
// and nothing is sent anywhere, so losing a guess loses nothing that counts.

const PREFIX = 'guess:'

export type SavedGuess = {
  /** The question that was asked, as Markdown. */
  question: string
  /** What the learner typed. */
  guess: string
  /** When, in ISO format. */
  at: string
  /**
   * Where the question came from: the lesson's own opening puzzle, which
   * shows the answer, or the topic's first goal, for a lesson without one.
   */
  source: 'puzzle' | 'goal'
}

type GuessStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>

function defaultStorage(): GuessStorage | null {
  try {
    return typeof localStorage === 'undefined' ? null : localStorage
  } catch {
    return null
  }
}

/** Keeps the learner's guess about a topic they haven't opened yet. */
export function saveGuess(
  topicId: string,
  guess: SavedGuess,
  storage: GuessStorage | null = defaultStorage(),
): void {
  try {
    storage?.setItem(PREFIX + topicId, JSON.stringify(guess))
  } catch {
    // Storage full or blocked: the guess just isn't kept.
  }
}

/** The guess waiting for a topic, if there is one. */
export function recallGuess(
  topicId: string,
  storage: GuessStorage | null = defaultStorage(),
): SavedGuess | null {
  try {
    const text = storage?.getItem(PREFIX + topicId)
    if (!text) return null
    const found: unknown = JSON.parse(text)
    return isSavedGuess(found) ? found : null
  } catch {
    return null
  }
}

/** Forgets a topic's guess: its answer has been seen. */
export function forgetGuess(
  topicId: string,
  storage: GuessStorage | null = defaultStorage(),
): void {
  try {
    storage?.removeItem(PREFIX + topicId)
  } catch {
    // Storage blocked: there was nothing to forget.
  }
}

function isSavedGuess(value: unknown): value is SavedGuess {
  if (value === null || typeof value !== 'object') return false
  const { question, guess, at, source } = value as Record<string, unknown>
  return (
    typeof question === 'string' &&
    typeof guess === 'string' &&
    guess.trim() !== '' &&
    typeof at === 'string' &&
    (source === 'puzzle' || source === 'goal')
  )
}
