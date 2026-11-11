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

Once the learner has opened a checkpoint's steps, a pass of its main build no longer counts as the build proof. A pass of any fresh version still does, as item 4 says, and so does a pass of the main build from before the steps were first opened. Every ready checkpoint has fresh versions; one without any would keep counting its main build, so a build can never become impossible to prove.

- **Why.** The steps are the build itself, worked through: each one shows the whole program but one part (item 3), it runs as practice with hints and the tutor on, and a passed step shows its reference solution. An audit on 2026-11-11 compared each ready checkpoint's last step with its main build: in Python Checkpoints 1, 2, 3 and 6 the solutions are the same line for line apart from comments, and in 4 and 5 they differ in one or two lines. Item 4 already said that after the steps the learner proves it on a fresh version, but nothing enforced it, so going back up to finish the main build, the natural move, passed the "blank editor, no hints" proof of [ADR-0002](0002-mastery-and-gating.md) with most of the answer just seen. A fresh version asks for the same skills in a different story, so it can prove the same thing without the steps' answer (but see "Where it falls short" below).
- **From when.** From the first time the steps are opened, not the first Check of a step: the steps show most of the program as soon as they open.
- **How it's known.** The checkpoint page saves the first opening of the steps on each visit as a `hint` event, since the steps are help with the build: the checkpoint's id, the build as its item, the context `prove`, and `source: "steps"` in its data. `hint` was already an event type, so no migration was needed. Progress (`web/src/progress/progress.ts`) reads these openings with the rest of the history and goes by the earliest. Times are compared as the learner's devices recorded them.
- **Earlier history.** Openings were first saved on 2026-11-11. History from before has none, so every pass of a main build in it still counts, as it did. A Check of a step in that history isn't read as a sign the steps were opened: that would change what history already saved means.
- **What the learner sees.** Before the "Show the steps" button, the page says that opening them moves the proof to a fresh version, and the suggestion that appears after two failing Checks says so too, since its button opens the steps straight away. Once the steps have been opened (on this visit or an earlier one) and until the build is proved, a note above the build says a pass there no longer counts, with a button to the fresh version, and the closed explain check says it opens once a fresh version passes. The main build stays on the page for practice, and its Checks are saved and bring missed skills back as before (item 1).
- **Alternatives considered.**
  - **Leave it to the learner.** The page already said "prove it on a fresh version", but a saved "build passed" would still mean less than it says.
  - **Count from the first Check of a step.** It misses a learner who only reads the steps, and they show most of the program without a Check.
  - **Take the main build off the page once the steps are opened.** It would hide the learner's own work and make the page change shape; a note is enough, and the build is still useful practice.
  - **Steps that show less of the build's program.** Showing the whole task with support is what makes them work (item 3, 4C/ID), so the proof moves instead.
- **The cost.** A learner who opens the steps out of curiosity before trying the build proves it on a fresh version instead: the same skills, so no harder, and the page says so before they choose.
- **Where it falls short.** Moving the proof to a fresh version helps only as far as the fresh versions differ from what the steps show. A count on 2026-11-11 of each fresh version's lines of code (comments left out) that appear nowhere in the solved example's or the steps' solutions found that in the six Python checkpoints and in ML Checkpoints 3 and 7, 40 to 94 percent of a fresh version is still the learner's to write. In ML Checkpoints 1, 4, 5, 6 and 8 and Cloud Checkpoint 1 only 6 to 20 percent is: their fresh versions share most of their code with what the steps show. In ML Checkpoints 4, 5, 6 and 8 the solved example alone holds most of it, and ML Checkpoint 8's example is its fresh versions with a different set of glyphs. ML Checkpoint 2 is in between, at 29 percent. For those checkpoints, fresh versions (or solved examples) that differ in more than their data are content work still to do; this rule is what makes that work count.

Decided under the owner's delegation of 2026-11-11 and recorded in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".

## Amendment (2026-11-11): further parts after the build and the debug

- **Status:** Proposed. Designed under the owner's delegation of 2026-11-11 (the best learning experience and memory retention first, and free), and built on until the owner rules; see [docs/owner-queue.md](../owner-queue.md), "Decided for you".

**Context.** A checkpoint's `prove` held one build, one debug and one explain, and `web/src/progress/progress.ts` passed a checkpoint on those three. The cloud track's spec gives several checkpoints more parts than that: Checkpoint 2 has three, and Checkpoints 3, 5 and 7 have two or three each. Checkpoint 1 met the same wall and, in its 2026-11-11 rewrite, folded its second part (a service killed and throttled) into its debug as two more faults, which works because both parts are one broken server. Checkpoint 2's parts can't be folded honestly: a sizing sheet in a plain lab, four slow VMs' recorded evidence, and an Active Directory domain stood up in a systemd lab with a second machine. Leaving the third part out would make the checkpoint narrower than its spec, which the 2026-11-10 audit recorded as a fault in Checkpoint 1.

**Decision.**

1. **The shape.** `prove` gains an optional `more`: a list of further parts, each `{id, versions}`. `id` names a build or debug exercise in the checkpoint's folder; `versions` lists fresh versions of it, in other stories, and may be left out when there are none. Only checkpoints have `more`.

   ```yaml
   prove:
     build: build-the-right-machine # part 1
     debug: debug-slow-vms # part 2
     more:
       - id: build-stand-up-the-domain # part 3
         versions: [build-stand-up-the-domain-clinic]
     explain: ...
   ```

2. **Passing.** A checkpoint is Passed once its build (or a fresh version, as the amendment above says), its debug, every part in `more` (the part itself or any of its versions) and its explain have passed, in any order. A part's Checks are `code_check` events in the `prove` context, like the build's, so there is no new event and no migration, and no saved event means anything new. Progress notes each part's first pass on its own (`partsPassed`, beside `passed`), so a checkpoint without parts, and every topic, has exactly the progress it had. Item 1's rules on what counts as a missed test hold for a part as for the build.
3. **The steps rule is the build's alone.** A part's pass counts whenever it came, before or after the build's steps were first opened. That rule exists because the steps show most of the main build's own program; they show nothing of a part's, and a part has no steps of its own. If a part is ever given steps, the same rule comes with them.
4. **The explain still opens once the main build passes** (the amendment of 2026-11-10), not once every part has. What that rule hides is a prompt that overlaps the build's code. Waiting for every part would hold a 20-minute explain behind the longest part for no gain. With parts, the closed check says "once your part 1 build passes", since there is more than one build. So the prompt is open while the further parts are still to do, and an author keeps a part's answer out of it, as the build's already is.
5. **What the validator checks.** For a ready checkpoint: every part is a build or a debug; every version has the same stage as its part (its runtime may differ, so a cloud version of a lab part can come later); a build part has at least one fresh version, because the reason for fresh versions, a second try that can't be passed from memory, holds for every build; a debug part needs none, as "Debug and explain" above says; and every test of every part and version names its skills in `test_skills`. Whatever the checkpoint's status: every part and version exists; no exercise is named twice in `prove`; no part or version is also the solved example, a step or a fresh version of the build; and a topic has no `more`.
6. **Support.** The four additions stay attached to the main build: one solved sibling, three or four steps, two fresh versions. A further part's practice is the module's topics, which its failed tests bring back on Today through `test_skills` (item 1). The follow-ups and the skill index read every checkpoint exercise's tests by exercise, whichever slot of `prove` names it, so nothing there changed. If learners are seen to get stuck on a part, steps for it are a later amendment.
7. **The page.** A checkpoint with further parts numbers every part: the build is "Part 1", the debug "Part 2", and each further part follows the debug, in order, as "Part 3", "Part 4" with its own editor or lab, before the explain. "Your proof so far" lists them the same way ("Part 3, build"), and the intro above them counts the checks. Below a part with a fresh version, a note says that its missed skills come back on Today, and that a fresh version is a second try that isn't from memory; a button shows one, chosen as for the build (one the learner hasn't Checked yet, else the one Checked longest ago). It never opens by itself. A checkpoint without parts looks exactly as it did.

**Alternatives considered.**

- **Folding every part into the build or the debug,** as Checkpoint 1 did. Right when the parts are one system; wrong when they are different machines, because the combined lab is long, its image holds everything, and a failure in one part blocks proving the others.
- **A list in place of `build` and `debug`** (`builds: [...]`, `debugs: [...]`). Cleaner in the long run, but it changes every existing checkpoint, the progress code and the event readers for no gain today.
- **Leaving the third part to a topic's own build, and amending the spec.** Honest, and the fallback if this weren't built. But a checkpoint is where a module's skills are retrieved together weeks after they were learned, which is what the part is for.
- **Showing a part's fresh version only after a failed Check of the part.** Closer to "a second try", but the page would have to read the history before it could draw the part, and a learner coming back days later to retry would find nothing to retry with until they failed again. A button that stays closed until asked keeps the learner in charge, as the steps do.
- **No fresh version for a build part.** A retry of the same build can be passed from memory, which item 4 exists to prevent.

**Consequences.**

- One field in `Prove` (`tools/content_model.py`), a few validator checks, `partsPassed` in `progress.ts`, a component for the parts (`web/src/checkpoints/MoreParts.tsx`), and their tests. No migration.
- Writers of Checkpoints 2, 3, 5 and 7 can match their spec. A checkpoint with three parts takes longer; its `estimated_minutes` says so.
- The map's note on a checkpoint in progress ("Proof checks passed: build, debug and explain") doesn't count further parts yet, so it can list all three while a part is still to do. It should list the parts before a checkpoint with them is `ready`.
