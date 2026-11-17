import { describe, expect, it } from 'vitest'
import { isLateEvening } from './evening.ts'

// Local times on this machine's clock, as the learner's device would read
// them: new Date(year, month, day, hour, minute) is local time.
const at = (hour: number, minute = 0) => new Date(2026, 10, 16, hour, minute)

describe('isLateEvening', () => {
  it('is late from 21:00', () => {
    expect(isLateEvening(at(20, 59))).toBe(false)
    expect(isLateEvening(at(21, 0))).toBe(true)
    expect(isLateEvening(at(23, 30))).toBe(true)
  })

  it('stays late past midnight until 04:00', () => {
    expect(isLateEvening(at(0, 30))).toBe(true)
    expect(isLateEvening(at(3, 59))).toBe(true)
    expect(isLateEvening(at(4, 0))).toBe(false)
  })

  it('is not late in the daytime', () => {
    expect(isLateEvening(at(9))).toBe(false)
    expect(isLateEvening(at(15))).toBe(false)
  })

  it('reads an ISO time on the local clock', () => {
    expect(isLateEvening(at(22).toISOString())).toBe(true)
  })
})
