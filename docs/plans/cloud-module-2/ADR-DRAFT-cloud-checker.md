# ADR-0025 (draft): The cloud checker's first form, for Module 2's Azure lab

- **Status:** Proposed. Not needed before Module 2 is written: build it when the owner schedules the first run of the Azure lab.
- **Date:** 2026-11-11

## Context

[ADR-0014](0014-cloud-labs.md) decided that cloud labs are checked by a tool on the learner's machine, with read-only access, whose checks are small Python functions over what the clouds' APIs return, tested in CI against recorded responses, and that every lab is run once for real by the owner before it is `ready`. Its amendment of 2026-11-10 lets a lab that needs a real cloud be built in the owner's Azure subscription inside its $150 monthly credit. Nothing of the cloud checker has been built; the local checker ([ADR-0018](0018-lab-checker-local-mode.md)) checks containers only.

Module 2's first real-cloud lab is optional: a Windows Server domain controller, a Windows member and an Ubuntu member in one resource group, no public addresses, reached through Azure Bastion's free Developer tier, about $0.60 a three-hour sitting. It can't count as a proof until something checks it. Two facts shape the smallest checker:

- The checks need to ask a Windows VM what it knows (is it a domain controller; did a Windows client apply a Group Policy object). The only way in without an inbound port is Run Command, which runs a script through the VM agent as System. Running one needs `Microsoft.Compute/virtualMachines/runCommand/action` (Virtual Machine Contributor or higher), which is more than Reader. Output is limited to 4,096 bytes, a run takes at least about 20 seconds, one runs at a time, and it needs outbound access from the VM (Microsoft's Run Command page, read 2026-11-11).
- Nobody has run the lab, so every recorded response CI would test against can only be written from documentation until the owner's first run.

## Decision

1. **`tools/cloudcheck.py`, beside `labcheck.py`.** A lab's checks are listed in `checks.yaml`, each an `az ... -o json` command (or an `az vm run-command invoke` whose script prints one line of JSON) and the name of a small Python predicate in the lab's `checks.py`. `check` runs them with the learner's own `az` sign-in and prints the same result JSON the lab page already accepts. Nothing else leaves the machine: no subscription, tenant, resource or user names.
2. **Recordings.** `check --record DIR` saves every command's output with identifiers scrubbed. `test` replays saved outputs in CI: one set from a correct build must pass every check, one set per known-wrong build must fail the check it was written for. Until the owner's first run, recordings written from documentation are labelled as such and the lab stays outside proofs.
3. **`runtime: cloud`** on an exercise marks it. The validator checks its structure (checks, predicates, recordings) and CI runs the replay; nothing is deployed in CI.
4. **The read-only rule, and its one exception.** Every check reads. Run Command is the exception ADR-0014 didn't foresee: the scripts only read, but the permission could write. For a single learner in their own subscription, the learner's own sign-in is accepted; a custom role of Reader plus the one run-command action is the documented alternative, and is required before any second learner uses the checker.
5. **Guardrails and teardown are checks:** a budget with an enabled notification exists; every VM has an auto-shutdown schedule; everything carries the lab's tag; no network interface has a public address and no rule admits the internet on 3389, 22, 5985 or `*`; and, after deletion, nothing with the tag remains.
6. **The first real run is the owner's**, with the owner's go-ahead, from the runbook. Its recordings replace the documentation-written ones; only then does the lab take a place in the ladder (an optional build in `csa.hw.domain-join`, and a fresh version of Checkpoint 2 part 3).

## Alternatives considered

- **Checking over SSH from the learner's machine to the Linux member** (the checkpoint designer's `where: ssh`): it can prove the Linux join and, through a directory search, that the Windows member has a computer account, but not that a Windows client applied a policy, and it needs a reachable address or Bastion's native client (Standard tier, $0.29 an hour).
- **WinRM to the Windows VMs:** needs an inbound port and credentials handled by the checker.
- **Screenshots or pasted output graded by AI:** easy to fake (ADR-0014 already rejected it).

## Consequences

- A small new tool, its tests, and recordings that need refreshing when `az`'s output changes (the checker pins nothing it can't).
- The Azure lab can become a proof only after the owner's run; until then it is labelled optional and unproven.
- Later cloud labs (Module 8 on) extend the same tool rather than start one.
