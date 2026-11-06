# Roadmap

**Current phase: 0 (setup and v1 planning).**

The owner works full time, split between learning (mornings, on the platform once it exists) and building (afternoons). The roadmap serves both: the platform's content stays one module ahead of the owner's own learning.

## Phase 0: Setup and planning (now)

- [x] Research: Brilliant, roadmap.sh, Math Academy ([competitors](research/competitors.md))
- [x] Product concept and key decisions ([vision](vision.md), ADR-0002 to ADR-0006)
- [x] Repository, documentation and development process (backed up to a private GitHub repo)
- [x] Accept a tech stack ([ADR-0007](decisions/0007-tech-stack.md))
- [ ] v1 spec: feature list, data model for the topic map and learner progress, the first 30 Python topics
- [ ] Scaffold the app, CI and first deploy

## Phase 1: v1 for an audience of one (weeks 1–4)

Built mostly with AI help while the owner starts learning Python from curated free resources.

- Topic map (graph view) with prerequisites
- Lesson view: embedded resource plus AI intro and recap
- Python exercises that run in the browser and check themselves with tests
- Review scheduler (FSRS)
- Hint-only AI tutor
- Progress saved to a database, with append-only answer and review logs
- Content: about 30 Python fundamentals topics

## Phase 2: Make "prove it" real (months 2–4)

Mornings learning on the platform, afternoons building it.

- Placement test, including math
- Blank-editor challenges with hidden tests
- Explain-it-back with AI grading
- Debug-unfamiliar-code challenges
- Topic states, gating with test-out, and the living map
- Content: finish Python fundamentals; math diagnostic and refresher

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
- Monthly spending cap for the Claude API
- Hidden tests run in the browser, so a determined learner could peek. Fine for personal use; revisit before a public launch.
- When and how to open it to other learners
