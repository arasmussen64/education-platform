# ADR-0012: Getting unstuck on a checkpoint

- **Status:** Accepted (the owner asked for all four additions on every checkpoint; details settled while building it are in the Decision)
- **Date:** 2026-11-06

## Context

- Each module ends with a checkpoint ([F10](../specs/v1.md#f10-module-checkpoints)): a bigger build, a debug with several bugs, and a module-level explain. It gates the next module.
- A checkpoint combines a module's skills. Getting stuck on one usually means one or two of those skills are still shaky, or the learner doesn't yet know how to break a bigger problem into steps.
- The owner asked what happens if someone really struggles with a checkpoint. Until now, nothing special:
  - proof checks have no hints;
  - mistakes come back for topic skills ([ADR-0011](0011-mistakes-come-back.md)), but nothing ties a failed checkpoint to the skill behind it.
- **What the research suggests:**
  - **Mastery learning:** after an assessment, give corrective practice aimed at what was missed, then a *parallel* re-test, a fresh version of the same task (Bloom; Guskey).
  - **Worked examples and completion problems:** for novices facing complex tasks, studying a solved example and finishing a partly written solution beat unsupported problem solving. The support is then faded as skill grows (Sweller's worked-example effect; van Gog et al. on example-problem pairs; Renkl & Atkinson on fading; van Merriënboer's 4C/ID model).

## Decision

Every checkpoint gets four additions. The content checker won't mark a checkpoint `ready` without them.

1. **Find the weak skill.** Every test of a checkpoint's builds and debug names the skills it checks, as `topic/skill`. For example, a test that reads the tip percentage names `py.strings-and-input/convert`. A failed test opens a follow-up on those skills (ADR-0011), so targeted practice comes back on Today.
   - As with code exercises, a test counts as missed only if no Check passed it that day. Failing on the way to a working program isn't a mistake.
   - A program that crashes fails every test, so it points at every skill they name. Once it runs, only the tests that still fail count.
   - A passed test counts as a correct answer on its skills.
2. **Study a solved sibling.** A worked example of a *similar* project, in a different story, shows how to break the problem into parts.
3. **Try it in steps.** The build itself, as 3 or 4 fill-in exercises with hints.
   - Each step gives the whole program except one part: read the inputs, work out the numbers, or print the result.
   - The last step gives only an outline, as comments.
   - Together they're completion problems whose support fades step by step (Renkl & Atkinson).
   - The steps are always one click away. After 2 failing Checks on the build, the page also suggests them, next to the build. They never open by themselves: the learner decides when to use them.
4. **Prove it on a fresh version.** Besides the main build, each checkpoint has at least 2 fresh versions: the same skills in different stories.
   - After the steps, the learner builds one from a blank editor, with no hints.
   - The page offers a version the learner hasn't Checked yet, or else the one Checked longest ago, so a second try is fresh too.
   - Passing any version counts the same as passing the main build.

**Debug and explain:**
- The debug's tests name skills too (item 1).
- A second debug program waits until learners actually get stuck on debugs. Unlike a build, a debug can be worked through by running it and comparing outputs.
- Explanation feedback that asks guiding questions comes with grading in Milestone B ([ADR-0003](0003-ai-roles-and-guardrails.md)).

## Alternatives considered

- **Hints inside the checkpoint itself.** That would turn the proof into practice. Hints belong in the steps instead ([ADR-0002](0002-mastery-and-gating.md), ADR-0003).
- **Retrying the same checkpoint until it passes.** A learner can end up remembering one answer instead of learning to build it.
- **Sending the learner back to re-read the module.** Passive re-reading works worse than retrieval and practice.
- **Steps that each build one part on its own.** Practicing parts in isolation transfers worse than practicing the whole task with support (4C/ID), so each step shows the whole program.
- **Opening the steps automatically after 2 failing Checks.** Some productive struggle helps, and a panel that opens by itself takes that choice away. A suggestion keeps the learner in charge.

## Consequences

- Each checkpoint needs more content: besides its build, debug and explain, a solved sibling, 3 or 4 steps, and 2 fresh versions of the build. The content checker runs every one of them like any other exercise.
- Every test of a checkpoint's builds and debug names its skills, in `test_skills` in its exercise.yaml. Each Check already saves which tests failed, so this needs no new data.
- The Today page also loads checkpoints from the learner's history, and the topics their tests name.
- Milestone B's progress tracking must count a pass on any version as passing the checkpoint's build.

## Amendment (2026-11-10): the explain check opens after the build

On a checkpoint page, the explain check stays closed until the checkpoint's build has passed. Until then the page shows its heading and one line, "Explain it back opens once your build passes", and nothing of its prompt.

- **Why.** The page used to show all three proof checks together, and a checkpoint's explain prompt often says "here's a working program" and then asks how it works. An audit on 2026-11-10 found that in Python Checkpoints 2 to 6 that program overlaps the build's own reference solution: Checkpoint 2's prompt is the solution minus five lines. An honest learner scrolling the page saw most of the answer while doing the "blank editor" build. That is a hint inside the checkpoint, which this ADR rejected (see Alternatives considered), and it made a saved "build passed" mean less than it says.
- **What counts as passed.** The same rule as the rest of the page and `web/src/progress/progress.ts`: a passing Check of the main build or of any fresh version, on any day. A Check passed during the visit opens the explain check straight away, with no reload.
- **When the page can't tell.** While the learner's progress is loading, or if it couldn't load, the explain check stays closed and says why (with "Try again" in the second case). It also stays closed for a signed-out visitor: nothing they do is saved, so the page never learns that their build passed, and an explanation can't be checked without signing in anyway.
- **What doesn't change.** Regular topics still show all three checks at once; this is only for checkpoints, where the overlap was found. The debug stays open from the start on a checkpoint too. Progress is still worked out the same way from the saved events, so an explanation that passed before this change still counts.
- **Alternative considered: rewriting the five prompts around a different program.** That fixes today's checkpoints but leaves the next one free to repeat the mistake. Hiding the prompt holds whatever the prompt says, and needs no content change. Prompts that lean less on the build's own code would still be better content, and can follow.

## Amendment (2026-11-11): once the steps are opened, only a fresh version proves the build

Once the learner has opened a checkpoint's steps, a pass of its main build no longer counts as the build proof. A pass of any fresh version still does, as item 4 says, and so does a pass of the main build from before the steps were first opened.

- **Why.** The steps are the build itself, worked through: each one shows the whole program but one part (item 3), it runs as practice with hints and the tutor on, and a passed step shows its reference solution. An audit on 2026-11-11 compared each ready checkpoint's last step with its main build: in Python Checkpoints 1, 2, 3 and 6 the solutions are the same line for line apart from comments, and in 4 and 5 they differ in one or two lines. Item 4 already said that after the steps the learner proves it on a fresh version, but nothing enforced it, so going back up to finish the main build, the natural move, passed the "blank editor, no hints" proof of [ADR-0002](0002-mastery-and-gating.md) with most of the answer just seen. A fresh version asks for the same skills in a different story, so it proves the same thing without the steps' answer.
- **From when.** From the first time the steps are opened, not the first Check of a step: the steps show most of the program as soon as they open.
- **How it's known.** The checkpoint page saves the first opening of the steps on each visit as a `hint` event, since the steps are help with the build: the checkpoint's id, the build as its item, the context `prove`, and `source: "steps"` in its data. `hint` was already an event type, so no migration was needed. Progress (`web/src/progress/progress.ts`) reads these openings with the rest of the history and goes by the earliest. Times are compared as the learner's devices recorded them.
- **Earlier history.** Openings were first saved on 2026-11-11. History from before has none, so every pass of a main build in it still counts, as it did. A Check of a step in that history isn't read as a sign the steps were opened: that would change what history already saved means.
- **What the learner sees.** Before the "Show the steps" button, the page says that opening them moves the proof to a fresh version, and the suggestion that appears after two failing Checks mentions the fresh version too. Once the steps have been opened (on this visit or an earlier one) and until the build is proved, a note above the build says a pass there no longer counts, with a button to the fresh version, and the closed explain check says it opens once a fresh version passes. The main build stays on the page for practice, and its Checks are saved and bring missed skills back as before (item 1).
- **Alternatives considered.**
  - **Leave it to the learner.** The page already said "prove it on a fresh version", but a saved "build passed" would still mean less than it says.
  - **Count from the first Check of a step.** It misses a learner who only reads the steps, and they show most of the program without a Check.
  - **Take the main build off the page once the steps are opened.** It would hide the learner's own work and make the page change shape; a note is enough, and the build is still useful practice.
  - **Steps that show less of the build's program.** Showing the whole task with support is what makes them work (item 3, 4C/ID), so the proof moves instead.
- **The cost.** A learner who opens the steps out of curiosity before trying the build proves it on a fresh version instead: the same skills, so no harder, and the page says so before they choose.

Decided under the owner's delegation of 2026-11-11 and recorded in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".
