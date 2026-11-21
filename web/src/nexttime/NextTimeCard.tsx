import { useId, useState } from 'react'
import { Link } from 'react-router'
import { Markdown } from '../components/Markdown.tsx'
import { CODE_BOX, SECONDARY_BUTTON, TEXT_INPUT } from '../components/styles.ts'
import { recallGuess, saveGuess } from './guesses.ts'
import type { NextTime } from './nextTime.ts'

/**
 * The open question a session ends on (ADR-0030, nexttime/nextTime.ts): a
 * guess at the next topic's opening puzzle, kept on this device until the
 * topic is opened, or the next unanswered question of a topic in progress,
 * to sleep on. Nothing here is graded.
 */
export function NextTimeCard({ nextTime }: { nextTime: NextTime }) {
  const headingId = useId()
  return (
    <section
      aria-labelledby={headingId}
      className="space-y-3 rounded-lg border border-line-strong bg-card p-4"
    >
      <p
        id={headingId}
        className="text-sm font-semibold tracking-wide text-muted uppercase"
      >
        {nextTime.kind === 'guess'
          ? 'One question before you go'
          : 'One to sleep on'}
      </p>
      {nextTime.kind === 'guess' ? (
        <Guess nextTime={nextTime} />
      ) : (
        <ToSleepOn nextTime={nextTime} />
      )}
    </section>
  )
}

function Guess({
  nextTime,
}: {
  nextTime: Extract<NextTime, { kind: 'guess' }>
}) {
  const { topic, question, source } = nextTime
  // A guess kept on an earlier visit shows as kept.
  const [kept, setKept] = useState(() => recallGuess(topic.id)?.guess ?? null)
  const [guess, setGuess] = useState('')
  const guessId = useId()
  const where =
    source === 'puzzle'
      ? 'The answer is waiting at the start of its lesson.'
      : "You'll see your guess again when you open it, to compare with what the lesson says."

  return (
    <>
      <p className="text-sm text-muted">
        Your next topic is <span className="font-medium">{topic.title}</span>.
        It starts with this:
      </p>
      <div className="font-medium">
        <Markdown>{question}</Markdown>
      </div>
      {kept !== null ? (
        <div className="space-y-2">
          <p className="text-sm text-muted">
            <span className="font-semibold">Your guess:</span> {kept}
          </p>
          <p>
            Kept on this device. {where}{' '}
            <Link to={`/topic/${topic.id}`} className="underline">
              Open {topic.title}
            </Link>{' '}
            when you're back.
          </p>
        </div>
      ) : (
        <form
          className="space-y-2"
          onSubmit={(event) => {
            event.preventDefault()
            const text = guess.trim()
            if (!text) return
            saveGuess(topic.id, {
              question,
              guess: text,
              at: new Date().toISOString(),
              source,
            })
            setKept(text)
          }}
        >
          <label htmlFor={guessId} className="block text-sm font-medium">
            Your guess
          </label>
          <textarea
            id={guessId}
            rows={2}
            value={guess}
            onChange={(event) => setGuess(event.target.value)}
            className={TEXT_INPUT}
          />
          <p className="text-sm text-muted">
            Any guess, even "no idea, maybe…". It isn't marked. A guess made
            before the lesson helps you remember the answer, right or wrong, and
            the answer stays hidden until you open the topic.
          </p>
          <button
            type="submit"
            disabled={!guess.trim()}
            className={SECONDARY_BUTTON}
          >
            Keep my guess for next time
          </button>
        </form>
      )}
    </>
  )
}

const PROOF_NOTES = {
  build: 'It is the build: one of the three proofs, from a blank editor.',
  debug: 'It is the debug: one of the three proofs.',
}

function ToSleepOn({
  nextTime,
}: {
  nextTime: Extract<NextTime, { kind: 'question' }>
}) {
  const { topic, prompt, code, proof } = nextTime
  return (
    <>
      <p className="text-sm text-muted">
        The next thing waiting in{' '}
        <span className="font-medium">{topic.title}</span>:
      </p>
      <div className="font-medium">
        <Markdown>{prompt}</Markdown>
      </div>
      {code && <pre className={CODE_BOX}>{code}</pre>}
      <p className="text-sm text-muted">
        {proof && `${PROOF_NOTES[proof]} `}
        No need to answer it now. A question left open is easier to come back to
        than a blank page.{' '}
        <Link to={`/topic/${topic.id}`} className="underline">
          It'll be here
        </Link>{' '}
        when you're back.
      </p>
    </>
  )
}
