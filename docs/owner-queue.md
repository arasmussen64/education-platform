# Owner queue

The short list of things only the owner can do or decide. It replaces the "Decisions for you to review" lists that used to sit at the bottom of devlog entries (405 items by 2026-11-10, of which about 18 needed the owner).

**How it works**

- Something goes under _Open_ only if it involves money, the live site or database, a setting on one of your accounts, making something public, or is hard to undo. Each item has the question, the options, a recommendation, what it holds up, and the exact command if it's a step. The open list stays at about seven items.
- Product and content questions that would once have waited for you are decided for you while you're away (your message of 2026-11-11), by three tests in this order: the best learning experience, the best memory retention, and free or inside the $150 Azure credit. Each is listed under _Decided for you_, so you can overturn it in a line.
- Every other judgement call is recorded as "Author notes" in the devlog entry, for the record, not for a ruling.
- Answer in a line, in any session. The answer is recorded under _Answered_ with the date, and the item leaves the list.
- Nothing here blocks building unless the item says so under "Holds up".

## Open

### 1. Apply two migrations to the live database

A migration is a script that changes the database's structure. Two are waiting. `20261109220000_placement_events.sql` lets the live database accept the placement test's events. `20261111164541_raise_event_data_limit.sql` (#232) raises the size limit on an event's details from 16 KB to 128 KB, so the Run or Check of a long program (Module 8's run to 12,323 characters) is kept whole.

- **Step:** `npx supabase db push --remote --dry-run` lists what the live database is missing and changes nothing. If it lists only those two, run it again with `--yes` in place of `--dry-run`.
- **Or:** say "push it" and Claude runs those two commands.
- **Holds up:** placement results taken on the live site aren't saved until this is done, and neither is the Run or Check of a program too long for the old limit. Since 2026-11-10 the app keeps refused answers on the device, says so in the header, and sends them again by itself once the database accepts them, so nothing is lost by waiting. Do it before studying Module 8, and before item 2.

### 2. Make the AI proxy's fixes live

The AI proxy is the small server program that talks to Claude for the tutor and the explain-it-back grader. #232 fixed three things in it: the $10 monthly budget now counts every call, and stops calling Claude when it can't count one; the tutor reads programs up to 20,000 characters (today it fails on Module 8's longest and blames the connection); and a learner's text can no longer break out of its place in a prompt. Merging deployed the web app, not the proxy. After item 1, in this order:

- **Two paid test runs, about 2.5 cents in all,** because what Claude receives has changed. They use the key in `supabase/functions/.env`. `npm run fn:eval` costs about $0.02 on Claude Haiku 5.5, and every sample should get its expected verdict. `npm run fn:eval:tutor` costs about half a cent: no reply should be replaced or hold a forbidden line, and you read the replies.
- **Deploy it:** `npx supabase functions deploy ai --no-verify-jwt --yes`. Then check it without calling Claude: `curl -s -X POST https://<ref>.supabase.co/functions/v1/ai -H "apikey: <publishable key>"` should answer 401 and `{"error":"Sign in first."}`.
- **In the Anthropic Console,** check that the $10 monthly spending limit is set. It's the backstop [ADR-0013](decisions/0013-explain-grading.md) names, and nothing records it as set.
- **Or:** say "go ahead with the proxy" and Claude runs the two test sets, shows you the replies, and deploys if they pass. The Console check is yours.
- **Recommendation:** yes, in one sitting after item 1.
- **Holds up:** the tutor on Module 8's long programs, and the stronger budget cap and prompt escaping on the live site. Until then the live tutor and grader work as they do today.

### 3. Accept the decisions built on while you were away

Four design decisions were made under your message of 2026-11-11 and built on. Each is marked _Proposed_ until you rule:

- [ADR-0024](decisions/0024-estimate-questions.md), estimate questions: a typed number, checked within a tolerance and proved by the validator.
- [ADR-0012's amendment on further parts](decisions/0012-checkpoint-support.md#amendment-2026-11-11-further-parts-after-the-build-and-the-debug): a checkpoint can have a Part 3 and beyond.
- [ADR-0018's first amendment of 2026-11-11](decisions/0018-lab-checker-local-mode.md#amendment-2026-11-11-a-shell-command-a-start-that-keeps-the-work-and-what-privileged-means): the lab checker's `shell` command, a `start` that keeps the work, `status` and `stop --all`, and a short-lived helper container that lets go of disks dead labs left attached. The helper sees the whole of Docker's machine (`--privileged --pid=host`), and `stop --all` leaves a test run's containers alone unless given `--tests`.
- [ADR-0018's second amendment](decisions/0018-lab-checker-local-mode.md#amendment-2026-11-11-second-a-checks-own-time-limit): a lab check's own time limit, up to 300 seconds, and 600 for a lab's checks in all.
- **Recommendation:** accept all four. A "yes" is enough; Claude records it in each status line.
- **Holds up:** nothing.

### 4. Confirm three design decisions marked accepted without your explicit yes

ADR-0020, 0021 and 0022 (backups, the placement test, step-through) were marked _Accepted_ because you asked for Phase 2 to be built, not because you read them. In a sentence each: backups are a nightly encrypted copy of the database committed to a private repository of yours; the placement test finds a starting point by probing topics with their own review questions and never ticks a topic off; step-through records each line's effect under Python's own trace hook and plays it back.

- **Recommendation:** accept all three. A "yes" is enough; Claude records it in each status line.
- **Holds up:** nothing.

### 5. Protect `main` on GitHub

Today nothing but habit stops a direct push, a force-push or a merge with failing checks from reaching the live site.

- **Step:** say "protect main" and Claude adds a ruleset: changes arrive by pull request, the CI jobs must pass, no force-pushes, no deleting the branch. It also turns on GitHub's free secret scanning. Both can be switched off again in the repository's settings.
- **Recommendation:** yes.
- **Holds up:** nothing.

### 6. Optional: ask GitHub to drop the erased commit

The two stray files were erased from `main`'s history on 2026-11-10, but GitHub keeps the old commit reachable by its ID for anyone who already has that ID, through pull request #198's hidden reference. Only GitHub Support can remove that, and only the repository's owner can ask.

- **Recommendation:** not worth the effort. Neither file held a key or a password, and no branch contains them any more.
- **Holds up:** nothing.

### 7. Optional: Module 2's runs in your clouds (about $1.45 in all)

Module 2 is complete without them: every topic is proven locally, for free. These make parts of it real.

- **(a) A budget alert on your Azure subscription.** Free. It e-mails you when spending passes a set amount, so a forgotten lab shows up as an e-mail rather than a bill. The steps are in the Active Directory lab's runbook, in [plans/cloud-module-2](plans/cloud-module-2/MODULE-2-BRIEF.md) section 7.
- **(b) One sitting of the Azure Active Directory lab.** About $0.60 and three hours: real Windows Server, guardrails first, everything deleted at the end. Your run records the answers the checker's tests replay, and lets the lab count as a proof.
- **(c) Capture runs for more genuine examples.** A free-tier Google `e2-micro`, and about $0.85 of Azure.
- **Recommendation:** (a) and (b) when you have an evening; (c) only if you'd like the examples to be real rather than constructed.
- **Holds up:** only the Azure lab's place among the proofs.

## Decided for you

Made under your message of 2026-11-11. Say the word to overturn any of them.

- **2026-11-11, debug exercises that name their bugs.** About 70 debug exercises (Python Modules 4 to 6, ML Module 3 onward, half of cloud Module 1) told the learner each bug and often the fix, which makes "debug unfamiliar code" ([ADR-0002](decisions/0002-mastery-and-gating.md)) closer to following instructions. **Decided:** rewrite them all so a prompt gives what the program should do, the symptom and how many bugs there are, with the specifics moved into hints. Order: cloud Module 1 first, then Python, then ML. **Why:** finding the bug is the skill being proven, and effort spent finding it is what makes it stick. **The cost:** the hard modules get harder, with the tutor off during proofs; the specifics are kept as hints in the content, but the app shows no hints on a debug exercise, since every debug is a proof. Each rewritten debug was checked to be findable from its symptom, a Run and its Check messages alone. **Done** in all three tracks: cloud Module 1's ten (#223 to #226), then 79 Python and ML prompts (#218, #219, #228 to #230). Three cloud Module 1 debug labs still say where or what their faults are (Users, permissions and SSH; Package management and patching; How containers work) and are the next to rewrite.
- **2026-11-11, Module 2 has eight topics, not six.** "Cores, memory and noisy neighbours" is split into it and "Memory tiers and disks"; "Windows Server and Active Directory" into "Active Directory: domains, names and tickets" and "Joining machines, Group Policy and Entra ID". Why: shorter topics reach their proofs and first reviews sooner, and every proof tests what its topic just practised.
- **2026-11-11, Module 2 is proven locally, for free.** Its Active Directory topics use a Samba domain controller in the lab's container. A real Windows Server lab in Azure (about $0.60 a three-hour sitting) is an optional extra, outside the proofs until you've run it once.
- **2026-11-11, a new question type: estimate.** A typed number checked within a tolerance, for quick calculations (sizing, cost, memory). Why: producing a number is remembered better than picking one, and it needs no Python before Module 6. Built in #220 ([ADR-0024](decisions/0024-estimate-questions.md), Proposed: Open, item 3).
- **2026-11-11, a checkpoint can have more than two parts,** so Checkpoint 2 can hold all three the spec asks for. A further part counts whenever it passed: the rule that the main build stops counting once its steps are opened is the main build's alone. Built in #221 (an amendment to [ADR-0012](decisions/0012-checkpoint-support.md), Proposed: Open, item 3).
- **2026-11-11, a lab check may take longer than 30 seconds.** A check may ask for up to 300 seconds with `timeout:`, and a lab's checks for 600 in all, as a rule rather than a warning, because a learner whose lab is still broken waits for every check. Why: topic 15's checks can then boot the learner's virtual machine instead of trusting a log the learner could write by hand. A check that runs out of time is now stopped inside the lab too. Built in #222 (the second amendment of 2026-11-11 to [ADR-0018](decisions/0018-lab-checker-local-mode.md), Proposed: Open, item 3).
- **2026-11-11, right-sizing is taught in Module 2** (a new skill in "Cores, memory and noisy neighbours"), because Checkpoint 2 needs it and nothing taught it.
- **2026-11-11, checkpoint time targets are stated, not timed.** You hold yourself to them.
- **2026-11-11, "Arm saves 20 to 40%" becomes "what Arm saves, from price lists".** AWS's own page now says "up to 20% less".
- **2026-11-11, a debug lab shows its checks only after your first try.** A lab page listed "What the checker looks for" before you started. For a debug each check describes the state a fix must reach ("svc-report is enabled"), which points at the fault you're meant to find. **Decided:** a debug lab says how many checks there are, and lists them once you've recorded a result; every other lab is unchanged. Built in #235.

Module 2 is written (2026-11-11, #238 to #246). Its whole plan is in [plans/cloud-module-2](plans/cloud-module-2/README.md).

The learning engine's rules, fixed after the audit (#210 to #215):

- **2026-11-11, when the Mastered star comes.** A topic could be Mastered right after a failed review, because the week was counted from Learned, and open follow-ups didn't hold the star back though ADR-0011 said they should. **Decided:** a review rated Again starts the week over, and a topic isn't Mastered while one of its skills is being relearned. **Why:** "survives a delayed review" should mean a week survived. **The cost:** some stars turn back to Learned until a good review a week on, or until the follow-up closes ([ADR-0002](decisions/0002-mastery-and-gating.md), amended).
- **2026-11-11, what relearns a mistake.** A follow-up could be closed by answering the missed question again on three days in a row, or by a lab walkthrough. **Decided:** a right day counts only on or after its due day, keeping the 1, 3 and 7 day gaps, and on a different question (the missed one only if the skill has no other); worked examples count for nothing either way. **Why:** fresh questions at growing gaps are what make relearning stick. **The cost:** some follow-ups you'd closed come back on Today ([ADR-0011](decisions/0011-mistakes-come-back.md), amended).
- **2026-11-11, a checkpoint's steps and its build.** A checkpoint's steps show most of the build's own program. **Decided:** once you open them, passing the main build no longer counts; a fresh version (the same skills in another story) proves it. A build passed before you opened them still counts, and so does everything passed before 2026-11-11. **Why:** the build shows you can write it from a blank editor. **The cost:** opening the steps out of curiosity means proving the build on a fresh version ([ADR-0012](decisions/0012-checkpoint-support.md), amended).
- **2026-11-11, placement ties pass,** one right and one wrong out of two, as [ADR-0021](decisions/0021-placement-test.md) always said. It affects the 11 topics with only two questions. **The cost:** on those, one lucky guess can place you past a topic until its own proof catches it.
- **2026-11-11, the review scheduler is FSRS-4.5 exactly.** It pulled difficulty toward the wrong value, so reviews came a little late. **Decided:** FSRS-4.5's own formulas and limits, checked against the reference Python package. **Why:** reviews at the 90% recall target are what keep a topic remembered. **The cost:** some intervals get a few days shorter ([ADR-0009](decisions/0009-reviews.md), amended).
- **2026-11-11, a review left half-way still counts.** Your first answers since a topic fell due carry into the next visit and rate it. **Why:** a wrong answer at review time is the sign a topic is fading. **The cost:** you can't restart a review you started badly.
- **2026-11-11, "20 reviews a day" is a calendar day,** not a page load. **The cost:** after a long break, catching up takes more days.
- **2026-11-11, a Check that couldn't run isn't an answer.** When Python didn't start, a package didn't download or an exercise's tests couldn't load, it's saved with no verdict and counts nowhere; code past its time limit still counts as wrong ([ADR-0008](decisions/0008-event-log.md), amended).
- **2026-11-11, your own day on every event.** Every event now records your calendar day and time zone, and follow-ups count in it, wherever your history is read ([ADR-0008](decisions/0008-event-log.md), amended).
- **2026-11-11, drafts of what you type.** Code and explanations are kept on this device until the item passes, with a Start over button. Reviews, the placement test and worked examples keep none, because they measure what you remember. Drafts are per device, not per account.
- **2026-11-11, a question's `rev` keeps your past answers.** Bumping a question's revision doesn't discard what you answered before (the devlog once said otherwise).

Cloud Module 1, hardened after the audit (#209, #223 to #227, #233):

- **2026-11-11, `labcheck start` keeps the work.** Running `start` on a lab that already exists leaves it as it is: a stopped one is started again with its files, a paused one unpaused. Only `start --fresh` removes one. **Why:** after a reboot, following the tool's own advice used to delete the lab and your work in it, and a "remove it? (y/n)" prompt would be the same trap with a pause. **The cost:** after a restart, 12 of the 79 labs need a step done again (a program started by hand, a mount), as a real server would; and an author who changes a lab must use `--fresh` to see the change ([ADR-0018](decisions/0018-lab-checker-local-mode.md), amended, Proposed: Open, item 3).
- **2026-11-11, a pasted lab result must name exactly the lab's checks.** One with other checks, or with some missing, records nothing and says to run `check` again. **Why:** a result made before a lab's checks changed could read as a pass. **The cost:** none for an honest result. It isn't a trust fix: results are still unsigned.
- **2026-11-11, a multiple-choice answer can't stand out by its length.** In 102 of the cloud track's 108 questions the right answer was the longest choice, so "pick the long one" passed without knowing the topic. **Decided:** 106 of the 108 are rewritten, and the validator now fails an item whose right answer is more than 1.5 times as long as its longest wrong choice, and a topic of four or more items where the right answer is the longest in more than half. **The cost:** 73 older items (72 in the Python and ML tracks, one in the placement test) and 16 topics break the rules and stay as they are for now, listed in `tools/mcq_length_baseline.yaml`. That list can only shrink, and no cloud item may be on it.
- **2026-11-11, the CPU debug lab keeps its cap.** The lesson teaches that removing a CPU limit is one way to fix a throttled service, and the CPU build asks for no cap on an idle machine. The debug's machine is described as shared, with a rule that the cap stays, so the learner has to choose a sensible one (more than one CPU, at most two). **Why:** a lab about limits shouldn't be passed by taking the limit away. Say if you'd rather the lab accepted removing it.

## Parked by you

- **Backups and "Download my data"** (2026-11-10: "I don't care about downloading my data right now while we're still just building this thing"). The nightly backup is built but not switched on; the four one-time steps are in [setup.md](setup.md#back-up-your-learning-data). Say the word when your learning history starts to matter.

## Answered

- **2026-11-10, pace and direction.** "I'm going to just go at my own pace and bounce around from track to track so your job is to just build. Let's focus the build on the cloud track until it's completely finished and then start working on the ML track again." Content is no longer held to one module ahead of your learning; the build order is the cloud track to its end, then ML from Module 9.
- **2026-11-10, the audit's fixes.** "You can execute all of item 2": the stray files removed, the generators archived in the repository, refused events sent again, checkpoint explain checks opened only after the build, Module 8's time limits and a CI check on the browser's limit, the confirmed content corrections, and this queue.
- **2026-11-10, the stray files.** "Erase the stray files": `k.html` and `y.html` erased from `main`'s history, not just deleted going forward. You ran the erase yourself.
- **2026-11-10, labs that need a real cloud.** "My goal for this is to make the only paid portion of the site the AI so either local labs or have me build something in Azure is best", then: "Let's utilize the AWS and Google free tiers. Also, it's actually $150/month for azure credits." So:
  - **Azure:** a lab that needs a real cloud can be one you build in your own subscription, with its estimated cost stated and a teardown step, a month's labs kept well inside the $150 credit.
  - **AWS and Google Cloud:** real labs where they fit the provider's free tier, each naming the allowance it relies on, with a budget alert set before the first one and teardown at the end.
  - **Everything else:** proven locally (containers, emulators, drills, design work).

  Recorded as an amendment to [ADR-0014](decisions/0014-cloud-labs.md). This unblocks cloud Module 2's Windows Server and Active Directory labs.

- **2026-11-10, ADR-0023.** "I accept ADR-0023": NumPy in both runtimes is _Accepted_.
- **2026-11-11, deciding while you're away.** "I'll be away from my laptop for a long time. Your job is to build as much as you can. If you need a question answered for me just use your best judgement and error on the side of whatever provides the best learning experience and optimal memory retention and is free or falls within the $150 azure budget." Product and content questions are now decided under _Decided for you_. Steps on the live site, your accounts' settings and anything that spends money still wait for you under _Open_; Claude creates nothing in your Azure subscription.
