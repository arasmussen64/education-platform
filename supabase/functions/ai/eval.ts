// Runs the grading test set against Claude (ADR-0013), to choose the
// cheapest model that gets every sample's verdict right. It uses the very
// same request and reading as the proxy (grading.ts).
//
// Every run costs real money: about $0.02 for the whole set on Claude Haiku
// 5.5, and about $0.80 on Claude Opus 5.5. So the owner approves each run.
// It reads the API key from supabase/functions/.env.
//
//   npm run fn:eval -- [model] [effort]     (defaults: claude-haiku-5-5 low)
import Anthropic from 'npm:@anthropic-ai/sdk@1.6.0'
import { costOf, isPricedModel } from './cost.ts'
import {
  type Effort,
  GradingUnavailable,
  gradingRequest,
  readGrading,
} from './grading.ts'
import { loadTestSet } from './test-set.ts'

const [model = 'claude-haiku-5-5', effort = 'low'] = Deno.args
if (!isPricedModel(model)) {
  throw new Error(`No price for ${model}: add it to cost.ts first`)
}
const apiKey = Deno.env.get('ANTHROPIC_API_KEY')
if (!apiKey) {
  throw new Error('Put ANTHROPIC_API_KEY in supabase/functions/.env first')
}
const claude = new Anthropic({ apiKey })

let right = 0
let total = 0
let spent = 0
for (const { topicId, explain, samples } of await loadTestSet()) {
  for (const [index, sample] of samples.entries()) {
    total++
    const input = { ...explain, explanation: sample.text }
    const message = await claude.messages.create(
      gradingRequest(input, model, effort as Effort),
    )
    spent += costOf(model, message.usage)

    let verdict: string
    let detail = ''
    try {
      const grading = readGrading(message, input)
      verdict = grading.verdict
      const unmet = grading.rubric.filter((item) => !item.met).map((item) => item.id)
      detail = `unmet: ${unmet.join(', ') || 'none'}; questions: ${grading.questions.join(' | ') || 'none'}`
    } catch (error) {
      if (!(error instanceof GradingUnavailable)) throw error
      verdict = 'unavailable'
      detail = error.message
    }

    const ok = verdict === sample.expect
    if (ok) right++
    console.log(
      `${ok ? 'ok  ' : 'MISS'} ${topicId} #${index + 1}: ${verdict}, expected ${sample.expect} (${sample.why})`,
    )
    if (!ok) console.log(`       ${detail}`)
  }
}

console.log(
  `\n${right} of ${total} right with ${model} at ${effort} effort, for $${spent.toFixed(4)}.`,
)
if (right < total) Deno.exit(1)
