import { useCallback, useEffect, useRef, useState } from 'react'
import { clearDraft, type DraftKey, loadDraft, saveDraft } from './drafts.ts'

/** How long typing pauses before the draft is saved. */
export const SAVE_DELAY_MS = 500

export type DraftHandle = {
  /** What to show first: the draft from last time, or else the starter. */
  initial: string
  /** Whether `initial` is a draft from last time, not the starter. */
  restored: boolean
  /** Saves the text once typing pauses. */
  save: (text: string) => void
  /** Start over: forgets the draft. What's typed next is saved again. */
  discard: () => void
  /**
   * The item has passed: forgets the draft and saves nothing more on this
   * visit, so the next visit starts from the starter.
   */
  finish: () => void
}

/**
 * The learner's draft for one item (see drafts.ts). With no `key`, nothing
 * is kept: the text starts as the starter, and saving does nothing.
 */
export function useDraft(
  key: DraftKey | undefined,
  starter: string,
): DraftHandle {
  // Read once, when the editor first appears.
  const [restored] = useState(() => (key ? loadDraft(key) : null))
  const keyRef = useRef(key)
  const starterRef = useRef(starter)
  const waiting = useRef<string | null>(null)
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined)
  const finished = useRef(false)

  // Always save under the latest key without rebuilding the functions below.
  useEffect(() => {
    keyRef.current = key
    starterRef.current = starter
  })

  /** Saves the text that's waiting, if any, straight away. */
  const flush = useCallback(() => {
    clearTimeout(timer.current)
    const text = waiting.current
    const current = keyRef.current
    waiting.current = null
    if (text === null || !current || finished.current) return
    // Back to the starter is the same as no draft at all.
    if (text === starterRef.current) clearDraft(current)
    else saveDraft(current, text)
  }, [])

  // Save what's waiting when the learner leaves before the pause is over:
  // the page closing or reloading (pagehide), the tab going to the
  // background (visibilitychange), or the editor going away (a link,
  // "Prove it now", "Hide the steps").
  useEffect(() => {
    window.addEventListener('pagehide', flush)
    document.addEventListener('visibilitychange', flush)
    return () => {
      window.removeEventListener('pagehide', flush)
      document.removeEventListener('visibilitychange', flush)
      flush()
    }
  }, [flush])

  function forget() {
    clearTimeout(timer.current)
    waiting.current = null
    if (keyRef.current) clearDraft(keyRef.current)
  }

  return {
    initial: restored ?? starter,
    restored: restored !== null,
    save(text) {
      waiting.current = text
      clearTimeout(timer.current)
      timer.current = setTimeout(flush, SAVE_DELAY_MS)
    },
    discard: forget,
    finish() {
      forget()
      finished.current = true
    },
  }
}
