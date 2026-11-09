import { beforeEach, describe, expect, it, vi } from 'vitest'
import { sendReport } from './report.ts'

// A stand-in for the Supabase table client: each test says what the
// database answers.
const table = vi.hoisted(() => ({ insert: vi.fn() }))
vi.mock('../supabase/client.ts', () => ({
  getSupabase: () => ({ from: () => table }),
}))

const USER = '11111111-1111-1111-1111-111111111111'

describe('sendReport', () => {
  beforeEach(() => {
    table.insert.mockReset()
  })

  it('saves the report with the item and its revision', async () => {
    table.insert.mockResolvedValue({ error: null })
    const result = await sendReport(
      USER,
      { topicId: 'py.variables', itemId: 'fill-swap', itemRev: 2 },
      '  The hint mentions a line that is not there.  ',
    )
    expect(result).toBe('sent')
    expect(table.insert).toHaveBeenCalledWith({
      user_id: USER,
      topic_id: 'py.variables',
      item_id: 'fill-swap',
      item_rev: 2,
      message: 'The hint mentions a line that is not there.',
    })
  })

  it('can be about the topic as a whole', async () => {
    table.insert.mockResolvedValue({ error: null })
    await sendReport(
      USER,
      { topicId: 'py.variables' },
      'The video link is dead.',
    )
    expect(table.insert).toHaveBeenCalledWith(
      expect.objectContaining({ item_id: null, item_rev: null }),
    )
  })

  it('says it failed when the database errs or cannot be reached', async () => {
    table.insert.mockResolvedValueOnce({ error: { message: 'RLS' } })
    expect(await sendReport(USER, { topicId: 't' }, 'x')).toBe('failed')
    table.insert.mockRejectedValueOnce(new Error('offline'))
    expect(await sendReport(USER, { topicId: 't' }, 'x')).toBe('failed')
  })
})
