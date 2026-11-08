import { useId, useState } from 'react'
import { Link } from 'react-router'
import { useAuth } from '../auth/useAuth.ts'
import { Markdown } from '../components/Markdown.tsx'
import { BUTTON, CARD, TEXT_INPUT } from '../components/styles.ts'
import { useAttemptTimer } from '../components/useAttemptTimer.ts'
import type { Explain, Topic } from '../content/types.ts'
import { useRecordEvent } from '../events/useEvents.ts'
import {
  type GradeExplanation,
  gradeExplanation,
  type GradeOutcome,
} from './grade.ts'

/** The longest explanation the AI proxy takes. */
export const MAX_EXPLANATION_CHARS = 4000

type State = { status: 'idle' } | { status: 'working' } | GradeOutcome

/**
 * The explain-it-back check (F7): the learner writes an explanation, and
 * Claude grades it against the rubric (ADR-0013). Every attempt is saved,
 * graded or not. The rubric and the model answer are never shown.
 */
export function ExplainCheck({
  topic,
  explain,
  grade = gradeExplanation,
}: {
  topic: Topic
  explain: Explain
  /** Tests pass a fake. */
  grade?: GradeExplanation
}) {
  const auth = useAuth()
  const record = useRecordEvent()
  const timer = useAttemptTimer()
  const boxId = useId()
  const [text, setText] = useState('')
  const [state, setState] = useState<State>({ status: 'idle' })
  const working = state.status === 'working'

  async function check() {
    const explanation = text.trim()
    setState({ status: 'working' })
    const outcome = await grade(topic.id, explain, explanation)
    const graded = outcome.status === 'graded' ? outcome : null
    record({
      type: 'explain_submit',
      topic_id: topic.id,
      // Not an item in the content: the topic's one explain check.
      item_id: 'explain',
      item_rev: topic.rev,
      context: 'prove',
      // Only a grading says whether it passed; otherwise it's saved ungraded.
      correct: graded ? graded.grading.verdict === 'pass' : undefined,
      duration_ms: timer.lap(),
      data: {
        text: explanation,
        status: outcome.status,
        ...(graded && {
          verdict: graded.grading.verdict,
          rubric: graded.grading.rubric,
          questions: graded.grading.questions,
          ai_call_id: graded.ai_call_id,
          model: graded.model,
        }),
      },
    })
    setState(outcome)
  }

  return (
    <section aria-labelledby="explain" className={CARD}>
      <h3 id="explain" className="text-lg font-semibold">
        Explain it back
      </h3>
      <Markdown>{explain.prompt}</Markdown>
      {auth.status === 'signed-out' ? (
        <p className="text-sm text-slate-600 dark:text-slate-400">
          <Link to="/sign-in" className="underline">
            Sign in
          </Link>{' '}
          to have your explanation checked.
        </p>
      ) : (
        <div className="space-y-3">
          <div>
            <label htmlFor={boxId} className="text-sm font-medium">
              Your explanation
            </label>
            <textarea
              id={boxId}
              value={text}
              onChange={(event) => setText(event.target.value)}
              onFocus={timer.start}
              maxLength={MAX_EXPLANATION_CHARS}
              rows={6}
              autoComplete="off"
              className={TEXT_INPUT}
            />
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              A few sentences, in your own words, as if teaching a friend.
            </p>
          </div>
          <button
            type="button"
            onClick={() => void check()}
            disabled={working || text.trim() === ''}
            className={BUTTON}
          >
            Check my explanation
          </button>
          {/* <output> is announced by screen readers when its text changes. */}
          <output className="block">
            <Result state={state} />
          </output>
        </div>
      )}
    </section>
  )
}

function Result({ state }: { state: State }) {
  switch (state.status) {
    case 'idle':
      return null
    case 'working':
      return <span>Checking your explanation…</span>
    case 'graded':
      return state.grading.verdict === 'pass' ? (
        <span className="font-medium">
          <span aria-hidden="true">✓ </span>
          Passed. Your explanation shows every idea it needs to.
        </span>
      ) : (
        <span className="block space-y-1">
          <span className="block font-medium">
            Needs work. Some questions to think about, then try again:
          </span>
          <span className="block">
            {state.grading.questions.map((question) => (
              <span key={question} className="block">
                <span aria-hidden="true">• </span>
                {question}
              </span>
            ))}
          </span>
        </span>
      )
    case 'not_allowed':
      return (
        <span>
          Checking explanations isn't switched on for your account yet. Your
          explanation is saved.
        </span>
      )
    case 'paused':
      return (
        <span>
          Checking is paused until next month, because this month's AI budget is
          used up. Your explanation is saved.
        </span>
      )
    case 'unavailable':
      return (
        <span>
          Checking isn't available right now. Your explanation is saved; try
          again later.
        </span>
      )
    case 'failed':
      return (
        <span>
          Your explanation couldn't be checked, but it's saved. Check your
          connection, then try again.
        </span>
      )
  }
}
