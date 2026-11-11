// Keeps what the learner has typed into a code editor or the explain box, on
// this device, so a reload, an error page or a stray click on a link doesn't
// throw their work away. A convenience, not a record: a draft is never sent
// to the server and never counts as an answer (only a Check does that). It
// lives in localStorage, which can be empty, full or switched off (a private
// window, cleared site data), and everything works the same without it, just
// with no drafts.

/** Where a draft belongs: one item of one topic, at one revision. */
export type DraftKey = { topicId: string; itemId: string; rev: number }

/** One saved draft, and when it was saved (milliseconds since 1970). */
type Draft = { rev: number; text: string; savedAt: number }

/** Every draft on this device, by topic and item. */
type Drafts = Record<string, Draft>

type DraftStorage = Pick<Storage, 'getItem' | 'setItem'>

// All the drafts live under one key, so they're easy to count and trim.
const STORAGE_KEY = 'drafts-v1'

/**
 * The most characters all the drafts together may take. localStorage holds
 * only a few million characters, and the event outbox (answers not yet sent
 * to the server, which matter far more than drafts) lives there too, so
 * drafts keep to a small share. When they'd go over, the oldest are dropped.
 */
export const DRAFTS_BUDGET = 250_000

/**
 * The longest draft that's kept. Far longer than any exercise's answer: a
 * draft this long is a stray paste, and keeping it would push out real work.
 */
export const MAX_DRAFT_CHARS = 50_000

function defaultStorage(): DraftStorage | null {
  try {
    return typeof localStorage === 'undefined' ? null : localStorage
  } catch {
    // With storage switched off, even looking at localStorage throws.
    return null
  }
}

/** The name a draft is filed under. Its rev is kept inside it, not here. */
function idOf({ topicId, itemId }: DraftKey): string {
  return `${topicId}/${itemId}`
}

function isDraft(value: unknown): value is Draft {
  const draft = value as Partial<Draft> | null
  return (
    typeof draft?.rev === 'number' &&
    typeof draft.text === 'string' &&
    typeof draft.savedAt === 'number'
  )
}

/** The saved drafts. Anything unreadable or damaged is left out. */
function readDrafts(storage: DraftStorage): Drafts {
  try {
    const saved = JSON.parse(storage.getItem(STORAGE_KEY) ?? '{}') as unknown
    if (typeof saved !== 'object' || saved === null) return {}
    return Object.fromEntries(
      Object.entries(saved).filter(([, draft]) => isDraft(draft)),
    )
  } catch {
    // Unreadable, or storage is switched off: as if there were none.
    return {}
  }
}

/** Saves the drafts; false if the browser wouldn't (storage full or off). */
function writeDrafts(storage: DraftStorage, drafts: Drafts): boolean {
  try {
    storage.setItem(STORAGE_KEY, JSON.stringify(drafts))
    return true
  } catch {
    return false
  }
}

/** The drafts without the one saved longest ago. */
function withoutOldest(drafts: Drafts): Drafts {
  const oldestFirst = Object.entries(drafts).sort(
    ([, a], [, b]) => a.savedAt - b.savedAt,
  )
  return Object.fromEntries(oldestFirst.slice(1))
}

/** How many characters of the learner's text the drafts hold. */
function sizeOf(drafts: Drafts): number {
  return Object.values(drafts).reduce(
    (total, draft) => total + draft.text.length,
    0,
  )
}

/**
 * The draft saved for this item, or null if there's none. A draft saved for
 * another revision of the item isn't given back: the item has changed, so
 * the learner starts again from its new starter.
 */
export function loadDraft(
  key: DraftKey,
  storage: DraftStorage | null = defaultStorage(),
): string | null {
  if (!storage) return null
  const draft = readDrafts(storage)[idOf(key)]
  return draft?.rev === key.rev ? draft.text : null
}

/** Saves the learner's text for this item, replacing any earlier draft. */
export function saveDraft(
  key: DraftKey,
  text: string,
  storage: DraftStorage | null = defaultStorage(),
  now = Date.now(),
): void {
  if (!storage || text.length > MAX_DRAFT_CHARS) return
  let drafts: Drafts = {
    ...readDrafts(storage),
    [idOf(key)]: { rev: key.rev, text, savedAt: now },
  }
  // This draft is the newest, so in both loops below it's dropped last.
  while (sizeOf(drafts) > DRAFTS_BUDGET) drafts = withoutOldest(drafts)
  // The browser can say storage is full before the drafts reach their
  // budget (the outbox shares it). Then older drafts make room, one at a
  // time; if even this one alone won't fit, it just isn't saved.
  while (!writeDrafts(storage, drafts)) {
    if (Object.keys(drafts).length <= 1) return
    drafts = withoutOldest(drafts)
  }
}

/** Forgets the draft for this item, whatever revision it was saved for. */
export function clearDraft(
  key: DraftKey,
  storage: DraftStorage | null = defaultStorage(),
): void {
  if (!storage) return
  const drafts = readDrafts(storage)
  if (!(idOf(key) in drafts)) return
  delete drafts[idOf(key)]
  writeDrafts(storage, drafts)
}
