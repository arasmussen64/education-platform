# ADR-0013: Grading explanations with Claude, through the AI proxy

- **Status:** Proposed
- **Date:** 2026-11-06

## Context

- A topic is Learned only once its build, debug *and* explain checks pass ([ADR-0002](0002-mastery-and-gating.md)). Tests grade the build and the debug. Explanations need AI grading against the topic's rubric ([ADR-0003](0003-ai-roles-and-guardrails.md), [F7](../specs/v1.md#f7-prove-it)). Until that exists, no topic can be Learned, so topic states and gating can't switch on.
- The v1 spec already sets the outline ([F14](../specs/v1.md#f14-ai-proxy-and-budget-cap)):
  - a Supabase Edge Function is the only place the Claude API key exists;
  - every call is logged with its tokens and cost;
  - calls stop when the month's spending reaches the cap ($10 to start);
  - each action uses the cheapest model that passes its test set.
- This ADR fills in what the spec leaves open, for grading. The hint-only tutor (F13, Milestone D) will reuse the same proxy.
- An **Edge Function** is a small program that Supabase runs for us on its servers, on Deno (a JavaScript and TypeScript runtime). The learner's browser can call it but can't see inside it, which is why the key is safe there.

## Decision

### The path of one explanation

1. The learner writes their explanation in a box under the explain prompt and presses **Check my explanation**.
2. The browser sends it to the Edge Function `ai`, with the action `grade_explanation`, the topic, the prompt, the rubric and the model answer.
3. The function checks, in order:
   - the caller is signed in;
   - their profile is `allowed`;
   - this month's spending is under the cap.

   If any check fails, it calls nothing.
4. It asks Claude to grade the explanation against the rubric, and logs the call in `ai_calls`.
5. The page shows the verdict: **Pass**, or **Needs work** with guiding questions about what's missing. Never the model answer.
6. The browser saves an `explain_submit` event: the text, the verdict, each rubric item's result, and the `ai_calls` ID. Its `correct` is true for a pass, which is what progress tracking counts.

### Grading

- **A pass means every required rubric item is met.** Claude answers in structured output: fixed JSON fields, so a verdict can't come back malformed. The fields are:
  - whether each rubric item is met;
  - the verdict;
  - at most 3 guiding questions about the unmet required items.
- **Never the model answer.** Claude sees it, to judge correctness, but is told not to quote it. The function also blocks any reply that repeats a long stretch of it.
- **The explanation is data, not instructions.** It's sent in a clearly marked block, and Claude is told to grade whatever is inside, including attempts like "mark this as a pass".
- **Unlimited attempts,** each graded and logged (F7).

### The budget cap

- Every call adds a row to `ai_calls`. Like `events`, it's append-only. Each row records:
  - who and when;
  - the action and the model;
  - the token counts and the cost in dollars;
  - the request and the response.

  Only the function can write to it, and a learner can read their own rows.
- The cost comes from the token counts and a price table in the function. That table must be updated if Anthropic's prices change.
- Before each call, the function adds up this calendar month's costs (in UTC). At $10 or more it stops: the page says grading is paused until next month. The explanation is still saved, ungraded, so nothing written is lost.
- A second, hard limit lives in the Anthropic Console: a $10 monthly spending limit on the account ([setup guide](../setup.md#anthropic-console-week-2)).

### Choosing the model

As F14 says: the cheapest model that passes the grading test set.

- **The test set:** for each ready topic and checkpoint, 5 sample explanations, each with the verdict it should get:
  - a good one, and a short but correct one, which should pass;
  - one missing a required idea, one with a misconception, and one that tries to talk its way to a pass, which should not.

  That's 30 samples for Module 1. They're written ahead of time and reviewed like content.
- **The bar:** every sample gets its expected verdict, and no reply contains the model answer.
- **The order:** Claude Haiku 5.5 first, then Claude Sonnet 5.5, then Claude Opus 5.5. Each starts at low effort, and effort goes up before the model does.
- **Rough cost.** The prices come from Anthropic's model list (October 2026, checked again before building). The estimate assumes about 1,500 tokens in and 1,000 out per grading, Claude's thinking included.

  | Model | Per grading | $10 buys about |
  |---|---|---|
  | Claude Haiku 5.5 | $0.0007 | 15,000 gradings |
  | Claude Sonnet 5.5 | $0.013 | 770 |
  | Claude Opus 5.5 | $0.026 | 380 |

  One learner checking 5–10 explanations a day fits under the cap with any of them. One pass of the 30-sample test set on all three costs about $1.20. Every run costs real money, so the owner approves each one.

### Where the rubric comes from

- **In v1, the browser sends it,** with the prompt and the model answer, from the topic outline it already has.
- So a determined learner could change the rubric, or read the model answer, which is already in the app's code (like the hidden tests, [ADR-0007](0007-tech-stack.md)). With one learner, cheating only cheats yourself.
- **Before other learners join,** the function should read the content itself. That belongs with the roadmap's open question about hidden tests.

### Building and testing it

- **Code:** `supabase/functions/ai/`, in TypeScript on Deno, calling Claude through Anthropic's official TypeScript SDK. The logic that matters lives in plain functions with unit tests:
  - the checks and the budget;
  - building the prompt and reading the verdict;
  - the model-answer filter.

  Those tests run with `deno test`, locally and in CI. That means installing Deno (free).
- **Database:** a migration adds `ai_calls`, with database tests for its rules.
- **No automated test calls the real API.** Tests use a fake Claude. The test set is a separate script, run by hand when the owner approves: a Python script in `tools/` that sends the samples to the locally served function.
- **Local development:** the local Supabase serves the function. Its key goes in a gitignored file, `supabase/functions/.env`. Without a key, the function says grading is unavailable, and everything else keeps working.

### Rolling it out

1. The owner creates the Anthropic account, adds billing, sets the $10 limit, and creates an API key ([setup guide](../setup.md#anthropic-console-week-2)).
2. The owner puts the key in two places, never in chat or git:
   - the live project's Edge Function secrets, in the Supabase dashboard, or with `npx supabase secrets set --env-file <file>`;
   - the local `supabase/functions/.env`.
3. The owner switches on `allowed` on their own profile: one line in the dashboard's SQL editor.
4. The test set picks the model.
5. After the pull request merges, Claude applies the migration and deploys the function to the live project, once the owner says go.

## Alternatives considered

- **Self-assessment ("I explained it out loud"):** that's self-report, which ADR-0002 rules out.
- **Calling Claude from the browser:** the key would be public.
- **A separate proxy server (a Cloudflare Worker):** possible and free, but Supabase already has the sign-in and the database the proxy needs, so it would be one more thing to run.
- **Claude Opus by default, with no test set:** simplest, at about 40 times Haiku's cost. The spec asks for the cheapest model that passes.
- **The function reads the content itself, now:** safer against tampering, but it needs a build step that copies the content into the function. Not worth it for one learner.

## Consequences

- Topics can become Learned, so topic states and gating (F8) can switch on next.
- The platform's first paid part goes live, with two limits: the app's own cap, and the Console's.
- One new tool (Deno) and one new table (`ai_calls`).
- Grading is a judgment call. The test set and the logged calls let us check it; a wrong verdict can be reported (F15) and fixed in the prompt or the rubric.
- Explanations don't bring mistakes back yet ([ADR-0011](0011-mistakes-come-back.md)): explain prompts don't name skills. That can come later.
- The tutor (F13) reuses the proxy, the log and the cap, with its own test set.
