// The AI proxy (ADR-0013, ADR-0015): the one place the Claude API key
// exists. The browser calls it with the learner's sign-in; it checks them,
// checks the month's budget, asks Claude, and logs the call. Two actions:
// grading an explanation, and a hint from the tutor.
//
// Settings, from the function's secrets (never from the browser):
//   ANTHROPIC_API_KEY   the Claude API key; without it, the AI is unavailable
//   GRADER_MODEL        which model grades (default claude-haiku-5-5)
//   GRADER_EFFORT       how hard it thinks (default low)
//   TUTOR_MODEL         which model gives hints (default claude-haiku-5-5)
//   TUTOR_EFFORT        how hard it thinks (default low)
import Anthropic from 'npm:@anthropic-ai/sdk@1.6.0'
import { createClient } from 'npm:@supabase/supabase-js@2.119.0'
import { costOf, isPricedModel, type PricedModel } from './cost.ts'
import {
  type Effort,
  GradingUnavailable,
  gradingRequest,
  PROMPT_VERSION,
  readGrading,
} from './grading.ts'
import { createHandler, type Graded, type Hinted } from './handler.ts'
import {
  type HintInput,
  HintUnavailable,
  readHint,
  TUTOR_PROMPT_VERSION,
  tutorRequest,
} from './tutor.ts'

/** Calls stop once this month's spending reaches this many US dollars. */
const CAP_USD = 10

/** A model name from the settings, checked against the price table. */
function pricedModel(setting: string, fallback: PricedModel): PricedModel {
  const model = Deno.env.get(setting) ?? fallback
  if (!isPricedModel(model)) {
    throw new Error(`No price for ${model}: add it to cost.ts first`)
  }
  return model
}

const graderModel = pricedModel('GRADER_MODEL', 'claude-haiku-5-5')
const graderEffort = (Deno.env.get('GRADER_EFFORT') ?? 'low') as Effort
const tutorModel = pricedModel('TUTOR_MODEL', 'claude-haiku-5-5')
const tutorEffort = (Deno.env.get('TUTOR_EFFORT') ?? 'low') as Effort

// Supabase gives every Edge Function its project's address and service role
// key. The service role skips row-level security, so this client is only
// used for the checks and the log below, never for the learner's own data.
const admin = createClient(
  Deno.env.get('SUPABASE_URL') ?? '',
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '',
  { auth: { persistSession: false } },
)

const apiKey = Deno.env.get('ANTHROPIC_API_KEY')
const claude = apiKey ? new Anthropic({ apiKey }) : null

async function grade(
  input: Parameters<typeof gradingRequest>[0],
): Promise<Graded> {
  if (!claude) throw new Error('No API key')
  const message = await claude.messages.create(
    gradingRequest(input, graderModel, graderEffort),
  )
  const usage = {
    input_tokens: message.usage.input_tokens,
    output_tokens: message.usage.output_tokens,
  }
  const cost_usd = costOf(graderModel, usage)
  try {
    return {
      model: graderModel,
      usage,
      cost_usd,
      grading: readGrading(message, input),
    }
  } catch (error) {
    if (!(error instanceof GradingUnavailable)) throw error
    return {
      model: graderModel,
      usage,
      cost_usd,
      grading: null,
      problem: error.message,
    }
  }
}

async function hint(input: HintInput): Promise<Hinted> {
  if (!claude) throw new Error('No API key')
  const message = await claude.messages.create(
    tutorRequest(input, tutorModel, tutorEffort),
  )
  const usage = {
    input_tokens: message.usage.input_tokens,
    output_tokens: message.usage.output_tokens,
  }
  const cost_usd = costOf(tutorModel, usage)
  try {
    return { model: tutorModel, usage, cost_usd, hint: readHint(message, input) }
  } catch (error) {
    if (!(error instanceof HintUnavailable)) throw error
    return { model: tutorModel, usage, cost_usd, hint: null, problem: error.message }
  }
}

Deno.serve(
  createHandler({
    async userFor(authorization) {
      const token = authorization?.replace(/^Bearer\s+/i, '')
      if (!token) return null
      // Asks the sign-in service itself, so a forged token gets nowhere.
      const { data, error } = await admin.auth.getUser(token)
      return error || !data.user ? null : data.user.id
    },
    async isAllowed(userId) {
      const { data, error } = await admin
        .from('profiles')
        .select('allowed')
        .eq('id', userId)
        .maybeSingle()
      if (error) throw new Error(error.message)
      return data?.allowed === true
    },
    async spentThisMonth() {
      const { data, error } = await admin.rpc('ai_spend_this_month')
      if (error) throw new Error(error.message)
      return Number(data)
    },
    grade: claude ? grade : null,
    hint: claude ? hint : null,
    async logCall(call) {
      const { data, error } = await admin
        .from('ai_calls')
        .insert(call)
        .select('id')
        .single()
      if (error) throw new Error(error.message)
      return data.id as string
    },
    capUsd: CAP_USD,
    promptVersion: PROMPT_VERSION,
    tutorPromptVersion: TUTOR_PROMPT_VERSION,
  }),
)
