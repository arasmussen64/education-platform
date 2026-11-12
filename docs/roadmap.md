# Roadmap

## Where the project stands

_Last updated 2026-11-12._ This is the one place the project's status is written down. Other documents link here instead of repeating it.

**Current phase: Phases 1 and 2 are built (2026-11-09 and 2026-11-10). Phase 3's content is under way, and the build is on the Cloud Solutions Architect track until that track is finished.**

**Content.** 124 topics are `ready`, meaning written, machine-checked and shown to learners. Another 345 are outlines: a title, a summary and prerequisites, shown on the map with nothing to learn yet.

| Track                                                           | Ready               | Outlines            |
| --------------------------------------------------------------- | ------------------- | ------------------- |
| [Python Foundations](specs/python-foundations.md)               | 36, the whole track | 0                   |
| [Machine Learning Foundations](specs/ml-foundations.md)         | 64, Modules 1 to 8  | 8, Module 9         |
| [Cloud Solutions Architect](specs/cloud-solutions-architect.md) | 24, Modules 1 and 2 | 337, the rest of it |

**Since the audit** (2026-11-11, details in the [devlog](devlog.md)):

- **Cloud Module 1 is hardened.** The lab checker opens a lab's shell itself, keeps a lab in progress when `start` runs again, and lists and stops forgotten labs; Checkpoint 1 proves what its spec promises; all thirteen debug labs give symptoms, not faults, and their checks refuse the shortcuts their prompts forbid; Shell essentials teaches what its labs ask for; and a multiple-choice answer can no longer be picked by its length, which the validator now checks.
- **Debug prompts are rewritten in all three tracks** to give the symptom and the number of bugs, never what or where they are: all thirteen of cloud Module 1's, and 79 in the Python and ML tracks.
- **The AI proxy is fixed** (the budget cap counts every call, the tutor reads long programs, prompts can't be broken out of), and is live once the owner deploys it.
- **Cloud Module 2 is written** (#238 to #246): eight topics and Checkpoint 2, "the right machine", from [its plan](plans/cloud-module-2/README.md). All of it is proven locally, for free: 51 labs, among them QEMU virtual machines the checks boot themselves, real disks capped with `io.max`, and a Samba Active Directory domain with a Linux member. Built for it: estimate questions ([ADR-0024](decisions/0024-estimate-questions.md), proposed), a lab check's own time limit, checkpoints with more than two parts, and a debug lab that lists its checks only after a first try.
- **Cloud Module 3 is planned and its platform built** (#251 and the platform's pull request): sixteen topics and Checkpoint 3 from [its plan](plans/cloud-module-3/README.md), and one network-lab base every network lab starts from, whose machines are network namespaces running real FRRouting, strongSwan, BIND, Unbound, nginx and HAProxy. Every Module 3 lab is restarted in CI after its solution passes, so a fix that wouldn't survive a reboot fails ([ADR-0018](decisions/0018-lab-checker-local-mode.md)'s third amendment, proposed).

**Build order.** The owner set it on 2026-11-10: "I'm going to just go at my own pace and bounce around from track to track so your job is to just build. Let's focus the build on the cloud track until it's completely finished and then start working on the ML track again." So:

1. **The Cloud Solutions Architect track, to its end.** Modules 1 and 2 are written. Module 3, networking, is planned (2026-11-11, [plans/cloud-module-3](plans/cloud-module-3/README.md)) and being built, then the rest in the order of [its spec](specs/cloud-solutions-architect.md), along with the tools its later proofs need. The steps are listed under [Cloud Solutions Architect](#cloud-solutions-architect-the-track-being-built), below.
2. **Then the Machine Learning Foundations track again,** from Module 9, transformers, which is outlined, to Module 10, ML systems, which is still prose in [its spec](specs/ml-foundations.md).

What comes after those two isn't decided. The unbuilt items of Phases 3 and 4 are listed below.

Content is no longer held to one module ahead of the owner's own learning, which was the rule until 2026-11-10. The owner learns at their own pace, on any track, and the build doesn't wait for it.

**Waiting for the owner.** Things only the owner can do or decide are kept in [owner-queue.md](owner-queue.md), a short list. Open on 2026-11-11: applying two migrations to the live database, the placement test's ([ADR-0021](decisions/0021-placement-test.md)) and the one that raises an event's size limit; making the AI proxy's fixes live (two small paid test runs, the deploy, and checking the $10 limit in the Anthropic Console); accepting [ADR-0024](decisions/0024-estimate-questions.md) and the proposed amendments to [ADR-0012](decisions/0012-checkpoint-support.md) and [ADR-0018](decisions/0018-lab-checker-local-mode.md), which the build already rests on; confirming ADR-0020, 0021 and 0022, which were marked Accepted on the strength of the owner's request to build Phase 2; protecting `main` on GitHub; and, optionally, asking GitHub Support to drop an erased commit and running Module 2's optional labs in the owner's clouds (about $1.45 in all). Since 2026-11-11 the queue also lists, under "Decided for you", the product and content questions settled while the owner is away, by the owner's three tests: the best learning experience, the best memory retention, and free or inside the $150 Azure credit.

**Decided by the owner on 2026-11-10.**

- [ADR-0023](decisions/0023-packages-in-both-runtimes.md), NumPy in both Python runtimes, is accepted. Across the ML track's Modules 3 to 8, 39 ready topics import NumPy and rest on it.
- What a cloud lab may cost ([ADR-0014](decisions/0014-cloud-labs.md#amendment-2026-11-10-what-a-lab-may-cost-and-who-pays), amended): the Claude API stays the only thing that costs real money. A lab that needs a real cloud is an Azure lab in the owner's own subscription, inside its $150 monthly credit, or an AWS or Google Cloud lab inside that cloud's free tier. Everything else is proven locally.

**Parked.** Nightly backups ([ADR-0020](decisions/0020-automated-backups.md)) are built but not switched on, so no automatic backup is being taken. The owner parked the setup on 2026-11-10 while the platform is still being built, and set aside downloading their own data for the same reason: "I don't care about downloading my data right now while we're still just building this thing." Neither is raised again until the owner asks. The steps are in [setup.md](setup.md), under "Back up your learning data".

**Audit.** The whole repository was audited on 2026-11-10; what it found and what was fixed is in the [devlog](devlog.md).

## Phase 0: Setup and planning (done)

- [x] Research: Brilliant, roadmap.sh, Math Academy ([competitors](research/competitors.md))
- [x] Product concept and key decisions ([vision](vision.md), ADR-0002 to ADR-0006)
- [x] Repository, documentation and development process (backed up to a GitHub repo, private then and public since 2026-11-09)
- [x] Accept a tech stack ([ADR-0007](decisions/0007-tech-stack.md))
- [x] v1 spec ([specs/v1.md](specs/v1.md)): features and milestones, the [data model](specs/data-model.md), and the [first 30 Python topics](specs/python-foundations.md)

## Phase 1: v1 for an audience of one (done 2026-11-09)

Spec: [specs/v1.md](specs/v1.md). Built mostly with AI help, in thin end-to-end slices, so the owner can start learning on it after the first one. Until then, the owner learns from the curated resources directly.

- **A. Walking skeleton:** deployed app, sign-in, content pipeline, lessons, self-checking Python exercises, progress saved. Module 1 content.
- **B. Prove it:** build, debug and explain checks; topic states and gating with "prove it now"; the topic map; module checkpoints.
- **C. Keep it:** FSRS reviews, the Today page, recall items, interleaved practice.
- **D. Tutor and polish:** the hint-only tutor with a budget cap, problem reports, data export. Content for modules 2–6.

Content: the [Python Foundations track](specs/python-foundations.md), 30 topics and 6 checkpoints.

### Milestone A progress

- [x] Web app scaffold and CI
- [x] Python runner in the browser (shared harness, Pyodide worker, editor with Run and Check)
- [x] Content format and validator, with the whole Python Foundations map as outlines
- [x] The app loads content, with topic pages for lessons and exercises
- [x] Local Supabase in Docker, with the profiles and event-log tables
- [x] Sign-in: GitHub on the live site, email links locally
- [x] Saving answers to the event log, with an offline outbox
- [x] Deploy to Cloudflare (every merge to `main` deploys automatically)
- [x] Module 1 content: five topics, and Checkpoint 1 (a receipt calculator) with its way through for a stuck learner
- [x] Mistakes come back as fresh questions until relearned ([ADR-0011](decisions/0011-mistakes-come-back.md)): "Mistakes to revisit" on the Today page
- [x] Getting unstuck on a checkpoint ([ADR-0012](decisions/0012-checkpoint-support.md)): missed checkpoint tests bring their skills back; a solved sibling, the build in steps, and fresh versions

### Milestone B progress

- [x] Export my data (F16, planned for D), built first so the learning history has a backup ([ADR-0010](decisions/0010-environments.md))
- [x] Progress tracking, part 1: the rules for topic states, and which proof checks have passed, on the map and topic pages
- [x] Explain it back, graded by AI (F7), through the AI proxy with its budget cap (F14), as decided in [ADR-0013](decisions/0013-explain-grading.md). Graded by Claude Haiku 5.5, which got the 30-sample test set right twice. Live since 2026-11-08.
- [x] Topic states and gating, with "Prove it now" (F8, F9), and "Next up" on the Today page (F12). Built 2026-11-08, once grading was live: until explanations could pass, no topic could be Learned, and gating would have locked every topic after the first.
- [x] Module 2 content, ready before the owner finishes Module 1 (2026-11-08): five topics and Checkpoint 2, ticket pricing

Milestone B is complete.

### Milestone C progress

- [x] Reviews (F11, [ADR-0009](decisions/0009-reviews.md)): one card per Learned topic, FSRS scheduling, two-item sessions rated from first attempts, and the states Mastered, Fading and Relearning (2026-11-08)
- [x] The Today page in full (F12): due reviews, mistakes to revisit, next up (2026-11-08)
- [x] Interleaved practice: one recall item from an earlier topic in each practice ladder (F5) (2026-11-08)
- [x] Module 3 content (loops), ready before the owner finishes Module 2 (2026-11-08)

Milestone C is complete.

### Milestone D progress

- [x] The hint-only AI tutor (F13, [ADR-0015](decisions/0015-hint-only-tutor.md)) through the AI proxy and its budget cap (F14): a hint ladder under practice exercises, off during Prove it and reviews. Built 2026-11-08, live since 2026-11-09, its test set run the same day: 25 of 25 replies fine on Haiku 5.5.
- [x] Report a problem (F15): a note under any lesson, item or check, saved with the item it's about. Built 2026-11-08, in the live database since 2026-11-09.
- [x] Export my data (F16): built early, in Milestone B
- [x] Module 4 content (functions), ready before the owner finishes Module 3 (2026-11-09)
- [x] Module 5 content (collections) (2026-11-09)
- [x] Module 6 content, and the end of the Python Foundations track (2026-11-09)
- [x] Smaller app bundle: load the cloud track's outlines only when the map asks for them (2026-11-09)

Milestone D is complete (2026-11-09): the AI proxy with the tutor is live, its test set run, and the problem-reports table is in the live database. With it, Phase 1 is done: the owner can learn on the platform end to end, from Programs and print to the CSV report capstone, with proofs, reviews, a tutor and a way to report problems.

## Phase 2: Adaptivity and better practice (built 2026-11-10)

Every item below is built (2026-11-10). Two of them aren't fully in use yet: the placement test's migration waits for the owner, and the backups aren't switched on. Both are under [Where the project stands](#where-the-project-stands), above.

- [x] A placement test that walks the topic map, including a math diagnostic (2026-11-09, [ADR-0021](decisions/0021-placement-test.md)): a walk by halving through a track's unlearned topics, probing each with its own review questions; the result is a place to start and a list of topics to prove first, never a tick. The math ladder has seven levels, arithmetic to the first ideas of calculus, each with a free refresher to point at until the platform's own exists.
- More exercise types: [x] Parsons problems ([ADR-0016](decisions/0016-parsons-problems.md), 2026-11-09, one in 29 of the 30 topics); [x] a step-through code visualizer (2026-11-09, [ADR-0022](decisions/0022-step-through.md)): the harness records each line's effect under Python's own trace hook, in the browser and in CI alike; a Step through button beside Run, and under predict-the-output questions once answered, plays it back with the variables and the output so far.
- The living map: topics fade as their predicted memory strength drops. [x] First version (2026-11-09): each Learned topic shows "Memory: N%" and a bar from the scheduler's predicted retrievability; dimming the rows themselves was left out for legibility.
- [x] A practice-hours tracker (the owner's idea, 2026-11-06): total time spent in active practice, from the attempt durations in the event log, with milestones from 1 hour on the way to 10,000. It counts deliberate practice (attempts, proof checks, reviews), not time with the site open, because that's what the research behind "10,000 hours" measured. Built early, on the Today page (2026-11-09). [x] Counted per track, each on its own ladder ([ADR-0019](decisions/0019-today-across-tracks.md), 2026-11-09).
- [x] Today shows every track (2026-11-09, [ADR-0019](decisions/0019-today-across-tracks.md)): one Next up per track, with how far along each is, so a learner on two tracks sees where they stand on both.
- [ ] Automated data backups: built (2026-11-09, [ADR-0020](decisions/0020-automated-backups.md)), not switched on. A nightly encrypted dump to a private backups repository, with the restore rehearsed on every pull request. The nightly run does nothing until the owner adds three secrets, and the owner parked that on 2026-11-10.
- Content: intermediate Python; a math refresher for the ML track. Both live in the new **Machine Learning Foundations** track ([spec](specs/ml-foundations.md), 2026-11-09): Module 1 is the math refresher (the placement test's seven levels as topics, each proven in Python), Module 2 intermediate Python; both were outlined that day. [x] Module 1 is complete (2026-11-10): seven topics and a checkpoint that fits a line by gradient descent. [x] Module 2 is complete (2026-11-10): seven topics and a checkpoint that builds a small data library, so every outlined topic of the track is ready. [x] Module 3, linear algebra, is complete (2026-11-10): seven NumPy topics and a checkpoint that fits a plane and compresses the same points, written on the NumPy decision in [ADR-0023](decisions/0023-packages-in-both-runtimes.md), which was proposed then and accepted by the owner on 2026-11-10. Modules 4 to 9 are under Phase 3, below.

## Phase 3: CS and ML tracks (content begun 2026-11-10)

- Content: math for ML ([x] linear algebra, the ML track's Module 3, 2026-11-10; [x] calculus, the ML track's Module 4, 2026-11-10: seven topics and a checkpoint that trains a network from scratch; [x] probability, the ML track's Module 5, 2026-11-10: seven topics and a checkpoint that judges two models), core CS ([x] data structures and algorithms, the ML track's Module 6, 2026-11-10: seven topics and a checkpoint that builds a pipeline's algorithms; [x] how computers and GPUs work, the ML track's Module 7, 2026-11-10: seven topics and a checkpoint that makes a pipeline fast), then neural networks from scratch ([x] the ML track's Module 8, 2026-11-10: seven topics and a checkpoint that trains a network to read digits), building up to transformers ([ ] the ML track's Module 9, outlined 2026-11-10, to be written once the cloud track is finished)
- The owner writes a growing share of the platform's code
- Senior-engineer code review and the practice generator

## Phase 4: Capstone and opening up (after Phase 3)

- **ML capstone:** fit the review scheduler and a knowledge-tracing model to the owner's own learning data
- Content: ML systems (training, evaluation, serving)
- AI-assisted coding track ("earn the AI")
- Decide whether to open it, free, to other beginners

## Cloud Solutions Architect: the track being built

- **Cloud Solutions Architect, multi-cloud.** Specified on 2026-11-08: [the spec](specs/cloud-solutions-architect.md), with 30 modules in 4 stages and about 320 topics, up to principal level, on AWS, Azure and Google Cloud. It was cross-referenced the same day with the owner's own knowledge map ([docs/research](research/senior-cloud-architect-knowledge-map.md)), which added a 24-month example path and a self-assessment. The track assumes nothing about the learner and starts from zero. How its cloud work is proven is [ADR-0014](decisions/0014-cloud-labs.md), accepted 2026-11-09 and amended 2026-11-10 on what a lab may cost.

  Building it, in the order the spec's _Building it_ section gives:
  - [x] More than one track in the app: the map and topic pages know every track (2026-11-08)
  - [x] The track on the map as `planned` outlines, generated from the spec (2026-11-08)
  - [x] Decide how the shell is taught and proven ([ADR-0017](decisions/0017-shell-in-the-browser.md), accepted 2026-11-09): a `predict_shell` item proven by real `bash` in the validator, local container labs through the lab checker, a browser VM later
  - [ ] Stage 1 content: Module 1's lessons and recall first ([x] all 14 topics drafted on 2026-11-09, with 228 recall items), then their labs ([x] Shell essentials ready on five labs, 2026-11-09; [x] Services and logs, the first systemd labs, 2026-11-09; [x] Processes and signals, 2026-11-09; [x] Users, permissions and SSH, 2026-11-09; [x] Package management and patching, 2026-11-09; [x] Disks and filesystems, 2026-11-09; [x] Memory and the OOM killer, 2026-11-09; [x] CPU scheduling and cgroups, 2026-11-09; [x] How containers work, 2026-11-09; [x] Networking from the host, 2026-11-09; [x] Boot, cloud-init and instance metadata, 2026-11-09; [x] Shell scripting, 2026-11-09; [x] Performance triage, 2026-11-09; [x] Hardening, 2026-11-09 (all 14 topics ready); [x] Checkpoint 1: the broken server, 2026-11-09, so Module 1 is complete; [x] hardened after the audit, 2026-11-11), then the drills that run in the browser
  - [x] Module 2, virtualization, hardware and Windows: [x] planned (2026-11-11, [plans/cloud-module-2](plans/cloud-module-2/README.md)), [x] its platform built (estimate questions, [ADR-0024](decisions/0024-estimate-questions.md); a lab check's own time limit; checkpoints with further parts, [ADR-0012](decisions/0012-checkpoint-support.md), amended), [x] its eight topics and Checkpoint 2 (2026-11-11), so Module 2 is complete
  - [ ] Module 3, networking: [x] planned (2026-11-11, [plans/cloud-module-3](plans/cloud-module-3/README.md)): sixteen topics, a shared network-lab base every network lab starts from, and Checkpoint 3 in three parts; [x] its platform (2026-11-12: the base in `content/lab-bases/net/`, a restart trial in the lab contract, dotted quads in estimate questions, Labs CI on eight machines, and six probe labs tried on GitHub's runners); [ ] its topics and Checkpoint 3
  - [ ] The lab checker ([ADR-0014](decisions/0014-cloud-labs.md), accepted 2026-11-09). [x] Local mode (2026-11-09, [ADR-0018](decisions/0018-lab-checker-local-mode.md)): `tools/labcheck.py` builds a lab's container from `content/`, runs its checks, prints a result to paste, and proves every lab's contract in CI; the first lab is Shell essentials' build. [x] The lab view on the topic page (2026-11-09). [x] 2026-11-11: `shell`, a `start` that keeps the work, `status` and `stop --all`, a check's own `timeout:`, and every lab proved in CI once a week ([ADR-0018](decisions/0018-lab-checker-local-mode.md), amended). [ ] Cloud mode, with recordings.
  - [ ] Design reviews, game days and "Defend it"

  The content's order from here: the rest of Stage 1 (Modules 2 to 7), then Stage 2 (Modules 8 to 15 and Capstone 1), Stage 3 (Modules 16 to 24 and Capstone 2) and Stage 4 (Modules 25 to 30 and Capstone 3). Most of Stage 1's practice runs in containers on the learner's machine, which is free. From Stage 2 on, labs run in real cloud accounts, and they need the lab checker's cloud mode. What such a lab may cost was settled by the owner on 2026-11-10 ([ADR-0014's amendment](decisions/0014-cloud-labs.md#amendment-2026-11-10-what-a-lab-may-cost-and-who-pays)): an Azure lab runs in the owner's own subscription and states its estimated cost, so that a month's labs stay well inside the $150 credit; an AWS or Google Cloud lab names the free-tier allowance it relies on; every real-cloud lab ends with a teardown step; and whatever fits neither is proven locally, in containers, emulators, drills or design exercises. Module 2 meets this early: its Windows Server and Active Directory labs need Windows machines in a real cloud account. They had been waiting on the question of paying for those machines ([devlog](devlog.md), 2026-11-10), and can now be Azure labs. (2026-11-11: the [Module 2 plan](plans/cloud-module-2/README.md) proves them locally instead, with a Samba domain controller in a lab container; a real Windows Server lab in Azure, about $0.60 a sitting, is an optional extra, outside the proofs until the owner has run it once.)

## The owner's 12-month learning milestone

- Solid CS foundations and the math behind ML
- Build and train a small GPT from scratch, understanding every line
- Ship an ML system end to end (the capstone counts)

Principal-engineer level stays the long-term ceiling of the map. It takes years of real-world experience, so it isn't a 12-month goal.

## Open questions

- License: open source or proprietary? This matters if it becomes a company. The repository has been public since 2026-11-09 and its README says "Not decided yet. All rights reserved for now."
- Final product name ([ADR-0006](decisions/0006-working-name.md))
- Hidden tests run in the browser, so a determined learner could peek. Fine for personal use; revisit before a public launch.
- When and how to open it to other learners
- ~~When to build the Cloud Solutions Architect track, relative to the rest of v1 and the ML path~~ Answered by the owner on 2026-11-10: now, to its end, and then the ML track again.
