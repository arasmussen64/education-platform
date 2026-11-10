# ADR-0023: Packages beyond the standard library, in both Python runtimes

- **Status:** Proposed
- **Date:** 2026-11-10

## Context

Learner Python runs in two places that must agree ([harness/README.md](../../harness/README.md)): the browser, inside Pyodide, and CPython on GitHub, where the content validator proves every reference solution passes and every known-wrong solution fails. Until now both used the standard library only.

The Machine Learning Foundations track's Module 3, linear algebra ([spec](../specs/ml-foundations.md)), is written in NumPy, as every ML library is. Module 1 taught vectors and matrices as lists on purpose, so the learner knows what the array is doing for them; from Module 3 on, the tool itself is the lesson. Later modules add more (plotting is its own question, left open here).

What's true of the runtimes:

- Pyodide ships NumPy as a package built for the browser, downloaded on request from the same CDN as Pyodide itself (about ten megabytes, cached by the browser afterwards; two seconds on a good connection). The exact version is pinned by the Pyodide release the app uses.
- CPython gets NumPy from PyPI through uv, where the same version is available.
- Loading a package takes longer than a learner's program is allowed to run (five seconds), so it can't hide inside a Run.
- Most topics don't need it. Python Foundations, the cloud track and the first two ML modules shouldn't pay the download.

## Decision

1. **A topic declares the packages its code imports:** `packages: [numpy]` in `topic.yaml`. The content model allows only names on a short list (NumPy, to start), and the validator refuses code that imports a package its topic doesn't declare, so a topic can't work on GitHub and fail in the browser.
2. **The browser loads a topic's packages on first use, before the first Run, Check or Step through on that topic,** with its own time limit (two minutes) separate from the program's. Once loaded, a worker keeps them; a worker replaced after a time-out loads them again on the next request. Topics without packages are untouched: nothing is downloaded.
3. **CPython pins the version Pyodide ships** (`numpy==2.4.6` for Pyodide 314.0.7, in the root `pyproject.toml`), the way the Python minor version is already pinned, so the two runtimes print the same arrays and raise the same errors. Bumping Pyodide means bumping the pin, and the Pyodide test (`content.pyodide.test.ts`) runs every ready solution with the packages loaded, so a mismatch shows up on the pull request.
4. **One package at a time.** Adding another name to the list is a small change, but it needs the same two checks: that Pyodide ships it, and that the version can be matched on PyPI.

## Alternatives considered

- **Pure-Python lists for Module 3,** as in Module 1: teaches the ideas, not the tool, and every later module (neural networks from scratch, transformers) needs arrays anyway. Rejected for Module 3 onward; kept for Module 1, where it was the point.
- **Load NumPy for every topic at start-up:** simplest, but ten megabytes for a learner on a phone doing Python Foundations, for nothing. Rejected.
- **Self-host the package files on Cloudflare** instead of the CDN: no advantage while the CDN is the same one Pyodide already comes from, and it would make every Pyodide bump a bigger change. Not now.
- **Let any PyPI package in through micropip:** pure-Python packages would work, compiled ones wouldn't, and nothing would pin versions between the runtimes. Rejected; the short list is the point.

## Consequences

- The ML track's Module 3 can be written in NumPy, and the first topic, NumPy arrays, proves the path end to end.
- A new field in the content model and the web types, a `load` message in the Python worker's protocol, and a longer time limit for it; the content validator gains a check that imports match declarations.
- The first Run on a NumPy topic takes a few seconds longer while the package downloads; the button shows it's working. The learner's answer and review logs are unchanged.
- CI's Pyodide test downloads NumPy from the CDN on each run (Node caches it in `node_modules` within a run). If that proves flaky, the wheel can be cached between runs like the other dependencies.
- The owner's choice: accept NumPy in the browser on these terms, or ask for Module 3 in plain Python.
