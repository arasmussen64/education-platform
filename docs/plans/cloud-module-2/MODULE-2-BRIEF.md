# Module 2 brief: Virtualization, hardware and Windows

The final plan for Module 2 of the Cloud Solutions Architect track, merged from the four designers' briefs in this folder by the critic on 2026-11-11. Nothing here is in the repository yet.

**How to use it.** This file decides; the designers' briefs hold the detail. Where they disagree, this file wins. Each topic section below names the designer's file and lists only what changes; everything it doesn't mention stands as the designer wrote it. [CRITIQUE.md](CRITIQUE.md) lists every problem found and what was done about it. The four ADR drafts beside this file are the decisions the platform work needs.

The owner's rule for open questions (2026-11-11) decided every judgement call here: the best learning experience first, then memory retention, then free or inside the $150 Azure credit. Each such call is also listed in section 8, for the owner queue's _Decided for you_.

## 1. The plan in one screen

- **Eight topics, not six.** Topic 17 (330 minutes as designed) and topic 19 (360) are each split in two along the seams their designers drew: `csa.hw.disks` comes out of cores-memory, and `csa.hw.domain-join` out of windows-ad. Shorter topics reach their proofs and first reviews sooner, and every proof now tests skills the topic just practised. The spec changes (section 10).
- **Everything is proven locally, at no cost.** QEMU and recorded captures for hypervisors, cross-compilers and an emulator for Arm, systemd limits and loop disks for cores and disks, recorded GPU evidence and dated tables for GPUs, a Samba domain controller in the lab container for Active Directory, `awk` over dated price sheets for licensing.
- **The Azure lab is an optional, priced extra** (about $0.60 a three-hour sitting) until the owner has run it once. It sits outside practice, proofs and reviews. Claude creates nothing in the owner's subscription.
- **One new question type before writing starts:** `estimate`, a typed number checked within a tolerance (draft ADR-0024). About 70 items across topics 16 to 22 use it.
- **Checkpoint 2 has three parts** in three slots: a sizing build, a recorded-evidence debug, and a domain build in a new `prove.more` slot (draft amendment to ADR-0012).
- **Time:** 2,135 minutes of topics and 200 of checkpoint, about 39 hours. The optional Azure lab adds 180.

## 2. Topic order and real prerequisites

Every Module 2 topic depends on `csa.m1.checkpoint`, directly or through another Module 2 topic: the v1 spec's F10 says "the next module's topics depend on" a module's checkpoint. Two designers proposed dropping that gate; it stays. The Module 1 topics each brief lists are for the writer (which lesson taught which term), not for `prerequisites:`.

| # | Id | Title | `prerequisites:` | Builds on (Module 1, for the writer) | Skills | Minutes |
| --- | --- | --- | --- | --- | --- | --- |
| 15 | `csa.hw.hypervisors` | Hypervisors | `csa.m1.checkpoint` | cpu, memory, containers, boot, storage, net-tools, scripting, shell, permissions | `hypervisor-types`, `read-the-guest`, `device-paths`, `cloud-hypervisors`, `isolation-limits` | 280 |
| 16 | `csa.hw.cpu-architectures` | CPU architectures | `csa.hw.hypervisors` | processes, memory (exit 128 + signal), packages, containers, scripting, shell | `read-arch`, `instruction-sets`, `rebuild-inventory`, `arm-families`, `price-performance` | 290 |
| 17 | `csa.hw.cores-memory` | Cores, memory and noisy neighbours | `csa.hw.hypervisors` | cpu, memory, services, triage, shell, scripting | `vcpu-to-core`, `burst-credits`, `stolen-or-capped`, `numa`, `right-size` | 280 |
| 18 | `csa.hw.disks` | Memory tiers and disks | `csa.hw.hypervisors` | storage, services, triage, shell | `storage-tiers`, `what-survives`, `disk-caps` | 205 |
| 19 | `csa.hw.gpus` | GPU basics | `csa.hw.cores-memory`, `csa.hw.disks` | triage, shell, scripting | `gpu-vs-cpu`, `vram-fit`, `read-nvidia-smi`, `gpu-starvation`, `gpu-instance-choice`, `gpu-sharing` | 290 |
| 20 | `csa.hw.windows-ad` | Active Directory: domains, names and tickets | `csa.m1.checkpoint` | shell, permissions, services, net-tools, hardening | `directory-structure`, `dc-discovery`, `kerberos-tickets` | 270 |
| 21 | `csa.hw.domain-join` | Joining machines, Group Policy and Entra ID | `csa.hw.windows-ad` | the same, plus scripting | `domain-join`, `group-policy`, `entra-vs-adds` | 235 |
| 22 | `csa.hw.windows-licensing` | Windows licensing in the cloud | `csa.hw.hypervisors`, `csa.hw.cores-memory` | shell, scripting | `core-counting`, `licence-included`, `bring-your-own`, `dedicated-hosts`, `sql-editions`, `look-it-up` | 285 |
| | `csa.m2.checkpoint` | Checkpoint 2: the right machine | all eight above | | (draws on all) | 200 |

Write them in this order. Topics 16, 17 and 18 can be taken in any order after 15, and 20 can be started straight after Module 1; the map's numbering is the suggested path.

## 3. Rules every Module 2 item follows

These correct things several briefs got wrong, or that changed after they were written (the Module 1 hardening now on local branches).

### 3.1 Multiple choice

- The validator (branch `fix/cloud-mcq-lengths-a`) fails an item whose right answer is more than 1.5 times its longest wrong choice, and a topic with four or more items in which the right answer is the longest in more than half. Nothing in the cloud track may sit in the baseline file.
- **The hypervisors, CPU-architectures, windows-ad and licensing briefs give wrong answers as fragments** ("install the `kvm` package"; "Both have 180 days"), and the licensing brief's own 18 written choices fail: the right one is longest in 14, and 10 are over 1.5 times. The writer writes every choice out in full, in the same grammatical shape, before anything else. The cores-memory and GPU briefs already pass (right longest in 5 of 16 and 12 of 27; none over 1.5 times) and are the model.
- The teaching goes in `explanation`; no explanation names a choice by its position.

### 3.2 Debug prompts

A prompt gives what the system is for (its intended configuration may be stated, as Checkpoint 1's rewritten prompt does), what is observably wrong, how many faults there are, and the rules of the fix. It never says what or where a fault is. Two prompts need a word changed: topic 16's "three faults in how the release is built" becomes "three faults"; topic 21's "nothing about dc1 typed into a hosts file or a Kerberos config" stays, as a rule of the fix, beside the other rules. Check descriptions state end states only. Hints stay out of proofs.

### 3.3 Numbers

- **Quick calculations are `estimate` items** (section 6, P1). Each carries `given`, `working` and at least one named mistake outside its tolerance, which the validator proves. Every calculation skill gets at least three estimate items with different numbers and stories.
- **A proof never reuses a practice or review item's numbers.** Four places did and are changed in the topic sections: the licensing build's break-even (28, the same host and instance as `dh-break-even`), the GPU build's chat model (7 billion at 16 bits: 13.0 GiB and $515.99, which three practice items already use), checkpoint workload w2 (the same Azure pair as `sql-size-by-memory`) and checkpoint ticket vm-a (80% steal on a 20% baseline, which is `steal-from-proc-stat`).
- **No answer on a knife edge.** A check's right answer must survive a change of convention (GB or GiB, 720 or 730 hours) or clear every wrong option by a stated margin. The GPU build's *tune* job did neither and is changed.

### 3.4 Fixtures

- Two labels, never mixed: **captured** (real output of a named machine on a named date, identifiers masked) and **constructed** (a teaching example built to a documented format with invented numbers). A file is never called "recorded" or "captured" unless it was. The topic 17 and 19 fixtures are constructed until the authors' capture runs (section 7.2); the hypervisors brief's capture rule applies only to files labelled captured.
- No stand-in command prints made-up numbers in the learner's shell. Evidence is files that say what they are (the GPU brief's rule). The Module 1 pattern of a stand-in `vmstat` first in `PATH` is for running the learner's *script* inside a check, and nowhere else.
- The owner's laptop capture (`laptop-wsl2`) goes into the public repository with the CPU model name masked (`Intel(R) Core(TM) Ultra (model masked)`). The kernel string is generic to WSL 2 and stays.

### 3.5 Labs

- **Restart trial.** `labcheck start` now keeps a lab across a Docker or computer restart (branch `fix/labcheck-shell-and-restart`). Before a lab is `ready` its author applies the solution, restarts the container (`docker restart`), and runs the checks again. A check that reads a counter a restart resets (topic 17's `memory.events high`) reads a file the learner saved instead.
- **Fixes must last.** Where a fix can be made at runtime only (`systemctl set-property --runtime`), a check rejects it: the property must come from `/etc`, not `/run` (`systemctl show -p DropInPaths`), and a `wrong/runtime-only.sh` proves it.
- **Shared layers.** Each topic's labs share one first `RUN`; topics 20 and 21 and Checkpoint 2 part 3 share the Samba layer (486 MB) and keep its second `RUN` identical.
- **CI time.** About twelve Samba labs at 7 to 8 minutes each will be added. Raise the Labs job's shard list (`.github/workflows/labs.yml`, now 4) when a shard passes 30 minutes; public-repository runners are free.

### 3.6 Prices

- Questions carry their own dated table (the estimate note's design), with `prices_as_of` and `prices_source`. Labs carry the dated CSV and a README, and checks compute from it and confirm its checksum.
- **Correct the fixture before it is committed** (it is still scratch): AWS `g5.xlarge` and `g6.xlarge` list their cards as **22 GiB** in AWS's specification table (re-read 2026-11-11), not 24 GB from the marketing pages; `g6e.xlarge` is an L40S with 44 GiB (now confirmed, so it can join the CSV). Give every GPU row two columns, `gpu_mem_as_stated` (the provider's own figure and unit) and `gpu_mem_gib` (converted by the author), and compute only with the second. The lesson teaches the disagreement once; no lab asks the learner to pretend GB are GiB.
- Azure's B-series v1 (`B1s`, `B2s`, `B2ms`) is **End of Life with an announced retirement** (Microsoft's lifecycle list, read 2026-11-11). Teach and size with Bsv2: `Standard_B2ls_v2` (2 vCPUs, 4 GiB, base 30%) lists at the same $0.0416 as `B2s` and `t3.medium` in East US.
- AWS's Graviton page now says Graviton instances "cost up to 20% less" (read 2026-11-11). The spec's "20–40%" goes (section 10).

### 3.7 Terms

Module 1 never uses the words "DNS", "resolver", "zone", "vCPU", "percentile", "architecture" or "compile" (searched in all fourteen lessons). Each topic defines what it uses at first use; the topic sections add what the designers missed.

## 4. The topics

### 15. `csa.hw.hypervisors` (designer: [csa.hw.hypervisors.md](csa.hw.hypervisors.md))

- **Skills:** as designed (five).
- **Practice ladder:** as designed, 22 items: `example-whats-under-me`, 17 recall items, `fill-under-me`, `write-boot-vm`. Changes: every multiple-choice item written out to equal length (3.1); NVMe defined in one clause (topic 18 teaches it properly); `hv-vulnerabilities` uses eight lines of the laptop capture holding exactly its four `Mitigation` lines; `hv-azure-two-nics` and `hv-nitro-devices` wait for the runner captures, and if those never come they are replaced by multiple choice built on the documentation (fact 16 of the brief), not by constructed output.
- **Proofs:** build `build-fleet-report` as designed. Debug `debug-slow-guest` as designed, with one change: with the per-check `timeout:` (P2), its checks run the learner's `~/bin/shop-vm` themselves (`timeout: 120`) and read the guest's own report, so a hand-edited `boot.log` no longer passes; keep the security wrong fixes (`chmod 644`, `sudo chown root`). Explain as designed.
- **Review pool:** the ten marked ● plus `mcq-detect-none`. `mcq-what-is-shared` is about what is isolated (memory, devices) against what is shared (performance); topic 17 owns the measuring of it.
- **Resources:** main Brendan Gregg, "AWS EC2 Virtualization 2017: Introducing Nitro" (re-opened 2026-11-11: exists, free, about 2,200 words, eight stages, SR-IOV and Nitro explained; the "often less than 1%" overhead is one engineer's estimate and must be called that). Then Red Hat (re-opened), Hyper-V architecture (re-opened: 999 words, dated 2026-01-21), the AWS whitepaper's components page, its side-channels page (this topic reads "Side-channel protections in the broader EC2 service"; topic 17 rereads two paragraphs of it), the Accelerated Networking page, Google's live migration page (re-opened), Azure isolation, `systemd-detect-virt(1)`, the QEMU introduction.
- **Minutes:** 280.

### 16. `csa.hw.cpu-architectures` (designer: [csa.hw.cpu-architectures.md](csa.hw.cpu-architectures.md))

- **Skills:** as designed (five). "What a vCPU is" belongs to topic 17's `vcpu-to-core`; this topic says it in one sentence because `price-performance` needs it.
- **Practice ladder:** as designed, with changes: `mcq-what-is-a-vcpu` moves to topic 17 (it duplicates `est-cores-three-rows`), and `mcq-which-generation` (the designer's review addition) takes its place; `arch-saving-percent` and the new `arch-pay-back` become `estimate` items with numbers of their own (keep `arch-fleet-month` as `predict_shell`); multiple choice written out (3.1). Google's N4A rows are used only if the series is generally available on the day (one line of Google's price page called it preview; the Arm page doesn't say); otherwise the Google rows are C4A and T2A. Leave the `t4g.small` free trial out of the lesson: it ends on 2026-12-31.
- **Proofs:** build `build-move-to-arm`, debug `debug-wont-start-on-arm` (prompt as in 3.2), explain: as designed. No checked `docker buildx` lab before Module 6.
- **Review pool:** the ten marked ● with the changes above; every skill keeps at least two.
- **Resources:** main Crash Course Computer Science #8, "Instructions & Programs" (re-opened 2026-11-11: CrashCourse, 10 min 36 s, embeddable), #7 (11 min 37 s, embeddable), the Graviton transition guide, Docker "Multi-platform builds", Red Hat's x86-64-v2 post, Google's Arm page, Azure's Cobalt page (re-opened: Neoverse N2, 3.4 GHz, guest list ends at Windows 11 Client), AWS's Graviton page (re-opened), the Graviton README table (re-opened: Graviton2 N1 without SVE, Graviton3 V1 with SVE, Graviton4 V2 with SVE2, Graviton5 V3), the OCI index spec.
- **Minutes:** 290.

### 17. `csa.hw.cores-memory` (designer: [csa.hw.cores-memory.md](csa.hw.cores-memory.md), sections 1 to 9 minus the disk material)

- **Skills:** `vcpu-to-core`, `burst-credits`, `stolen-or-capped`, `numa` as designed, and a new **`right-size`**: what a percentile is (the value a given share of samples falls below, read off a sorted list), sizing on the busy hours (the 95th percentile of CPU against a stated headroom, the peak of memory against a stated headroom), why the average undersizes and the maximum oversizes, then the cheapest size that fits, and when a burstable size fits (average per vCPU at or under its baseline, peaks short). Checkpoint 2 part 1 depends on it, and nothing else in the track teaches it.
- **Terms to add:** percentile, 95th percentile, headroom, region, on-demand price, "a month is 730 hours" (topics 19 and 22 depend on this topic, not on topic 16, for these). **Remove:** tenant, dedicated host, sole-tenant node (topic 15 teaches them).
- **Lesson plan:** the designer's sections 4.1 to 4.5, then right-sizing. Section 4.2 ("what a neighbour can and cannot take") is cut to what is new here: on a fixed-size instance `st` should sit near zero, so the witnesses of a neighbour are elsewhere. Topic 15 has already taught what is and isn't isolated.
- **Practice ladder:**
  1. `example-read-the-slice`, now a **systemd** lab: the designer's steps 1 to 8 of 7.1, then steps 6 to 8 of 7.5 (squeeze a cache with `MemoryHigh`, let it go, pin with `AllowedCPUs`), then save. Checks: `cores.txt`, `siblings.txt`, no `spin` left, `shop-cache` back at `MemoryHigh=infinity` with empty `AllowedCPUs`, and `~/example/squeeze.txt` holding the `high` count the learner read during the squeeze (a positive integer). Reading the live counter would fail after a restart (3.5).
  2. The recall of 7.2 (eight items), with `mcq-what-is-a-vcpu` from topic 16 added.
  3. **Right-size, new:** `metrics-p95` (`predict_shell`: twenty constructed CPU samples, `sort -n` and an `awk` nearest-rank line that prints the 19th of 20; the writer pins the output), `est-vcpus-busy-hours` (estimate, exact: a 95th percentile of 45% on 8 vCPUs, policy "no more than 60% of the new vCPUs at the 95th percentile", answer 6; mistakes 4 from the average and 12 from the peak), `est-memory-headroom` (estimate, ±0.1: peak 22 GiB, at most 80% used, answer 27.5; mistakes 22 and 17.6), `mcq-size-on-what` and `mcq-burstable-fits`. Numbers must differ from the checkpoint's five workloads.
  4. The credits block of 7.3 and `fill-credit-bucket`.
  5. The stolen-or-capped block of 7.4 and `write-steal-pct`.
- **Proofs:**
  - Build `build-capacity-review`, now a **plain** lab: the designer's keys for cores, NUMA, steal and credits, plus `size.web` (the cheapest size in a small dated table that meets a stated policy for a week of constructed metrics) and one recorded-format ticket, `ticket.cause`, `ticket.evidence`, `ticket.fix`, for a VM that is simply too small (`too-few-cpus`). The ticket gives the learner the checkpoint's cause and fix vocabulary once before the checkpoint uses it. Wrong fixes as designed plus `sized-on-average.sh` and `ticket-called-steal.sh`.
  - Debug `debug-crawling-db` (systemd): three faults, a `CPUQuota=` far below what `shop-db` needs (this replaces the disk fault, which moves to topic 18), `MemoryHigh=48M` under a 150 MB working set with `MemoryMax=256M` correct, and `AllowedCPUs=0` on the batch job's CPU. The prompt states an allowance ("up to one and a half CPUs' worth") so the quota fix has a ceiling. Checks: both running; the quota finite and inside the allowance; `nr_throttled` barely rising over 5 seconds; `MemoryMax` kept; the `high` count steady and swap not forbidden; a CPU of its own; the batch job still on CPU 0; **fixes last** (3.5). Wrong fixes: `quota-removed`, `still-throttled`, `memory-max-raised`, `swap-forbidden`, `still-on-cpu-0`, `batch-unpinned`, `runtime-only`. Confirm on CI that each fault alone turns only its own checks red, as the designer cautioned.
  - Explain: the designer's prompt without the local-disk clause, and with "how you would size it from a week of its numbers"; rubric rows `vcpu`, `credits`, `stolen-capped-busy`, `neighbours` (one sentence, as a review of topic 15), `clouds-differ`, a new required `right-size` row, and `numa` optional.
- **Review pool:** the designer's ladder and review-only items for the four skills, plus `est-vcpus-busy-hours`, `mcq-size-on-what` and a review-only `est-p95-rank` (which of 2,016 sorted samples is the 95th percentile: 1,916; mistakes 1,915 and 101).
- **Resources:** main resource **AWS, "Key concepts for burstable performance instances"** (re-opened 2026-11-11; it carries the credit table and formulas the biggest skill needs). The Nitro side-channels page, the designer's main resource, is topic 15's reading; here the lesson asks for two paragraphs of it again (pinned cores; burstable instances taking turns). For `right-size`: **AWS Compute Optimizer, "Rightsizing recommendation preferences"**, section "CPU and memory utilization" (opened 2026-11-11: defines a percentile, P90/P95/P99.5 thresholds and headroom; about 5 minutes; copyright AWS, linked). The rest as designed: CPU options, Azure B-series credit model, Google shared-core sections, Google CPU platforms, Azure mitigation guidance (the `lscpu` part), PSI, `proc_stat(5)`, the kernel's NUMA page, HBv3, the man pages.
- **Minutes:** 280.

### 18. `csa.hw.disks` (new; designer material: [csa.hw.cores-memory.md](csa.hw.cores-memory.md) sections 4.6, 5 facts 26 to 35 and 39, 6 resources 13 to 17, 7.5 steps 1 to 5, 7.6, and the disk keys of 8.1)

- **Title:** Memory tiers and disks. **Skills:** `storage-tiers` (cache, memory, local NVMe and network disks by rough speed, as orders of magnitude), `what-survives` (local ephemeral against network disks: reboot, stop, host failure, resize, on each cloud), `disk-caps` (IOPS × block size until the throughput cap; the smaller of the disk's and the VM's allowance; a deeper queue doesn't beat a cap).
- **Terms:** NVMe, local or ephemeral disk (instance store, temporary disk, Local SSD), network-attached disk (EBS, managed disk, Persistent Disk and Hyperdisk), provisioned IOPS, cache (L1 to L3) and the memory hierarchy, GiB against GB and MiB/s against MB/s, `io.max` and `IOWriteIOPSMax=`. IOPS, throughput, latency and queue depth are Module 1's (`csa.linux.storage` defines each); this topic adds the arithmetic.
- **Practice ladder:** `example-cap-a-disk` (systemd: 7.5 steps 1 to 5 and the save; checks a and d of 7.5); the six recall items of 7.6 plus `mcq-tiers-order` and `mcq-local-disk-three-clouds` moved into practice; **`fill-disk-cap`** (new fill-in: a drop-in for `shop-db` with gaps for the directive, the device and the value; checks read `systemctl show` and the live write rate; wrong fixes: the cap on reads, the wrong device, bytes where MiB were meant); **`write-io-rate`** (new write: `~/bin/io-rate UNIT SECONDS` prints writes a second, MiB a second and which cap binds, from two `io.stat` readings and `io.max`; checked against the check's own numbers on two live services).
- **Proofs:**
  - Build `build-disk-tier` (systemd): the designer's keys `disk-4k-iops`, `disk-1m-mib-per-s`, `disk-1m-binding` and the state check that `shop-db` runs under its tier's two write caps, plus `disk-for.orders`, `disk-for.sort-scratch`, `disk-for.cache` (`local` or `network`). Wrong fixes from 8.1: `cap-on-reads`, `stopped-the-db`, `iops-only`, plus `everything-local`.
  - Debug `debug-slow-nights` (systemd, new): the shop's database writes to `/dev/lab/data` (a network-style disk with a stated allowance) and a nightly sort uses scratch space meant for `/dev/lab/scratch` (a local disk, wiped at every stop). Symptoms: checkout is slow every night, and the orders taken on Saturday evening were missing after Sunday's maintenance stop. Three faults: the data disk's write cap at a twenty-fifth of its allowance; the sort's scratch directory on the data disk, so it spends the database's allowance; the order spool on the scratch disk. Checks: the allowance right and still applied; the sort's scratch path on the scratch disk's mount; the spool on the data disk; both services running; the database's write rate up. Wrong fixes: `cap-removed`, `scratch-still-on-data`, `spool-to-tmp` (a memory-backed folder, lost at reboot), `cap-on-reads`. Prove it under `labcheck test` before writing the lesson.
  - Explain: why the weekend's orders vanished and what a network disk would have cost in speed; IOPS × block size; which cap binds; one difference between the clouds (the designer's `disks` and `clouds-differ` rubric rows).
- **Review pool:** `est-iops-times-block`, `est-vm-or-disk-cap`, `io-stat-rate`, `mcq-queue-depth-at-a-cap`, `mcq-what-survives-a-stop`, `mcq-which-disk-for-what`, review-only `est-throughput-bound-iops`, `mcq-tiers-order`, and a new `est-lookup-time` (10,000 random reads one after another at 1 ms: 10 seconds; mistakes 0.01 and 1,000).
- **Resources:** main **Azure, "Virtual machine and disk performance"** (the two capping examples; 9 minutes), then AWS instance store lifetime, Azure's temporary disk section, Google's Local SSD persistence section, AWS gp3 (re-opened 2026-11-11: 3,000 IOPS and 125 MiB/s included, up to 80,000 and 2,000 MiB/s; the older 16,000 and 1,000 apply on Outposts only), Azure disk types (re-opened: Ultra to 400,000 IOPS, Premium SSD v2 baseline 3,000 IOPS and 125 MB/s free), Colin Scott's latency page (orders of magnitude only).
- **Minutes:** 205.

### 19. `csa.hw.gpus` (designer: [csa.hw.gpus.md](csa.hw.gpus.md))

- **Skills:** as designed (six). **Prerequisites:** `csa.hw.cores-memory`, `csa.hw.disks` (the disk-starvation material is topic 18's).
- **Practice ladder:** as designed (33 items). Changes: GPU tables use the two memory columns of 3.6, so the lab README no longer says "treat every figure as GiB"; fixtures are labelled constructed (3.4) until the capture run; the T4 stays as "the small, older card", dated.
- **Proofs:** build `build-gpu-plan` with two changes so it neither repeats practice nor sits on a knife edge: *chat* gets a model size no practice item uses (the writer picks it so that the no-headroom and decimal-GB wrong fixes still change the answer by more than 5%), and *tune* becomes 6 billion parameters at 16 bits, four times the weights: 44.7 GiB, so `NC24ads_A100_v4` (an 80 GB card, $3.673) is the only single card that fits and `g6e.xlarge` (44 GiB) narrowly doesn't. Drop the "cheaper by four hundredths of a cent" trap. Debug `debug-fit-check` and explain as designed.
- **Review pool:** as designed; replace `est-monthly-serving`'s $515.99 with an instance and hours the build doesn't use.
- **Resources:** as designed. Re-opened 2026-11-11: the NVIDIA blog (main), Hugging Face's LLM guide (the 4 × X and 2 × X rules, 15.2 GB at 8 bits and 9.5 GB at 4 bits), the `nvidia-smi` definitions of GPU-Util and memory utilisation, NVIDIA's time-slicing page, AWS's accelerated-computing table, Google's free-tier page ("GPUs and TPUs are not included"). Link the MIG guide's PDF or index, not a sub-page (they redirected on the 11th).
- **Minutes:** 290.

### 20. `csa.hw.windows-ad` (designer: [csa.hw.windows-ad.md](csa.hw.windows-ad.md), sections 2 to 11 and 16, the first half)

- **Title:** Active Directory: domains, names and tickets. **Skills:** `directory-structure` (now including domain-wide settings such as the password policy), `dc-discovery`, `kerberos-tickets`.
- **Terms to add:** DNS (the internet's system for turning names into addresses), name server and resolver, zone, record (A, SRV, PTR), conditional forwarder. Module 1 ran `dig` and read A and CNAME records but never used these words. Also standing up a domain: provisioning, the domain administrator, the password policy.
- **Practice ladder:**
  1. `example-meet-the-domain`: the designer's steps 1 to 7 of 9.1 (no join). Checks: `srv.txt` through the machine's own resolver; `tickets.txt` with `krbtgt/` and `ldap/dc1` lines.
  2. Recall: the `dir-*`, `dns-*` and `krb-*` rows of 9.2 (17 items, written out), plus `dir-password-settings` (`predict_shell` on the captured `samba-tool domain passwordsettings show` output in 16.5) and `mcq-password-policy`.
  3. **`fill-provision-dc`** (new fill-in, on the unprovisioned image of the prototype `build-stand-up-the-domain`): `~/bin/stand-up-dc` with gaps for the realm and short name, the DNS forwarder, enabling `dc1.service`, the reverse zone and its PTR record, and the password settings. Checks: the domain answers, forwards, resolves backwards, demands the stated password rules, and starts at boot. Wrong fixes: `not-enabled`, `no-forwarder`, `no-reverse-zone`, `default-password-rules`.
  4. **`write-domain-report`**: the designer's `fill-domain-report`, now from a blank file, with one change: the second line checks a service account's keytab (`svc-report`), because this topic's machine isn't joined.
- **Proofs:**
  - Build **`build-stand-up-dc`**: the prototype `build-stand-up-the-domain` without its join and logins: dc1 provisioned for `ad.shop.test` and forwarding, started at boot; an OU with two users and a group; the password rules; `lab` finding the domain and resolving dc1's address back to its name through its own resolver; a Kerberos-authenticated LDAP search by name working; dc1 still refusing passwords over plain LDAP. Its checks and `make_wrong.py` variants are reused; add `hosts-file.sh` (dc1 typed into `/etc/hosts`) and `forward-zone-only.sh`. The prototype's contract was never run (its log is empty): prove it first.
  - Debug **`debug-tickets-refused`** (new): the nightly directory report on `lab` signs in with `svc-report`'s keytab and lists each group's members over Kerberos-authenticated LDAP. Since Monday it prints nothing, and its log ends in Kerberos errors. Three faults, each with its own captured error (16.5): the site resolver forwards the forward zone but not the reverse one (`Server not found in Kerberos database`); `svc-report` was disabled on dc1 (`Client's credentials have been revoked`); the report's settings give the realm in lower case (`KDC reply did not match expectations`). Rules of the fix: don't change `svc-report`'s password or keytab, don't type dc1 into any file, leave dc1 as strict as it is. Checks: the report right for two groups (one the prompt doesn't name); reverse lookups through the machine's own resolver; `svc-report` enabled with its keytab still valid; plain-LDAP passwords still refused. Wrong fixes: `hosts-entry.sh`, `reverse-off.sh` (`ldapsearch -N`, which hides the missing zone), two of three fixed (three files).
  - Explain: the designer's prompt cut to this topic's half: what a domain holds, how a member finds a controller and proves who someone is, the two things outside the directory that this depends on (DNS and time), and when two domains need a trust. Rubric rows `what-the-domain-does` (the directory half), `finding-and-proving`, `trust`, `samba-limit` (not required).
- **Review pool:** `dir-dn-parts`, `mcq-trust-direction`, `mcq-ou-or-group`, `dns-srv-fields`, `mcq-wrong-resolver`, `krb-klist-lines`, `krb-ticket-hours`, `mcq-krb-by-address`; the rest can come back.
- **Resources:** main Microsoft Learn, "Introduction to AD DS" (re-opened 2026-11-11: 8 units, 60 minutes in all, marked Intermediate with Windows Server and networking as its prerequisites, so the lesson names units 2 to 5 to read and says what to skip), then R2, R3's first half (re-opened: the SRV lookup `_ldap._tcp.<domain>` and site detection from the client's subnet), R4, R8's first third, R5 and R15 to R16 optional.
- **Minutes:** 270.

### 21. `csa.hw.domain-join` (new id; designer material: [csa.hw.windows-ad.md](csa.hw.windows-ad.md), the join, Group Policy and Entra parts, sections 10, 12 and 13, and the built labs)

- **Title:** Joining machines, Group Policy and Entra ID. **Skills:** `domain-join`, `group-policy`, `entra-vs-adds`.
- **Practice ladder:** `example-join-and-log-in` (the designer's steps 8 to 10 of 9.1, plus `realm permit -g` and `samba-tool gpo list` for two people); the `join-*`, `gpo-*` and `entra-*` recall rows of 9.2 (13 items, written out); **`fill-join-script`** (new: `~/bin/join-this-server` with gaps for the join, home directories and the group permit; checks: joined, alice logs in, bob is refused, and running it twice is safe, Module 1's idempotence habit; wrong fixes: `permit-a-user`, `no-home-directories`, `everyone-permitted`); `write-policy-scope` as designed.
- **Proofs:** build `build-join-the-domain` and debug `debug-nobody-can-log-in`, both built and passing the real checker on 2026-11-11 (the designer's 16.3); add the missing `dc-weakened.sh` wrong fix. Explain: the designer's 10.3 prompt and rubric (`what-the-domain-does` for joined servers, `entra-differs`, `what-to-run`, `samba-limit`).
- **The Azure extra** (designer section 12) is linked from this topic's lesson, under a heading that says what it is: optional, about $0.60 and three hours, real Windows Server, not yet run by anyone. It is outside `practice`, `prove` and `review_pool` until the owner's first run (section 7). One change to its runbook: the Entra token step pipes the token straight into the decoder (`az account get-access-token --query accessToken -o tsv | cut -d. -f2 | base64 -d 2>/dev/null`) and never prints it, and says why (anyone holding it can act as you for about an hour). `unset PW` after the VMs are created.
- **Review pool:** `mcq-right-password-refused`, `mcq-machine-key-stale`, `gpo-who-gets-what`, `gpo-refresh-arithmetic`, `mcq-app-speaks-kerberos`, `mcq-which-join`.
- **Resources:** R6 (Ubuntu's SSSD guide: the critic could not reach `documentation.ubuntu.com` from this machine on 2026-11-11; the designer read it that day; open it again before linking), R7 (re-opened: refresh every 90 minutes plus up to 30; local, site, domain, OU; enforced beats block), R9, R10, R11, R12 to R14.
- **Minutes:** 235.

### 22. `csa.hw.windows-licensing` (designer: [csa.hw.windows-licensing.md](csa.hw.windows-licensing.md))

- **Skills:** as designed (six). **Prerequisites:** `csa.hw.hypervisors`, `csa.hw.cores-memory`.
- **Practice ladder:** as designed (the worked example, 26 quick items, `fill-licence-count`, `write-monthly-cost`), with every multiple-choice item rewritten (3.1: 10 of its 18 fail the item rule and the topic fails the 'longest in more than half' rule). Add one fact the critic read in AWS's licensing guidance on 2026-11-11: Windows Server brought to a Dedicated Host must be licensed on **all the host's physical cores**, not on vCPUs.
- **Proofs:** build `build-price-the-estate` with its six AWS servers moved off the practice item's numbers: an M6i Dedicated Host ($6.758, 32 `m6i.xlarge`) against licence-included `m6i.xlarge` ($0.376 with Windows), so the break-even is 18, not the 28 of `dh-break-even`. Debug `debug-the-quote` and explain as designed.
- **Review pool:** the 19 review-only items plus practice items 5, 10, 13 and 22, as designed.
- **Resources:** main John Savill, "An Overview of Azure Hybrid Benefit" (re-opened 2026-11-11: John Savill's Technical Training, 855 s, 2022-11-22, embeddable; its chapter list includes "8 core minimum per VM", which suggests the current rule). A writer watches it before it is `resources[0]`; if it states an older rule, Microsoft Learn's "Azure Hybrid Benefit for Windows Server" (re-opened: 8 core licences per VM, 180 days for Standard, Datacenter indefinitely by VM, unlimited VMs on a fully licensed dedicated host) becomes the main resource. The rest as designed; re-opened: AWS's licensing guidance, Google's "Microsoft licenses" page.
- **Minutes:** 285.

## 5. Checkpoint 2: the right machine (designer: [csa.m2.checkpoint.md](csa.m2.checkpoint.md); part 2 from [csa.hw.cores-memory.md](csa.hw.cores-memory.md), its last section; part 3 from the prototype in `proto-windows-ad/content/csa.m2.checkpoint/`)

**Prerequisites:** the eight topics. **`estimated_minutes`: 200.** **Objectives** name no cause of part 2 ("Find out why a VM is slow from the evidence it left, and choose the fix that fits each cause").

```yaml
prove:
  build: build-the-right-machine        # part 1
  debug: debug-slow-vms                 # part 2
  more:                                 # part 3, needs P5 (draft amendment to ADR-0012)
    - id: build-stand-up-the-domain
      versions: [build-stand-up-the-domain-clinic]
  explain: ...                          # opens after the part 1 build passes (ADR-0012, amended 2026-11-10)
unstuck:
  example: example-the-right-machine-clinic
  steps: [step-size-from-the-metrics, step-count-the-licence, step-arm-and-gpu, step-the-whole-sheet]
  versions: [build-the-right-machine-bakery, build-the-right-machine-print-shop]
```

### Part 1, build `build-the-right-machine` (plain lab, 60 minutes)

As designed (five workloads, a stated sizing policy, `metric-summary`, 14 checks, 11 wrong fixes), with these corrections, after which the designer's sizing prototype is run again to confirm the accepted sets and that the nearest wrong choice is still well outside 15%:

- **w2** changes to an Azure pair no practice item uses: today `D16s_v5` (16 vCPUs, 64 GiB) with Windows and SQL Server Standard; the 95th percentile and peak memory chosen so the answer is `E8s_v5` (8 vCPUs, 64 GiB), both rows already in the fixture.
- **w4** uses the corrected GPU memory column (3.6). With AWS's 22 GiB, `g6.xlarge` still fits a 19.4 GiB peak at 90%; recheck that it lands inside the 15% band and `g5.xlarge` outside.
- **w5**'s Azure answer is `B2ls_v2` (base 30%, $0.0416), not the retiring `B2s`.
- **`test_skills`** use the real ids: `w1-fits` `csa.hw.cores-memory/right-size` and `csa.hw.cpu-architectures/rebuild-inventory`; `w1-not-oversized`, `w3-not-oversized` `csa.hw.cores-memory/right-size`; `w2-fits` `csa.hw.cores-memory/right-size`; `w2-not-oversized` `csa.hw.windows-licensing/sql-editions`; `w3-fits` `csa.hw.cpu-architectures/price-performance` and `/rebuild-inventory`; `w4-fits` `csa.hw.gpus/vram-fit`; `w4-not-oversized` `csa.hw.gpus/gpu-instance-choice`; `w5-*` `csa.hw.cores-memory/burst-credits`; `estimates-right`, `saving-right` `csa.hw.windows-licensing/licence-included`.
- The README's policy uses "95th percentile", which topic 17's `right-size` now teaches.

Support steps (ADR-0012): the solved sibling, four fill-in steps and two fresh versions as designed.

### Part 2, debug `debug-slow-vms` (plain lab, 40 minutes, target stated not enforced)

The cores-memory designer's half A: four VMs' evidence as files (`ticket.txt`, `lscpu.txt`, `vmstat.txt` in Ubuntu 24.04's layout, `mpstat.txt`, two `/proc/stat` lines, `pressure/*`, the main service's cgroup files before and after, `dmesg.txt`), the same file list in every folder. Truths: steal from spent credits, the service's CPU quota, memory pressure, one thread at its limit. The learner writes `cause`, `evidence` and `fix` for each from the published lists, which are longer than the truths. Checks and `test_skills` as that brief's table: `csa.hw.cores-memory/stolen-or-capped` and `/burst-credits`, `csa.linux.cpu/throttling`, `csa.linux.memory/swap-paging`, `csa.linux.triage/first-minute`. Wrong answers as listed there.

Changes: vm-a's numbers move off the practice item (for example a 30% baseline and about 70% steal); the fixtures are labelled constructed; **half B, the live VM, is dropped**, because topic 17's debug already makes the learner fix a quota and a memory throttle by hand, and the checkpoint designer's alternative (a `vmstat` stand-in showing made-up steal in the learner's shell, and a `lab-instance` console) would put a model where the real tool belongs (3.4). A second debug waits until learners are seen to get stuck, as ADR-0012 says.

### Part 3, build `build-stand-up-the-domain` (systemd lab, 60 minutes; in `prove.more`)

The prototype as written: stand up `ad.shop.test` on an unconfigured dc1 (forwarder, started at boot), an OU with `dana` and `erin`, `linux-admins` with dana only, password rules (14 characters, lockout at 5), a GPO linked to the OU, `lab` finding the domain through its own resolver and joined, linux-admins able to log in over SSH into a home made on first login and nobody else, dc1 still strict. Every element is now practised first: provisioning, password rules and forwarding in topic 20, the join, permits and GPO links in topic 21. `test_skills`: `domain-answers`, `dc-forwards`, `finds-the-dc` `csa.hw.windows-ad/dc-discovery`; `people`, `password-rules` `csa.hw.windows-ad/directory-structure`; `policy-linked` `csa.hw.domain-join/group-policy`; `joined`, `dana-logs-in`, `erin-kept-out` `csa.hw.domain-join/domain-join`; `dc-still-strict` `csa.hw.windows-ad/kerberos-tickets`. Wrong fixes: the six of `make_wrong.py`. One fresh version, `-clinic`, in another story (other realm, people and group). Its contract has never been run: it is the first Samba lab to prove.

**Real Windows.** After the owner's first run of the Azure extra (section 7), and only then, the Azure build becomes a further fresh version of part 3 (`runtime: cloud`, P6), so a learner may prove part 3 either way.

### The explain

The checkpoint designer's prompt and rubric (the vCPU slice, four numbers for four causes, Arm, a GPU, what a domain controller is for and how Entra ID differs, Windows cost and owned licences), with the `directory` row worded from topic 21's `entra-differs`. 20 minutes.

### Time

Part 1 60, part 2 40, part 3 60, explain 20: 180 minutes of work, `estimated_minutes: 200`. Targets are stated in each prompt, as Checkpoint 1 now does ("the target is yours to hold yourself to"). No platform work measures them.

## 6. Platform work, in order

| # | What | Smallest version | ADR | Blocks |
| --- | --- | --- | --- | --- |
| P0 | Land the Module 1 hardening now on local branches | Merge `fix/labcheck-shell-and-restart` (shell command, start that keeps work, status and stop, weekly CI, ADR-0018 amendment), `fix/cloud-mcq-lengths-a` and `-b` (the length rules and baseline), the debug-prompt and Checkpoint 1 branches | Already drafted on the branch (ADR-0018 amendment, Proposed) | All Module 2 writing: its labs, prompts and choices are written against these |
| P1 | The `estimate` recall item | `tools/content_model.py` `EstimateItem` (`prompt`, `unit`, `answer`, `tolerance` with exactly one of `absolute` or `percent`, `given`, `working`, `mistakes` of at least one, `explanation`, `skills`, optional `prices_as_of` with `prices_source`); `validate_content.py` `check_estimate` (a small safe evaluator over `given`; `working` gives `answer`; every mistake's working gives its value and lies outside the tolerance; values distinct; every `given` number appears in the prompt; price fields when the prompt holds a currency amount); counts in `recall_count`, `review_kinds` and the review-pool "code or predict" rule; `web/src/content/answers.ts` `parseNumber` and `withinTolerance`; `EstimateQuestion.tsx`; one branch in `PracticeItem.tsx`; `isCodeOrPredict` in `reviews.ts`; one fake item; docs. No migration | [ADR-DRAFT-estimate-questions.md](ADR-DRAFT-estimate-questions.md) (ADR-0024) | Topics 16 to 22 and their review pools |
| P2 | A per-check time limit | Optional `timeout:` (seconds, 1 to 300, default 30) on a check in `checks.yaml`, read where `tools/labcheck.py` runs a check in `check` and `test`; the validator's schema; one sentence in `content/README.md` | [ADR-DRAFT-check-timeout.md](ADR-DRAFT-check-timeout.md) (amendment to ADR-0018) | Topic 15's write and debug labs |
| P3 | A CI spike | One early pull request with the first systemd lab of topic 17 and the first Samba lab of topic 20, to read the Labs job: `io.max` on a loop device, `MemoryHigh` with swap, `AllowedCPUs` and the cpuset, Samba provisioning (its ACLs and extended attributes). GitHub may now run a public repository's Linux jobs on AWS as well as Azure (changelog of 2026-10-28, re-read 2026-11-11), so look for both in the runner logs. Raise the shard count if needed | None | Topics 17, 18, 20, 21 and the checkpoint |
| P4 | Capture tooling | `tools/lab-capture` from the draft in `experiments/hv/` (read `journalctl -k -b` before `dmesg`; record each device's full `/sys` path; mask identifiers) and a manually started workflow that runs it on `ubuntu-latest` and `ubuntu-24.04-arm` and uploads the folders as an artifact. Free on the public repository | None (authoring tooling; record in the devlog) | Fixtures labelled captured in topics 15 and 16 |
| P5 | More than two parts in a checkpoint | `prove.more`: a list of `{id, versions}`, each a build or debug exercise with `test_skills`; the validator checks them; `progress.ts` counts the checkpoint passed only when every part (or one of its versions) has passed; the checkpoint page shows "Part 3" | [ADR-DRAFT-checkpoint-parts.md](ADR-DRAFT-checkpoint-parts.md) (amendment to ADR-0012) | Checkpoint 2 only (and Checkpoints 3, 5 and 7 later); not the topics |
| P6 | The cloud checker, smallest form | `tools/cloudcheck.py`: checks as `az ... -o json` commands with small Python predicates; `check` prints the result JSON the lab page accepts; `--record DIR` saves scrubbed answers; `test` replays them in CI; `runtime: cloud` exercises validated for structure | [ADR-DRAFT-cloud-checker.md](ADR-DRAFT-cloud-checker.md) (ADR-0025) | Only the optional Azure extra, after the owner's first run. **Not before writing starts** |

Decided against, so nobody builds them: an `advisory` time check (targets are stated, as in Checkpoint 1); support for two worked examples in one ladder (the splits removed the need); a host mode for a checked `docker buildx` lab (Module 6); a stand-in `vmstat` or console for steal (3.4).

## 7. Cost

### 7.1 The Azure Active Directory lab (the extra in topic 21)

Designed by the windows-ad designer (section 12 of that brief), unchanged except as noted in topic 21. Prices are pay-as-you-go list prices in **East US 2**, read from the public Azure Retail Prices API on 2026-11-11 by the designer and re-read by the critic the same day.

| Item | Choice | Per hour |
| --- | --- | --- |
| `dc1` | `Standard_B2s` with Windows Server | $0.0496 |
| `app1` | `Standard_B2s` with Windows Server | $0.0496 |
| `web1` | `Standard_B1s`, Ubuntu 24.04 | $0.0104 |
| NAT gateway | Standard, plus $0.045 per GB processed | $0.045 |
| The gateway's address | Standard static public IPv4 | $0.005 |
| Disks | three 32 GiB Standard SSD (E4, $2.40 a month each) and a small data disk; transactions $0.002 per 10,000 | about $0.011 |
| Access | Azure Bastion Developer: free, one connection at a time, portal only, in East US 2 (not in East US or West US 2) | $0 |
| **Total** | | **about $0.17** |

- **A three-hour sitting:** about $0.52, plus a few cents of NAT data: **about $0.60**, 0.4% of the $150 credit.
- **Forgotten for a day with the VMs running:** about $4.15.
- **Forgotten after auto-shutdown has deallocated the VMs:** the gateway, its address and the disks still bill, about $1.45 a day, **about $44 a month**. Running all month: about $126. Deleting the resource group is the only thing that ends the bill; auto-shutdown is a seat belt.
- **Guardrails, in this order, before anything bills:** a budget with an e-mail alert on the subscription (an alert, not a cap; Azure evaluates it once a day); one resource group; the tag `topic=csa.hw.domain-join` on everything; auto-shutdown on every VM; no public address on any VM and no inbound rule from the internet (Bastion Developer is the way in); teardown as the last check.
- **The size risk.** The designer found that the owner's subscription lists only the first-generation B sizes in East US 2. Those (Bv1) are End of Life with an announced retirement, and Microsoft says such series have "restrictions when you deploy through new subscriptions". On the day of the run, `az vm list-skus -l eastus2 --size Standard_B` again. If Bv1 can't be deployed and Bsv2 isn't offered, the fallback is two `Standard_D2as_v5` with Windows ($0.178 each) and one `Standard_D2as_v5` Linux ($0.086): **about $0.50 an hour, $1.50 a sitting, $12 a day if forgotten running**.
- **What stays unproven until the owner runs it once:** every command in the runbook working together; `B2s` promoting a forest comfortably and how long it takes; the "smalldisk" image's real size; Bastion Developer reaching VMs behind a security group with only the default rules; Run Command returning output through the NAT gateway; the budget command's syntax (preview) and whether deleting the group removes the budget; Ubuntu's join against a real Windows Server controller; each check's output fitting Run Command's 4,096 bytes; the real cost.

### 7.2 Optional authors' capture runs (all need the owner)

| Run | Where | Cost | What it buys |
| --- | --- | --- | --- |
| `lab-capture` on a free-tier `e2-micro` | Google Cloud (us-central1, us-west1 or us-east1), deleted afterwards | free tier (one e2-micro a month and 30 GB-months of standard disk, read 2026-11-11); check on the day whether the VM's external IPv4 address is charged | a captured Google guest for topic 15 |
| Accelerated Networking on, then off | Azure, one `D2s_v5` for about 30 minutes | about $0.05 | captured Azure guests with and without a virtual function |
| CPU topology and a drained burstable VM | Azure: `D2s_v5`, `D2ps_v6`, `D2as_v5` for 15 minutes; `B2ts_v2` flat out for 90 minutes | under $0.25 | genuine topic 17 fixtures; whether an Azure guest shows steal when its credits are gone (nobody knows) |
| `nvidia-smi` under four conditions | Azure `NC4as_T4_v3` for an hour | about $0.55 (about $0.20 on Spot); may need a GPU quota request | genuine topic 19 fixtures and the three formats nobody could confirm |

None blocks `ready`. Together with one sitting of the AD lab: about $1.45 of the credit.

## 8. Decided for the owner, and for the owner queue

**Decided under the owner's rule** (each goes under _Decided for you_ in `docs/owner-queue.md`, overturnable in a line):

1. Split topic 17 into `csa.hw.cores-memory` and `csa.hw.disks`, and topic 19 into `csa.hw.windows-ad` and `csa.hw.domain-join`. Better learning and retention: shorter topics reach proofs and first reviews sooner, and every skill is proven where it was practised. Cost: four more proofs to write; free.
2. Module 2's topics keep `csa.m1.checkpoint` as their gate (the v1 spec's F10).
3. Add the `estimate` question type before writing (draft ADR-0024): producing a number is remembered better than picking one, it is quick enough for spaced review, and it needs no Python before Module 6.
4. Add `prove.more` so Checkpoint 2 has all three parts (draft amendment to ADR-0012).
5. Checkpoint 2 part 3 is the local Samba domain; the Azure build becomes an optional fresh version after the owner's first run.
6. Checkpoint 2 part 2 is recorded evidence only; no stand-in tools in the learner's shell.
7. Right-sizing is taught in topic 17 (new skill `right-size`), because the checkpoint needs it and nothing taught it.
8. Time targets are stated and self-timed, not measured or enforced.
9. GPU tables carry each provider's stated memory and a converted GiB column; calculations use the second.
10. The laptop capture is published with its CPU model masked.
11. The spec's "Arm saves 20–40%" becomes "what Arm saves, from price lists".

**For the owner queue's _Open_ list,** as one item (it involves money and the owner's accounts):

> **Module 2's runs in your clouds (optional, about $1.45 in all).** Module 2 is complete without them. (a) First, a budget alert on your Azure subscription (free; the exact steps are in the runbook). (b) One sitting of the Active Directory lab: about $0.60 and three hours, real Windows Server, guardrails first, everything deleted at the end; your run records the answers the checker's tests replay, and lets the lab count as a proof. (c) Optional capture runs for more genuine examples: Google `e2-micro` (free tier), Azure about $0.85. Recommendation: (a) and (b) when you have an evening; (c) only if you'd like the examples to be real. Holds up: only the Azure lab's place in the proofs.

## 9. Look up again on the day of writing

- **Every price** a question or lab uses, against a new fixture file if anything moved (a fixture is never edited once committed). The 2026-11 fixture's corrections in 3.6 come first.
- **Azure sizes for the lab:** `az vm list-skus -l eastus2 --size Standard_B` (Bv1's retirement date; whether Bsv2 is offered to this subscription); `az vm image list-skus` for the Windows Server image names; Bastion Developer's regions; the default-outbound-access rule.
- **Arm:** Google N4A's status; Azure `D*ps_v7` (Cobalt 200) documentation; Windows Server on Arm on any cloud; the Graviton README's Graviton5 row.
- **Licensing:** the Product Terms entries for Windows Server, SQL Server and Microsoft Azure; AWS's Windows FAQ lines on 2022 and 2025 BYOL; Microsoft's Listed Providers document (a .docx; Microsoft names four including itself, AWS's guide names three: use Microsoft's); SQL Server 2025's limits. Teach the rules "as the Product Terms stand in November 2026".
- **GitHub runners:** whether this repository's jobs land on AWS, and whether systemd labs behave the same there (P3).
- **Resources not fully read:** the Savill video and the Crash Course videos (watch once); Microsoft Learn's AD DS module units; Ubuntu's SSSD guide (unreachable from here on 2026-11-11); the QEMU documentation's and OCI specification's licences; the MIG guide's web pages (linked through the PDF or index until they stop redirecting); AWS re:Post's steal article (HTTP 403: cite nothing from it).
- **What nobody has seen:** what an Azure B-series guest shows when its credits are gone; `nvidia-smi`'s CSV header, a T4's or L4's MiB total and an application's GPU out-of-memory line; what `systemd-detect-virt` prints on a cloud bare-metal instance; `Exec format error` and its exit status on a machine without an emulator (a CI runner).
- **Dates that will pass:** AWS's `t4g.small` trial (2026-12-31) is left out; Google's T4 "approaching end of support" note.

## 10. Replacement text for the spec

All in `docs/specs/cloud-solutions-architect.md`. After the change, run `python -m uv run python tools/outline_cloud_track.py` to create the outlines for `csa.hw.disks` and `csa.hw.domain-join` (it never touches a topic being written).

**10.1 The Module 2 section** (from `### Module 2: Virtualization, hardware and Windows` to the line before `### Module 3: Networking`) becomes:

```markdown
### Module 2: Virtualization, hardware and Windows

Every cloud instance is a slice of a physical machine. Knowing what the slice is made of explains prices, performance surprises and a whole class of outages. Windows is here because most enterprise estates have it.

| #   | Topic                                        | ID                         | You'll be able to…                                                                                                                                                                       |
| --- | -------------------------------------------- | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 15  | Hypervisors                                  | `csa.hw.hypervisors`       | tell type 1 from type 2 hypervisors; explain KVM/QEMU, Hyper-V and AWS Nitro, paravirtualization and SR-IOV; read from inside a guest what it runs on; say what a hypervisor can and can't isolate |
| 16  | CPU architectures                            | `csa.hw.cpu-architectures` | compare x86 and Arm (Graviton, Ampere, Cobalt, Axion); explain instruction sets; say what Arm saves, from price lists, and what has to be rebuilt to get it                                |
| 17  | Cores, memory and noisy neighbours           | `csa.hw.cores-memory`      | explain vCPU versus physical core, hyperthreading, NUMA, burstable credits and noisy neighbours; tell CPU the host withheld from a limit of the machine's own; size a machine from a week of its metrics |
| 18  | Memory tiers and disks                       | `csa.hw.disks`             | place cache, memory, local NVMe and network disks by speed; choose between local ephemeral and network-attached disks; work out what a disk and a VM together will deliver              |
| 19  | GPU basics                                   | `csa.hw.gpus`              | explain CUDA cores versus tensor cores, VRAM as the constraint, NVLink and MIG partitioning; read a GPU's utilization and say what's starving it                                         |
| 20  | Active Directory: domains, names and tickets | `csa.hw.windows-ad`        | explain Active Directory Domain Services, how members find it through DNS and prove identity with Kerberos, and domain trusts; stand up a domain controller                             |
| 21  | Joining machines, Group Policy and Entra ID  | `csa.hw.domain-join`       | join a server to a domain and control who may log in; predict which Group Policy objects apply; say how Entra ID differs from AD DS                                                     |
| 22  | Windows licensing in the cloud               | `csa.hw.windows-licensing` | price a Windows and SQL Server estate with bring-your-own licences, hybrid benefit and dedicated hosts; say when a dedicated host is cheaper                                             |

**Checkpoint 2: the right machine** (`csa.m2.checkpoint`).

1. Right-size five described workloads across the three clouds to a stated sizing policy, including a move to Arm and a GPU job. Code checks each choice and its monthly cost within 15%.
2. Diagnose four slow VMs from the evidence each one left, and choose the fix that fits each cause.
3. Stand up a small Active Directory domain and join a Linux server to it so that only one group may log in, and explain how Entra ID would differ. An optional Azure version joins a Windows and a Linux VM to a Windows Server domain controller.
```

Keep the table's column padding as the rest of the file has it (the rows above are padded by hand; re-pad if a formatter disagrees).

**10.2 Renumber every later topic.** Two rows were added, so every topic row after Module 2's table moves up by two (Module 3's first topic, now 21, becomes 23, and so on to the end). From the repository root, in Git Bash:

```bash
awk '/^### Module 3:/ {s = 2} s && /^\| [0-9]+ +\|/ {match($0, /[0-9]+/); n = substr($0, RSTART, RLENGTH) + s; w = RLENGTH; $0 = substr($0, 1, RSTART - 1) sprintf("%-" w "d", n) substr($0, RSTART + RLENGTH)} {print}' docs/specs/cloud-solutions-architect.md > /tmp/spec.md && mv /tmp/spec.md docs/specs/cloud-solutions-architect.md
```

Then check one table by eye: a two-digit number that becomes three digits needs one more space of padding in that column.

**10.3 Stage 1's opening paragraph.** Replace "The exception is Module 2's Windows Server and Active Directory labs, which need Windows machines in a real cloud and can be Azure labs ([Lab safety and cost](#lab-safety-and-cost))." with:

> Module 2 is proven locally too: its Active Directory topics use a Samba domain controller in the lab's container, and an optional Azure lab, priced inside the owner's credit, adds real Windows Server ([Lab safety and cost](#lab-safety-and-cost)).

**10.4 "How competency is proven", the "Survives spaced review" row, last cell.** Replace "Drills run as Python in the browser, code katas are tested offline, and the checker covers rebuilds." with:

> Quick drills are estimate questions, a typed number checked within a tolerance, in the browser; drills written as code run as Python in the browser from Module 6. Code katas are tested offline, and the checker covers rebuilds.

(The drills table's Subnetting row says "The browser (Python)" for a Module 3 drill; Module 3's designers should settle it the same way.)

**10.5 The drills table's Right-sizing row,** last cell, from "Within one size" to:

> Within one size for quick drills; a proof states its sizing policy and accepts anything within 15% of the cheapest size that meets it

**10.6 "Lab safety and cost", the "Guardrails first" bullet.** Replace "A lab that reaches a cloud before Module 8, as Module 2's Azure labs do, sets a budget alert on that cloud first." with:

> A lab that reaches a cloud before Module 8, as Module 2's optional Azure lab does, sets a budget alert on that cloud first.
