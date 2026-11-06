import { type Ref, useContext, useEffect, useId, useState } from 'react'
import { useAuth } from '../auth/useAuth.ts'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { SECONDARY_BUTTON } from '../components/styles.ts'
import type { TopicContent, Unstuck as WayThrough } from '../content/types.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import type { Attempt } from '../followups/followUps.ts'
import {
  fetchAttempts,
  localAttempt,
  mergeAttempts,
} from '../followups/history.ts'
import { chooseVersion } from './versions.ts'

/** Reads the learner's attempts in one topic. Tests pass a fake. */
export type LoadAttempts = (topicId: string) => Promise<Attempt[]>

type Props = {
  content: TopicContent
  unstuck: WayThrough
  open: boolean
  onToggle: () => void
  /** The section's heading, so the suggestion by the build can move focus here. */
  headingRef?: Ref<HTMLHeadingElement>
  loadAttempts?: LoadAttempts
}

/**
 * A checkpoint's way through its build for a learner who's stuck
 * (ADR-0012): study a solved sibling, build it in steps with hints, then
 * prove it on a fresh version. Always one click away; it never opens by
 * itself.
 */
export function Unstuck({
  content,
  unstuck,
  open,
  onToggle,
  headingRef,
  loadAttempts = fetchAttempts,
}: Props) {
  const panelId = useId()
  const version = useFreshVersion(
    content.topic.id,
    unstuck.versions,
    loadAttempts,
  )
  const { example, steps, versions } = unstuck

  return (
    <section aria-labelledby="unstuck" className="space-y-4">
      <h2
        id="unstuck"
        ref={headingRef}
        // Focused from the suggestion next to the build.
        tabIndex={-1}
        className="text-2xl font-bold"
      >
        Stuck? Try it in steps
      </h2>
      <div className="space-y-2 text-slate-600 dark:text-slate-400">
        <p>
          A checkpoint is the first time you put a whole module together, so
          getting stuck is normal. When you are, take it in three parts:
        </p>
        <ol className="list-decimal space-y-1 pl-6">
          <li>Study a solved program like the build, in a different story.</li>
          <li>Build the checkpoint's program in steps, with hints.</li>
          <li>
            Prove it on a fresh version, from a blank editor. Passing it counts
            the same as passing the build above.
          </li>
        </ol>
        <p>
          Any test you miss, here or above, also brings its skill back for
          practice on your Today page.
        </p>
      </div>
      <button
        type="button"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={onToggle}
        className={SECONDARY_BUTTON}
      >
        {open ? 'Hide the steps' : 'Show the steps'}
      </button>
      <div id={panelId} hidden={!open} className="space-y-4">
        {/* Rendered only when open: each one holds a code editor. */}
        {open && (
          <>
            {example && (
              <PracticeItem
                itemId={example}
                content={content}
                context="practice"
                position="1. Study a solved one"
              />
            )}
            {steps.map((itemId, index) => (
              <PracticeItem
                key={itemId}
                itemId={itemId}
                content={content}
                context="practice"
                position={`2. Build it in steps: step ${index + 1} of ${steps.length}`}
              />
            ))}
            {versions.length > 0 &&
              (version ? (
                <PracticeItem
                  itemId={version}
                  content={content}
                  context="prove"
                  position="3. Prove it on a fresh version"
                />
              ) : (
                <p className="text-slate-500 dark:text-slate-400">
                  Finding a version you haven't tried…
                </p>
              ))}
          </>
        )}
      </div>
    </section>
  )
}

/**
 * The fresh version to offer, chosen once from the learner's history so it
 * can't change while they work on it. Signed-out learners have no saved
 * history, so they get the first.
 */
function useFreshVersion(
  topicId: string,
  versions: string[],
  loadAttempts: LoadAttempts,
): string | null {
  const auth = useAuth()
  const log = useContext(EventLogContext)
  const [fetched, setFetched] = useState<Attempt[] | null>(null)
  const [choice, setChoice] = useState<{ version: string | null } | null>(null)

  useEffect(() => {
    if (auth.status !== 'signed-in') return
    let active = true
    loadAttempts(topicId).then(
      (attempts) => {
        if (active) setFetched(attempts)
      },
      // Which version comes first is only a preference: without the
      // history, offer the first.
      () => {
        if (active) setFetched([])
      },
    )
    return () => {
      active = false
    }
  }, [auth.status, loadAttempts, topicId])

  const history = auth.status === 'signed-out' ? [] : fetched
  if (choice === null && history !== null) {
    // Checks from this visit may not have reached the server yet.
    const local = log
      .getLocalRows()
      .map(localAttempt)
      .filter((attempt) => attempt !== null)
    setChoice({
      version: chooseVersion(topicId, versions, mergeAttempts(history, local)),
    })
  }
  return choice?.version ?? null
}

/**
 * Shown next to the build after a few failing Checks (ADR-0012): a
 * suggestion, so the learner decides whether to use it.
 */
export function SuggestSteps({ onOpen }: { onOpen: () => void }) {
  return (
    <p className="rounded-md border border-sky-300 bg-sky-50 px-3 py-2 text-sm text-sky-950 dark:border-sky-800 dark:bg-sky-950 dark:text-sky-100">
      Stuck on the build? That's normal on a checkpoint.{' '}
      <button type="button" onClick={onOpen} className="font-medium underline">
        Try it in steps
      </button>
      : a solved example, then the build in parts, with hints.
    </p>
  )
}
