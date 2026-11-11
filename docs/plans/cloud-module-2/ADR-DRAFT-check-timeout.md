# Amendment to ADR-0018 (draft): a check may take longer than 30 seconds

To be added to `docs/decisions/0018-lab-checker-local-mode.md` as a dated section, status _Proposed_, after the amendment of 2026-11-11 now on `fix/labcheck-shell-and-restart`.

## Amendment (2026-11-11): a check's own time limit

- **Status:** Proposed.

**Context.** `tools/labcheck.py` gives every check 30 seconds (`CHECK_TIMEOUT_SECONDS`). That has been enough for Module 1. Module 2's hypervisors topic boots a small virtual machine with QEMU, without hardware help, inside the lab container: 16 to 27 seconds per boot on the owner's PC with other containers busy, and unmeasured on a CI runner running four labs at once. So its designer had the checks read a log the learner's own run left (`boot.log`), with a freshness test. A log is a file the learner can write by hand, so in the topic's debug, a proof, a hand-edited log would pass. The honest check runs the learner's launcher itself and reads what the guest reports, and that takes longer than 30 seconds.

**Decision.**

1. A check in `checks.yaml` may say `timeout: N`, a whole number of seconds from 1 to 300. Without it, 30 seconds as now.
2. The checker uses it wherever it runs that check: `check` on the learner's machine and `test` in CI.
3. The validator checks the field's type and range, and warns when a lab's checks add up to more than ten minutes.
4. `content/README.md` says when to use it: a check that has to run something slow to observe it (booting a VM, a service's first start), never to wait out a race. A check that reads a state the learner made should stay fast.

**Alternatives considered.** Raising the limit for every check (slow failures everywhere, for one topic's sake); reading the learner's log (passes a hand-written log in a proof); booting the VM at the container's start (the VM is the thing the learner is fixing).

**Consequences.** About ten lines in the checker and one in the validator's schema, with tests. Topic 15's write and debug checks run the learner's launcher with `timeout: 120`. CI's Labs job gets slower by the boots it now does; the shard count can rise if it needs to.
