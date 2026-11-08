// What a call to Claude costs (ADR-0013), for the monthly budget cap.

/**
 * US dollars per million tokens, from Anthropic's model list (October 2026).
 * Update this when prices change: the cap is only as right as these numbers.
 * Claude Haiku 5.5 costs more for prompts over 100,000 tokens, which grading
 * never comes near (the proxy limits what it's sent).
 */
export const PRICES = {
  'claude-haiku-5-5': { input: 0.1, output: 0.5 },
  'claude-sonnet-5-5': { input: 2, output: 10 },
  'claude-opus-5-5': { input: 4, output: 20 },
} as const

export type PricedModel = keyof typeof PRICES

export function isPricedModel(model: string): model is PricedModel {
  return Object.hasOwn(PRICES, model)
}

/** Token counts, as Claude reports them (thinking is part of the output). */
export type Usage = { input_tokens: number; output_tokens: number }

/** The cost of one call, in US dollars. */
export function costOf(model: PricedModel, usage: Usage): number {
  const price = PRICES[model]
  return (
    (usage.input_tokens * price.input + usage.output_tokens * price.output) /
    1_000_000
  )
}
