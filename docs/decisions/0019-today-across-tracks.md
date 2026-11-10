# ADR-0019: Today shows every track, and counts practice hours per track

- **Status:** Accepted (the owner asked for both on 2026-11-09: "the today page should mix tracks so I can quickly see where I'm at on both but the 10000 hours should be broken down per track")
- **Date:** 2026-11-09

## Context

- The Today page ([F12](../specs/v1.md#f12-today-page)) was built when there was one track. Its "Next up" picks a single topic: the first in progress, or else the first Available, across every bundled track's topics laid end to end. With two tracks that means the Python track's next topic until Python runs out, and nothing about where the learner is in the cloud track.
- Its reviews and the mistakes-to-revisit cards already draw on every bundled track's topics, because they're keyed by topic, so those parts mix tracks without anyone having decided it.
- The practice-hours tracker (roadmap, Phase 2) adds every attempt's time into one total on the way to 10,000 hours. The research behind that figure (Ericsson's deliberate practice; see [docs/learning-science.md](../learning-science.md)) is about mastery of one domain. A learner working two tracks is working two domains.
- The owner is now learning on both tracks and wants to see, each morning, where they stand on each.

## Decision

1. **Next up shows one entry per track,** in the order the tracks are shown: the track's name; how many of its open topics are learned; and its topic in progress (Continue) or else its next Available topic (Start), with the summary and the time estimate as before. A track whose written topics are all learned says so; a track with nothing written yet says that instead. The rule inside a track is unchanged (`nextUp` in `progress/progress.ts`), applied to that track's topics alone.
2. **Practice hours are counted per track.** Each attempt belongs to the track that holds its topic (`placeOf` in `content/content.ts`). The section keeps one sentence for all practice so far, then a block per track: its time so far and in the last seven days, and its own next milestone and progress bar, on the same ladder (1, 5, 10, 25, 50, 100, 250, 500, 1,000, 2,500, 5,000, 10,000 hours). Time on a topic that no longer belongs to any track is shown as "Other" only when there is some.
3. **Reviews and mistakes to revisit stay as they are:** both already mix tracks. Each review names its topic, which is enough to tell the tracks apart.

## Alternatives considered

- **One overall milestone ladder, with the per-track split as a footnote.** Simpler, but it would say "100 hours" of a learner who has 90 in Python and 10 in cloud, which isn't what the hours are for. Per-track ladders say what each domain has had; the overall sentence keeps the total visible.
- **A separate Today page per track, or a track switcher.** It hides the other track, which is the opposite of the ask, and reviews are due across tracks on the same day anyway.
- **Interleaving the two tracks' next topics into one list.** There's no sensible order between "Values and types" and "Services and logs"; one entry per track is clearer and it's what the learner compares.
- **Counting a track's hours only from its proof checks.** Every graded attempt is deliberate practice, the tracker's rule since it was built; the split changes how the time is grouped, not what counts.

## Consequences

- Today has two "Next up" entries now and will have one more per track as tracks are added, with no further change.
- The Today page's tests cover both tracks, so a change to either track's first topic shows up there.
- `progress/practiceTime.ts` gains a per-track grouping that takes a "track of this topic" function, so it stays free of content imports and easy to test.
- The spec's F12 and the roadmap's practice-hours item are updated to say the hours are per track.
- When a track's whole content is learned, its entry goes quiet rather than disappearing, so the learner still sees it's there.
