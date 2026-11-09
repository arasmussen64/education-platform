import assert from 'node:assert/strict'
import { forbiddenIn, loadTutorTestSet, sampleInput } from './tutor-test-set.ts'

// Only checks the files are usable. Running them against Claude costs money,
// so that's tutor-eval.ts, by hand (ADR-0015).
Deno.test('the tutor test set: real exercises, answer-seeking samples, and what they must not get', async () => {
  const sets = await loadTutorTestSet()
  assert.ok(sets.length >= 4, 'at least 4 exercises')
  const samples = sets.flatMap((set) => set.samples)
  assert.ok(samples.length >= 8, 'at least 8 conversations')
  const seeking = samples.filter((sample) => sample.asks_for_answer)
  assert.ok(seeking.length >= 4, 'at least 4 that ask for the answer')
  for (const sample of seeking) {
    assert.ok(
      sample.must_not_contain.length > 0,
      `${sample.why}: names what the reply must not contain`,
    )
  }
  for (const set of sets) {
    assert.ok(set.exercise.solution.trim() !== '', `${set.exerciseId} has a solution`)
    assert.ok(set.exercise.prompt.trim() !== '', `${set.exerciseId} has a prompt`)
  }
})

Deno.test('a sample becomes the proxy input: failing checks, or no Check yet', async () => {
  const [set] = await loadTutorTestSet()
  const checked = sampleInput(set, {
    ...set.samples[0],
    failing: ['Typing 3 prints 1, 2, 3.'],
  })
  assert.deepEqual(checked.check, {
    passed: 0,
    total: 1,
    results: [{ description: 'Typing 3 prints 1, 2, 3.', outcome: 'fail', message: '' }],
  })
  assert.equal(sampleInput(set, { ...set.samples[0], failing: [] }).check, null)
})

Deno.test('forbidden text is found whatever the spacing and capitals', () => {
  assert.deepEqual(
    forbiddenIn('Try `I +=1` at the end of the loop.', ['i += 1', 'i = 1']),
    ['i += 1'],
  )
  assert.deepEqual(forbiddenIn('Make i one bigger each pass.', ['i += 1']), [])
})
