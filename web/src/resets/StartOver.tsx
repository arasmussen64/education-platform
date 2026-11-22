import { useContext, useState } from 'react'
import { BUTTON, CARD, SECONDARY_BUTTON } from '../components/styles.ts'
import { topicIdsOf, tracks } from '../content/content.ts'
import type { Track } from '../content/types.ts'
import { clearDraftsOfTopics } from '../drafts/drafts.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import { useRecordEvent } from '../events/useEvents.ts'
import { forgetGuess } from '../nexttime/guesses.ts'
import { forgetPart } from '../parts/partMemory.ts'
import { forgetPlace } from '../place/placeMemory.ts'
import { type ProgressState, useProgress } from '../progress/useProgress.ts'
import { eraseHistory } from './erase.ts'
import {
  everythingResetEvent,
  freshStart,
  trackOfTopic,
  trackResetEvent,
} from './resets.ts'

/** No topics of its own: useProgress adds every bundled topic. */
const NO_TOPICS: never[] = []

/**
 * Starting a track over (ADR-0029): one button per track, and a second
 * step that says exactly what goes and what stays before anything happens.
 * For a track nothing is deleted: the reset is one more event in the
 * learner's log, and from then on the app counts nothing from that track
 * before it. Under the tracks is "Everything", which is different: it
 * deletes the whole history for good (amended 2026-11-22).
 */
export function StartOver() {
  const progress = useProgress(NO_TOPICS)
  return (
    <section aria-labelledby="start-over" className="space-y-3">
      <h2 id="start-over" className="text-xl font-semibold">
        Start a track over
      </h2>
      <p className="text-muted">
        Start fresh on a track: every topic in it goes back to not started, as
        if you'd never studied it. A track's history isn't erased; it just stops
        counting. Starting everything over, at the bottom, is different: it
        deletes your history for good.
      </p>
      <ul className="space-y-3">
        {tracks().map((track) => (
          <li key={track.id}>
            <TrackRow track={track} progress={progress} />
          </li>
        ))}
        <li>
          <EverythingRow progress={progress} />
        </li>
      </ul>
    </section>
  )
}

/**
 * What this device remembers about these topics: typed drafts, the part
 * and place last viewed, a guess waiting for its answer. Conveniences,
 * never records: the event log keeps everything.
 */
function forgetOnThisDevice(topicIds: string[]) {
  clearDraftsOfTopics(topicIds)
  for (const id of topicIds) {
    forgetPart(id)
    forgetPlace(id)
    forgetGuess(id)
  }
}

/**
 * Starting everything over: the learner's whole history is deleted from
 * the database, for good (ADR-0029, amended 2026-11-22). Every track, and
 * what a track's reset keeps (practice hours, weeks, the forgetting curve,
 * how sure the learner is, the math check). The account is as it was on
 * its first day. A track's reset only hides; this is the one thing in the
 * app that can't be undone, so it says so before anything happens.
 */
function EverythingRow({ progress }: { progress: ProgressState }) {
  const log = useContext(EventLogContext)
  const [step, setStep] = useState<
    'idle' | 'asking' | 'erasing' | 'done' | 'failed'
  >('idle')

  const ready = progress.status === 'ready'
  const lastStart = ready ? freshStart(progress.resets) : undefined

  async function startOver() {
    setStep('erasing')
    try {
      // Anything still waiting on this device goes up first, so that it is
      // deleted with the rest and can't arrive afterwards.
      await log.sync()
      await eraseHistory()
    } catch (error) {
      console.error('Erasing the history failed', error)
      setStep('failed')
      return
    }
    // One event marks the fresh start. This page still holds what it read
    // before the deletion, and another device may yet send an old answer:
    // nothing from before this moment counts, whatever turns up.
    log.record(everythingResetEvent())
    forgetOnThisDevice(tracks().flatMap(topicIdsOf))
    setStep('done')
  }

  return (
    <div className={CARD}>
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="font-semibold">Everything</h3>
        <p className="text-sm text-muted">
          {!ready
            ? progress.status === 'failed'
              ? "Your progress couldn't load."
              : 'Loading…'
            : 'Every track, and your practice hours too'}
          {lastStart && ` · started over ${formatDay(lastStart)}`}
        </p>
      </div>
      {/* Announced when everything has been erased, or couldn't be. */}
      <output className="block">
        {step === 'done' && (
          <span className="block text-sm">
            Everything has been erased. Your practice hours and every track
            begin again from zero.
          </span>
        )}
        {step === 'failed' && (
          <span className="block text-sm">
            Your history couldn't be erased, and nothing was changed. Check your
            connection, then try again.
          </span>
        )}
      </output>
      {step !== 'asking' && step !== 'erasing' ? (
        <button
          type="button"
          className={SECONDARY_BUTTON}
          disabled={!ready}
          onClick={() => setStep('asking')}
        >
          Start everything over…
        </button>
      ) : (
        <fieldset className="space-y-3 rounded-md border border-line-strong bg-sunken p-3 text-sm">
          <legend className="font-medium">Start everything over?</legend>
          <ul className="list-disc space-y-1 pl-5">
            <li>
              <strong>
                This deletes your history for good. It can't be undone.
              </strong>{' '}
              Every answer, Check, review and placement result you've saved is
              removed from the database.
            </li>
            <li>
              Every topic on every track goes back to not started. Your practice
              hours and weeks go back to zero. Your forgetting curve, your usual
              answer times, how sure you are against how often you're right, and
              the math check start again too.
            </li>
            <li>
              Code and explanations you've typed but not checked are cleared
              from this browser.
            </li>
            <li>Kept: your study plan and your sign-in.</li>
            <li>
              Want a copy first? "Download my data", above, saves all of it as
              one file.
            </li>
          </ul>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className={BUTTON}
              disabled={step === 'erasing'}
              onClick={startOver}
            >
              {step === 'erasing'
                ? 'Erasing…'
                : 'Yes, delete everything and start over'}
            </button>
            <button
              type="button"
              className={SECONDARY_BUTTON}
              disabled={step === 'erasing'}
              onClick={() => setStep('idle')}
            >
              Cancel
            </button>
          </div>
        </fieldset>
      )}
    </div>
  )
}

function TrackRow({
  track,
  progress,
}: {
  track: Track
  progress: ProgressState
}) {
  const record = useRecordEvent()
  const [asking, setAsking] = useState(false)
  const [done, setDone] = useState(false)

  const ready = progress.status === 'ready'
  const studied = ready ? topicsStudied(track, progress.attempts) : 0
  const lastReset = ready ? progress.resets.get(track.id) : undefined

  function startOver() {
    record(trackResetEvent(track.id))
    // What this device remembers about the track's topics goes too, so its
    // editors open on their starters and its pages at the top.
    forgetOnThisDevice(topicIdsOf(track))
    setAsking(false)
    setDone(true)
  }

  return (
    <div className={CARD}>
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="font-semibold">{track.title}</h3>
        <p className="text-sm text-muted">
          {!ready
            ? progress.status === 'failed'
              ? "Your progress couldn't load."
              : 'Loading…'
            : studied === 0
              ? 'Not started'
              : `${studied} ${studied === 1 ? 'topic' : 'topics'} with progress`}
          {lastReset && ` · started over ${formatDay(lastReset)}`}
        </p>
      </div>
      {/* Announced when the track has been started over. */}
      <output className="block">
        {done && (
          <span className="block text-sm">
            {track.title} has been started over. Its topics are back to not
            started.
          </span>
        )}
      </output>
      {!asking ? (
        <button
          type="button"
          className={SECONDARY_BUTTON}
          disabled={!ready}
          onClick={() => {
            setDone(false)
            setAsking(true)
          }}
        >
          Start {track.title} over…
        </button>
      ) : (
        <fieldset className="space-y-3 rounded-md border border-line-strong bg-sunken p-3 text-sm">
          <legend className="font-medium">Start {track.title} over?</legend>
          <ul className="list-disc space-y-1 pl-5">
            <li>
              Every topic in it goes back to not started: its proofs, reviews,
              mistakes coming back and placement results stop counting.
            </li>
            <li>
              Code and explanations you've typed but not checked in its topics
              are cleared from this browser.
            </li>
            <li>
              Kept: your practice hours and weeks, your forgetting curve, and
              your progress on every other track. Topics on other tracks that
              build on this one may wait for you to learn its topics again.
            </li>
            <li>
              Nothing is deleted. Your full history stays in your data, and
              "Download my data" still includes it.
            </li>
          </ul>
          <div className="flex flex-wrap gap-2">
            <button type="button" className={BUTTON} onClick={startOver}>
              Yes, start {track.title} over
            </button>
            <button
              type="button"
              className={SECONDARY_BUTTON}
              onClick={() => setAsking(false)}
            >
              Cancel
            </button>
          </div>
        </fieldset>
      )}
    </div>
  )
}

/** How many of the track's topics have a counted attempt. */
function topicsStudied(track: Track, attempts: { topic_id: string }[]): number {
  const studied = new Set(
    attempts
      .map((attempt) => attempt.topic_id)
      .filter((topicId) => trackOfTopic(topicId) === track.id),
  )
  return studied.size
}

/** A reset's day, like "Nov 21, 2026", on the learner's own clock. */
function formatDay(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
