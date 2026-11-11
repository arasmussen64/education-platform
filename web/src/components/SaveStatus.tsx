import { Link } from 'react-router'
import { couldNotSave, keptAndRetried } from '../events/refusedText.ts'
import { useEventLogStatus } from '../events/useEvents.ts'

const BADGE =
  'rounded-md bg-amber-100 px-2 py-1 text-xs font-medium text-amber-900 dark:bg-amber-900 dark:text-amber-100'

/**
 * Says when some of the learner's work is still only on this device. There
 * are two cases:
 *
 * - "Not saved yet": after a failed save, for example while offline. Saving
 *   normally takes a moment, so there's nothing to show while it's working.
 * - "3 pieces of your work couldn't be saved yet": the server refused them.
 *   They stay on this device and are tried again later, and the line stays
 *   until they're saved. It links to the account page, which explains more.
 */
export function SaveStatus() {
  const { pending, syncing, refused } = useEventLogStatus()
  const unsaved = pending > 0 && !syncing
  // <output> is a status area that screen readers announce when it changes.
  // It's always on the page, so a badge is announced when it appears.
  return (
    <output className="flex flex-wrap items-center gap-2">
      {unsaved && (
        <span
          title="Your latest work is kept on this device. It will be saved to your account when the connection returns."
          className={BADGE}
        >
          Not saved yet
        </span>
      )}
      {refused > 0 && (
        <Link
          to="/account"
          title={`${keptAndRetried(refused)} Your account page says more.`}
          className={`${BADGE} underline`}
        >
          {couldNotSave(refused)}
        </Link>
      )}
    </output>
  )
}
