# ADR-0012: Getting unstuck on a checkpoint

- **Status:** Proposed
- **Date:** 2026-11-06

## Context

- Each module ends with a checkpoint ([F10](../specs/v1.md#f10-module-checkpoints)): a bigger build, a debug with several bugs, and a module-level explain. It gates the next module.
- A checkpoint combines a module's skills. Getting stuck on one usually means one or two of those skills are still shaky, or the learner doesn't yet know how to break a bigger problem into steps.
- The owner asked what happens if someone really struggles with a checkpoint. Today, nothing special:
  - proof checks have no hints;
  - mistakes come back for topic skills ([ADR-0011](0011-mistakes-come-back.md)), but nothing ties a failed checkpoint to the skill behind it.
- **What the research suggests:**
  - **Mastery learning:** after an assessment, give corrective practice aimed at what was missed, then a *parallel* re-test, a fresh version of the same task (Bloom; Guskey).
  - **Worked examples and completion problems:** for novices facing complex tasks, studying a solved example and finishing a partly written solution beat unsupported problem solving. The support is then faded as skill grows (Sweller's worked-example effect; Renkl & Atkinson on fading; van Merriënboer's 4C/ID model).

## Decision (proposed)

1. **Find the weak skill.** Each checkpoint test names the module skill it checks, for example "reads the tip percentage" names the `convert` skill of Strings and input. A failed checkpoint test opens a follow-up on that skill (ADR-0011), so targeted practice comes back on Today.
2. **Study a solved sibling.** A worked example of a *similar* project, with a different story, shows how someone breaks the problem down.
3. **Try it in steps.** The same project split into 3 or 4 small exercises (for the receipt: read the inputs, work out the totals, format the receipt), each partly written, with hints allowed. It's offered after 2 failing Checks on the build, or any time with a "Try it in steps" button. Getting stuck isn't a failure; it's the signal to use this.
4. **Prove it on a fresh version.** Each checkpoint has 2 parallel versions: the same skills in a different story. After the steps, the learner proves it from a blank editor on a version they haven't seen. Passing any version passes the checkpoint's build.
5. **Debug and explain** get the same treatment where it fits: a second debug program with different bugs, and, once explanations are graded, feedback that asks guiding questions ([ADR-0003](0003-ai-roles-and-guardrails.md)).

## Alternatives considered

- **Hints inside the checkpoint itself.** That would turn the proof into practice. Hints belong in the stepped version instead ([ADR-0002](0002-mastery-and-gating.md), ADR-0003).
- **Retrying the same checkpoint until it passes.** A learner can end up remembering one answer instead of learning to build it.
- **Sending the learner back to re-read the module.** Passive re-reading works worse than retrieval and practice.

## Consequences

- More content per checkpoint: a solved sibling, a stepped version of 3 or 4 exercises, and 2 parallel versions of the build.
- Checkpoint tests need to name skills from the module's topics, as a `topic/skill` pair.
- The content checker validates every step and version like any other exercise.
