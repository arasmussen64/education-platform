# Roadmap

**Current phase: 1, Milestone A (walking skeleton).**

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
- [ ] The app loads content, with topic pages for lessons and exercises
- [x] Local Supabase in Docker, with the profiles and event-log tables
- [x] Sign-in: GitHub on the live site, email links locally
- [ ] Saving answers to the event log (comes with the topic pages)
- [ ] Deploy to Cloudflare
- [ ] Module 1 content

## Phase 2: Adaptivity and better practice (months 2–4)

Mornings learning on the platform, afternoons building it.

- A placement test that walks the topic map, including a math diagnostic
- More exercise types: Parsons problems, a step-through code visualizer
- The living map: topics fade as their predicted memory strength drops
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
