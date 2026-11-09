# Vision

> **Switchback** is a working name. See [ADR-0006](decisions/0006-working-name.md).

## In one line

An adaptive learning platform that takes you from total beginner to principal engineer. Nothing counts as learned until you can build with it from a blank editor, and still can weeks later.

## The problem

Most people who learn computer science online hit one of these walls:

1. **Forgetting.** You learn a topic, pass the quiz, and it's gone a few weeks later.
2. **Tutorial hell.** You can follow along, but freeze in front of an empty editor. *This is the main problem Switchback exists to fix.*
3. **Shallow understanding.** You can use a tool but can't explain why it works.
4. **Self-deception.** Progress is self-reported (a checkbox) or a one-time quiz, so nobody, including you, knows what you really know.

## Who it's for

- **Adaptive by design.** A placement test finds where each learner's knowledge stops, and everything after that is personalized.
- **Starts at zero.** The first users are total beginners.
- **No ceiling.** The map runs all the way to principal-engineer level.
- **First learner: the owner.** The platform is built partly by and for its first learner, who is learning to code while building it.
- **First track:** CS foundations → ML engineering.
- **Next track (specified, not built):** [Cloud Solutions Architect](specs/cloud-solutions-architect.md), on AWS, Azure and Google Cloud, up to principal level.

## How it compares

| | Strength | What's missing | Switchback |
|---|---|---|---|
| roadmap.sh | Map of everything to learn | Doesn't teach; progress is self-checked | Same kind of map, but every topic must be proven |
| Brilliant | Interactive teaching | Stops at intro-level CS; puzzles, not building | Interactive, aimed at building real things, all the way up |
| Math Academy | Adaptive mastery and spaced review | Math only | The same engine idea, for CS and ML |

Details: [research/competitors.md](research/competitors.md).

## How each topic works

1. **Learn.** A short AI-written intro ("what to watch for"), then the best existing resource on the topic (an embedded video or reading), then an AI recap. A hint-only tutor is available if you're stuck.
2. **Practice.** The help fades: first a fully worked example, then half-finished code, then a blank file. Problems come in fresh variations and are mixed with older topics, so you learn to recognize which approach fits.
3. **Prove it.** Build it from a blank file against hidden tests with no AI; explain it in your own words; debug code you didn't write that uses it. Small topics get quick versions of these checks; each module ends with full-size ones.
4. **Keep it.** Reviews are timed to how fast *you* forget. Reviewing an advanced topic also counts as practice for the simpler topics underneath it, so the review pile stays manageable.

### Topic states

| State | Meaning |
|---|---|
| Locked | Prerequisites aren't proven yet (you can still preview it) |
| Available | Ready to learn |
| Learned | Passed the three "prove it" checks |
| Mastered | Also passed a review at least a week later |
| Fading | A review is due; the map shows it fading |

Exact rules: [ADR-0002](decisions/0002-mastery-and-gating.md).

## How it adapts

- **Topic map (knowledge graph).** Every topic and its prerequisites, from algebra and Python up through ML systems and principal-level design.
- **Placement test.** Walks the map to find where your knowledge runs out, math included.
- **Gating with test-out.** A topic unlocks once its prerequisites are proven. You can prove a topic directly and skip its lessons.
- **A living map.** Your map shows what you know *today*. Topics fade as reviews come due, so forgetting is visible.
- **Next best task.** Each session it picks the most useful thing to do: a new lesson, practice, a review or a project.

## AI, with guardrails

| Role | Rule |
|---|---|
| Socratic tutor | Hints one step at a time; never the full answer; off during "prove it" checks |
| Senior-engineer reviewer | Reviews your code like a mentor, after it passes the tests |
| Practice generator | Every generated problem is verified (the reference solution must pass its tests) before you see it |
| AI-assisted coding | **Earn the AI:** the AI-assisted version of a skill unlocks only after you've proven it without AI |

Details: [ADR-0003](decisions/0003-ai-roles-and-guardrails.md).

## Content

The best free resources do the main explaining. AI writes short original material around them. The practice, projects and checks belong to the platform. Every resource's license is recorded. Details: [ADR-0004](decisions/0004-content-model.md).

## Business model and constraints

- **Free, and personal-use first.** The owner uses it for their own learning, then maybe opens it to others for free. A paid company is a possible later step.
- **Free hosting** until that's no longer possible ([ADR-0005](decisions/0005-free-hosting-first.md)).

## Not in v1

Mobile apps, social features or leaderboards, certificates, languages other than Python, payments, and teacher or classroom features.

## Risks

| Risk | Mitigation |
|---|---|
| Errors in AI-drafted advanced content | Ground it in trusted sources; make every exercise runnable; add a "report a problem" button; get expert review before any paid launch |
| Scope: beginner to principal is a huge map | Build the engine to work for any topic; only add content just ahead of where the first learner is |
| Building it with AI without understanding it | Don't merge code the owner couldn't explain back |
| Free tiers change or run out | Pick portable tech (plain Postgres, static hosting) so moving is cheap |
| Cheating on in-browser hidden tests | Doesn't matter for personal use (cheating only hurts the cheater); revisit before a public launch |
