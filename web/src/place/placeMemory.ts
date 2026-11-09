// Remembers where on a topic page the learner was, on this device, so the
// next visit can offer to continue there. A convenience, not a record: it
// lives in localStorage, which can be empty or missing (a private window,
// cleared site data), and the page works the same without it.

const PREFIX = 'place:'

type PlaceStorage = Pick<Storage, 'getItem' | 'setItem'>

function defaultStorage(): PlaceStorage | null {
  try {
    return typeof localStorage === 'undefined' ? null : localStorage
  } catch {
    return null
  }
}

/** Remembers the place the learner is looking at on a topic's page. */
export function rememberPlace(
  topicId: string,
  placeId: string,
  storage: PlaceStorage | null = defaultStorage(),
): void {
  try {
    storage?.setItem(PREFIX + topicId, placeId)
  } catch {
    // Storage full or blocked: the place just isn't remembered.
  }
}

/** The place remembered for a topic, if any. */
export function recallPlace(
  topicId: string,
  storage: PlaceStorage | null = defaultStorage(),
): string | null {
  try {
    return storage?.getItem(PREFIX + topicId) ?? null
  } catch {
    return null
  }
}
