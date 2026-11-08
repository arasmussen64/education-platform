import assert from 'node:assert/strict'
import { loadTestSet } from './test-set.ts'

// Only checks the files are usable. Running them against Claude costs money,
// so that's eval.ts, by hand (ADR-0013).
Deno.test('every topic in the test set has an explain check and 5 or more samples, both kinds', async () => {
  const sets = await loadTestSet()
  assert.ok(sets.length >= 6, 'Module 1 has 6 explain checks')
  for (const { topicId, explain, samples } of sets) {
    assert.ok(
      explain.rubric.some((item) => item.required),
      `${topicId}: the rubric has a required item`,
    )
    assert.ok(samples.length >= 5, `${topicId}: at least 5 samples`)
    for (const expect of ['pass', 'needs_work']) {
      assert.ok(
        samples.some((sample) => sample.expect === expect),
        `${topicId}: at least one sample that should get ${expect}`,
      )
    }
  }
})
