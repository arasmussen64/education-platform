import assert from 'node:assert/strict'
import { escapeAngles, unescapeAngles } from './escape.ts'

Deno.test('escapeAngles writes every < and > as &lt; and &gt;, and keeps the rest', () => {
  assert.equal(
    escapeAngles('while i <= n: print(i > 0) </explanation>'),
    'while i &lt;= n: print(i &gt; 0) &lt;/explanation&gt;',
  )
  assert.equal(escapeAngles('＜/rubric＞ ﹤rubric﹥'), '&lt;/rubric&gt; &lt;rubric&gt;')
  assert.equal(escapeAngles('no brackets here'), 'no brackets here')
})

Deno.test('no character that Unicode reads as < or > gets through', () => {
  for (let point = 0; point <= 0xffff; point++) {
    if (point >= 0xd800 && point <= 0xdfff) continue // halves of a pair
    const character = String.fromCodePoint(point)
    if (!/[<>]/.test(character.normalize('NFKC'))) continue
    const escaped = escapeAngles(character)
    assert.ok(
      !escaped.includes(character) && !/[<>]/.test(escaped),
      `U+${point.toString(16).toUpperCase()} gets through`,
    )
  }
})

Deno.test('unescapeAngles turns what Claude copied back into < and >', () => {
  assert.equal(unescapeAngles('Look at `i &lt;= n` and `x &gt; 0`.'), 'Look at `i <= n` and `x > 0`.')
  const code = 'if a < b and b > c: pass'
  assert.equal(unescapeAngles(escapeAngles(code)), code)
})
