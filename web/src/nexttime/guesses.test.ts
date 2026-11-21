import { describe, expect, it } from 'vitest'
import {
  forgetGuess,
  recallGuess,
  type SavedGuess,
  saveGuess,
} from './guesses.ts'

/** A stand-in for localStorage. */
function fakeStorage() {
  const values = new Map<string, string>()
  return {
    getItem: (key: string) => values.get(key) ?? null,
    setItem: (key: string, value: string) => void values.set(key, value),
    removeItem: (key: string) => void values.delete(key),
    values,
  }
}

const GUESS: SavedGuess = {
  question: 'Why does `print` start a new line?',
  guess: 'It adds one at the end',
  at: '2026-11-21T18:00:00.000Z',
  source: 'puzzle',
}

describe('a guess kept for next time', () => {
  it('is kept for its topic, and for no other', () => {
    const storage = fakeStorage()
    saveGuess('py.print', GUESS, storage)
    expect(recallGuess('py.print', storage)).toEqual(GUESS)
    expect(recallGuess('py.variables', storage)).toBeNull()
  })

  it('is forgotten once its answer has been seen', () => {
    const storage = fakeStorage()
    saveGuess('py.print', GUESS, storage)
    forgetGuess('py.print', storage)
    expect(recallGuess('py.print', storage)).toBeNull()
  })

  it('reads as nothing when what is stored is not a guess', () => {
    const storage = fakeStorage()
    storage.values.set('guess:py.print', 'not json')
    expect(recallGuess('py.print', storage)).toBeNull()
    storage.values.set('guess:py.print', JSON.stringify({ guess: '  ' }))
    expect(recallGuess('py.print', storage)).toBeNull()
  })

  it('works without storage: nothing is kept, and nothing breaks', () => {
    saveGuess('py.print', GUESS, null)
    expect(recallGuess('py.print', null)).toBeNull()
    forgetGuess('py.print', null)
  })

  it('survives storage that throws, as a full or blocked one does', () => {
    const broken = {
      getItem: () => {
        throw new Error('blocked')
      },
      setItem: () => {
        throw new Error('full')
      },
      removeItem: () => {
        throw new Error('blocked')
      },
    }
    saveGuess('py.print', GUESS, broken)
    expect(recallGuess('py.print', broken)).toBeNull()
    forgetGuess('py.print', broken)
  })
})
