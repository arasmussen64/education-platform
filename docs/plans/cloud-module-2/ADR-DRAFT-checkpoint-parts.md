# Amendment to ADR-0012 (draft): a checkpoint with more than one build or debug

To be added to `docs/decisions/0012-checkpoint-support.md` as a dated section, status _Proposed_.

## Amendment (2026-11-11): a checkpoint's further parts

- **Status:** Proposed.

**Context.** A checkpoint's `prove` holds one build, one debug and one explain (`tools/content_model.py`, `Prove`), and `web/src/progress/progress.ts` passes a checkpoint on its build (or any of `unstuck.versions`) and its debug. The cloud track's spec gives several checkpoints more parts than that: Checkpoint 2 has three, and Checkpoints 3, 5 and 7 have two or three each. Checkpoint 1 met the same wall and, in its 2026-11-11 rewrite, folded its second part (a service killed and throttled) into its debug as two more faults, which works because both parts are one broken server. Checkpoint 2's parts can't be folded honestly: a sizing sheet in a plain lab, four slow VMs' recorded evidence, and an Active Directory domain stood up in a systemd lab with a second machine. Leaving the third part out would repeat what the 2026-11-10 audit recorded about Checkpoint 1, a checkpoint narrower than its spec.

**Decision.**

1. `prove` gains an optional `more`: a list of further parts, each `{id, versions}`. `id` names an exercise in the checkpoint's folder whose stage is `build` or `debug`; `versions` lists zero or more fresh versions of it, in other stories, with the same stage.

   ```yaml
   prove:
     build: build-the-right-machine
     debug: debug-slow-vms
     more:
       - id: build-stand-up-the-domain
         versions: [build-stand-up-the-domain-clinic]
     explain: ...
   ```
2. **Passing.** A checkpoint is passed when its build (or one of `unstuck.versions`), its debug, every part in `more` (or one of that part's versions) and its explain have passed. A part's check counts like any other Check of that exercise ([ADR-0011](0011-mistakes-come-back.md)'s rules on what counts as missed are unchanged).
3. **What the validator checks for a ready checkpoint:** every `more` id and version exists, has the stated stage, and names `test_skills` for every check, as the build and debug must; a `more` build has at least one fresh version (the reason for fresh versions, a second try that can't be passed from memory, applies to every build); a `more` part is not also the build, the debug or a step.
4. **Support.** The four additions of this ADR stay attached to the main build: one solved sibling, three or four steps, two fresh versions. A further part's practice is the module's topic labs, which its failed checks bring back through `test_skills`; it has no steps of its own. If learners are seen to get stuck on a further part, steps for it are a later amendment.
5. **The page** shows the parts in order, numbered as the spec numbers them ("Part 3: stand up the domain"), each with its own lab or editor. The explain still opens only after the main build passes (the amendment of 2026-11-10).

**Alternatives considered.**

- *Folding every part into the build or the debug,* as Checkpoint 1 did. Right when the parts are one system; wrong when they are different machines, because the combined lab is long, its image holds everything, and a failure in one part blocks proving the others.
- *A list in place of `build` and `debug`* (`builds: [...]`, `debugs: [...]`). Cleaner in the long run, but it changes every existing checkpoint, the progress code and the event readers for no gain today.
- *Leaving the third part to the topic's own build and amending the spec.* Honest, and the fallback if this isn't built, but a checkpoint is where a module's skills are retrieved together weeks after they were learned, which is what the part is for.

**Consequences.** One field in `Prove`, a few validator checks, a few lines in `progress.ts` and the checkpoint page, and their tests. No migration: Checks are events per exercise already. Writers of Checkpoints 2, 3, 5 and 7 can match their spec. A checkpoint with three parts takes longer; its `estimated_minutes` says so.
