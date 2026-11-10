# Roadmap

**Current phase: Phase 1 is complete (2026-11-09). Phase 2, adaptivity and better practice, is next,** alongside the cloud track's first steps, now that [ADR-0014](decisions/0014-cloud-labs.md) and [ADR-0017](decisions/0017-shell-in-the-browser.md) are accepted (2026-11-09).

The owner works full time, split between learning (mornings, on the platform once it exists) and building (afternoons). The roadmap serves both: the platform's content stays one module ahead of the owner's own learning.

## Phase 0: Setup and planning (done)

- [x] Research: Brilliant, roadmap.sh, Math Academy ([competitors](research/competitors.md))
- [x] Product concept and key decisions ([vision](vision.md), ADR-0002 to ADR-0006)
- [x] Repository, documentation and development process (backed up to a private GitHub repo)
- [x] Accept a tech stack ([ADR-0007](decisions/0007-tech-stack.md))
- [x] v1 spec ([specs/v1.md](specs/v1.md)): features and milestones, the [data model](specs/data-model.md), and the [first 30 Python topics](specs/python-foundations.md)

## Phase 1: v1 for an audience of one (weeks 1–4, done 2026-11-09)

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

## Phase 2: Adaptivity and better practice (months 2–4, next)

Mornings learning on the platform, afternoons building it.

- A placement test that walks the topic map, including a math diagnostic
- More exercise types: [x] Parsons problems ([ADR-0016](decisions/0016-parsons-problems.md), 2026-11-09, one in 29 of the 30 topics); [ ] a step-through code visualizer
- The living map: topics fade as their predicted memory strength drops. [x] First version (2026-11-09): each Learned topic shows "Memory: N%" and a bar from the scheduler's predicted retrievability; dimming the rows themselves was left out for legibility.
- [x] A practice-hours tracker (the owner's idea, 2026-11-06): total time spent in active practice, from the attempt durations in the event log, with milestones from 1 hour on the way to 10,000. It counts deliberate practice (attempts, proof checks, reviews), not time with the site open, because that's what the research behind "10,000 hours" measured. Built early, on the Today page (2026-11-09). [x] Counted per track, each on its own ladder ([ADR-0019](decisions/0019-today-across-tracks.md), 2026-11-09).
- [x] Today shows every track (2026-11-09, [ADR-0019](decisions/0019-today-across-tracks.md)): one Next up per track, with how far along each is, so a learner on two tracks sees where they stand on both.
- [x] Automated data backups (2026-11-09, [ADR-0020](decisions/0020-automated-backups.md)): a nightly encrypted dump to a private backups repository, with the restore rehearsed on every pull request; three secrets for the owner to add.
- Content: intermediate Python; a math refresher for the ML track

## Phase 3: CS and ML tracks (months 5–9)

- Content: math for ML (linear algebra, calculus, probability), core CS (data structures, algorithms, how computers and GPUs work), then neural networks from scratch, building up to transformers
- The owner writes a growing share of the platform's code
- Senior-engineer code review and the practice generator

## Phase 4: Capstone and opening up (months 10–12)

- **ML capstone:** fit the review scheduler and a knowledge-tracing model to the owner's own learning data
- Content: ML systems (training, evaluation, serving)
- AI-assisted coding track ("earn the AI")
- Decide whether to open it, free, to other beginners

## Other tracks

- **Cloud Solutions Architect, multi-cloud.** Specified on 2026-11-08: [the spec](specs/cloud-solutions-architect.md), with 30 modules in 4 stages and about 320 topics, up to principal level, on AWS, Azure and Google Cloud. It was cross-referenced the same day with the owner's own knowledge map ([docs/research](research/senior-cloud-architect-knowledge-map.md)), which added a 24-month example path and a self-assessment. The track assumes nothing about the learner and starts from zero. How its cloud work is proven is [ADR-0014](decisions/0014-cloud-labs.md), accepted 2026-11-09.

  Building it, in the order the spec's _Building it_ section gives:
  - [x] More than one track in the app: the map and topic pages know every track (2026-11-08)
  - [x] The track on the map as `planned` outlines, generated from the spec (2026-11-08)
  - [x] Decide how the shell is taught and proven ([ADR-0017](decisions/0017-shell-in-the-browser.md), accepted 2026-11-09): a `predict_shell` item proven by real `bash` in the validator, local container labs through the lab checker, a browser VM later
  - [ ] Stage 1 content: Module 1's lessons and recall first ([x] all 14 topics drafted on 2026-11-09, with 228 recall items), then their labs ([x] Shell essentials ready on five labs, 2026-11-09; [x] Services and logs, the first systemd labs, 2026-11-09; [x] Processes and signals, 2026-11-09; [x] Users, permissions and SSH, 2026-11-09; [x] Package management and patching, 2026-11-09; [x] Disks and filesystems, 2026-11-09; [x] Memory and the OOM killer, 2026-11-09; [x] CPU scheduling and cgroups, 2026-11-09; [x] How containers work, 2026-11-09; [x] Networking from the host, 2026-11-09; [x] Boot, cloud-init and instance metadata, 2026-11-09; [x] Shell scripting, 2026-11-09; [x] Performance triage, 2026-11-09; [x] Hardening, 2026-11-09 (all 14 topics ready); [x] Checkpoint 1: the broken server, 2026-11-09, so Module 1 is complete), then the drills that run in the browser
  - [ ] The lab checker ([ADR-0014](decisions/0014-cloud-labs.md), accepted 2026-11-09). [x] Local mode (2026-11-09, [ADR-0018](decisions/0018-lab-checker-local-mode.md)): `tools/labcheck.py` builds a lab's container from `content/`, runs its checks, prints a result to paste, and proves every lab's contract in CI; the first lab is Shell essentials' build. [x] The lab view on the topic page (2026-11-09). [ ] Cloud mode, with recordings.
  - [ ] Design reviews, game days and "Defend it"

## The owner's 12-month learning milestone

- Solid CS foundations and the math behind ML
- Build and train a small GPT from scratch, understanding every line
- Ship an ML system end to end (the capstone counts)

Principal-engineer level stays the long-term ceiling of the map. It takes years of real-world experience, so it isn't a 12-month goal.

## Open questions

- License: open source or proprietary? This matters if it becomes a company.
- Final product name ([ADR-0006](decisions/0006-working-name.md))
- Hidden tests run in the browser, so a determined learner could peek. Fine for personal use; revisit before a public launch.
- When and how to open it to other learners
- When to build the Cloud Solutions Architect track, relative to the rest of v1 and the ML path
