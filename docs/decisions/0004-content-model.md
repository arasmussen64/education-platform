# ADR-0004: Content model

- **Status:** Accepted
- **Date:** 2026-11-05

## Context

The owner can't yet write advanced CS lessons alone, and the map runs from beginner to principal. Excellent free resources already exist for most topics. The platform's real value is in practice, proof and review, which have to be its own. The owner chose to combine curated resources with AI-written material.

## Decision

Each topic has three layers:

1. **Main lesson (curated):** the best existing resource for the topic. That's an official YouTube embed, text embedded where its license allows it, or a link.
2. **Supporting material (AI-written, original):** a short intro ("what to watch for"), a recap, and alternative explanations. The AI writes its own explanations of the concepts and never paraphrases or copies copyrighted text.
3. **Practice (owned by the platform):** recall questions, exercises, projects and "prove it" checks.

**Content lives in the repository as files**: lessons, exercises, tests and the topic graph. It's version-controlled and reviewed like code.

**Every exercise is machine-verified** before it's published, automatically in CI:

- its reference solution passes its tests;
- known-wrong solutions fail them, which shows the tests actually catch mistakes;
- the topic graph has no cycles, and every prerequisite exists.

AI-drafted content goes through the same path as code: generated, verified, reviewed, merged.

**Licenses.** Every external resource records its license. Some of the best resources are **non-commercial only**; MIT OpenCourseWare and Harvard's CS50, for example, are CC BY-NC-SA. Linking to them and using official YouTube embeds is fine. Copying or adapting their text is not, especially if the platform ever goes commercial.

**Error reporting.** Every lesson and exercise gets a "report a problem" button.

## Alternatives considered

- **Curated links only (like roadmap.sh):** fastest, but learners leave the platform, so it can't adapt to them.
- **Hand-written by the owner:** deep learning for the owner, but far too slow for this scope.
- **Recruiting experts now:** not affordable at this stage. Revisit before a paid launch.

## Consequences

- Fast to build, with the best explanations on the internet from day one.
- Depends on third-party resources staying online, so links need periodic checks.
- AI-written material at advanced levels needs expert review before any paid launch.
