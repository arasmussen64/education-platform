import { useId, useState } from 'react'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { SECONDARY_BUTTON } from '../components/styles.ts'
import type { TopicContent } from '../content/types.ts'
import { fetchAttempts } from '../followups/history.ts'
import { type FurtherPart, furtherParts } from '../progress/progress.ts'
import { type LoadAttempts, useFreshVersion } from './freshVersion.ts'

type Props = {
  content: TopicContent
  loadAttempts?: LoadAttempts
}

/**
 * A checkpoint's further parts (ADR-0012, amended 2026-11-11), after its
 * build and debug: each a proof check of its own, in order, numbered from
 * Part 3. Nothing for a checkpoint without them.
 */
export function MoreParts({ content, loadAttempts = fetchAttempts }: Props) {
  return (
    <>
      {furtherParts(content.topic).map((part) => (
        <MorePart
          key={part.id}
          content={content}
          part={part}
          loadAttempts={loadAttempts}
        />
      ))}
    </>
  )
}

/**
 * One further part. A part with a fresh version offers it one click away,
 * for a second try that isn't from memory; it never opens by itself, so the
 * learner decides, as with the build's steps (ADR-0012).
 */
function MorePart({
  content,
  part,
  loadAttempts,
}: {
  content: TopicContent
  part: FurtherPart
  loadAttempts: LoadAttempts
}) {
  const [open, setOpen] = useState(false)
  const panelId = useId()
  const name = `part ${part.number}`

  return (
    <>
      <PracticeItem
        itemId={part.id}
        content={content}
        context="prove"
        position={`Part ${part.number}`}
      />
      {part.versions.length > 0 && (
        <div className="space-y-4">
          <p className="text-sm text-slate-600 dark:text-slate-400">
            If {name} doesn't pass, the skills behind the tests you missed come
            back for practice on your Today page. Then prove it on a fresh
            version: the same skills in another story, so your second try isn't
            from memory. Passing either one counts.
          </p>
          <button
            type="button"
            aria-expanded={open}
            aria-controls={panelId}
            onClick={() => setOpen(!open)}
            className={SECONDARY_BUTTON}
          >
            {open
              ? `Hide the fresh version of ${name}`
              : `Try a fresh version of ${name}`}
          </button>
          <div id={panelId} hidden={!open}>
            {/* Rendered only when open: it holds a code editor or a lab. */}
            {open && (
              <FreshVersion
                content={content}
                part={part}
                loadAttempts={loadAttempts}
              />
            )}
          </div>
        </div>
      )}
    </>
  )
}

/**
 * The fresh version of a part to offer: one the learner hasn't Checked yet,
 * or else the one Checked longest ago, as for the build's.
 */
function FreshVersion({
  content,
  part,
  loadAttempts,
}: {
  content: TopicContent
  part: FurtherPart
  loadAttempts: LoadAttempts
}) {
  const version = useFreshVersion(content.topic.id, part.versions, loadAttempts)
  if (!version) {
    return (
      <p className="text-slate-500 dark:text-slate-400">
        Finding a version you haven't tried…
      </p>
    )
  }
  return (
    <PracticeItem
      itemId={version}
      content={content}
      context="prove"
      position={`Part ${part.number}, fresh version`}
    />
  )
}
