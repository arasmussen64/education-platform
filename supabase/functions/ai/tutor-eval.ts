// Runs the tutor test set against Claude (ADR-0015), to check that no reply
// gives a solution away, and to read the hints it gives. It uses the very
// same request and reading as the proxy (tutor.ts).
//
// Every run costs real money: about $0.01 for the whole set on Claude Haiku
// 5.5, about $0.15 on Claude Sonnet 5.5. So the owner approves each run.
// It reads the API key from supabase/functions/.env.
//
//   npm run fn:eval:tutor -- [model] [effort]     (defaults: claude-haiku-5-5 low)
import Anthropic from 'npm:@anthropic-ai/sdk@1.6.0'
import { costOf, isPricedModel } from './cost.ts'
import type { Effort } from './grading.ts'
import { forbiddenIn, loadTutorTestSet, sampleInput } from './tutor-test-set.ts'
import { HintUnavailable, readHint, tutorRequest } from './tutor.ts'

const [model = 'claude-haiku-5-5', effort = 'low'] = Deno.args
if (!isPricedModel(model)) {
  throw new Error(`No price for ${model}: add it to cost.ts first`)
}
const apiKey = Deno.env.get('ANTHROPIC_API_KEY')
if (!apiKey) {
  throw new Error('Put ANTHROPIC_API_KEY in supabase/functions/.env first')
}
const claude = new Anthropic({ apiKey })

let fine = 0
let total = 0
let spent = 0
for (const set of await loadTutorTestSet()) {
  for (const [index, sample] of set.samples.entries()) {
    total++
    const input = sampleInput(set, sample)
    const message = await claude.messages.create(
      tutorRequest(input, model, effort as Effort),
    )
    spent += costOf(model, message.usage)

    const problems: string[] = []
    let text = ''
    let level = ''
    try {
      const hint = readHint(message, input)
      text = hint.text
      level = hint.level
      if (hint.replaced) problems.push(`replaced: ${hint.reason}`)
      const forbidden = forbiddenIn(text, sample.must_not_contain)
      if (forbidden.length > 0) problems.push(`contains ${forbidden.join(', ')}`)
    } catch (error) {
      if (!(error instanceof HintUnavailable)) throw error
      problems.push(`unavailable: ${error.message}`)
    }

    const ok = problems.length === 0
    if (ok) fine++
    console.log(
      `${ok ? 'ok  ' : 'MISS'} ${set.exerciseId} #${index + 1} (${level || '-'}): ${sample.why}`,
    )
    for (const problem of problems) console.log(`       ${problem}`)
    for (const line of text.split('\n')) console.log(`       > ${line}`)
  }
}

console.log(
  `\n${fine} of ${total} replies fine with ${model} at ${effort} effort, for $${spent.toFixed(4)}. Read them: a reply can pass the filter and still be a poor hint.`,
)
if (fine < total) Deno.exit(1)
