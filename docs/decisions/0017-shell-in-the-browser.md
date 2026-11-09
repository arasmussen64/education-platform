# ADR-0017: Teaching and proving the shell

- **Status:** Accepted (2026-11-09)
- **Date:** 2026-11-09

## Context

The Cloud Solutions Architect track ([spec](../specs/cloud-solutions-architect.md)) opens with Module 1, Linux and the command line: fourteen topics from shell essentials to hardening, and a checkpoint that hands the learner a broken server to fix. Everything later in the track stands on it, and a learner can't reach the later modules (where the browser drills of [ADR-0014](0014-cloud-labs.md) live) without passing it.

The platform can run and check Python in the browser (Pyodide) and nothing else. ADR-0014 settled how cloud work is proven: in the learner's own sandboxes, checked by a local tool, the lab checker, that only reads. It said that Stage 1 practice "runs locally, in containers on your own machine", but not how the shell is *taught* in the browser, nor what a shell drill or recall item looks like when the browser has no shell.

What exists, as of this writing, for a shell in the browser:

- **v86** (BSD-2-Clause): an x86 emulator in WebAssembly that boots a 32-bit Alpine Linux. A 2 MB engine plus a root filesystem of roughly 60 MB, loadable in pieces as static files; the host page can read the guest's files through a shared 9p filesystem, which is what a checker would need. A real shell, slow but real.
- **CheerpX / WebVM**: the smoothest experience, but the engine is proprietary and self-hosting needs a licence from the vendor, which rules it out under [ADR-0005](0005-free-hosting-first.md).
- **container2wasm** (Apache-2.0): runs whole containers by bundling an emulator; experimental, and heavier still.
- **Writing a shell simulator** in Python on top of the harness: full control, but every command's semantics would be ours to get wrong, and a learner would be practising on a model of a shell rather than a shell.

Hosting stays on free tiers, the browser's Python already exists, and the owner's machine has Docker Desktop and Git Bash.

## Decision

1. **Lessons and recall first, in the browser, without running a shell.** Module 1's topics get lessons built on freely licensed material (MIT's *The Missing Semester of Your CS Education*, CC BY-NC-SA 4.0, covers the shell, shell tools, data wrangling and scripting) and the usual recall items. One new recall type, **`predict_shell`**, shows a command or pipeline over a small set of fixture files and asks what it prints, like `predict_output` does for Python. The learner's browser runs nothing; the **validator runs the command in real `bash`** (CI's Linux runners, and Git Bash on the owner's machine) inside a temporary folder holding the fixtures, with no network, and checks the expected output matches. Every item is thus proven against a real shell before a learner sees it.
2. **Builds, debugs and the checkpoint run in containers on the learner's own machine,** as ADR-0014 said, checked by the lab checker. The first thing to build in the checker is the local mode: a lab is a container image with the scenario inside (the broken server, a full disk, a key with the wrong permissions), the learner works in it, and the checker runs read-only probes with `docker exec` and reports which checks passed. The same recording-based CI tests as ADR-0014 apply: a recording from a correct fix must pass, one from each known-wrong fix must fail.
3. **"Write a command" practice waits for the local mode too.** A drill that asks the learner to type a pipeline needs a shell to run it; until a shell runs in the browser, those are local katas, run by the checker, like the infrastructure-as-code katas in ADR-0014. Until then, the browser's practice ladder for Module 1 is worked examples, `predict_shell` and multiple choice, and the fill-in and write steps are local.
4. **A real VM in the browser is the enhancement, not the base.** v86 with a 32-bit Alpine image is the candidate: open licence, static files, a readable filesystem for checks. It would let a learner without Docker (a Chromebook, a phone) do the local work in the browser. It's deferred until the local mode works and the download cost (tens of megabytes on first use) has been weighed against what it buys.
5. **No shell simulator.** The platform never claims a model of a shell is the shell.

## Alternatives considered

- **Build the simulator first** (fast to start, no download): rejected because the skill being taught is the real tool's behaviour, and a simulator's gaps become the learner's misconceptions.
- **v86 first:** the most honest browser shell, but a 60 MB first download for a learner's first cloud topic, a 32-bit guest, and a checker that doesn't exist yet. Better as a later addition to a working local path.
- **CheerpX / WebVM:** not self-hostable without a licence.
- **Teach the shell with text only, no `predict_shell`:** cheaper, but predicting output is the reading skill that comes before writing, as in the Python track, and the validator can prove the predictions.
- **Skip Module 1 and start the cloud track at networking:** the spec puts Linux first for a reason; every cloud instance is a Linux box.

## Consequences

- Two new things to build before Stage 1 content: the `predict_shell` item type (content model, validator with `bash`, web type and view) and the lab checker's local container mode. The checker is the bigger piece and was already on the roadmap.
- The validator needs `bash` available: CI has it; on Windows the owner's Git Bash serves. Items must stay portable across both (no GNU-only flags that Git Bash's tools lack, or the validator says so).
- Module 1 can be written in two passes: lessons and recall now, local labs when the checker's local mode exists, each topic staying `draft` until both halves are there.
- The owner's choice to make: accept this order (local first, browser VM later), or ask for the browser VM first and accept the download and the 32-bit guest.
