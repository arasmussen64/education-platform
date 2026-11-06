# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [Semantic Versioning](https://semver.org/) once there's a release.

## [Unreleased]

### Added

- Web app scaffold in `web/`: Vite, React, TypeScript, Tailwind CSS and React Router, with placeholder Today, Map and Topic pages. The product name is kept in a single setting.
- CI on GitHub Actions: formatting, lint, type-check, tests and build on every pull request and every push to `main`.
- v1 spec, data model and Python Foundations track plan, in `docs/specs/`.
- ADR-0008 (append-only event log) and ADR-0009 (per-topic reviews, graded automatically), both accepted.
- Project documentation: vision, learning-science principles, roadmap, competitor research, devlog.
- Decision records ADR-0001 to ADR-0007: decision process, mastery and gating, AI roles, content model, free hosting, working name, tech stack.
- `CLAUDE.md` with the development process and the product rules that constrain code.
- Repository config: `.gitignore`, `.gitattributes` (LF line endings), `.editorconfig`.

### Changed

- Roadmap: the "prove it" checks, topic states and gating move from Phase 2 into Phase 1.
