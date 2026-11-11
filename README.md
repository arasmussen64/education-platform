# Switchback

*Working name. It may change.*

An adaptive computer-science learning platform that takes you from total beginner to principal engineer, and doesn't let you fool yourself along the way.

> Learn it. Build it. Keep it.

Most courses get you through the test, and then you forget. Here:

- **There's a map of all of CS**, showing every topic and what it depends on. You can't tick topics off. You have to prove them.
- **Every topic is taught** using the best free resource on it, with AI-written intros and recaps and a tutor that gives hints, not answers.
- **A topic counts once you can build it from a blank file**, explain it, debug code that uses it, and still do it weeks later.
- **Reviews are scheduled** around how fast *you* forget.

**Status:** kept in one place, the top of the [roadmap](docs/roadmap.md#where-the-project-stands): what's built, how much there is to learn, and what gets built next.

**Live:** https://education-platform.arasmussen64.workers.dev (it updates automatically on every merge to `main`).

## Documentation

| Doc | What's in it |
|---|---|
| [Vision](docs/vision.md) | The concept: who it's for, how it works, what makes it different |
| [Learning science](docs/learning-science.md) | The research-backed methods and the features they drive |
| [Roadmap](docs/roadmap.md) | Where the project stands, what gets built next, phases, open questions |
| [v1 spec](docs/specs/v1.md) | What v1 does, plus the [data model](docs/specs/data-model.md) |
| Track specs | What each track teaches: [Python Foundations](docs/specs/python-foundations.md), [Machine Learning Foundations](docs/specs/ml-foundations.md) and [Cloud Solutions Architect](docs/specs/cloud-solutions-architect.md) |
| [Decisions](docs/decisions/) | Architecture and product decision records (ADRs) |
| [Competitors](docs/research/competitors.md) | Brilliant, roadmap.sh, Math Academy and others |
| [Devlog](docs/devlog.md) | Dated log of each working session |
| [Changelog](CHANGELOG.md) | Notable changes |
| [Setup](docs/setup.md) | What to install and which accounts to create |
| [Web app](web/README.md) | How to run, test and build the app |
| [Content](content/README.md) | The lessons and exercises, as files: their layout, and how to write a topic |
| [Harness](harness/README.md) | The Python that runs learner code and its tests, in the browser and in CI |
| [Tools](tools/README.md) | The content validator, the lab checker and other scripts |
| [Database](supabase/README.md) | The local and live databases, migrations, and the AI proxy |
| [CLAUDE.md](CLAUDE.md) | Instructions for Claude Code, the AI pair programmer on this project |

## License

Not decided yet. All rights reserved for now.
