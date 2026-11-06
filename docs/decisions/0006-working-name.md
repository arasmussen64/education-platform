# ADR-0006: "Switchback" is a working name

- **Status:** Accepted
- **Date:** 2026-11-05

## Context

The owner picked **Switchback** from a shortlist. A switchback is a mountain trail that zigzags back over the same ground while climbing higher, like returning to topics on the long climb from beginner to principal. The owner may still change the name.

## Decision

- Use "Switchback" in docs, marked as a working name.
- In code, the product name lives in **one** config constant. Never hard-code it in components, URLs, package names or database names.
- Repository and package names stay neutral, for example `education-platform`.
- No domain purchase for now (ADR-0005).

## Notes for a future naming decision

- On 2026-11-05, switchback.com and switchback.dev were taken. switchbackcs.com, switchbackcs.dev, learnswitchback.com, learnswitchback.dev and switchbackacademy.com were unregistered.
- No learning product named Switchback was found. A trademark search is still needed before investing in the brand (USPTO: education is Class 41, software is Classes 9 and 42).
- Other names considered: Anneal, Cairn, Whetstone, Kiln, Belay, Ground Truth, Generalize, Masterwork. Engram was ruled out because several learning apps already use it.
- Taglines considered: "Learn it. Build it. Keep it." / "Don't overfit to the test." / "From zero to principal."

## Consequences

Renaming later means changing one config value and the docs, not refactoring.
