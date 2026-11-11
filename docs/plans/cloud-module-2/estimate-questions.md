# How Module 2 asks for an estimate, and how prices live in content

A design note for the critic and for whoever writes ADR-0024. It settles two things the Module 2 briefs depend on: the kind of question that takes a number and checks it within a tolerance, and how a question carries prices that will go out of date.

**Recommendation in one paragraph.** Add one recall item type, `estimate`: a prompt, a number typed by the learner, and a tolerance. Use it for every quick calculation and estimate in Module 2 and in the review pools. Keep bigger, multi-step sizing and costing work (the topic builds and Checkpoint 2's part 1) as labs, where the learner writes answers to a file in a container and the checks compute the truth from the data. Do not ask for estimates as Python functions before Module 6. Until `estimate` exists, each estimate question in the briefs has a mechanical fallback as a multiple-choice question.

## The problem

- The spec's drills are "checked within a tolerance" and "run in the browser" (cost within 15%, within 30% before opening a calculator; capacity within 20%; right-sizing within one size; availability within 0.01%).
- The platform has four recall types: `mcq`, `predict_output`, `predict_shell`, `parsons`. None takes a number with a tolerance. Exercises are Python programs or labs.
- The spec says drills "run as Python in the browser", but also that Python Foundations is needed only from Module 6. A learner in Module 2 may not have written a line of Python. Module 5's checkpoint ("estimates are checked within a tolerance") has the same gap, so the answer here is needed again soon.

## What was read

- `tools/content_model.py`: `RecallItem` is a union of four models chosen by `type`; every model forbids unknown fields.
- `tools/validate_content.py`: a ready topic needs at least 2 recall items in practice (`recall_count` sums four type names), a review pool with at least one of `predict_output`, `predict_shell`, `parsons` or `review_code`, and only those kinds plus `mcq` may be in a review pool (`review_kinds`). Each skill needs 2 questions that can come back; every recall item counts, whatever its type (`check_skills`).
- `web/src/content/types.ts` and `content.ts`: the same union in TypeScript; `withRecallDefaults` fills optional fields.
- `web/src/components/PracticeItem.tsx`: `describe()` picks a component by `type` and turns its answer into an `answer` event with a small `data` object. `McqQuestion.tsx` and `PredictOutput.tsx` are each about 120 to 190 lines: one attempt, then the answer and the explanation; a `quiet` mode for the placement test with "I don't know this".
- `web/src/reviews/reviews.ts`: a review asks 2 items from the pool, at least one "code or predict" (`isCodeOrPredict`), oldest-answered first.
- `web/src/followups/followUps.ts`: a missed item opens a follow-up on its skills; any recall item on the skill can be the come-back question. Nothing there looks at the type.
- `web/src/events/payloads.ts`: `answer` events carry free-form `data`; no database change is needed for a new kind of answer.

## The options

| | A. New `estimate` recall type | B. A small Python function | C. `predict_shell` with shell arithmetic | D. Multiple choice with numbers | E. Answers file in a lab |
| --- | --- | --- | --- | --- | --- |
| Needs knowledge the track hasn't taught | no | yes: functions, from Python Foundations | no | no | no (the shell, from Module 1) |
| The learner produces the number | yes | yes, as code | no: the command shows the sum, the learner only does the arithmetic | no: picks from four | yes |
| Tolerance | yes | yes, in the tests | no: exact text only | by spacing the choices | yes, in the check |
| Time to answer | 30 seconds to 2 minutes | 5 to 10 minutes | 1 minute | 30 seconds | 10 minutes and up |
| Fits a 2-question review session | yes | no | yes | yes | no |
| Feedback on a miss | the right number, how far off, the working, and the named mistake when the answer matches one | which test failed | the right output | the explanation | which check failed |
| Checks the method, not only the result | no | yes: tests can use other inputs | no | no | partly: a script can be run on a second input |
| Can be memorised | yes, if the same numbers come back | hardly | yes | yes | no |
| Cost to write one | one YAML file | a function, tests, a solution, wrong solutions | one YAML file | one YAML file | a lab |
| Platform work | one model, one validator check, one component, about ten files touched | none | none | none | none |

**Why A.** The owner's rule puts the learning experience first and retention second. Typing a number is producing the answer, which is remembered better than recognising it among four (the generation effect; `docs/learning-science.md` builds on retrieval practice). It is quick enough to come back in spaced review, which is where retention is made. It needs nothing the track hasn't taught. It is free. B fails the "no assumed knowledge" rule in Modules 2 to 5 and is too heavy for review at any stage. C gives the method away. D is recognition, and its choices give away the size of the answer; it stays useful for judgement questions and as the fallback.

**Why E as well.** A proof should show the whole job: read an inventory, apply the rules, compare options, state a total. That is ten numbers that depend on each other, and Module 1 already gave the learner the tools to work them out (`awk -F,` over a CSV, a script). A lab checks each number from the data, can run the learner's script on a second inventory so typed-in answers fail, and keeps Module 1's shell skills in use, which is spaced practice for them.

## The smallest `estimate` that works

```yaml
id: count-windows-three-vms
type: estimate
rev: 1
prompt: |
  Three Azure VMs will use Azure Hybrid Benefit for Windows Server. They have 2, 8 and 12 vCPUs.
  How many Windows Server core licences must you set aside for them?
unit: core licences          # shown after the box, so the learner never types it
answer: 28
tolerance:
  absolute: 0                # exactly one of: absolute, percent, factor
given: { a: 2, b: 8, c: 12, floor: 8 }
working: "max(floor, a) + max(floor, b) + max(floor, c)"
mistakes:
  - id: no-floor
    value: 22
    working: "a + b + c"
    why: "That counts vCPUs. Each VM needs at least 8 core licences, so the 2-vCPU VM takes 8."
  - id: floor-everywhere
    value: 24
    working: "3 * floor"
    why: "That gives every VM the minimum. A VM bigger than 8 vCPUs needs one licence per vCPU: the 12-vCPU VM takes 12."
explanation: |
  8 + 8 + 12 = 28. The minimum is 8 per VM; above 8, it's one per vCPU.
skills: [core-counting]
```

For a question with prices, two more fields:

```yaml
prices_as_of: 2026-11-10
prices_source: https://aws.amazon.com/ec2/pricing/on-demand/
```

**Fields.**

| Field | Meaning | Rule |
| --- | --- | --- |
| `prompt` | Markdown. Holds every number the learner needs, including any price table. | |
| `unit` | A few words shown after the input box. | Required. |
| `answer` | The right number. | A number. |
| `tolerance` | One of `absolute: d` (within ±d; 0 means exact), `percent: p` (within ±p% of the answer), `factor: f` (between answer ÷ f and answer × f). | Exactly one. `factor` needs a positive answer and f > 1. |
| `given` | The named numbers the working uses. | Optional. |
| `working` | The sum, as arithmetic over `given`. Shown to the learner after they answer. | Required. |
| `mistakes` | The wrong answers a learner is likely to give, each with the wrong sum and a sentence on what went wrong. | At least 1. |
| `explanation` | Markdown, shown after answering. | Required, like the other types. |
| `prices_as_of`, `prices_source` | The date the prices in the prompt were read, and the page that shows today's. | Both or neither. |
| `skills` | As for every item. | |

`factor` is there for "within one size" (a size up or down is a factor of 2 in vCPUs) and for Module 5's "within a factor of 2". It costs one comparison.

**Grading, in the browser.**

1. Read the typed text: trim it; drop a leading currency sign and a trailing `%`; drop commas between digits; then it must be a plain number with an optional decimal point. Anything else ("about 1,200", "1.2k", "1.168,50") shows "Type a number, like 1168" and is not counted as an attempt.
2. Correct when the number is inside the tolerance.
3. One attempt, like the other recall types. Then show: right or not; the answer with its unit and the accepted range; how far off the learner was ("you were 22% high"); the working; the explanation; and, when the typed number matches a `mistakes` value (within 0.5%), that mistake's `why` first.
4. The `answer` event's `data`: the typed text (clipped), the parsed value, the signed relative error, and the matched mistake's id or null. This is the log the future ML work will want: calibration over time, and which mistake.
5. `quiet` mode for the placement test, with "I don't know this", as the other types have.

A calculator is allowed and the lesson says so. The skill is setting up the sum and knowing the rule, not long multiplication. Module 1 taught `$(( ))` and `awk`, and any calculator will do.

**What the validator proves.** This is ADR-0004's rule for a question whose answer is a number: the reference answer passes and the known-wrong answers fail.

- `working`, evaluated over `given`, equals `answer` (to the number of decimals `answer` is written with). The evaluator accepts numbers, names from `given`, `+ - * / // % **`, brackets, and `min`, `max`, `round`, `ceil`, `floor`, `abs`, `sum`; nothing else.
- Each mistake's `working` equals its `value`, and each `value` falls **outside** the tolerance. A tolerance wide enough to accept a known mistake is a bug in the question, and this is the check that finds it.
- Mistake values differ from each other.
- Every number in `given` appears in the prompt (ignoring commas and trailing zeros), so a table that says one thing and a working that uses another is caught.
- `prices_as_of` and `prices_source` are present when the prompt contains a currency amount.
- A warning, not an error, when `percent` is above 30 or `factor` above 2: wider than any target in the spec.

**How it comes back.**

- It is a recall item, so it is a follow-up candidate with no change to `followUps.ts`, and it can sit in a review pool once `review_kinds` allows it.
- It should count as "code or predict" in `isCodeOrPredict` and in the validator's review-pool rule: the learner produces an answer rather than choosing one.
- **Numbers can be memorised.** If the same question returns three times in six months, "28" is recalled, not worked out. The first defence is content: every calculation skill gets at least three estimate questions with different numbers and stories, which is one more than the validator's minimum. The item's come-back order (unseen first, then oldest) does the rest. The second defence, if the event log later shows answers arriving faster than the sum could be done, is a `variants` list inside one item (several sets of `given`, `answer` and mistake values; the page shows the next set each time the item returns). It is left out now because it needs numbers templated into the prompt, which is more than the smallest thing that works.

**What it takes to build.**

| File | Change |
| --- | --- |
| `tools/content_model.py` | `Tolerance`, `Mistake`, `EstimateItem`; add to the `RecallItem` union. |
| `tools/validate_content.py` | `check_estimate` (the proofs above; pure arithmetic, so it also runs under `--no-run`); add `estimate` to `recall_count`, to `review_kinds`, and to the kinds that satisfy "the review pool needs a predict-the-output, Parsons or review_code item". |
| `tools/tests/` | The fixture and tests for each rule: a wrong `working`, a mistake inside the tolerance, a missing date. |
| `web/src/content/types.ts`, `content.ts` | The type; defaults for `given`, `mistakes`, the price fields. |
| `web/src/content/answers.ts` | `parseNumber` and `withinTolerance`, with tests. These two small pure functions are the grading. |
| `web/src/components/EstimateQuestion.tsx` and its test | About the size of `McqQuestion.tsx`. |
| `web/src/components/PracticeItem.tsx` | One more branch in `describe()`; heading "Work it out". |
| `web/src/reviews/reviews.ts` | `estimate` in `isCodeOrPredict`. |
| `web/src/test/fakeContent.tsx` | One fake item. |
| `docs/specs/data-model.md`, `content/README.md`, the cloud spec's "Drills" table | The format; "tips for estimate questions"; drills "run in the browser", not "as Python". |

No database migration, no new event type, no change to progress or follow-ups.

## What ADR-0024 must decide

1. **Whether to add the type at all,** against asking for Python Foundations before Module 2 or living with multiple choice. This note recommends adding it.
2. **The name and the fields,** above. In particular whether `working` and `mistakes` are required. Recommended: yes, both. They are what makes an estimate "machine-verified" in ADR-0004's sense, and `mistakes` is what makes the feedback worth reading.
3. **The tolerance kinds** (`absolute`, `percent`, `factor`) and their limits.
4. **What the learner may type** and what counts as "not a number" without costing the attempt.
5. **Whether it counts as "code or predict"** in review sessions and in the review-pool rule. Recommended: yes.
6. **What the event records.** Recommended: text, value, relative error, matched mistake.
7. **Time.** The spec's drill targets ("about a minute each") are fluency standards. Recommended for now: the attempt's duration is already saved with every answer, so decide nothing yet and show no clock; revisit with the owner's own data.
8. **Prices:** the two price fields and the validator's rule, below.
9. **The spec.** Amend "Drills run as Python in the browser" to say that quick drills are estimate questions, and that Python drills (subnetting by code, the estate inventory) start in Module 6.
10. **Variants,** recorded as the planned next step with the signal that would trigger it.

## The fallback while `estimate` doesn't exist

Every estimate question in the briefs converts to multiple choice without new thought: the choices are the answer and its `mistakes` values, the explanation is the working plus each mistake's `why`. Numbers are all about the same length, so the audit's "the right answer is the longest choice" can't happen. For a tolerance question, the prompt says "which is closest?" The topic then needs its `predict_shell` items for the review-pool rule, and the briefs include some. A topic written this way should be revisited when the type lands: the items keep their ids, change `type`, and bump `rev`.

## Prices in content

Right-sizing and cost questions need prices, and prices change. The design has four parts.

1. **The question carries its own dated table.** A small Markdown table in the prompt, only the rows the question needs, with a caption: "On-demand prices, US East (N. Virginia), read 2026-11-10. Use 730 hours a month." The answer is worked from that table, so the question stays right when the real price moves. `prices_as_of` and `prices_source` hold the date and the live page as data, so the page can print the same line under every such question: "These prices were read on 10 November 2026. Today's are at [link]; expect them to differ."
2. **The lesson teaches the look-up once, by doing it.** One short step in each topic that uses prices: open the provider's price page, find one named instance, and compare it with the lesson's table. It isn't graded, because today's number can't be checked. The licensing topic also has a skill, `look-it-up`, whose questions ask where a rule or a price is settled and which facts go stale, and those are graded.
3. **Labs carry the table as a file.** The dated CSV is in the image (`/srv/.../prices.csv`, with a `README` giving the date, the region and the source pages). Checks compute the right answer from the CSV and never hold a number, which is the README's own rule ("compute it in the check"). A check confirms the file hasn't been edited (its checksum), since the learner has `sudo`.
4. **One fixture per reading.** Writers copy rows from [price-fixture-2026-11.md](price-fixture-2026-11.md). A fixture is never edited; a later reading is a new file. A yearly look at the fixture against live prices is enough: if a question's story has stopped being true (the cheaper option is no longer cheaper), rewrite the question and bump its `rev`; if only the cents moved, leave it.

**What a question must never do:** state a price in prose without a date; ask for "the current price"; rely on a price the learner is expected to remember. The one number worth remembering is a rule of thumb the lesson names as such (Windows Server adds $0.046 a vCPU-hour, about $34 a vCPU a month, on all three clouds as of this reading), and questions that test it use the 30% tolerance.

## Open questions, each with a recommendation

- **Should an estimate allow a second try?** The other recall types give one attempt. A second try after "you were 40% high" would teach, but it changes what "correct" means in the log. Recommended: one attempt, as now; the come-back question is the second try.
- **Should the page offer a calculator or scratch area?** Recommended: no. It is more to build and the learner has one.
- **Should the accepted range be shown before answering** ("within 15%")? Recommended: yes, in the prompt's last line. Knowing how exact to be is part of estimating, and hiding it makes people over-work an estimate.
- **Should right-sizing "within one size" be an estimate or a choice from a list of sizes?** Recommended: an estimate of the vCPUs (or the memory) with `factor: 2` for quick drills, and the lab's answers file for the checkpoint, where the check can use the price sheet's real sizes.
