# Roadmap

**Current phase: 1, Milestone B (prove it).** Milestone A is done.

The owner works full time, split between learning (mornings, on the platform once it exists) and building (afternoons). The roadmap serves both: the platform's content stays one module ahead of the owner's own learning.

## Phase 0: Setup and planning (done)

- [x] Research: Brilliant, roadmap.sh, Math Academy ([competitors](research/competitors.md))
- [x] Product concept and key decisions ([vision](vision.md), ADR-0002 to ADR-0006)
- [x] Repository, documentation and development process (backed up to a private GitHub repo)
- [x] Accept a tech stack ([ADR-0007](decisions/0007-tech-stack.md))
- [x] v1 spec ([specs/v1.md](specs/v1.md)): features and milestones, the [data model](specs/data-model.md), and the [first 30 Python topics](specs/python-foundations.md)
## Phase 1: v1 for an audience of one (weeks 1–4, now)

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
- [ ] Topic states and gating, with "Prove it now" (F8, F9). Next up. They were waiting for grading: until explanations could pass, no topic could be Learned, and gating would have locked every topic after the first. Grading is live now.
- [ ] Module 2 content, ready before the owner finishes Module 1

## Phase 2: Adaptivity and better practice (months 2–4)

Mornings learning on the platform, afternoons building it.

- A placement test that walks the topic map, including a math diagnostic
- More exercise types: Parsons problems, a step-through code visualizer
- The living map: topics fade as their predicted memory strength drops
- A practice-hours tracker (the owner's idea, 2026-11-06): total time spent in active practice, from the attempt durations in the event log, with milestones from 10 hours on the way to 10,000. It counts deliberate practice (attempts, proof checks, reviews), not time with the site open, because that's what the research behind "10,000 hours" measured.
- Automated data backups
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

- **Cloud Solutions Architect, multi-cloud.** Specified on 2026-11-08: [the spec](specs/cloud-solutions-architect.md), with 30 modules in 4 stages and about 320 topics, up to principal level, on AWS, Azure and Google Cloud. It was cross-referenced the same day with the owner's own knowledge map, which added depth levels, a 24-month path for an experienced learner and a self-assessment. How its cloud work is proven is [ADR-0014](decisions/0014-cloud-labs.md), proposed. Building it needs support for more than one track in the app, and the lab checker.

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
