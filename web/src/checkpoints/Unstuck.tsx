import { type Ref, useId } from 'react'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { SECONDARY_BUTTON } from '../components/styles.ts'
import type { TopicContent, Unstuck as WayThrough } from '../content/types.ts'
import { fetchAttempts } from '../followups/history.ts'
import { furtherParts } from '../progress/progress.ts'
import { type LoadAttempts, useFreshVersion } from './freshVersion.ts'

export type { LoadAttempts }

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
  // With further parts there's more than one build above, and all of this
  // is for part 1 alone (ADR-0012, amended 2026-11-11).
  const numbered = furtherParts(content.topic).length > 0

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
      {/* Said before the button, so the learner knows when they choose. */}
      {numbered ? <PartOneIntro /> : <BuildIntro />}
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

/** The way through, and what opening the steps means for the proof. */
function BuildIntro() {
  return (
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
        The steps show most of the build's own program. So once you open them,
        passing the build above no longer counts as your proof: a fresh version
        does. A build you passed before opening them still counts.
      </p>
      <p>
        Any test you miss, here or above, also brings its skill back for
        practice on your Today page.
      </p>
    </div>
  )
}

/**
 * The same, on a checkpoint with further parts (ADR-0012, amended
 * 2026-11-11). There's more than one build above, and the way through is
 * for part 1 alone, so it says so, and that the other parts still count
 * whenever they pass. It doesn't say "three parts" for its three stages,
 * since "part" names the proof checks above.
 */
function PartOneIntro() {
  return (
    <div className="space-y-2 text-slate-600 dark:text-slate-400">
      <p>
        A checkpoint is the first time you put a whole module together, so
        getting stuck is normal. If you're stuck on part 1, the first build,
        take it one stage at a time:
      </p>
      <ol className="list-decimal space-y-1 pl-6">
        <li>Study a solved program like part 1, in a different story.</li>
        <li>Build part 1's program in steps, with hints.</li>
        <li>
          Prove it on a fresh version, from a blank editor. Passing it counts
          the same as passing part 1 above.
        </li>
      </ol>
      <p>
        The steps show most of part 1's own program. So once you open them,
        passing part 1 above no longer counts as your proof: a fresh version
        does. If you passed part 1 before opening them, it still counts. The
        steps show nothing of the other parts, so they count whenever they pass.
      </p>
      <p>
        Any test you miss, here or above, also brings its skill back for
        practice on your Today page.
      </p>
    </div>
  )
}

/** The look of a note beside the build. */
const NOTE =
  'rounded-md border border-sky-300 bg-sky-50 px-3 py-2 text-sm text-sky-950 dark:border-sky-800 dark:bg-sky-950 dark:text-sky-100'

/**
 * Shown next to the build after a few failing Checks (ADR-0012): a
 * suggestion, so the learner decides whether to use it. `numbered` is for a
 * checkpoint with further parts, where the build is part 1 and "parts" names
 * the proof checks (ADR-0012, amended 2026-11-11).
 */
export function SuggestSteps({
  onOpen,
  numbered = false,
}: {
  onOpen: () => void
  numbered?: boolean
}) {
  return (
    <p className={NOTE}>
      {numbered ? 'Stuck on part 1?' : 'Stuck on the build?'} That's normal on a
      checkpoint.{' '}
      <button type="button" onClick={onOpen} className="font-medium underline">
        Try it in steps
      </button>
      : a solved example, then{' '}
      {numbered ? 'part 1 a piece at a time' : 'the build in parts'}, with
      hints, then a fresh version to prove it. Once you've opened the steps,
      that fresh version is your proof instead of this build.
    </p>
  )
}

/**
 * Shown above the build once the learner has opened the steps, until the
 * build is proved (ADR-0012, amended 2026-11-11): the steps showed most of
 * this program, so passing it here no longer proves it. A fresh version does.
 * On a checkpoint with further parts (`numbered`) it names part 1, and says
 * the other parts aren't affected, since some of them are builds below too.
 */
export function ProveOnAFreshVersion({
  onGoToSteps,
  numbered = false,
}: {
  onGoToSteps: () => void
  numbered?: boolean
}) {
  return (
    <p className={NOTE}>
      You've opened the steps, which show most of this program, so passing{' '}
      {numbered ? 'part 1' : 'the build'} below no longer counts as your proof.
      You can still practise on it.{' '}
      <button
        type="button"
        onClick={onGoToSteps}
        className="font-medium underline"
      >
        Prove it on a fresh version
      </button>{' '}
      instead, at the end of the steps.
      {numbered && ' Your other parts count whenever they pass.'}
    </p>
  )
}
