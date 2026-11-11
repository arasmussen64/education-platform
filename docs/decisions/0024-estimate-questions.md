# ADR-0024: Estimate questions, a typed number checked within a tolerance

- **Status:** Proposed. Designed under the owner's delegation of 2026-11-11 (the best learning experience, then memory retention, then free), and built on until the owner rules; listed in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".
- **Date:** 2026-11-11

## Context

The Cloud Solutions Architect track's drills are "checked within a tolerance" and "run in the browser" ([spec](../specs/cloud-solutions-architect.md#drills-practice-that-builds-speed)): cost within 15%, within 30% before opening a calculator, capacity within 20%. Module 2, the first module that needs them, asks for about 70 quick calculations: core licences with their minimums, a month's licence cost, when a burstable instance's credits run out, whether a model fits a GPU's memory, which disk allowance binds.

The platform had four recall item types, `mcq`, `predict_output`, `predict_shell` and `parsons`, and none takes a number. Exercises are Python programs or labs. The spec says drills "run as Python in the browser", but also that Python Foundations is needed only from Module 6, so a learner in Modules 2 to 5 may not have written a function. Module 5's checkpoint ("estimates are checked within a tolerance") has the same gap.

Each way a number could be asked before this loses something. As multiple choice, the learner recognises rather than produces, and the four numbers give away the answer's size. As `predict_shell`, the command does the sum and only reading it is the learner's. As a Python function, it needs what the track hasn't taught and takes ten minutes, too long to come back in a two-item review. As a lab with an answers file, it is right for a proof (Module 2's builds do this) and far too heavy for a quick question.

## Decision

Add one recall item type, `estimate`: the learner works out a number and types it, and it's right when it lies within the item's tolerance. The validator proves every item from its own numbers, the way [ADR-0004](0004-content-model.md) proves an exercise: the reference answer passes and the known-wrong answers fail.

```yaml
# content/topics/<topic>/recall/count-windows-three-vms.yaml
id: count-windows-three-vms
type: estimate
rev: 1
prompt: |
  Three Azure VMs will use Azure Hybrid Benefit for Windows Server. They have
  2, 8 and 12 vCPUs. How many Windows Server core licences must you set aside
  for them? Exactly.
unit: core licences
answer: 28
tolerance: { absolute: 0 }
given: { small: 2, medium: 8, large: 12 }
# 8 is the per-VM minimum the learner must know, so it isn't given.
working: max(8, small) + max(8, medium) + max(8, large)
mistakes:
  - id: no-minimum
    value: 22
    working: small + medium + large
    why: That counts vCPUs. Each VM needs at least 8 core licences, so the 2-vCPU VM takes 8.
  - id: minimum-everywhere
    value: 24
    working: 3 * 8
    why: That gives every VM the minimum. A VM bigger than 8 vCPUs needs one licence per vCPU.
explanation: 8 + 8 + 12 = 28. The minimum is 8 per VM; above 8, it's one per vCPU.
skills: [core-counting]
```

1. **Fields.**
   - `prompt` holds every number the learner needs, including any price table, and ends by saying how exact to be ("Exactly", "Within 15%"). Knowing how exact to be is part of estimating.
   - `unit` is shown after the number box, so the learner never types it.
   - `answer` is the number, worked out exactly; the tolerance does the forgiving.
   - `tolerance` is exactly one of `absolute: d` (within d either side; 0 means exactly) or `percent: p` (within p% of the answer either side, with p above 0 and at most 30, the widest target the drills set). A percentage needs an answer that isn't 0.
   - `given` names the numbers the prompt states, as the prompt writes them: 30 for "30%", not 0.3. At least one.
   - `working` is the sum over those names that gives the answer. A number the learner must know rather than read, like the 8-core minimum, is written into the working as a plain number, so the check that every given number is in the prompt never forces the prompt to give a rule away. The working may use numbers, the given names, `+ - * / // % **`, brackets, and `min`, `max`, `round`, `ceil`, `floor` and `abs`; `round` sends a half away from zero, as taught at school, not to the even number as Python's does.
   - `mistakes`: at least one wrong answer a learner is likely to give, each with an `id`, its `value`, the `working` that gives it, and `why`, the sentence a learner sees when their answer matches it.
   - `explanation` and `skills`, as on every recall item.
   - `prices_as_of` (a date) and `prices_source` (an `https://` page with today's prices): both or neither, and both when the prompt holds an amount of money.
   - Numbers are numbers: `"28"` in quotes is refused, and so are `10_000`, `012` and `1:30`, which Python's YAML reads as numbers (YAML 1.1) and the browser's reads as text or as a different number (YAML 1.2).
2. **What the validator proves**, with plain arithmetic, so `--no-run` checks it too. The working is parsed with Python's `ast` module and worked out with exact fractions (`tools/arithmetic.py`), never run with `eval()`, so content can't run code and 0.1 + 0.2 is 0.3. It refuses any number in a sum of more than about 300 digits and any sum nested thousands deep, so no working can make the validator hang. Then:
   - the working gives the answer, once rounded to the decimals the answer is written with, and the exact result also lies inside the tolerance, so a learner who works it out to the last digit is marked right;
   - each mistake's working gives its value the same way, and neither the value nor the exact result lies inside the tolerance, edges included: a tolerance that accepts a known mistake is a bug in the question;
   - no two mistakes give the same value;
   - every given number appears in the prompt (commas between thousands and trailing zeros don't matter), and no given takes a function's name or a word Python keeps for itself, like `in`;
   - a prompt with an amount of money ($, €, £, ¥, or USD, EUR, GBP beside a number, outside code) has its prices dated.
3. **On the page.** A labelled number box, the unit beside it, and Check, which Enter also presses. A phone shows its full keyboard there, not its decimal keypad, which offers the decimal mark of the phone's region (a comma in much of Europe) and may have no minus. What the learner types is read forgivingly: spaces around it, a sign, a currency sign in front, commas between groups of three, and a % after it when the unit is a percentage. Anything else ("about 1200", "1.2k", "1.168,50", and "11,68", which much of Europe would read as 11.68) gets a note on how to type a number and counts nothing: no attempt, no event. One attempt, as for the other types; the come-back question is the second try. Afterwards the page says right or not, the answer with its unit, how far off in the tolerance's own terms ("17% low" for a percentage, "6 low" for an absolute one) and, for a wrong answer, the accepted range, the matched mistake's `why` when a wrong answer is within half a percent of a mistake's value (the nearest, if two are), the working with its given numbers, and the explanation. Half a percent allows for rounding along the way but not for a different slip; telling a learner they made a mistake they didn't would mislead. A question with prices says when they were read and links today's. In the placement test it has the quiet mode the other types have, with "I don't know this". There's no clock and no calculator: a calculator of the learner's own is allowed, and the lesson says so, because the skill is setting up the sum.
4. **Where it counts.** It is a recall item everywhere a recall item goes: the practice ladder's recall count, the review pool, follow-ups after a miss ([ADR-0011](0011-mistakes-come-back.md)), interleaved questions, and the placement test's probes, where it isn't a choice. In review sessions (`isCodeOrPredict`) and in the validator's review-pool rule it counts as "code or predict" ([ADR-0009](0009-reviews.md)), because that rule exists so every session has an item whose answer is produced, not picked, and an estimate's number is produced. A topic's review pool can meet the rule with an estimate alone.
5. **The event.** An `answer` event like the other recall items ([ADR-0008](0008-event-log.md)), with `correct`, and in `data`: `typed`, what the learner typed (clipped like other text); `number`, what it was read as; `relative_error`, how far off as a signed share of the answer (0.22 for 22% high, null when the answer is 0); and `mistake`, the matched mistake's id, or null. "I don't know this" saves `dont_know: true` with those four null. No new event type, no migration, and no existing event changes meaning.
6. **Content rules.** Every calculation skill gets at least three estimate items with different numbers and stories, so a returning question is worked out, not recalled by heart. A proof never reuses a practice or review item's numbers. An answer must not sit on a knife edge: it survives a change of convention (GB or GiB, 720 or 730 hours) or every wrong option clears it by a stated margin.
7. **The spec.** "Drills run as Python in the browser" changes: quick drills are estimate questions, and drills written as code start in Module 6.

## Alternatives considered

- **Multiple choice with numbers.** Nothing to build, and it stays the right type for judgement questions and the fallback while a topic waits for this. Recognition is weaker than recall for retention, and the choices tell the learner the answer's size.
- **A small Python function.** Checks the method, not just the number, but needs Python Foundations, which this track requires only from Module 6, and takes too long for a review.
- **`predict_shell` with shell arithmetic.** Exists already, but the command does the sum: it tests reading a pipeline.
- **An answer and a tolerance only.** Smaller, but the validator could prove nothing beyond "these are numbers", and the feedback could only say "wrong". The working and the mistakes are what make an estimate machine-verified and worth reading after a miss.
- **A list of numbers the learner must know, beside `given`.** It would name the 8 in `max(8, small)`. A plain number in the working says the same with nothing new to build.
- **Python's own rounding.** It sends 2.5 to 2, which no learner checking the working by hand would expect.
- **A warning, not a limit, for a tolerance over 30%.** The validator reports problems and has no warnings, and 30% is already the loosest target in the spec. A module that needs wider (Module 5's "within a factor of 2") adds a `factor` tolerance then, with its own ADR.
- **Matching a mistake within the question's own tolerance.** It would name a slip more often, but a 30% band around a mistake catches answers that came from something else, and a wrong "you did this" misleads.
- **Dropping commas anywhere between digits.** It would read "1.168,50" as 1.1685 and "11,68" as 1168.
- **Variants** (several sets of numbers in one item, shown in turn). Left out: it needs numbers templated into the prompt. The next step if the event log shows answers arriving faster than the sum could be done.

## Consequences

- One new item type in the content model, the validator, the web types, one component and its grading functions; the review rule in both places now includes it. No database migration.
- Module 2 can be written with numbers produced, not picked, and Modules 3 to 5 inherit the type for capacity, availability and cost drills.
- Writing an estimate costs more than a multiple-choice item: the working and one to three named mistakes, each proved.
- A typed number can be memorised. Three items per skill is the first defence, variants the second.
- The given-number rule only checks that each number appears somewhere in the prompt, not that it means what the name says; a writer still reads the prompt against the working.
