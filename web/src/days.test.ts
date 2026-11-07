import { describe, expect, it } from 'vitest'
import { addDays, dayOf } from './days.ts'

describe('days', () => {
  it('adds days across months and years', () => {
    expect(addDays('2026-11-30', 1)).toBe('2026-12-01')
    expect(addDays('2026-12-31', 1)).toBe('2027-01-01')
    expect(addDays('2026-11-06', 3)).toBe('2026-11-09')
  })

  it('names the local calendar day of a moment', () => {
    expect(dayOf(new Date(2026, 10, 6, 23, 59))).toBe('2026-11-06')
  })
})
