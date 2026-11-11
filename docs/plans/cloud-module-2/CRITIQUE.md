# Critique of the Module 2 design briefs

Every problem the critic found in the four designers' briefs (and the context that changed since), and what was done about it. Written 2026-11-11. The decisions themselves are in [MODULE-2-BRIEF.md](MODULE-2-BRIEF.md); section numbers below point there.

Read: the workflow's rules (COMMON and the four PARTS), all seven briefs, the estimate note, the price fixture (md and csv), the prototypes in `proto-windows-ad/` (both built labs, the unrun checkpoint lab, the extras, the logs) and the experiments' capture files; on `main`, `docs/owner-queue.md`, ADR-0012, ADR-0014 with its amendment, the spec's Stage 1, Module 1 and 2 sections, "How competency is proven", "Drills", "Lab safety and cost", "One topic in full" and "Before authoring", `content/README.md`'s lab rules, the content model and the checkpoint validator; on the local hardening branches, the multiple-choice length rules, the new `labcheck` (shell, start that keeps work, weekly CI, the ADR-0018 amendment), and Checkpoint 1's and the storage debug's rewritten prompts. No lab was run; Docker was not touched.

## 1. Verification record

### 1.1 Facts re-fetched from their cited sources (2026-11-11)

| Brief | Facts re-checked | Result |
| --- | --- | --- |
| Hypervisors | 12 (AWS nested virtualization on virtual M7i, M8i, C8i, R8i and the rest; KVM and Hyper-V inner; no charge), 15 (Accelerated Networking: 2+ vCPUs, 4+ where hyperthreaded; not on a running VM; ConnectX and MANA), 19 (Azure VMs paused up to 30 s), 23 (live migration "typically much less than 1 second", clock jump up to 5 s, GPU and bare-metal VMs stopped), 33 (`clock_name` reads `hyperv`; `hv_utils`, `hv_vmbus`), 35 (Red Hat: KVM type 1, in Linux since 2007), 14 (Hyper-V root and child partitions, VMBus, enlightened I/O), 37 (GitHub multi-cloud runners, 2026-10-28) | All supported. Fact 37 adds a risk the brief didn't draw: CI's systemd labs may now run on AWS-hosted runners too (problem 31). |
| CPU architectures | 1 (Graviton table: N1 without SVE, V1 with SVE, V2 with SVE2, V3), 5 and 7 (Graviton page: "up to 20% less", "up to 60% less energy", `t4g.small` 750 hours a month to 2026-12-31), 8 (Cobalt 100: Neoverse N2, 3.4 GHz, a physical core per vCPU, Windows 11 Client the only Windows), 10 and 21 (C4A on V2 and T2A on Altra without SMT; N4A on N3), 19 (Azure name letters `a`, `p`, `s`, `d`, `l`, `t`); prices `D2ps_v6` $0.0702, `n4-standard-2` $0.0907, `c4a-standard-2` $0.0898, `e2-standard-2` $0.06701, `n4a-standard-2` $0.077 | All supported. Google's Arm page doesn't say whether N4A is generally available (problem 28). |
| Cores, memory | 11 to 13 (credit definition; t3.micro 12/288, t3.large 36/864; T8i exists; unlimited by default on T8i, T4g, T3a, T3; 7-day persistence; the T2/T4g vCPU note), 15 (break-even 42.5% with $0.0835 and $0.096; "about 1.5 times an M5"), 18 (Bsv2: B2ts_v2 20%/60/24/576, B2ls_v2 30%/60/36/864, B2s_v2 40%/60/48/1,152; 3,750 IOPS and 85 MBps; no local disk), 28 (gp3 3,000 IOPS and 125 MiB/s, to 80,000 and 2,000; 16,000 and 1,000 only on Outposts), 31 (Ultra 400,000 IOPS; Premium SSD v2 3,000 IOPS and 125 MB/s free; P10 500, P30 5,000), 10 (via the main resource: pinned cores, no simultaneous SMT sharing, LLC sharing, burstable sequential sharing, NUMA exposed) | All supported. |
| GPUs | 1 (NVIDIA blog), 5 (Hugging Face: 4 × X and 2 × X GB; Llama-2-70b 140 GB; 15.2 GB at 8 bits and 9.5 GB at 4 bits), 7 (GPU-Util and memory utilisation definitions, 1 s to 1/6 s), 14 (time-slicing: no memory or fault isolation), 16 (AWS table: g4dn 16 GiB, g5 and g6 22 GiB, g6e L40S 44 GiB, g6f 0.125 L4 2.79 GiB), 21 (no GPUs in Google's free tier or free trial); prices `g2-standard-4` $0.706832, `a2-highgpu-1g` $3.673385, `NC24ads_A100_v4` $3.673 | All supported. Fact 16 confirms the fixture's AWS "24 GB" is wrong (problem 18), and confirms `g6e`'s card, which the fixture had left out as unconfirmed. |
| Windows and AD | F4 (DC locator: `_ldap._tcp.<domain>`, site from subnet), F6 (Group Policy: 90 minutes plus up to 30; order; enforced and block), F10 (Entra Domain Services Standard $0.15 an hour, East US 2), F13 (only paid customers can create another workforce tenant), A1 to A3 (Bastion Developer free, no subnet or public IP, one VM at a time, East US 2 yes, East US and West US 2 no; Basic $0.19, Standard $0.29, Premium $0.45), A6 (Run Command: 4,096 bytes, about 20 s, one at a time, 90 minutes, outbound needed, VM Contributor), A7 (new VNets private by default for API versions after 2026-03-31); prices B2s Windows $0.0496, B2s Linux $0.0416, B1s $0.0104, NAT gateway $0.045 an hour and $0.045 a GB, static IPv4 $0.005, E4 $2.40 a month | All supported. A side-read found Bv1 (B1s, B2s, B2ms) is End of Life (problem 19). |
| Licensing | 7 to 11 (AHB: Software Assurance or subscription; Linux rate; 8 core licences per VM with the 4-core example; 180 days for Standard, Datacenter indefinitely by VM; unlimited VMs on a fully licensed dedicated host; Product Terms take precedence), 16 (SQL Server 2025: Standard "lesser of 4 sockets or 32 cores", 24 in 2022; Express 4 cores, 1,410 MB, 50 GB; two Developer editions; no Web edition), 19 (Listed Providers: the October 2019 rule; the list itself is in a .docx), 21 (AWS: License Mobility on shared tenancy, SQL Server 4 vCPUs minimum, Windows Server without License Mobility, the four conditions), 22 (AWS FAQ: Windows Server 2022 and 2025 not eligible for BYOL; SQL Server without SA on hosts "2017 or earlier"), 24 (Optimize CPUs rates $0.046, $0.166, $0.421, $0.063), 26 (Google: $0.046 per visible vCPU, $0.023 on f1-micro and g1-small; SQL $0.399, $0.1200, $0.011; four-core minimum), 27 (Google: Windows typically not eligible for License Mobility; the 2019 conditions; 90 days), 28 (sole-tenant premium 10%) | All supported. AWS's guidance also says Windows Server brought to a Dedicated Host must be licensed on all the host's physical cores; added to topic 22. |
| Checkpoint and fixture | Prices `D8s_v5` $0.384 and $0.752, `E4s_v5` $0.252 and $0.436, `n4-standard-4` $0.1814, `g2-standard-4`, `NC24ads_A100_v4`, B2s, Bsv2 (`B2ls_v2` $0.0416), fallbacks `D2as_v5` $0.086 and $0.178, `D2s_v5` $0.096 and $0.188, `B2ms` $0.0832 and $0.0912 | All supported, except the fixture's AWS GPU memory (problem 18). |

No sampled fact was contradicted by its source.

### 1.2 Resources re-opened (2026-11-11)

| Topic | Re-opened | Result |
| --- | --- | --- |
| 15 | Gregg's Nitro post (main), Red Hat "What is a hypervisor?", Hyper-V architecture, Google live migration | All exist and are free. Gregg's post is about 2,200 words, not 1,900. |
| 16 | Crash Course #8 (main) and #7, Cobalt overview, Graviton page, Graviton README | All exist; the videos are CrashCourse, 10:36 and 11:37, embeddable. |
| 17/18 | AWS side-channels whitepaper, AWS burstable concepts, AWS gp3, Azure disk types; and, new, AWS Compute Optimizer's rightsizing preferences (for the new `right-size` skill) | All exist. |
| 19 | NVIDIA blog (main), Hugging Face LLM guide, `nvidia-smi` documentation, NVIDIA time-slicing | All exist. |
| 20/21 | Microsoft Learn "Introduction to AD DS" (main), DC locator, Group Policy processing; Ubuntu's SSSD guide | The first three exist (the module is marked Intermediate and lists Windows Server and networking as prerequisites). **Ubuntu's guide could not be reached from this machine** (DNS failure); the designer read it the same day. Re-open before linking. |
| 22 | Savill's video (main), AWS licensing guidance, Google "Microsoft licenses" | All exist; the video is John Savill's Technical Training, 855 s, 2022-11-22, embeddable. Not watched. |

### 1.3 Prerequisite claims checked against the Module 1 lessons

Searched all fourteen Module 1 lessons. Confirmed as taught: steal (`st`) and "hypervisor" and "VM" in a clause (`csa.linux.cpu`); `nproc`, `systemd-run -p`, `systemctl show -p`, `cpu.stat` and `nr_throttled` (cpu); RSS, exit status 137 as 128 + 9, `memory.events`, `memory.max`, `vmstat` `si`/`so`, cgroup, pod (memory); namespaces, layers, tags and reading a Dockerfile, "not a VM" (containers); firmware, bootloader, kernel, initramfs, `dmesg`, serial console (boot); `/dev/nvme0n1` names, IOPS, throughput, latency, queue depth, per-volume and per-instance limits in one sentence (storage); `dig`, `nc`, veth pair, the office namespace (net-tools); `AllowGroups`, `sshd -T` (hardening); the USE method, `mpstat -P ALL`, `iostat -xz` (triage). Skill ids named in `test_skills` all exist (`csa.linux.shell/sed-awk`, `/navigate`, `/count-and-sort`; `csa.linux.scripting/quoting-vars`; `csa.linux.cpu/throttling`, `/cgroups-v2`; `csa.linux.memory/swap-paging`, `/container-memory`; `csa.linux.triage/first-minute`; `csa.linux.services/systemctl`).

Not taught anywhere in Module 1, though briefs leaned on them: the words **vCPU**, **DNS**, **resolver**, **zone**, **percentile**, **architecture**, **compile** and **binary**. The hypervisors and CPU-architectures briefs already list their own; the gaps are problems 2 and 12.

## 2. Problems found, and what was done

### Against the rules and the platform

| # | Problem | What was done |
| --- | --- | --- |
| 1 | The hypervisors and windows-ad briefs drop `csa.m1.checkpoint` from `prerequisites:`; the v1 spec's F10 says "the next module's topics depend on" a checkpoint. The cores-memory brief keeps it. | The gate stays on every Module 2 topic that has no Module 2 prerequisite; Module 1 topics are listed for writers only (MODULE-2-BRIEF §2). |
| 2 | Checkpoint part 1's policy uses the 95th percentile and a sizing method from a week of metrics; the checkpoint brief **assumed** topic 17 taught them, and it doesn't, nor does Module 1. Used before taught. | New skill `right-size` in topic 17, with items, a build key and a verified resource (AWS Compute Optimizer's preferences page) (§4.17). |
| 3 | Checkpoint part 3's local lab asks the learner to provision a domain controller and set the domain's password policy; topic 19's labs all start with dc1 provisioned, and password settings appear only as captured output. Used before taught. | Topic 20 gains `fill-provision-dc` and a password-settings item, and its build is the stand-up lab without the join (§4.20). |
| 4 | The briefs specify the number-with-tolerance type twice, differently (`numeric` in the hypervisors brief; `estimate` with working and mistakes in the licensing note). | One design, `estimate`, smaller than the note's (no `factor` yet); drafted as ADR-0024 (ADR-DRAFT-estimate-questions.md). |
| 5 | The licensing brief's own multiple-choice items fail the new length rules: right answer longest in 14 of 18 (topic rule) and over 1.5 times the longest wrong choice in 10 (item rule), though the brief states the rule. The hypervisors, CPU-architectures and windows-ad briefs give wrong answers as short fragments, which would fail too. The cores-memory and GPU briefs pass. | Rule 3.1: every choice written out in full before anything else; the two passing briefs are the model. |
| 6 | Topic 17's worked example checks a live `memory.events high` count; since `start` keeps a lab across restarts, a restart resets the counter and a learner who did the work fails. A lab that only works when run straight through. | The step saves the count to a file the check reads; a restart trial is required for every lab (3.5). |
| 7 | Topic 17's debug accepts `systemctl set-property --runtime` fixes, which vanish at reboot. | A "fixes last" check and `wrong/runtime-only.sh` (3.5, §4.17). |
| 8 | Topic 15's write and debug checks read a log the learner's own run left; in the debug, a proof, a hand-written log passes. | Per-check `timeout:` (P2, ADR-DRAFT-check-timeout.md) so the checks boot the learner's launcher themselves. |
| 9 | Checkpoint part 2 as the checkpoint designer drew it puts a `vmstat` stand-in showing made-up steal, and a `lab-instance` console, in the learner's shell. That passes a model off as the tool (ADR-0017's principle; the GPU brief's own rule), unlike Module 1's stand-in, which only feeds a check. | Part 2 is the cores-memory designer's four recorded tickets, as files that say what they are; the live half is dropped (§5). |
| 10 | Fixtures: the hypervisors brief's honesty rule ("captured, not typed") against the cores-memory and GPU briefs' invented numbers in real formats, called "representative". | Two labels, captured and constructed, never mixed (3.4). |
| 11 | The Entra comparison step prints a bearer access token to the terminal before decoding it. Teaching a beginner to display a credential. | The token is piped straight into the decoder and never shown; the runbook says why; `unset PW` after use (§4.21). |
| 12 | Terms assumed but never taught: DNS, resolver, zone (topic 19; Module 1 never uses the words); region and on-demand price (topics 19 and 22, which don't require topic 16, where they are defined). | Added to topic 20's and topic 17's term lists (§4.17, §4.20). |
| 13 | The owner's laptop capture, with its CPU model, would go into a public repository. Making something public is on CLAUDE.md's "ask before" list. | Published with the model name masked; overturnable (3.4, §8). |
| 14 | The debug prompt of topic 16 says where the faults are ("in how the release is built"). | Reworded to "three faults" (3.2). |
| 15 | Topic 21's built debug says "nothing about dc1 typed into a hosts file or a Kerberos config", which hints at the DNS fault. | Kept, framed as a rule of the fix, as Checkpoint 1's rewritten prompt frames its rules (3.2). |

### Between the briefs

| # | Problem | What was done |
| --- | --- | --- |
| 16 | Topics 17 (330 minutes) and 19 (360) are far longer than the rest; both designers recommended splitting, with seams drawn. Topic 17 also needed two worked examples in one ladder, which no topic has done. | Split into `csa.hw.cores-memory` and `csa.hw.disks`, and `csa.hw.windows-ad` and `csa.hw.domain-join`, with new fill-ins and proofs where a half lacked them; one worked example each (§4, §10). |
| 17 | The same concept taught twice: what a neighbour can and can't take from a VM, in topic 15's `isolation-limits` and topic 17's section 4.2, both with the AWS side-channels page as reading (it is topic 17's main resource). | Topic 15 owns isolation and dedicated tenancy; topic 17 owns measuring it; topic 17's main resource becomes AWS's burstable concepts page, and it rereads two paragraphs (§4.15, §4.17). |
| 18 | "A vCPU is a thread on x86, a core on Arm" is a skill in both topic 16 (`arm-families`, `mcq-what-is-a-vcpu`) and topic 17 (`vcpu-to-core`). Dedicated host and tenant defined in both 15 and 17. | Topic 17 owns vCPUs (the item moves there); topic 15 owns tenancy terms (§4.16, §4.17). |
| 19 | Checkpoint part 2: the checkpoint designer assumed a live lab with steal stand-ins built in topic 17; the cores-memory designer built recorded tickets and an optional live half. | Recorded tickets only (problem 9). |
| 20 | Checkpoint part 3: the checkpoint designer assumed topic 19's build was a required Azure lab that teaches the guardrails first, and priced a different design (B2ms, 128 GiB disks, a public IP, $0.78 a sitting, $189 a month if left). The windows-ad designer made Azure an optional extra (B2s smalldisk, NAT gateway, Bastion Developer, no public address, $0.60). The checkpoint's public IP contradicts "no public RDP". | Part 3 is the local Samba stand-up lab, in `prove.more`; the windows-ad Azure design is the only one; it becomes a fresh version of part 3 after the owner's run (§5, §7). |
| 21 | The windows-ad brief points to `csa.m2.checkpoint.part3.md`, which was never written (its designer stopped), and the checkpoint stand-up prototype's contract was never run (its log is empty). | Marked unproven; it is the first Samba lab to prove under `labcheck test` (§5). |
| 22 | The checkpoint brief's `test_skills` use placeholder ids (`vcpu-vs-core`, `right-size`, `noisy-neighbours`, `memory-pressure`, `arm-savings`, `rebuild-for-arm`, `read-gpu-utilisation`, `domain-basics`, `kerberos`, `what-is-isolated`). | Mapped to real ids for all three parts (§5). |
| 23 | Prerequisites disagree: cores-memory says `[m1.checkpoint, hypervisors]`; hypervisors says drop the checkpoint; GPU says `[cores-memory]` though its disk-starvation material moves to the new disks topic. | One table (§2). |
| 24 | The time targets: the checkpoint designer proposed `advisory: true` checks; Checkpoint 1's rewrite simply states its 45 minutes for the learner to time themselves. | State the targets the same way; no platform work (§5, §6). |

### Numbers, prices and facts

| # | Problem | What was done |
| --- | --- | --- |
| 25 | Proofs reuse practice numbers, so they can be passed from memory: the licensing build's break-even (28, same host and instance as `dh-break-even`); the GPU build's chat model (13.0 GiB and $515.99, in three practice items); checkpoint w2 (`D8s_v5` to `E4s_v5`, which is `sql-size-by-memory`); checkpoint vm-a (80% steal on a 20% baseline, which is `steal-from-proc-stat`). | Each changed (licensing: M6i host, break-even 18; GPU: new chat size; w2: `D16s_v5` to `E8s_v5`; vm-a: new numbers), and a rule that proofs never reuse practice numbers (3.3). |
| 26 | The GPU build's *tune* answer rests on a $0.000385 price difference, and under GiB conversion its 5 billion × 2 × 4 bytes equals an A100 40 GB card exactly. | *tune* becomes 6 billion parameters (44.7 GiB): one card fits, `g6e` narrowly doesn't, and the price trap goes (§4.19). |
| 27 | The price fixture lists AWS's A10G and L4 as 24 GB, from marketing pages; AWS's specification table says 22 GiB (re-read). The GPU brief's fix ("treat every figure as GiB") asks the learner to pretend. | The fixture is corrected before it is committed; every GPU row carries the stated figure and a converted GiB column, and calculations use the second (3.6). |
| 28 | Google's N4A is used in the CPU-architectures comparison but left out of the fixture as possibly preview; Google's Arm page doesn't say. | Used only if generally available on the day (§4.16, §9). |
| 29 | Azure's B-series v1 (B1s, B2s, B2ms) is End of Life with an announced retirement and deployment restrictions on new subscriptions (Microsoft's lifecycle list, read 2026-11-11). The Azure lab's three VMs and checkpoint w5 use it, and the designer found the owner's subscription offers no Bsv2. | w5 uses `B2ls_v2` (same price); the Azure lab checks sizes on the day, with a priced D-series fallback (about $1.50 a sitting) (3.6, §7.1). |
| 30 | AWS's `t4g.small` free trial ends 2026-12-31; a lesson saying so goes stale within weeks. | Left out (§4.16). |
| 31 | GitHub may now run a public repository's Linux jobs on AWS as well as Azure (changelog of 2026-10-28). No one has checked that privileged systemd containers, cgroup limits, loop devices and Samba's ACLs behave the same there; this affects Module 1's labs as well. | The CI spike (P3) looks for both kinds of runner. |
| 32 | About twelve Samba labs at 7 to 8 minutes each will be added to a Labs job of four shards. | Raise the shard count when needed (3.5). |
| 33 | The licensing brief misses one rule its own sources state: Windows Server brought to an AWS Dedicated Host is licensed on all the host's physical cores. | Added to topic 22 (§4.22). |
| 34 | Gregg's main post is about 2,200 words (the brief says 1,900); its "less than 1%" overhead is one engineer's estimate. | Noted for the writer (§4.15). |

### The spec

| # | Problem | What was done |
| --- | --- | --- |
| 35 | "Drills run as Python in the browser" while "Python Foundations is needed from Module 6"; the Subnetting drill (Module 3) says "The browser (Python)" too. | Replacement text: quick drills are estimate questions (§10.4); a note for Module 3's designers. |
| 36 | "Say when Arm saves 20–40%": list prices show 7 to 31% at equal size, two cases where Arm costs more, and AWS's own page now claims "up to 20% less". | Reworded (§10.1). |
| 37 | Checkpoint 2 part 2's text names the debug's causes, and the outline copied them into public objectives. | Reworded in the spec; the objectives name no cause (§5, §10.1). |
| 38 | Part 3 "join a Windows and a Linux VM" and topic 19's "join a cloud VM to a domain" can't be met locally. | Reworded, with the optional Azure version named (§10.1). |
| 39 | "Within one size" is too loose for a proof (the current size is often within one size of the right one). | The drills row says proofs use a stated policy and 15% (§10.5). |
| 40 | Two new topics shift every later topic's number. | A renumbering script and a reminder to regenerate outlines (§10.2). |

## 3. Left as the designers wrote it, after checking

- The hypervisors topic's QEMU labs (unprivileged, no KVM, 381 MB): the only free way to make emulated against paravirtual something the learner caused.
- No checked `docker buildx` lab before Module 6.
- The GPU topic with no GPU, said plainly in its lesson.
- The licensing topic as one topic of 285 minutes, with its `look-it-up` skill.
- The Samba labs' design, which passed the real checker for the build and the debug, with `.test` for the domain.
- The Azure lab's design (NAT gateway, Bastion Developer, no public address, guardrails first, Windows Server 2022 with a desktop).
- `metric-summary` provided in Checkpoint 2 part 1, now that percentiles are taught.
- Positional checkpoint ids.

## 4. Still unverified

See MODULE-2-BRIEF §9. In short: nothing in any ladder has run under `labcheck test` except the two built windows-ad labs; the checkpoint stand-up lab's contract; every lab on GitHub's runners; the Azure lab end to end; the Ubuntu SSSD guide (unreachable from here today); the videos' content; what an Azure B-series guest shows when its credits are gone; three `nvidia-smi` formats; whether a free-tier `e2-micro`'s external address is charged; Bv1's retirement date and whether Bsv2 is offered to the owner's subscription.
