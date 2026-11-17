import { describe, expect, it } from 'vitest'
import {
  clearStudyPlan,
  describePlan,
  dismiss,
  formatDays,
  formatTime,
  loadStudyPlan,
  type StudyPlan,
  saveStudyPlan,
  wasDismissed,
  wherePart,
} from './studyPlan.ts'

/** A storage that keeps things in memory, like localStorage. */
function memoryStorage() {
  const items = new Map<string, string>()
  return {
    getItem: (key: string) => items.get(key) ?? null,
    setItem: (key: string, value: string) => void items.set(key, value),
    removeItem: (key: string) => void items.delete(key),
  }
}

/** A storage that refuses everything, like a locked-down browser. */
const blocked = {
  getItem: () => {
    throw new Error('blocked')
  },
  setItem: () => {
    throw new Error('blocked')
  },
  removeItem: () => {
    throw new Error('blocked')
  },
}

const PLAN: StudyPlan = {
  days: ['MO', 'TH'],
  time: '19:30',
  place: 'the library',
}

describe('keeping the plan on this device', () => {
  it('saves a plan and reads it back', () => {
    const storage = memoryStorage()
    expect(loadStudyPlan(storage)).toBeNull()
    expect(saveStudyPlan(PLAN, storage)).toBe(true)
    expect(loadStudyPlan(storage)).toEqual(PLAN)
    clearStudyPlan(storage)
    expect(loadStudyPlan(storage)).toBeNull()
  })

  it('ignores anything stored that is not a plan', () => {
    const storage = memoryStorage()
    for (const junk of [
      'not json',
      '42',
      '{"days":[],"time":"19:30"}',
      '{"days":["MO"],"time":"7pm"}',
      '{"days":["XX"],"time":"19:30"}',
    ]) {
      storage.setItem('study-plan', junk)
      expect(loadStudyPlan(storage)).toBeNull()
    }
  })

  it('puts the days in week order and drops unknown ones', () => {
    const storage = memoryStorage()
    storage.setItem(
      'study-plan',
      '{"days":["TH","XX","MO"],"time":"07:05","place":3}',
    )
    expect(loadStudyPlan(storage)).toEqual({
      days: ['MO', 'TH'],
      time: '07:05',
      place: '',
    })
  })

  it('works without storage, or with storage that refuses', () => {
    expect(loadStudyPlan(null)).toBeNull()
    expect(saveStudyPlan(PLAN, null)).toBe(false)
    expect(loadStudyPlan(blocked)).toBeNull()
    expect(saveStudyPlan(PLAN, blocked)).toBe(false)
    expect(() => clearStudyPlan(blocked)).not.toThrow()
    expect(wasDismissed(blocked)).toBe(false)
    expect(() => dismiss(blocked)).not.toThrow()
  })

  it('remembers "Not now"', () => {
    const storage = memoryStorage()
    expect(wasDismissed(storage)).toBe(false)
    dismiss(storage)
    expect(wasDismissed(storage)).toBe(true)
  })
})

describe('the plan in words', () => {
  it('writes the days in a sentence', () => {
    expect(formatDays(['WE'])).toBe('Wednesday')
    expect(formatDays(['MO', 'TH'])).toBe('Monday and Thursday')
    expect(formatDays(['MO', 'WE', 'FR'])).toBe('Monday, Wednesday and Friday')
    expect(formatDays(['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'])).toBe(
      'every day',
    )
  })

  it('writes the time on a 12-hour clock', () => {
    expect(formatTime('19:30')).toBe('7:30 pm')
    expect(formatTime('07:05')).toBe('7:05 am')
    expect(formatTime('00:00')).toBe('12:00 am')
    expect(formatTime('12:15')).toBe('12:15 pm')
  })

  it('puts "at" before a place unless it has its own word', () => {
    expect(wherePart('the library')).toBe(', at the library')
    expect(wherePart('in the kitchen.')).toBe(', in the kitchen')
    expect(wherePart('  ')).toBe('')
  })

  it('says the whole plan in one line', () => {
    expect(describePlan(PLAN)).toBe(
      'Monday and Thursday at 7:30 pm, at the library.',
    )
    expect(describePlan({ ...PLAN, place: '' })).toBe(
      'Monday and Thursday at 7:30 pm.',
    )
  })
})
