import { act, renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { getTopic } from '../content/content.ts'
import { EventsProvider } from '../events/EventsProvider.tsx'
import type { Attempt } from '../followups/followUps.ts'
import { loadSkillIndex } from '../followups/skillIndex.ts'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { fakeEventsClient } from '../test/fakeEvents.ts'
import { stateOf } from './progress.ts'
import { useProgress } from './useProgress.ts'

// The real skill index, unless a test makes its download fail.
vi.mock('../followups/skillIndex.ts', async (importOriginal) => {
  const module =
    await importOriginal<typeof import('../followups/skillIndex.ts')>()
  return { ...module, loadSkillIndex: vi.fn(module.loadSkillIndex) }
})
// No checkpoint's steps were ever opened.
vi.mock('../checkpoints/stepsOpened.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../checkpoints/stepsOpened.ts')>()),
  fetchStepsOpened: vi.fn(async () => []),
}))

// Programs and print, a real topic, with the times given as days after it
// was Learned. Nothing here reads the clock: stateOf is asked at a time.
const PRINT = getTopic('py.programs-and-print')!
const TOPICS = [PRINT]
const LEARNED = Date.parse('2026-10-01T12:00:00.000Z')
const day = (days: number, hours = 0) =>
  new Date(LEARNED + (days * 24 + hours) * 60 * 60 * 1000).toISOString()

let lastId = 0
function event(fields: Partial<Attempt> & Pick<Attempt, 'type' | 'item_id'>) {
  return {
    id: `event-${++lastId}`,
    topic_id: PRINT.id,
    correct: true,
    occurred_at: day(0),
    ...fields,
  } satisfies Attempt
}

/** Learned on day 0, and a review rated Good on day 10: Mastered. */
const MASTERED: Attempt[] = [
  event({ type: 'code_check', item_id: PRINT.prove.build ?? '' }),
  event({ type: 'code_check', item_id: PRINT.prove.debug ?? '' }),
  event({ type: 'explain_submit', item_id: 'explain' }),
  event({
    type: 'review',
    item_id: 'review',
    rating: 'good',
    occurred_at: day(10),
  }),
]

function renderProgress(load: () => Promise<Attempt[]>) {
  const wrapper = ({ children }: { children: ReactNode }) => (
    <AuthProvider auth={fakeAuth(fakeUser())}>
      <EventsProvider client={fakeEventsClient()}>{children}</EventsProvider>
    </AuthProvider>
  )
  return renderHook(() => useProgress(TOPICS, load), { wrapper })
}

/** The hook's result once it's ready. */
async function ready(load: () => Promise<Attempt[]>) {
  const { result } = renderProgress(load)
  await waitFor(() => expect(result.current.status).toBe('ready'))
  if (result.current.status !== 'ready') throw new Error('not ready')
  return result.current
}

describe('useProgress', () => {
  it('is Mastered after a review survived a week later', async () => {
    const progress = await ready(async () => MASTERED)
    expect(stateOf(PRINT, progress.progress, day(10, 1))).toBe('mastered')
    expect(progress.followUps).toEqual([])
  })

  it("holds Mastered back while one of the topic's skills is being relearned", async () => {
    // A wrong answer an hour after the review opens a follow-up on its
    // skill (ADR-0011), found through the skill index.
    const missed = event({
      type: 'answer',
      item_id: 'predict-four-lines',
      correct: false,
      occurred_at: day(10, 1),
    })
    const progress = await ready(async () => [...MASTERED, missed])
    expect(progress.followUps).toEqual([
      expect.objectContaining({ topicId: PRINT.id, skillId: 'print-commas' }),
    ])
    expect(progress.progress.get(PRINT.id)?.openFollowUps).toEqual([
      'print-commas',
    ])
    expect(stateOf(PRINT, progress.progress, day(10, 2))).toBe('learned')
  })

  it('says so when the skill index fails to download, and tries again', async () => {
    vi.mocked(loadSkillIndex).mockRejectedValueOnce(new Error('offline'))
    const { result } = renderProgress(async () => MASTERED)
    await waitFor(() => expect(result.current.status).toBe('failed'))
    if (result.current.status !== 'failed') throw new Error('not failed')
    const { retry } = result.current
    act(() => retry())
    await waitFor(() => expect(result.current.status).toBe('ready'))
  })
})
