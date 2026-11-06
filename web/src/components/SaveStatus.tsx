import { useEventLogStatus } from '../events/useEvents.ts'

/**
 * Says when some of the learner's work is still only on this device: after a
 * failed save, for example while offline. Saving normally takes a moment, so
 * there's nothing to show while it's working.
 */
export function SaveStatus() {
  const { pending, syncing } = useEventLogStatus()
  const unsaved = pending > 0 && !syncing
  // <output> is a status area that screen readers announce when it changes.
  // It's always on the page, so the badge is announced when it appears.
  return (
    <output>
      {unsaved && (
        <span
          title="Your latest work is kept on this device. It will be saved to your account when the connection returns."
          className="rounded-md bg-amber-100 px-2 py-1 text-xs font-medium text-amber-900 dark:bg-amber-900 dark:text-amber-100"
        >
          Not saved yet
        </span>
      )}
    </output>
  )
}
