// Remembers which part of a topic the learner last looked at, on this device
// (ADR-0025), so the next visit can open there if it isn't done yet. A
// convenience, not a record: it lives in localStorage, which can be empty
// or missing (a private window, cleared site data), and the page works the
// same without it, opening at the first part that isn't done.

const PREFIX = 'part:'

type PartStorage = Pick<Storage, 'getItem' | 'setItem'>

function defaultStorage(): PartStorage | null {
  try {
    return typeof localStorage === 'undefined' ? null : localStorage
  } catch {
    return null
  }
}

/** Remembers the part of a topic the learner is looking at. */
export function rememberPart(
  topicId: string,
  partId: string,
  storage: PartStorage | null = defaultStorage(),
): void {
  try {
    storage?.setItem(PREFIX + topicId, partId)
  } catch {
    // Storage full or blocked: the part just isn't remembered.
  }
}

/** The part last looked at on a topic, if any. */
export function recallPart(
  topicId: string,
  storage: PartStorage | null = defaultStorage(),
): string | null {
  try {
    return storage?.getItem(PREFIX + topicId) ?? null
  } catch {
    return null
  }
}
