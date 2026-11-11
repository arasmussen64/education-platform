# ADR-0024: Estimate questions, a typed number checked within a tolerance

- **Status:** Proposed
- **Date:** 2026-11-11

## Context

The Cloud Solutions Architect track's drills are "checked within a tolerance" and "run in the browser" ([spec](../specs/cloud-solutions-architect.md#drills-practice-that-builds-speed)): cost within 15%, within 30% before opening a calculator, capacity within 20%. Module 2, the first module that needs them, asks for about 70 quick calculations: core licences with their floors, a month's licence cost, when a burstable instance's credits run out, whether a model fits a GPU's memory, which disk allowance binds.

The platform has four recall item types, `mcq`, `predict_output`, `predict_shell` and `parsons`, and none takes a number. Exercises are Python programs or labs. The spec says drills "run as Python in the browser", but also that Python Foundations is needed only from Module 6, so a learner in Modules 2 to 5 may not have written a function. Module 5's checkpoint ("estimates are checked within a tolerance") has the same gap.

The ways a number could be asked today each lose something. As multiple choice, the learner recognises rather than produces, and the four numbers give away the answer's size. As `predict_shell`, the command shows the sum and only the arithmetic is the learner's. As a Python function, it needs what the learner hasn't been taught and takes ten minutes, too long to come back in a two-question review. As a lab with an answers file, it is right for a proof (Module 2's builds do this) and far too heavy for a quick question.

Two of Module 2's designers specified a new type independently, differently: one (`numeric`) with an answer and a tolerance, one (`estimate`) that also carries the working and the likely mistakes, so the validator can prove the question the way ADR-0004 proves an exercise. This ADR settles one.

## Decision

Add one recall item type, `estimate`.

```yaml
id: count-windows-three-vms
type: estimate
rev: 1
prompt: |
  Three Azure VMs will use Azure Hybrid Benefit for Windows Server. They have 2, 8 and 12 vCPUs.
  How many Windows Server core licences must you set aside for them? Exact.
unit: core licences
answer: 28
tolerance: { absolute: 0 }
given: { a: 2, b: 8, c: 12, floor: 8 }
working: "max(floor, a) + max(floor, b) + max(floor, c)"
mistakes:
  - { id: no-floor, value: 22, working: "a + b + c", why: "That counts vCPUs; each VM needs at least 8." }
  - { id: floor-everywhere, value: 24, working: "3 * floor", why: "A VM over 8 vCPUs needs one licence per vCPU." }
explanation: |
  8 + 8 + 12 = 28. The minimum is 8 per VM; above 8, it's one per vCPU.
skills: [core-counting]
```

1. **Fields.** `prompt` (holds every number the learner needs, including any price table, and ends by saying how exact to be); `unit` (shown after the box); `answer`; `tolerance` with exactly one of `absolute` (within ±d; 0 is exact) or `percent` (within ±p% of the answer); `given` (the named numbers the working uses); `working` (arithmetic over `given`, shown after answering); `mistakes` (at least one: `id`, `value`, `working`, `why`); `explanation`; `skills`. A question with prices adds `prices_as_of` and `prices_source` (both or neither).
2. **Grading, in the browser.** The typed text is trimmed; a leading currency sign, a trailing `%` and commas between digits are dropped; what is left must be a plain decimal number, or the page says "Type a number, like 1168" and counts no attempt. Right means inside the tolerance. One attempt, as for the other types. Then the page shows: right or not, the answer with its unit and the accepted range, how far off ("22% high"), the matched mistake's `why` first when the typed number is within 0.5% of a mistake's value, the working and the explanation. A `quiet` mode serves the placement test, as for the other types.
3. **What the validator proves**, as ADR-0004 requires of anything with a right answer: `working` evaluated over `given` equals `answer` to the decimals `answer` is written with; each mistake's `working` equals its `value`, and every `value` lies **outside** the tolerance (a tolerance wide enough to accept a known mistake is a bug in the question); mistake values differ; every number in `given` appears in the prompt; the price fields are present when the prompt holds a currency amount. The evaluator accepts numbers, names from `given`, `+ - * / // % **`, brackets and `min`, `max`, `round`, `ceil`, `floor`, `abs`, and nothing else. It is pure arithmetic, so it runs under `--no-run` too. A tolerance over 30% is a warning.
4. **Reviews and follow-ups.** It is a recall item, so it can be a follow-up's come-back question with no change ([ADR-0011](0011-mistakes-come-back.md)). It may sit in a review pool, and it counts as "code or predict" both in review sessions (`isCodeOrPredict`) and in the validator's review-pool rule, because the learner produces the answer.
5. **The event.** The `answer` event's free-form `data` records the typed text (clipped), the parsed number, the signed relative error and the matched mistake's id or null. No new event type, no migration ([ADR-0008](0008-event-log.md)).
6. **Content rules.** Every calculation skill gets at least three estimate items with different numbers and stories, so a returning question isn't recalled by heart; a proof never reuses a practice item's numbers. A calculator is allowed and the lesson says so.
7. **The spec.** "Drills run as Python in the browser" is amended: quick drills are estimate questions; drills written as code start in Module 6.

## Alternatives considered

- **Multiple choice with numbers.** Nothing to build, and it stays the right type for judgement questions. Recognition is weaker than recall for retention, and the choices tell the learner the answer's size.
- **A small Python function.** Checks the method, not just the number, but needs Python Foundations, which this track requires only from Module 6, and takes too long for a review.
- **`predict_shell` with shell arithmetic.** Exists today, but the command does the sum: it tests reading a pipeline.
- **`numeric`: an answer and a tolerance only.** Smaller, but the validator could prove nothing beyond "these are numbers", and the feedback could only say "wrong". The working and the mistakes are what make an estimate machine-verified in ADR-0004's sense and worth reading after a miss.
- **A `factor` tolerance** (between answer ÷ f and answer × f), for "within one size" and Module 5's "within a factor of 2". Left out until a module needs it; it is one more comparison then.
- **Variants** (several sets of numbers in one item, shown in turn). Left out: it needs numbers templated into the prompt. Revisit if the event log shows answers arriving faster than the sum could be done.

## Consequences

- About ten files change (`tools/content_model.py`, `tools/validate_content.py` and its tests, `web/src/content/types.ts` and `content.ts`, a new `web/src/content/answers.ts` pair of functions, `EstimateQuestion.tsx` with its test, `PracticeItem.tsx`, `reviews.ts`, the fake content, `docs/specs/data-model.md`, `content/README.md`). No database migration.
- Module 2 can be written with numbers produced, not picked, and Modules 3 to 5 inherit the type (capacity, availability and cost drills).
- Writing an estimate costs more than a multiple-choice item: the working and two or three named mistakes, each proved by the validator.
- A typed number can be memorised; the three-items-per-skill rule is the first defence, variants the second.
