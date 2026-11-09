import { useContext, useId, useState } from 'react'
import { AuthContext } from '../auth/authContext.ts'
import { Markdown } from '../components/Markdown.tsx'
import { SECONDARY_BUTTON, TEXT_INPUT } from '../components/styles.ts'
import type { Exercise } from '../content/types.ts'
import type { CheckOutcome } from '../python/runner.ts'
import {
  type AskTutor,
  askTutor,
  type HintOutcome,
  LEVEL_LABELS,
  MAX_QUESTION_CHARS,
  type TutorHint,
} from './hint.ts'

/**
 * After this many hints on one exercise, the tutor stops (ADR-0015): the
 * "next step" rung could otherwise dictate a solution a line at a time.
 */
export const MAX_ASKS = 6

/** What the page saves when a hint arrives. */
export type TutorHintGiven = {
  hint: TutorHint
  /** How many tutor hints this exercise has had now, this one included. */
  count: number
  question: string
  aiCallId: string | null
  model: string
}

type Exchange = { question: string; hint: TutorHint }

type State = { status: 'idle' } | { status: 'working' } | HintOutcome

type Props = {
  topicId: string
  itemId: string
  exercise: Exercise
  /** The learner's code as it is now. */
  code: string
  /** Their latest Check, or null before the first one. */
  check: CheckOutcome | null
  onHint?: (given: TutorHintGiven) => void
  /** Tests pass a fake. */
  ask?: AskTutor
}

/**
 * The hint-only tutor (F13, ADR-0015), under a practice exercise: the
 * learner asks, optionally saying what they're stuck on, and gets one hint
 * at a time, each a rung further up the ladder. Never a solution.
 */
export function TutorBox({
  topicId,
  itemId,
  exercise,
  code,
  check,
  onHint,
  ask = askTutor,
}: Props) {
  // Read directly, not through useAuth(): the box also renders where no
  // sign-in exists (tests, previews), and then it simply isn't there.
  const auth = useContext(AuthContext)
  const questionId = useId()
  const [question, setQuestion] = useState('')
  const [exchanges, setExchanges] = useState<Exchange[]>([])
  const [state, setState] = useState<State>({ status: 'idle' })
  const working = state.status === 'working'
  const askedEnough = exchanges.length >= MAX_ASKS

  // Signed-out visitors can't call the proxy, and the page already asks them
  // to sign in once, at the top (ADR-0015).
  if (!auth || auth.status !== 'signed-in') return null

  async function askForHint() {
    const asked = question.trim()
    setState({ status: 'working' })
    const outcome = await ask({
      topicId,
      itemId,
      exercise,
      code,
      check,
      question: asked,
      earlier: exchanges.map((exchange) => exchange.hint.text),
    })
    if (outcome.status === 'hinted') {
      const count = exchanges.length + 1
      setExchanges([...exchanges, { question: asked, hint: outcome.hint }])
      setQuestion('')
      onHint?.({
        hint: outcome.hint,
        count,
        question: asked,
        aiCallId: outcome.ai_call_id,
        model: outcome.model,
      })
    }
    setState(outcome)
  }

  return (
    <section
      aria-label="Tutor"
      className="space-y-2 rounded-md border border-sky-200 bg-sky-50 p-3 dark:border-sky-900 dark:bg-sky-950/40"
    >
      <p className="text-sm font-semibold">Ask the tutor</p>
      <p className="text-xs text-slate-600 dark:text-slate-400">
        It asks questions and gives hints, one small step at a time. It won't
        write the answer for you.
      </p>
      {exchanges.length > 0 && (
        <ol className="space-y-2" aria-label="Hints from the tutor">
          {exchanges.map((exchange, index) => (
            // Exchanges are only ever added, so their position is a stable key.
            // oxlint-disable-next-line react/no-array-index-key
            <li key={index} className="space-y-1 text-sm">
              {exchange.question && (
                <p className="text-slate-600 italic dark:text-slate-400">
                  You: {exchange.question}
                </p>
              )}
              <p className="text-xs font-semibold tracking-wide text-sky-800 uppercase dark:text-sky-300">
                {LEVEL_LABELS[exchange.hint.level]}
              </p>
              <Markdown>{exchange.hint.text}</Markdown>
            </li>
          ))}
        </ol>
      )}
      {askedEnough ? (
        <p className="text-sm text-slate-600 dark:text-slate-400">
          That's all the tutor can give here. Read the lesson's recap again,
          then try the next step yourself.
        </p>
      ) : (
        <div className="space-y-2">
          <div>
            <label htmlFor={questionId} className="text-sm font-medium">
              What are you stuck on? (optional)
            </label>
            <input
              id={questionId}
              type="text"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              maxLength={MAX_QUESTION_CHARS}
              autoComplete="off"
              className={TEXT_INPUT}
            />
          </div>
          <button
            type="button"
            onClick={() => void askForHint()}
            disabled={working}
            className={SECONDARY_BUTTON}
          >
            {exchanges.length === 0 ? 'Ask the tutor' : 'Ask again'}
          </button>
        </div>
      )}
      {/* <output> is announced by screen readers when its text changes. */}
      <output className="block text-sm">
        <Status state={state} />
      </output>
    </section>
  )
}

function Status({ state }: { state: State }) {
  switch (state.status) {
    case 'idle':
    case 'hinted':
      return null
    case 'working':
      return <span>Thinking…</span>
    case 'not_allowed':
      return (
        <span>
          The tutor isn't switched on for your account yet. The written hints
          still are.
        </span>
      )
    case 'paused':
      return (
        <span>
          The tutor is paused until next month, because this month's AI budget
          is used up. The written hints still work.
        </span>
      )
    case 'unavailable':
      return (
        <span>
          The tutor isn't available right now. The written hints still work; try
          the tutor again later.
        </span>
      )
    case 'failed':
      return (
        <span>
          The tutor couldn't be reached. Check your connection, then try again.
        </span>
      )
  }
}
