# Writing brief: `csa.hw.cores-memory` (topic 17), Cores, memory and noisy neighbours

Design only. Nothing here is written into the repository yet. Sources were read on 2026-11-10 and 2026-11-11 (the session crossed midnight); each fact below carries its date. Lab mechanics marked "tried" were run in Docker on the owner's machine (Docker 29.8.2, WSL2 kernel 6.18, cgroups v2) and everything started was removed.

This brief also holds the hand-over for **Checkpoint 2, part 2** ("Diagnose a slow VM"): see the heading [For the checkpoint designer](#for-the-checkpoint-designer-checkpoint-2-part-2-diagnose-a-slow-vm).

It leans on two notes by the other Module 2 designers, in the same folder:

- `estimate-questions.md`: the proposed `estimate` recall type (a typed number checked within a tolerance) and its fallback to multiple choice. Every item below called an **estimate** is written in that shape.
- `price-fixture-2026-11.md` and `.csv`: the dated prices. Every price below is copied from it or read from the same source.

## 1. What the learner will be able to do

1. Look at `lscpu` on any Linux machine, or at a provider's instance table, and say how many sockets, physical cores and hardware threads there are, and so what a "vCPU" on that machine really is: one of two threads sharing a core, or a whole core.
2. Work a burstable instance's credit bucket by arithmetic: how fast it fills, how fast a workload drains it, when it runs dry, what happens then on each cloud, and when a fixed-size machine is cheaper.
3. Faced with "the VM is slow", tell three different stories apart from the numbers: CPU the host withheld (steal), a cap of the machine's own making (a cgroup quota, a memory limit, a disk allowance, spent credits) and a machine that is simply out of CPU or memory. Say what a neighbour can and cannot take from you, and which remedy fits which story.
4. Read a machine's NUMA layout (which CPUs and how much memory each node has), say why memory on the other node is slower, and pin a process to one node.
5. Place the layers of memory and storage in order of speed with rough numbers, choose between a local disk that vanishes on stop and a network disk that persists but is capped, and compute what a disk and VM together will really deliver.

**The six-month core.** What should still be there half a year on, and what the review pool is built around:

- A vCPU is usually a thread, not a core. Divide by threads per core; check with `lscpu` or the provider's table.
- A burstable instance is a bucket. It earns `vCPUs × baseline × 60` credits an hour and spends `vCPUs × utilisation` a minute. Steady load above the baseline empties it, however long it takes.
- `st` is the host's doing and nothing inside the VM fixes it. `nr_throttled`, `memory.events high` and a disk at its allowance are the machine's own caps. Neither is the same as being out of CPU.
- A local disk is fast, included in the price and gone when the instance stops. A network disk persists and is capped twice, by the disk and by the VM; you get the smaller.
- Throughput = IOPS × block size, until the throughput cap takes over.
- Remote memory is slower. Keep a process's CPUs and memory on the same NUMA node.

## 2. Prerequisites and terms

**Prerequisites (topic ids).**

| Topic | What this topic uses from it |
| --- | --- |
| `csa.hw.hypervisors` | Hypervisor, host and guest, a VM as a slice of a physical machine, overcommitting. This topic says what the slice is made of. |
| `csa.linux.cpu` | `top`'s CPU line including `st`, load average against `nproc`, cgroups v2, `cpu.max`, `cpu.stat` and `nr_throttled`, `systemd-run -p`, `systemctl show -p`. Steal is introduced there in two sentences; this topic measures it and tells it from its look-alikes. |
| `csa.linux.memory` | `free` and `available`, swap, `vmstat`'s `si` and `so`, the OOM kill, `memory.max`, `memory.events`. |
| `csa.linux.storage` | Block devices and their names (`/dev/nvme0n1`), `lsblk`, IOPS, throughput, latency, queue depth, the lab pattern of disks under `/dev/lab/`. |
| `csa.linux.triage` | The USE method, saturation against utilisation, `vmstat`, `mpstat -P ALL`, `iostat -xz`. |
| `csa.linux.services` | Units, drop-ins, `systemctl`, `journalctl -u`. Every systemd lab here needs them. |
| `csa.linux.shell`, `csa.linux.scripting` | `grep`, `awk`, `sort`, `$(( ))`, writing and running a small script. |

Recommended `prerequisites:` line: `[csa.m1.checkpoint, csa.hw.hypervisors]`. The checkpoint already requires all fourteen Module 1 topics, so listing them again adds nothing to gating; the table above is for the writer. `csa.hw.cpu-architectures` is deliberately **not** a prerequisite: the one fact needed from it (Arm cloud CPUs have one thread per core) is taught here in a sentence, so topics 16 and 17 can be done in either order.

**Terms this topic must define itself** (nothing earlier in the track teaches them):

- **Socket, core, hardware thread, simultaneous multithreading (SMT), Hyper-Threading** (Intel's name for SMT), **logical CPU**.
- **vCPU** as a provider's unit, and **threads per core** as a setting.
- **Instance type, family and size** (only as far as reading a table row: name, vCPUs, memory). Module 12 teaches choosing among families properly; this topic says so.
- **Burstable instance, baseline, CPU credit, credit balance, standard and unlimited mode, shared-core.**
- **Noisy neighbour, tenant, dedicated host, sole-tenant node, pinning** (`taskset`, `AllowedCPUs=`).
- **Steal** is defined in `csa.linux.cpu`; this topic adds where it is counted (`/proc/stat`, the eighth number) and how to compute a percentage over an interval.
- **Pressure stall information (PSI):** `some`, `full`, `avg10`.
- **`memory.high`** (a throttle, against `memory.max`, a wall), **`io.max`**.
- **NUMA, node, local and remote memory, node distance.**
- **Cache (L1, L2, L3), memory hierarchy.** One paragraph: small fast memory inside the CPU that holds what was used last.
- **NVMe** (the name appears in Module 1's device names but is never explained), **local or ephemeral disk** (instance store, temporary disk, Local SSD), **network-attached disk** (EBS, managed disk, Persistent Disk and Hyperdisk), **provisioned IOPS**.
- **GiB against GB, MiB/s against MB/s** where a provider's table uses one or the other. AWS and Google quote MiB/s; Azure quotes MB/s (10^6 bytes).

**The spec's phrase "memory tiers".** The spec row says "explain memory tiers, NVMe, and local ephemeral versus network-attached disks". This brief reads "memory tiers" as the hierarchy from CPU cache through RAM to local and network disks, with rough costs. If the owner meant something else (for example memory-optimised instance families), that belongs with instance families in Module 12; see Open questions.

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `vcpu-to-core` | Read `lscpu` (sockets, cores per socket, threads per core) and a provider's instance table; turn vCPUs into physical cores; say when a vCPU is a thread and when it is a whole core, and what switching SMT off changes |
| `burst-credits` | Burstable instances: baseline, credits earned and spent, time until the bucket is empty or full, what happens at zero in standard and unlimited mode, and how the three clouds differ |
| `stolen-or-capped` | Tell stolen CPU (steal, the host's doing) from a cap of the machine's own (a cgroup quota, a memory throttle, spent credits) from a machine that is out of CPU or memory, using `/proc/stat`, `vmstat`, `mpstat`, `cpu.stat`, `memory.events` and the pressure files; say what tenants share and which remedy fits |
| `numa` | Read NUMA nodes in `lscpu` and `numactl --hardware`; explain local and remote memory; pin a process to a node; say when it matters |
| `local-vs-network-disk` | The memory and storage tiers by rough speed; local ephemeral disks against network disks and what survives a stop; a disk's and a VM's IOPS and throughput allowances, which one binds, and IOPS × block size |

Five skills. Each has at least five questions that can come back (the count is at the end of section 7).

## 4. Lesson plan

The lesson is the `<Intro>` (what to watch for, with the explanations no resource gives a beginner), the main resource, and the `<Recap>`. The order of ideas, the resource section each leans on, and what the lesson itself must supply:

**1. The slice has parts.** A server board has sockets; each socket holds a CPU package; each package has cores; a core can present one or two hardware threads. Linux numbers every hardware thread as a CPU. *Resource:* AWS, "CPU options for Amazon EC2 instances" (the first paragraph and the m5.xlarge example). *The lesson supplies* the picture in words, because no provider page draws it for a beginner:

> A building (the host) has floors (sockets). Each floor has flats (cores). A flat has one kitchen and, on most x86 servers, two desks (hardware threads). Two people at the two desks get more done than one, but they share the kitchen, so not twice as much. A vCPU is a desk. Rent "4 vCPUs" on an Intel or older AMD machine and you get two flats; rent 4 vCPUs on an Arm machine and you get four flats, because those flats have one desk each.

Then `lscpu`: the three lines to multiply (`Socket(s)` × `Core(s) per socket` × `Thread(s) per core` = `CPU(s)`), and `lscpu -e`, which shows which CPU numbers are the two desks of one flat. *Honesty the lesson must include:* the lscpu manual says a guest sees what the hypervisor presents, which may not be the physical layout. AWS states that Nitro exposes the real topology; Azure's own guidance tells you to read `Thread(s) per core` in the guest. On the learner's own lab container, `lscpu` shows whatever Docker Desktop's VM presents (on the owner's PC: 8 CPUs as 8 cores of 1 thread, `Hypervisor vendor: Microsoft`), which is a live example of a guest's view.

**Where the clouds differ (mark it in the lesson):**

| | AWS | Azure | Google Cloud |
| --- | --- | --- | --- |
| A vCPU on most x86 sizes | one thread of a core; two per core | one thread; "ratio of vCPU to core is 2:1" | "a single hardware multithread"; two share a core |
| A vCPU that is a whole core | Graviton (Arm) sizes; C7a, M7a, R7a (AMD) | Arm sizes (Cobalt 100 Dpsv6, Ampere Dpsv5); HBv3; the AMD Fasv7 family ("comes without SMT... a vCPU is now mapped to a full physical core") | Arm sizes; Tau T2D; H3; H4D |
| Switch SMT off | "threads per core" = 1 in CPU options | VM vCore Customization (threads per core = 1) | "threads per core" = 1 |
| What you pay then | the same price | the same price | still billed for all the machine type's vCPUs |

**2. Why it matters: what a neighbour can and cannot take.** *Main resource:* AWS, "The EC2 approach to preventing side-channels" (from *The Security Design of the AWS Nitro System*). It is written about security, but it is the clearest first-hand account of what a cloud does and does not share between tenants: fixed-size instances get cores pinned to them for their lifetime; two customers never run on the two threads of one core at the same time; the top-level cache (L3) can be shared; burstable instances are overcommitted and take turns on a core. *The lesson supplies* the reading guide ("you are reading this for what is shared, not for the attacks") and the consequence in plain words: on a fixed-size instance a neighbour cannot take your CPU time, so `st` should sit near zero; what a neighbour can still do is crowd the shared cache, the memory bus, the disk backend and the network, and none of that shows up as `st`. On burstable and shared-core sizes the host really does hand your CPU to someone else, and that is where steal lives. The lesson must say that this account is AWS's; Azure and Google publish the vCPU-to-thread mapping (table above) but nothing as explicit about pinning was found, so the lesson claims it for AWS only.

**3. Burstable instances are a bucket.** *Resources:* AWS, "Key concepts for burstable performance instances" (the definitions and the credit table); Azure, "B-series CPU credit model" (short, with two worked sums); Google Cloud, "General-purpose machine family", section *Shared-core VMs* and *CPU bursting*. *The lesson supplies* the bucket picture and one worked sum on each of AWS and Azure, because the provider pages give formulas but not the "when does it run out" question an architect actually asks:

> A bucket with a tap and a drain. The tap runs at a fixed rate: `vCPUs × baseline × 60` credits an hour. The drain runs as hard as the machine works: `vCPUs × utilisation` credits a minute, where one credit is one vCPU flat out for one minute. Below the baseline the bucket fills, up to a day's worth. Above it, the bucket empties. A `t3.large` (2 vCPUs, baseline 30%) earns 36 an hour. Run it steadily at 35% and it loses 6 an hour: from a full bucket of 864 it is fine for six days and then it is not. Testing it for an afternoon would never show that.

**Where the clouds differ:**

| | AWS T family | Azure B family | Google Cloud E2 shared-core |
| --- | --- | --- | --- |
| The bucket | up to 24 hours of earnings | "Max Banked Credits", 24 hours of earnings | none you can see; a token bucket good for 30, 60 or 120 seconds of 100% (micro, small, medium) |
| At zero | *standard* mode: comes down to the baseline. *Unlimited* mode (the default on T3, T3a, T4g and T8i): keeps going and bills surplus credits | "throttled back to its base CPU performance" | back to its share: each of 2 vCPUs for 12.5%, 25% or 50% of the time |
| The surprise | a bill (unlimited) or a slowdown days later (standard) | a slowdown | a slowdown within a minute or two of sustained load |
| What the guest sees when held back | AWS's own troubleshooting article lists a depleted credit balance as a cause of high steal (known here from a search summary only; the page refused the fetch) | **not documented in what was read**; one Microsoft Q&A answer suggests the guest is not told. Do not state it either way until a capture run settles it (section 10) | not read |

**4. Stolen, capped or just busy.** Builds on `csa.linux.cpu`; does not repeat it. *Resources:* `proc_stat(5)` for the definition of the steal field; the kernel's "PSI: Pressure Stall Information"; the cgroup v2 document's entries for `memory.high` and `io.max`. *The lesson supplies* the decision table, which is the heart of the topic and of Checkpoint 2's part 2, and which no single resource contains:

| What you see | Whose doing | The witness | What helps | What does not |
| --- | --- | --- | --- | --- |
| `st` high in `vmstat`, `mpstat` or `/proc/stat`; the VM does less than it asks for | the host's | the eighth number on `/proc/stat`'s `cpu` line, as a share of all the time in the interval | a fixed-size instance; unlimited mode; a dedicated host for isolation | `nice`, cgroup settings, restarting the service |
| `st` 0, CPUs mostly idle, a service slow in bursts | the machine's own CPU quota | the service's `cpu.stat`: `nr_throttled` rising | raise or remove the quota (Module 1) | a bigger instance |
| `st` 0, a service alive but crawling, swap in use | the machine's own memory throttle or too little memory | `memory.events`: `high` rising; `memory.current` pinned at `memory.high`; `memory.pressure`; `si`/`so` | raise the throttle above what the service really uses, keep the wall | adding CPUs |
| `st` 0, `wa` high, the disk at a flat rate | the disk's or the VM's I/O allowance | `io.stat` rising at exactly the cap; `io.pressure`; in a cloud, the disk's and VM's metrics | a higher disk tier, a bigger VM, a local disk for scratch work | a deeper queue |
| `st` 0, `r` above the CPU count, `id` near 0 | nobody's: the machine is out of CPU | run queue, load against `nproc` | more or faster vCPUs | changing limits that are not set |

and two short explanations:

> **How steal is counted.** The kernel keeps a running total, per CPU, of the time the hypervisor ran something else while this VM had work ready. It is the eighth number on the `cpu` line of `/proc/stat`. One reading means nothing, because it has been counting since boot; take two readings and divide the growth in steal by the growth in all eight numbers together.

> **Pressure.** Three files, `/proc/pressure/cpu`, `memory` and `io`, answer one question each: for what share of the last 10, 60 and 300 seconds was work waiting for this? `some` means at least one task was waiting; `full` means everything was. Every cgroup has the same three files (`cpu.pressure`, `memory.pressure`, `io.pressure`), so the question can be asked of one service.

and one sentence on `memory.high`: Module 1's `memory.max` is a wall (reach it and the kernel kills); `memory.high` is a throttle (go over it and the kernel slows the service down and pushes its memory out), which is how a service ends up alive and a hundred times slower.

**5. NUMA.** *Resources:* the kernel's "What is NUMA?" (the first four paragraphs only; the rest is for kernel developers); Azure's HBv3 overview (the *VM topology* section: a real cloud VM with four NUMA domains, drawn); `numactl(8)`. *The lesson supplies:*

> Two towns (nodes), each with its own workers (cores) and its own warehouse (memory). A worker fetching from the other town's warehouse makes a longer trip every time. `numactl --hardware` prints each town's workers and warehouse size, and a table of distances: 10 means "here", 21 means "about twice as far". A small VM lives in one town and never notices. A machine with dozens of cores spans both, and a database whose CPUs are in one town and whose memory landed in the other is slower for no visible reason. `numactl --cpunodebind=0 --membind=0 COMMAND` keeps both in one town.

The lesson says plainly when it matters (large sizes, databases, HPC) and that most small VMs show `NUMA node(s): 1`.

**6. The tiers, and local against network disks.** *Resources:* AWS, "Data persistence for Amazon EC2 instance store volumes" (the events table); Azure, "Virtual machine and disk performance" (the two capping examples); Azure, "Overview of Azure Disk Storage" (the *Temporary disk* section); Google Cloud, "About Local SSD disks" (the *Local SSD data persistence* section). *The lesson supplies* the tiers table, with a warning that these are orders of magnitude for reasoning, not specifications:

| Tier | Roughly | If a cache hit took one second |
| --- | --- | --- |
| CPU cache (L1) | 1 ns | 1 second |
| RAM | 100 ns | under 2 minutes |
| Local NVMe disk, one random read | tens of microseconds | several hours |
| Network SSD disk, one operation | a millisecond or a few ("single-digit millisecond" on AWS gp3; under half a millisecond on the top tiers) | one or two weeks |

and the three rules with numbers:

- **What survives.** A table of events (reboot, stop and start, host failure, resize) against local disk and network disk on each cloud. Reboot: kept. Stop: gone, on all three. So local disks are for caches, scratch space, temporary files and data that is replicated elsewhere.
- **IOPS × block size = throughput, until the throughput cap.** AWS gp3 includes 3,000 IOPS and 125 MiB/s. At 16 KiB a write, 3,000 IOPS is 47 MiB/s: the IOPS cap binds. At 256 KiB a write, 3,000 IOPS would be 750 MiB/s, so the throughput cap binds instead and the disk does 500 a second.
- **You get the smaller of the disk's allowance and the VM's.** Azure's own example: three disks of 5,000 IOPS each on a VM allowed 12,800 deliver 12,800, not 15,000. A deeper queue does not get past a cap; it only makes each request wait longer (the lab shows 2 ms at depth 1 becoming 32 ms at depth 16, at the same 500 IOPS).

**Where the clouds differ:**

| | AWS | Azure | Google Cloud |
| --- | --- | --- | --- |
| Local disk | instance store; only on sizes with a `d` (for example `m6id`) and storage sizes; included in the price | temporary disk; many current sizes (Dsv5, Bsv2) have none; `d` sizes do | Local SSD, 375 GiB each, attached at creation |
| Lost on | stop, hibernate, terminate, resize, disk failure | stop, redeploy, a maintenance event | stop, preemption, some host errors |
| General network SSD, included performance | gp3: 3,000 IOPS and 125 MiB/s whatever the size | Premium SSD v2: 3,000 IOPS and 125 MB/s whatever the size; Premium SSD (P sizes): set by size | Balanced Persistent Disk: 3,000 IOPS baseline per instance plus 6 per GiB |
| VM-level cap | per instance type (the "EBS" columns of the instance tables) | per size ("uncached" IOPS and MBps) | rises with the number of vCPUs |

**Read now, and the labs.** One closing paragraph in the house style naming the resources in order and what each lab does.

**Recap.** Seven bullets, one per row of the six-month core plus NUMA.

## 5. Verified facts

Every specific claim the topic may make, where it was read and when. "Tool" in the last column means the page was fetched and searched as text with a script (`experiments/tools/grep_url.py`); "WebFetch" means read through the fetch tool.

| # | Claim | Source | Read |
| --- | --- | --- | --- |
| 1 | AWS: "Many Amazon EC2 instances support simultaneous multithreading (SMT)... Each thread is represented as a virtual CPU (vCPU)"; an m5.xlarge has two cores and two threads per core, four vCPUs | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-optimize-cpu.html | 2026-11-10 |
| 2 | AWS: threads per core cannot be changed on T2, C7a, M7a, R7a, Apple silicon Mac and Graviton instances; no extra charge for CPU options, and the price is the same as with the defaults (licence-included Windows and SQL Server aside) | same page | 2026-11-10 |
| 3 | AWS instance table rows (vCPUs, cores, threads per core): m5.large 2/1/2; m5.xlarge 4/2/2; m5.24xlarge 96/48/2; m7i.large 2/1/2; m7i.48xlarge 192/96/2; m7a.large 2/2/1; m7g.large 2/2/1; m8g.large 2/2/1; i4i.large 2/1/2; i8g.large 2/2/1 | https://docs.aws.amazon.com/ec2/latest/instancetypes/gp.html and `/so.html` | 2026-11-11 |
| 4 | Azure: "When a hyper-threaded VM is created, Azure allocates 2 threads per core - these are called vCPUs"; a D8_v3 is 8 vCPUs on 4 cores; to check, run `lscpu` and read `Thread(s) per core` | https://learn.microsoft.com/en-us/azure/virtual-machines/mitigate-se | 2026-11-10 |
| 5 | Azure: Dsv5 runs "in a hyper threaded configuration"; Dpsv6 (Cobalt 100) and Dpsv5 (Ampere Altra) each provide "an entire physical core for each virtual machine vCPU"; HBv3 has SMT disabled; the Fasv7 family "comes without Simultaneous Multithreading (SMT), meaning a vCPU is now mapped to a full physical core" | `.../sizes/general-purpose/dsv5-series`, `.../dpsv6-series`, `.../dpsv5-series`, `.../sizes/compute-optimized/f-family`, `.../sizes/high-performance-compute/hbv3-series-overview` on learn.microsoft.com | 2026-11-10, 2026-11-11 |
| 5a | AWS's credit table carries the note "Each vCPU is a thread of either an Intel Xeon core or an AMD EPYC core, except for T2 and T4g instances". What a T2 vCPU is instead is not stated on the pages read, so the lesson should not say | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-credits-baseline-concepts.html | 2026-11-10 |
| 6 | Azure: VM vCore Customization can set threads per core to 1 and reduce the vCPU count; "no extra charge... The base VM price remains the same" | https://learn.microsoft.com/en-us/azure/virtual-machines/vm-customization | 2026-11-10 |
| 7 | Google Cloud: "each hardware thread is called a virtual CPU (vCPU). Some machine series don't use SMT, and each vCPU instead represents a core"; H3, H4D and Tau T2D use one thread per core; "For Arm processors, Compute Engine uses one thread per core" | https://docs.cloud.google.com/compute/docs/cpu-platforms | 2026-11-10 |
| 8 | Google Cloud: with threads per core set to 1 on n2-standard-8 you run 4 vCPUs and "are still billed for 8"; SMT "can increase application throughput significantly" for general and I/O-heavy work and "can hinder overall application performance" when both threads are compute-bound | https://docs.cloud.google.com/compute/docs/instances/set-threads-per-core | 2026-11-10 |
| 9 | lscpu: "In virtualized environments, the CPU architecture information displayed reflects the configuration of the guest operating system which is typically different from the physical (host) system"; "On virtual hardware the number of cores per socket, etc. can be wrong"; `-s, --sysroot` reads another machine's data from a directory | https://man7.org/linux/man-pages/man1/lscpu.1.html and `lscpu --help` in ubuntu:24.04 | 2026-11-10 |
| 10 | AWS Nitro: fixed performance instances have CPU and memory "pre-allocated and dedicated"; cores are "pinned" and "not used to run other customer workloads"; "CPU cores are never simultaneously shared among customers via... SMT"; instances never share L1 or L2 cache; some sizes can share last-level cache; burstable instances "can be overcommitted" and two "run sequentially (not simultaneously) on the same core"; Nitro "accurately exposes the underlying CPU topology... including... NUMA" | https://docs.aws.amazon.com/whitepapers/latest/security-design-of-aws-nitro-system/the-ec2-approach-to-preventing-side-channels.html | 2026-11-11 |
| 11 | AWS: "1 CPU credit = 1 vCPU * 100% utilization * 1 minute"; credits earned per hour = baseline × vCPUs × 60; the accrual limit is a day's earnings | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-credits-baseline-concepts.html | 2026-11-10 |
| 12 | AWS credit table: t3.micro 12 an hour, limit 288, 2 vCPUs, 10%; t3.small 24, 576, 20%; t3.medium 24, 576, 20%; t3.large 36, 864, 30%; t3.xlarge 96, 2,304, 4 vCPUs, 40%; the same figures for t3a, t4g and t8i sizes of the same name; a T8i family now exists | same page | 2026-11-10 |
| 13 | AWS: T8i, T4g, T3a and T3 launch in unlimited mode by default, T2 in standard; in standard mode with no credits left the instance "gradually comes down to baseline CPU utilization"; credits persist 7 days after a stop (T2: lost) | same page, and `.../burstable-performance-instances-standard-mode-concepts.html` | 2026-11-10 |
| 14 | AWS surplus credits: $0.05 per vCPU-hour on T2 and T3 (Linux), $0.04 on T4g, $0.06 on T8i, $0.096 on T2 and T3 with Windows | https://aws.amazon.com/ec2/pricing/on-demand/ (section "Unlimited Mode Pricing") | 2026-11-10 |
| 15 | AWS: the break-even between t3.large in unlimited mode and m5.large is 42.5% average CPU; "If a T3 instance continuously bursts at 100% CPU, you end up paying approximately 1.5 times the price of an equivalently-sized M5 instance". The page's own table uses $0.0835 and $0.096 an hour | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-performance-instances-unlimited-mode-concepts.html | 2026-11-10 |
| 16 | **Disagreement:** the price fixture (AWS's price file, 2026-11-10) has t3.large at $0.0832, not the $0.0835 in fact 15's table. With $0.0832 the break-even works out at 42.8%. A question must carry its own prices and its answer must be worked from them | `price-fixture-2026-11.csv` | 2026-11-10 |
| 17 | Azure B-series: "Upon consuming all the CPU credits, a B-series virtual machine is throttled back to its base CPU performance"; credits banked per minute = ((base CPU performance × vCPUs) − (percentage CPU × vCPUs)) / 100; worked examples on B2ts_v2 (+0.2 a minute at 10%) and B32as_v2 (−6.4 a minute at 60%) | https://learn.microsoft.com/en-us/azure/virtual-machines/b-series-cpu-credit-model/b-series-cpu-credit-model | 2026-11-10 |
| 18 | Azure Bsv2 table: B2ts_v2 2 vCPUs, 1 GiB, base 20%, 60 initial credits, 24 banked an hour, 576 maximum; B2ls_v2 4 GiB, 30%, 36, 864; B2s_v2 8 GiB, 40%, 48, 1,152. Uncached disk limit for all three: 3,750 IOPS and 85 MBps. No local temporary disk in the series | https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/bsv2-series | 2026-11-10 |
| 19 | Google Cloud shared-core: e2-micro "sustains 2 vCPUs, each for 12.5% of CPU time"; e2-small 25% each; e2-medium 50% each; at 100% a burst lasts 30, 60 and 120 seconds; "The exact burst time is determined by a Token bucket"; "Bursting doesn't incur any additional charges" | https://docs.cloud.google.com/compute/docs/general-purpose-machines | 2026-11-10 |
| 20 | steal: "Stolen time, which is the time spent in other operating systems when running in a virtualized environment", the eighth value on the `cpu` line, in units of USER_HZ | https://man7.org/linux/man-pages/man5/proc_stat.5.html | 2026-11-10 |
| 21 | PSI: `some` is "the share of time in which at least some tasks are stalled on a given resource"; `full` is the share "in which all non-idle tasks are stalled... simultaneously"; averages over 10, 60 and 300 seconds; `total` in microseconds | https://docs.kernel.org/accounting/psi.html | 2026-11-10 |
| 22 | cgroup v2: `memory.high` is the "Memory usage throttle limit. If a cgroup's usage goes over the high boundary, the processes of the cgroup are throttled and put under heavy reclaim pressure"; `memory.events` `high` counts the times that happened; `io.max` "limits the maximum BPS and/or IOPS that a cgroup can consume on an IO device" | https://docs.kernel.org/admin-guide/cgroup-v2.html | 2026-11-10 |
| 23 | systemd: `MemoryHigh=` ("the processes are heavily slowed down"), `IOReadIOPSMax=`/`IOWriteIOPSMax=` (device, IOPS), `IOReadBandwidthMax=`/`IOWriteBandwidthMax=` (device, bytes), `AllowedCPUs=` (the cpuset controller) | https://man7.org/linux/man-pages/man5/systemd.resource-control.5.html | 2026-11-11 |
| 24 | NUMA: memory on a node's own cell is faster than memory on a remote cell; Linux groups CPUs and memory into nodes | https://docs.kernel.org/mm/numa.html | 2026-11-10 |
| 25 | Azure HBv3: 2 × 64-core CPUs, SMT disabled; the VM sees 4 NUMA domains; HB120rs_v3 has 30 cores per domain | https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/high-performance-compute/hbv3-series-overview | 2026-11-11 |
| 26 | AWS instance store: "The data on an instance store volume persists even if the instance is rebooted. However, the data does not persist if the instance is stopped, hibernated, or terminated"; also lost when the instance type is changed or the disk fails; "There is no additional charge" | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-store-lifetime.html and `.../InstanceStorage.html` | 2026-11-10, 2026-11-11 |
| 27 | AWS instance store sizes and random read / write IOPS: i4i.large 1 × 468 GB NVMe, 50,000 / 27,500; m6id.large 1 × 118 GB, 33,542 / 16,771 | https://docs.aws.amazon.com/ec2/latest/instancetypes/so.html and `/gp.html` | 2026-11-11 |
| 28 | AWS gp3: 3,000 IOPS and 125 MiB/s included whatever the size; up to 80,000 IOPS and 2,000 MiB/s for a fee; 1 GiB to 64 TiB; "single-digit millisecond latency". (The older limits of 16,000 IOPS and 1,000 MiB/s now apply only on Outposts: do not write them from memory.) io2 Block Express: "an average latency of under 500 microseconds for 16KiB I/O operations" | https://docs.aws.amazon.com/ebs/latest/userguide/general-purpose.html | 2026-11-10 |
| 29 | AWS EBS: "I/O size is capped at 256 KiB for SSD volumes"; a 1,024 KiB operation counts as four | https://docs.aws.amazon.com/ebs/latest/userguide/ebs-io-characteristics.html | 2026-11-11 |
| 30 | Azure temporary disk: "Data on the temporary disk might be lost during a maintenance event, when you redeploy a VM, or when you stop the VM. During a successful standard restart of the VM, data on the temporary disk persists" | https://learn.microsoft.com/en-us/azure/virtual-machines/managed-disks-overview | 2026-11-10 |
| 31 | Azure disks: Premium SSD v2 has "a baseline IOPS of 3,000 that is free of charge" and 125 MB/s, up to 80,000 IOPS; Ultra Disk up to 400,000 IOPS with "submillisecond latency"; Premium SSD P10 500 IOPS, P30 5,000 | https://learn.microsoft.com/en-us/azure/virtual-machines/disks-types | 2026-11-10 |
| 32 | Azure capping examples: Standard_D8s_v3 allows 12,800 uncached IOPS. Three E30 disks (500 each) asked for 10,000 deliver 1,500. Three P30 disks (5,000 each) asked for 15,000 deliver 12,800 | https://learn.microsoft.com/en-us/azure/virtual-machines/disks-performance | 2026-11-10, 2026-11-11 |
| 33 | Azure D2ds_v5: temporary disk 75 GiB, 9,000 random read IOPS; remote uncached 3,750 IOPS and 85 MBps | https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/ddsv5-series | 2026-11-11 |
| 34 | Google Local SSD: 375 GiB each; kept across a guest reboot and a live migration; not kept when the instance is stopped, preempted or stops for host maintenance; may be lost on a host error | https://docs.cloud.google.com/compute/docs/disks/local-ssd | 2026-11-10 |
| 35 | Google Persistent Disk: Balanced has a baseline of 3,000 IOPS and 140 MiB/s per instance and 6 IOPS per GiB; SSD 6,000, 240 and 30 per GiB; performance "increases with the instance's number of vCPUs"; at most 80,000 IOPS (Balanced) and 100,000 (SSD) | https://docs.cloud.google.com/compute/docs/disks/performance | 2026-11-11 |
| 36 | Dedicated hardware: AWS Dedicated Instances are "physically isolated at the host hardware level from instances that belong to other AWS accounts"; Google sole-tenant nodes are "a physical Compute Engine server that is dedicated to hosting only your project's VMs" and allow CPU overcommit; Azure has isolated sizes and dedicated hosts | `.../dedicated-instance.html` (AWS), `.../nodes/sole-tenant-nodes` (Google), `.../virtual-machines/isolation` (Azure) | 2026-11-11 |
| 37 | Free tiers, for the cost section: Google's free tier is one e2-micro a month in us-west1, us-central1 or us-east1 with a 30 GB standard disk. AWS: new accounts get $100 in credits and a free plan that closes after 6 months or when credits run out; the page read does not mention 750 free hours. Azure: free amounts for 12 months for new customers | https://docs.cloud.google.com/free/docs/free-cloud-features , https://aws.amazon.com/free/ , https://azure.microsoft.com/en-us/pricing/free-services | 2026-11-10 |
| 38 | Azure prices, East US, Linux, pay-as-you-go: B2ts_v2 $0.0104 an hour; B2s_v2 $0.0832; D2s_v5 $0.096; D2ps_v6 $0.0702; a Standard SSD E4 disk $2.40 a month; a standard static public IPv4 address $0.005 an hour | Azure Retail Prices API, https://prices.azure.com/api/retail/prices | 2026-11-10, 2026-11-11 |
| 39 | Latency orders of magnitude: L1 cache 1 ns, main memory 100 ns, SSD random read 16 µs, round trip in a datacentre 500 µs. These are **values from trend formulas** on an interactive page whose slider ends at 2020, not measurements; use them only as orders of magnitude | https://colin-scott.github.io/personal_website/research/interactive_latency.html (WebFetch) | 2026-11-11 |
| 40 | `vmstat` on Ubuntu 24.04 prints a `gu` column after `st`; Module 1's fixtures have the older layout without it. `mpstat -P ALL` has `%steal` as its ninth field; `numactl --hardware` prints `available: 1 nodes (0)`, `node 0 cpus:`, `node 0 size:`, `node 0 free:`, `node distances:` | run in ubuntu:24.04 with sysstat and numactl | 2026-11-11 |

**Sources that could not be opened, so they are not used as facts or resources:**

- AWS re:Post, "Troubleshoot high CPU utilisation" (https://repost.aws/knowledge-center/ec2-troubleshoot-cpu-utilization): HTTP 403 to both tools. A search summary says it lists a depleted credit balance among the causes of high steal and suggests keeping steal under 5%. Treat as unconfirmed.
- Netflix Technology Blog, "Predictive CPU isolation of containers at Netflix": HTTP 403.
- ACM Queue, "NUMA: An Overview" (Lameter): HTTP 403.

## 6. Resources

Linked, never copied. "Minutes" is the part the lesson asks for, at about 200 words a minute, from a word count of the page's main text.

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (main) | The EC2 approach to preventing side-channels, from *The Security Design of the AWS Nitro System* (AWS whitepaper) | https://docs.aws.amazon.com/whitepapers/latest/security-design-of-aws-nitro-system/the-ec2-approach-to-preventing-side-channels.html | reading | Copyright Amazon Web Services; linked, not copied | 13 (2,571 words, all of it) | `vcpu-to-core`, `stolen-or-capped`, a first sight of `burst-credits` and `numa` | 2026-11-11 |
| 1 | CPU options for Amazon EC2 instances | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-optimize-cpu.html | reading | Copyright AWS; linked | 2 (431 words) | `vcpu-to-core` | 2026-11-10 |
| 2 | Key concepts for burstable performance instances (AWS) | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-credits-baseline-concepts.html | reading | Copyright AWS; linked | 12 (2,327 words) | `burst-credits` | 2026-11-10 |
| 3 | B-series CPU credit model (Azure) | https://learn.microsoft.com/en-us/azure/virtual-machines/b-series-cpu-credit-model/b-series-cpu-credit-model | reading | CC BY 4.0 (Microsoft Learn; the licence file of MicrosoftDocs/azure-compute-docs was read) | 3 (617 words) | `burst-credits` | 2026-11-10 |
| 4 | General-purpose machine family for Compute Engine: the sections *Shared-core VMs* and *CPU bursting* only | https://docs.cloud.google.com/compute/docs/general-purpose-machines | reading | CC BY 4.0 (the page footer was read) | 3 (the two sections; the page is 30,000 words, so the lesson must name the sections) | `burst-credits` | 2026-11-10 |
| 5 | CPU platforms (Google Cloud): the opening section on cores, threads and vCPUs | https://docs.cloud.google.com/compute/docs/cpu-platforms | reading | CC BY 4.0 | 4 (the opening; 2,921 words in all) | `vcpu-to-core` | 2026-11-10 |
| 6 | Guidance for mitigating... side-channel vulnerabilities (Azure): the part on checking hyper-threading with `lscpu` | https://learn.microsoft.com/en-us/azure/virtual-machines/mitigate-se | reading | CC BY 4.0 | 3 (the Linux part; 1,511 words in all) | `vcpu-to-core` | 2026-11-10 |
| 7 | What Is Hyper-Threading? (Intel) | https://www.intel.com/content/www/us/en/gaming/resources/hyper-threading.html | reading | Copyright Intel; linked | 3 (about 550 words) | `vcpu-to-core` | 2026-11-11 (WebFetch; the script could not verify Intel's certificate) |
| 8 | PSI: Pressure Stall Information (Linux kernel documentation): the first half, to the end of the file format | https://docs.kernel.org/accounting/psi.html | reading | GPL-2.0 | 3 (of 6) | `stolen-or-capped` | 2026-11-10 |
| 9 | proc_stat(5): the `cpu` line | https://man7.org/linux/man-pages/man5/proc_stat.5.html | reading | Linux man-pages project (free documentation; linked) | 2 (of 4) | `stolen-or-capped` | 2026-11-10 |
| 10 | What is NUMA? (Linux kernel documentation): the first four paragraphs | https://docs.kernel.org/mm/numa.html | reading | GPL-2.0 | 3 (of 8) | `numa` | 2026-11-10 |
| 11 | HBv3-series virtual machine overview (Azure): *VM topology* | https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/high-performance-compute/hbv3-series-overview | reading | CC BY 4.0 | 5 (1,030 words) | `numa`, `vcpu-to-core` | 2026-11-11 |
| 12 | numactl(8) and lscpu(1) | https://man7.org/linux/man-pages/man8/numactl.8.html , https://man7.org/linux/man-pages/man1/lscpu.1.html | reading | numactl and util-linux man pages (free documentation; linked) | reference, 5 | `numa`, `vcpu-to-core` | 2026-11-10 |
| 13 | Data persistence for Amazon EC2 instance store volumes | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-store-lifetime.html | reading | Copyright AWS; linked | 3 | `local-vs-network-disk` | 2026-11-10 |
| 14 | Virtual machine and disk performance (Azure) | https://learn.microsoft.com/en-us/azure/virtual-machines/disks-performance | reading | CC BY 4.0 | 9 (1,762 words) | `local-vs-network-disk` | 2026-11-10 |
| 15 | About Local SSD disks (Google Cloud): *Local SSD data persistence* | https://docs.cloud.google.com/compute/docs/disks/local-ssd | reading | CC BY 4.0 | 3 (the section; 5,633 words in all) | `local-vs-network-disk` | 2026-11-10 |
| 16 | Amazon EBS General Purpose SSD volumes: the gp3 section | https://docs.aws.amazon.com/ebs/latest/userguide/general-purpose.html | reading | Copyright AWS; linked | 3 | `local-vs-network-disk` | 2026-11-10 |
| 17 | Latency Numbers Every Programmer Should Know (interactive, Colin Scott) | https://colin-scott.github.io/personal_website/research/interactive_latency.html | interactive | MIT (the repository's licence was read) | 3 | `local-vs-network-disk` | 2026-11-11 |

Reading the lesson asks for: about 60 minutes (resources 0 to 5, 8 to 11, 13 to 16). Resources 6, 7, 12 and 17 are "more resources".

**Why this main resource.** Nothing found explains cores, threads, pinning, cache sharing, overcommitted burstable instances and NUMA exposure in one place as directly as this chapter, and it is written by the people who built the system. Its framing is security, which a beginner needs to be told to read past; the Intro does that. The alternative is AWS's two-minute "CPU options" page as the main resource, which is easier but covers one skill of five.

**No video found worth recommending.** No talk was opened and checked, so none is listed.

## 7. Practice ladder

Order matters: each skill meets a worked example or reading questions before its fill-in or write, and every skill is practised before the proofs. Item kinds: `mcq`, `predict_shell`, **estimate** (the proposed type; until it exists each converts to `mcq` with the answer and its `mistakes` as the four choices) and labs.

**House rules applied to every item below.** Multiple-choice options are all about the same length, the right one is not always the same position, and the teaching goes in `explanation`. Every price or limit a question needs is in its own prompt with the date read. `predict_shell` commands use only `grep`, `awk`, `sed`, `sort`, `paste`, `cut`, `wc` and `$(( ))`, which run the same in CI's bash and in Git Bash.

**The predict commands were run.** Every `predict_shell` command quoted in this brief was run over its fixture in Git Bash on the owner's PC and in bash on `ubuntu:24.04` (whose `awk` is mawk), and printed the stated answer in both: `experiments/predict-check.sh` in this folder.

**Lab images.** The plain labs share one first `RUN` line: `ubuntu:24.04` with `sudo nano less procps sysstat numactl` and the `learner` user (`lscpu` and `taskset` are already in the base image). The systemd labs use the track's shared systemd layer unchanged and add `fio numactl sysstat` in this topic's `tail-common`.

### 7.1 `example-read-the-slice` (worked example, plain lab), skills `vcpu-to-core`, `numa`, `stolen-or-capped`

**What the container holds.**

- `/srv/machines/web-1`, `/srv/machines/arm-1`, `/srv/machines/db-1`: three recorded machines, each a small copy of the parts of `/proc` and `/sys` that `lscpu` reads. `seed.sh` builds them from a shape (sockets, cores per socket, threads, NUMA nodes), so the checks can compute the truth from the same trees. The real `lscpu --sysroot DIR` reads them. *Tried:* `experiments/sysroot3.sh` in this folder builds exactly these three and `lscpu` reports web-1 as 2 CPUs, 1 core, 2 threads; arm-1 as vendor ARM, 2 cores, 1 thread; db-1 as 96 CPUs, 2 sockets, 24 cores per socket, 2 threads, `NUMA node0 CPU(s): 0-23,48-71`, `NUMA node1 CPU(s): 24-47,72-95`. The files `lscpu` needs are the hexadecimal masks (`topology/thread_siblings`, `core_siblings`, `node/nodeN/cpumap`), not only the `_list` files; without them it aborts.
- `/srv/machines/db-1/numactl-hardware.txt`: a recording of `numactl --hardware` for db-1 (two nodes, CPU lists matching the tree, sizes, free memory with node 1 nearly full, distances 10 and 21).
- `/usr/local/bin/spin`: Module 1's spinner.

**What the learner does** (labelled steps, one line each in `solution.sh`):

1. *Your own lab machine.* `lscpu | grep -E '^CPU\(s\)|Thread|Core|Socket|NUMA node\(s\)|Hypervisor'`. The note says: this is a guest's view; `Hypervisor vendor` is the proof you are inside a VM.
2. *A two-vCPU x86 machine.* `lscpu --sysroot /srv/machines/web-1 | grep -E ...`: 2 CPUs = 1 socket × 1 core × 2 threads. One core.
3. *A two-vCPU Arm machine.* The same for arm-1: 2 CPUs = 2 cores × 1 thread. The note must say that the `Architecture:` line is the learner's own machine's, because `lscpu` takes that one line from the running kernel (tried: it prints `x86_64` for the Arm recording on an x86 host); everything else comes from the recording.
4. *A big database server.* The same for db-1, then `lscpu --sysroot /srv/machines/db-1 -e=CPU,NODE,SOCKET,CORE | awk '$4 == 0'`: CPUs 0 and 48 are the two threads of core 0.
5. *Count its cores.* `lscpu --sysroot /srv/machines/db-1 -p=CORE,SOCKET | grep -v '^#' | sort -u | wc -l`: 48.
6. *Its two NUMA nodes.* `cat /srv/machines/db-1/numactl-hardware.txt`, then `numactl --hardware` on the lab machine (one node) for contrast.
7. *Two programs on one hardware thread.* `taskset -c 0 spin & taskset -c 0 spin & sleep 3; ps -o pid,psr,pcpu,comm -C spin`: both show processor 0 and about half a CPU each while the other CPUs sit idle. This is what two tenants on one thread would look like, and why fixed-size instances are pinned to their own cores. Then `kill %1 %2`.
8. *Steal on this machine.* `head -n 1 /proc/stat; sleep 5; head -n 1 /proc/stat`: the eighth number is steal; here it barely moves.
9. *Save it.* `~/example/cores.txt` with three lines, `web-1 1`, `arm-1 2`, `db-1 48`, and `~/example/siblings.txt` with `0 48`.

**Checks.** (a) `cores.txt` equals the three counts the check computes from the trees with the pipeline of step 5. (b) `siblings.txt` equals what the check reads from db-1's tree. (c) No `spin` is left running (`! pgrep -x spin`).

**Wrong fixes the checks must reject.** `wrong/halved-everything.sh` (every machine's CPUs divided by two, so arm-1 is 1); `wrong/cpus-as-cores.sh` (2, 2, 96); `wrong/left-spinning.sh`.

### 7.2 Recall on the slice

| Id | Kind | Skill | Scenario | Right answer | Wrong answers and what each tests |
| --- | --- | --- | --- | --- | --- |
| `mcq-vcpu-is-a-thread` | mcq | `vcpu-to-core` | AWS's table (read 2026-11-11) lists `m5.xlarge`: 4 vCPUs, 2 cores, 2 threads per core. A build runs four compute-heavy processes on it. What do they run on? | "Two physical cores, each presenting two hardware threads, so the four processes share two cores" | "Four physical cores, one for each vCPU, so each of the four processes has a core"; "One physical core, which the hypervisor slices four ways among the processes"; "Eight physical cores, of which the hypervisor shows half to the guest" |
| `slice-lscpu-cores` | predict_shell | `vcpu-to-core` | `lscpu.txt` holds `CPU(s): 16`, `Thread(s) per core: 2`, `Core(s) per socket: 8`, `Socket(s): 1`, `NUMA node(s): 1`. Command: `awk -F': *' '/^Core\(s\) per socket/ {c = $2} /^Socket\(s\)/ {s = $2} /^Thread\(s\) per core/ {t = $2} END {print "physical cores:", c * s; print "hardware threads:", c * s * t}' lscpu.txt` | `physical cores: 8` then `hardware threads: 16` | The explanation: a "16 vCPU" machine that is 8 cores |
| `slice-siblings` | predict_shell | `vcpu-to-core` | `lscpu-e.txt` is `lscpu -e=CPU,NODE,SOCKET,CORE` for 8 CPUs where CPUs 0 to 3 have cores 0 to 3 and CPUs 4 to 7 have cores 0 to 3 again. Command: `awk 'NR > 1 && $4 == 2 {print "CPU", $1}' lscpu-e.txt; echo "cores: $(awk 'NR > 1 {print $4}' lscpu-e.txt \| sort -u \| wc -l)"` | `CPU 2`, `CPU 6`, `cores: 4` | Linux numbers the second thread of every core after all the first threads, so CPU 2's sibling is CPU 6, not CPU 3 |
| `est-cores-from-vcpus` | estimate | `vcpu-to-core` | A database is licensed per physical core. AWS's table (read 2026-11-11): `m5.24xlarge`, 96 vCPUs, 2 threads per core. How many cores must be licensed? Unit: cores. Tolerance: exact | 48. Working: `vcpus / threads` | 96 ("that counts hardware threads; two share each core"); 192 ("multiplied where it should divide") |
| `mcq-smt-off-bill` | mcq | `vcpu-to-core` | An HPC job runs best with one thread per core. On Google Cloud you set threads per core to 1 on an `n2-standard-8` (8 vCPUs). Google's page (read 2026-11-10) says what you then see and pay for. Which? | "The guest sees 4 vCPUs on 4 cores, and you are billed for all 8 vCPUs" | "The guest sees 4 vCPUs on 4 cores, and you are billed for those 4 vCPUs"; "The guest sees 8 vCPUs on 8 cores, and you are billed for 16 vCPUs"; "The guest sees 8 vCPUs on 4 cores, and you are billed for all 8 vCPUs". Explanation adds: AWS and Azure also charge the full size |
| `numa-hardware-read` | predict_shell | `numa` | `numactl.txt` is `numactl --hardware` for a 2-node, 32-CPU machine: node 0 free 41250 MB, node 1 free 2150 MB, distances 10 and 21. Command: `awk '/^node [0-9] free/ {print "node", $2, "free MB:", $4}' numactl.txt` | `node 0 free MB: 41250` then `node 1 free MB: 2150` | Explanation: a process on node 1's CPUs that asks for 8 GB will be given memory on node 0, at distance 21 |
| `numa-which-node` | predict_shell | `numa` | `lscpu.txt` has `NUMA node0 CPU(s): 0-23,48-71` and `NUMA node1 CPU(s): 24-47,72-95`. A database is pinned to CPUs 24 to 47. Command: `awk '/^NUMA node[0-9]/ && /24-47/ {print $1, $2}' lscpu.txt` | `NUMA node1` | Explanation: 72 to 95 are the sibling threads of the same 24 cores; pin to both ranges or to neither |
| `mcq-numa-remote-memory` | mcq | `numa` | A 96-vCPU database got slower after a restart though nothing else changed. `numastat -p` shows its CPUs are on node 0 and most of its memory on node 1 (distance 21 against 10). What happened and what do you do? | "Its memory landed on the far node, so every access travels further: bind its CPUs and memory to one node" | "Its memory was moved to swap by the kernel, so every access hits the disk: add more swap space to the server"; "Its CPUs are being taken by the host for another tenant, so it waits: move it to a dedicated host"; "Its threads are sharing cores two at a time, so each is slower: switch off SMT for the whole instance" |

### 7.3 Recall and a fill-in on credits

| Id | Kind | Skill | Scenario | Right answer | Wrong answers |
| --- | --- | --- | --- | --- | --- |
| `est-credits-per-hour` | estimate | `burst-credits` | AWS's table (read 2026-11-10): `t3.large`, 2 vCPUs, baseline 30% a vCPU. One credit is one vCPU at 100% for one minute. How many credits does it earn an hour? Tolerance: exact | 36. Working: `vcpus * baseline / 100 * 60` | 18 ("that is one vCPU's worth"); 60 ("that is vCPUs × baseline, without the 60 minutes") |
| `est-minutes-to-empty` | estimate | `burst-credits` | Azure's table (read 2026-11-10): `B2ts_v2`, 2 vCPUs, base 20%, starts with 60 credits. Azure's formula: credits banked a minute = ((base × vCPUs) − (CPU% × vCPUs)) / 100. A job runs both vCPUs at 100% from the moment the VM starts. After how many minutes are the credits gone? Tolerance: ±1 | 37.5. Working: `start / ((100 * v - base * v) / 100)` | 30 ("ignores what it earns while it runs"); 150 ("divides by the earning rate, not the net drain") |
| `credits-bucket-trace` | predict_shell | `burst-credits` | `usage.txt` holds six hourly average CPU percentages for a `t3.micro` (2 vCPUs, earns 12 an hour, limit 288) that starts with 30 credits: 5, 5, 60, 60, 10, 0. Command: `awk 'BEGIN {b = 30} {b = b + 12 - 2 * $1 * 60 / 100; if (b < 0) b = 0; if (b > 288) b = 288; print b}' usage.txt` | `36`, `42`, `0`, `0`, `0`, `12` | The trace: +6, +6, −60 (floors at 0), stays 0, exactly at baseline so still 0, then +12 |
| `mcq-standard-or-unlimited` | mcq | `burst-credits` | A `t3.large` left with a CPU-bound loop for a month in its default mode (AWS, read 2026-11-10: T3 launches as unlimited; surplus credits cost $0.05 a vCPU-hour). What happens? | "It never slows down, and the bill gains a surplus-credit charge for the CPU used above its baseline" | "It slows to its baseline after about a day, and the bill stays at the plain hourly price for the month"; "It is stopped by AWS when the credits run out, and must be started again by hand each day"; "It never slows down, and the bill stays at the plain hourly price because bursting is included" |
| `mcq-three-clouds-burst` | mcq | `burst-credits` | A cron job needs a full CPU for 10 minutes every hour on the smallest burstable size of each cloud (figures read 2026-11-10). Which statement is right? | "On a Google `e2-micro` the burst at 100% lasts about 30 seconds, so the job spends most of its 10 minutes held to its share" | "On a Google `e2-micro` credits bank for 24 hours as on AWS, so the job always finds a full bucket waiting"; "On an Azure B-series VM bursting is billed per vCPU-hour once credits run out, so the job never slows down"; "On an AWS `t3.micro` in standard mode surplus credits are billed, so the job never drops to its baseline" |

**`fill-credit-bucket` (fill-in, plain lab), skill `burst-credits`.**

- *Holds:* `/srv/burst/shop-web/instance.conf` (`vcpus=2`, `baseline_pct=20`, `start_credits=100`, `max_credits=576`: a `t3.small`) and `usage.csv` (`minute,cpu_pct` for 240 minutes: 5% for minutes 1 to 60, 90% for 61 to 180, 10% for 181 to 240, written by `seed.sh` from the minute number). A second folder, `/usr/local/lib/lab/hidden/shop-batch/` (readable by root only), has other numbers and a long idle stretch that reaches the maximum. `~/bin/credit-bucket` is the starter.
- *The script:* `credit-bucket DIR` walks the minutes in `awk` and prints three lines: `empty at minute: N` (or `never`), `minutes held to baseline: N` (minutes on which the balance was zero and the demand above the baseline) and `final balance: X.X`. Three lines have `...`: credits earned a minute (`vcpus * baseline / 100`), credits spent a minute (`vcpus * cpu / 100`), and the two clamps (not below 0, not above the maximum).
- *Expected on shop-web (worked by hand for the writer to confirm):* +0.3 a minute for 60 minutes gives 118; −1.4 a minute from minute 61 empties it during minute 145; held to baseline for minutes 145 to 180 (36 minutes); +0.2 a minute for the last 60 gives 12.0.
- *Checks:* no `...` left; each of the three lines, for shop-web and for the hidden folder, equals what the check's own `awk` computes from the same files (the final balance within 0.1).
- *Wrong fixes to reject:* `wrong/one-vcpu.sh` (earning without the vCPU count: fails on both folders); `wrong/no-floor.sh` (the balance goes negative, so the final balance is wrong); `wrong/no-ceiling.sh` (passes shop-web, fails the hidden folder, which is why the hidden folder idles long enough to hit the maximum).
- *Hints:* the two formulas in words; "a bucket can't hold less than nothing or more than its limit".

### 7.4 Recall and a write on stolen, capped or busy

| Id | Kind | Skill | Scenario | Right answer | Wrong answers |
| --- | --- | --- | --- | --- | --- |
| `steal-from-proc-stat` | predict_shell | `stolen-or-capped` | `before.txt` is the first line of `/proc/stat`, `cpu  210000 0 30000 900000 4000 0 1000 55000 0 0`; `after.txt` the same a minute later, `cpu  212160 0 30240 900000 4000 0 1000 64600 0 0`. Command: `paste before.txt after.txt \| awk '{for (i = 2; i <= 9; i++) {d = $(i + 11) - $i; t += d; if (i == 9) s = d}} END {print "steal:", s * 100 / t "%"}'` | `steal: 80%` | Deltas: user 2,160, system 240, steal 9,600 of 12,000. The explanation: this is a two-vCPU burstable VM held to a 20% baseline |
| `mcq-stolen-or-capped` | mcq | `stolen-or-capped` | An API on a fixed-size VM is slow in bursts. `vmstat 5` shows `st 0`, `id 70`, `r 1`. The service's `cpu.stat` shows `nr_throttled` rising by about 50 every 10 seconds. Whose doing is it, and what helps? | "The service's own CPU quota is stopping it each period: raise or remove that limit on the service" | "A neighbour on the host is taking its CPU time: move the VM to a dedicated host or bigger size"; "The VM's burst credits have run out for now: switch its credit mode or wait for them to refill"; "The VM has too few vCPUs for the work it has: resize it to the next size up in the same family" |
| `mcq-what-neighbours-share` | mcq | `stolen-or-capped` | AWS's Nitro paper (read 2026-11-11) says a fixed-size instance's cores are pinned to it and never run another customer's work. On such an instance, which of these can a busy neighbour on the same host still cause? | "Slower memory and cache access, because the last-level cache can be shared, with `st` staying near zero" | "High `st`, because the hypervisor lends the instance's idle hardware threads to other customers' work"; "Throttled periods in `cpu.stat`, because the host applies a quota whenever a neighbour gets busy"; "An out-of-memory kill, because the host hands the instance's memory pages to busier neighbours" |
| `psi-which-resource` | predict_shell | `stolen-or-capped` | Three files copied from `/proc/pressure/`: `cpu` (`some avg10=2.10 ...`), `memory` (`some avg10=45.20 ...`, `full avg10=31.70 ...`), `io` (`some avg10=6.00 ...`). Command: `grep -H '^some' pressure/* \| sed 's/ avg60.*//; s/pressure\///; s/:some avg10=/ /' \| sort -k2 -rn \| head -n 1` | `memory 45.20` | For 45% of the last ten seconds something was waiting for memory, and for 32% everything was |

**`write-steal-pct` (write, plain lab), skill `stolen-or-capped`.**

- *Holds:* `/srv/stat/` with three pairs of saved `/proc/stat` first lines, written by `seed.sh` from fixed deltas: `quiet` (steal 0.0%), `robbed` (37.5%), `mostly-idle` (steal 4.0% with idle dominating). A fourth pair, hidden for the checks.
- *The learner writes* `~/bin/steal-pct BEFORE AFTER`: prints the steal percentage over the interval to one decimal place, for example `37.5`. From a blank file; the prompt gives the usage line and says which number on the line is steal and that eight numbers make up the total.
- *Checks:* executable; on each of the three pairs and the hidden one, the printed number is within 0.1 of the check's own computation; exits non-zero with a usage message when given no arguments (Module 1's scripting habit).
- *Wrong fixes to reject:* `wrong/after-only.sh` (the absolute number, not the growth: every pair comes out near 5%); `wrong/iowait-field.sh` (the fifth number); `wrong/busy-only.sh` (steal over user + system + steal, which gives 100.0 for a VM that is idle apart from being robbed).
- *Hints:* `paste` puts two files side by side; in `awk`, `$(i + 11)` is the matching field of the second line.

### 7.5 `example-cap-and-squeeze` (worked example, systemd lab), skills `local-vs-network-disk`, `stolen-or-capped`

A second worked example, placed here because the next recall block and both proofs use what it shows. (The validator asks for at least one worked example and does not forbid two; see Open questions.)

**What the container holds.**

- A data disk at `/dev/lab/data`: a 256 MB image file attached as a loop device at boot by the storage labs' `disks.sh`, with their `teardown.sh`.
- `shop-db.service`: writes 4 KiB blocks straight to the disk in a loop, with `IOWriteIOPSMax=/dev/lab/data 200` in its unit.
- `shop-cache.service`: a small program that holds 150 MB and touches every page of it over and over, printing `passes N` once a second. *Tried* as a 6-line Perl script (Perl is in the base image); Python would do as well.

**Steps** (each tried; the numbers are from the owner's machine and will differ a little):

1. *The disk with no cap.* `sudo fio --name=t --filename=/dev/lab/data --direct=1 --rw=randwrite --bs=4k --iodepth=1 --runtime=5 --time_based | grep -E 'IOPS|lat.*avg'`: about 6,800 IOPS, 0.15 ms each.
2. *Cap it the way a cloud caps a network disk.* The same `fio` under `sudo systemd-run --wait --pipe -p "IOWriteIOPSMax=/dev/lab/data 500"`: 499 IOPS, 1,996 KiB/s, 2.0 ms each. 500 × 4 KiB is 2,000 KiB/s; one write every 1/500 of a second is 2 ms.
3. *A deeper queue does not beat a cap.* Add `--iodepth=16 --ioengine=libaio`: still 503 IOPS, now 31.8 ms each, which is 16 ÷ 500.
4. *Big blocks meet the other cap.* Add `-p "IOWriteBandwidthMax=/dev/lab/data 8M"` and use `--rw=write --bs=1M`: 7 or 8 IOPS, 7,809 KiB/s. The throughput cap binds. Back to `--bs=4k` with both caps: 499 IOPS again. The IOPS cap binds.
5. *A service at its allowance.* `cat /sys/fs/cgroup/system.slice/shop-db.service/io.max`; read `io.stat` twice five seconds apart: `wios` grows by exactly 1,000, 200 a second; `io.pressure` shows it waiting.
6. *Squeeze a cache.* `journalctl -u shop-cache -n 3 -o cat`: tens of passes a second. `sudo systemctl set-property --runtime shop-cache MemoryHigh=64M`. Thirty seconds later: about one pass in twelve seconds; `memory.events` shows `high` in the hundreds and climbing; `memory.current` sits at 63 MB; `memory.swap.current` is growing; `systemctl is-active shop-cache` still says `active`; `journalctl -k` has no OOM line. Slow, not dead.
7. *Let it go.* `sudo systemctl set-property --runtime shop-cache MemoryHigh=infinity`: the passes come back.
8. *systemd's `taskset`.* `systemctl show shop-db -p AllowedCPUs -p EffectiveCPUs`, then `sudo systemctl set-property --runtime shop-cache AllowedCPUs=0` and `taskset -cp "$(systemctl show shop-cache -p MainPID --value)"`: the service may now run only on CPU 0. Undo it with `AllowedCPUs=` (empty).
9. *Save it.* `~/example/disk.txt` with three lines: the IOPS measured in steps 2, 3 and 4 (the 1 MiB run).

**Checks.** (a) Lines 1 and 2 of `disk.txt` are between 450 and 550; line 3 between 5 and 10. (b) `shop-cache` is active, `systemctl show -p MemoryHigh` is `infinity`, and its `memory.events` `high` count is above 0 (it was squeezed). (c) `shop-cache`'s `AllowedCPUs` is empty again. (d) `shop-db` is active with its cap unchanged.

**Wrong fixes.** `wrong/never-capped.sh` (the uncapped numbers in the file); `wrong/left-squeezed.sh` (MemoryHigh still 64M).

**Two things the writer must know.** With swap available (Docker Desktop has 4 GB) the squeezed service pages out and `memory.pressure` stays low (about 2%) while throughput falls by a factor of several hundred; with swap forbidden (`MemorySwapMax=0`) it barely moves and `memory.pressure` goes to 33%. So checks read the `high` counter and the service's own pass count, never a pressure threshold. And `docker exec` shells live in `/init.scope`, outside every service, so a cap on a service never slows the learner's own shell.

### 7.6 Recall on disks

| Id | Kind | Skill | Scenario | Right answer | Wrong answers |
| --- | --- | --- | --- | --- | --- |
| `mcq-what-survives-a-stop` | mcq | `local-vs-network-disk` | A batch server on AWS keeps its work files on the instance store. AWS's table (read 2026-11-10): data persists on reboot; it does not persist on stop, hibernate or terminate. The team stops it on Friday to save money and starts it on Monday. What do they find? | "The instance starts normally and the instance store is empty, because a stop erases it" | "The instance starts normally and the files are intact, because only a terminate erases them"; "The instance will not start at all, because its instance store was given to another tenant"; "The instance starts normally and the files are intact, because a stop is treated like a reboot" |
| `est-iops-times-block` | estimate | `local-vs-network-disk` | An AWS gp3 volume includes 3,000 IOPS and 125 MiB/s (read 2026-11-10). A database writes 16 KiB at a time, as fast as the volume allows. How many MiB a second is that? Tolerance: ±2% | 46.9. Working: `iops * kib / 1024` | 125 ("that is the throughput cap; at this block size the IOPS cap is reached first"); 187.5 ("divided IOPS by the block size") |
| `est-vm-or-disk-cap` | estimate | `local-vs-network-disk` | Azure's example (read 2026-11-10): a `Standard_D8s_v3` allows 12,800 uncached IOPS. It has three P30 disks of 5,000 IOPS each. An application drives all three as hard as it can. How many IOPS does it get in total? Tolerance: exact | 12,800. Working: `min(vm, disks * each)` | 15,000 ("the disks would allow it; the VM does not"); 5,000 ("that is one disk") |
| `io-stat-rate` | predict_shell | `local-vs-network-disk` | Three files from a service's cgroup: `io.stat.t0` (`7:2 rbytes=0 wbytes=409600000 rios=0 wios=100000 dbytes=0 dios=0`), `io.stat.t5` five seconds later (`wios=101000`, `wbytes=413696000`), `io.max` (`7:2 rbps=max wbps=max riops=max wiops=200`). Command: `a=$(grep -o 'wios=[0-9]*' io.stat.t0 \| cut -d= -f2); b=$(grep -o 'wios=[0-9]*' io.stat.t5 \| cut -d= -f2); echo "$(( (b - a) / 5 )) writes a second, cap $(grep -o 'wiops=[0-9]*' io.max \| cut -d= -f2)"` | `200 writes a second, cap 200` | A rate that sits exactly on its cap is the mark of a cap, as `nr_throttled` is for CPU |
| `mcq-queue-depth-at-a-cap` | mcq | `local-vs-network-disk` | A disk capped at 500 IOPS was measured twice with 4 KiB writes: queue depth 1 gave 499 IOPS at 2.0 ms each; queue depth 16 gave 503 IOPS at 31.8 ms each. A colleague wants to raise the queue depth further "to get more out of the disk". What do the numbers say? | "The cap sets the rate, so a deeper queue only makes each request wait longer in line" | "The disk is healthy, so a deeper queue will raise the rate once it passes thirty-two"; "The latency is the limit, so a deeper queue will bring each request's wait back down"; "The block size is the limit, so a deeper queue helps only when blocks are made larger" |
| `mcq-which-disk-for-what` | mcq | `local-vs-network-disk` | Three needs on one cloud VM: (1) the only copy of an orders database; (2) scratch space for a nightly sort of 300 GB; (3) a cache that is rebuilt from the database in ten minutes. Which goes where? | "The database on a network disk; the scratch space and the cache on the local disk" | "The database and the cache on the local disk; the scratch space on a network disk"; "All three on the local disk, with a snapshot of the local disk taken each night"; "The database and the scratch space on a network disk; nothing on the local disk" |

### 7.7 Ladder order for `topic.yaml`

`example-read-the-slice`, `mcq-vcpu-is-a-thread`, `slice-lscpu-cores`, `slice-siblings`, `est-cores-from-vcpus`, `mcq-smt-off-bill`, `numa-hardware-read`, `numa-which-node`, `mcq-numa-remote-memory`, `est-credits-per-hour`, `est-minutes-to-empty`, `credits-bucket-trace`, `mcq-standard-or-unlimited`, `mcq-three-clouds-burst`, `fill-credit-bucket`, `steal-from-proc-stat`, `mcq-stolen-or-capped`, `mcq-what-neighbours-share`, `psi-which-resource`, `write-steal-pct`, `example-cap-and-squeeze`, `mcq-what-survives-a-stop`, `est-iops-times-block`, `est-vm-or-disk-cap`, `io-stat-rate`, `mcq-queue-depth-at-a-cap`, `mcq-which-disk-for-what`.

**Questions that can come back, by skill** (practice items plus the review-only items of section 9): `vcpu-to-core` 5 + 2; `burst-credits` 6 + 2; `stolen-or-capped` 5 + 3; `numa` 3 + 2; `local-vs-network-disk` 6 + 3.

## 8. Proofs

### 8.1 Build: `build-capacity-review` (systemd lab), skills: all five

**The brief the learner gets** (no starter, no hints, tutor off): the shop is moving three servers to the cloud and wants a one-page capacity review. The evidence is in `/srv/review/`; the database's future disk is `/dev/lab/data`. Write `~/review/answers.txt` with one `key=value` line per item in the list, and leave `shop-db` running under its new disk tier's allowance.

**What the container holds.**

- `/srv/review/machines/app-1`, `db-2`, `arm-2`: three recorded machines in new shapes (for example 8 CPUs as 4 cores × 2 threads; 64 CPUs as 2 sockets × 16 cores × 2 threads on 2 NUMA nodes; 16 CPUs as 16 cores × 1 thread).
- `/srv/review/burst/`: an `instance.conf` and a 24-hour `usage.csv` for the burstable size the web tier is proposed to run on.
- `/srv/review/stat-before.txt`, `stat-after.txt`: two `/proc/stat` first lines from the current VM, ten minutes apart.
- `/srv/review/disk-tier.txt`: `iops=500`, `mib_per_s=8`: the network disk tier the database moves to.
- `shop-db.service` running with no I/O settings, writing to `/dev/lab/data`.

**Keys and checks** (one check per key, so a failure points at one skill; the check ids are what a checkpoint's `test_skills` would name):

| Key | What it is | Check | Skill |
| --- | --- | --- | --- |
| `cores.app-1`, `cores.db-2`, `cores.arm-2` | physical cores | equals the count the check takes from each tree | `vcpu-to-core` |
| `numa-nodes.db-2` | number of nodes | equals the tree's | `numa` |
| `node-of-cpu-40.db-2` | which node CPU 40 is on (it is a sibling thread, so the answer is not "the second half") | equals the tree's | `numa` |
| `steal-pct` | steal over the ten minutes | within 0.5 of the check's computation | `stolen-or-capped` |
| `credits-empty-minute` | the minute the bucket empties, or `never` | equals the check's simulation | `burst-credits` |
| `minutes-held-to-baseline` | as in the fill-in | equals the check's simulation | `burst-credits` |
| `disk-4k-iops` | writes a second at 4 KiB under the tier | between 450 and 550 | `local-vs-network-disk` |
| `disk-1m-mib-per-s` | MiB a second at 1 MiB under the tier | between 6.8 and 9.2 | `local-vs-network-disk` |
| `disk-1m-binding` | `iops` or `throughput` | `throughput` | `local-vs-network-disk` |
| (state) | `shop-db` runs under the tier | `systemctl show shop-db -p IOWriteIOPSMax -p IOWriteBandwidthMax` names `/dev/lab/data` with 500 and 8388608; the service is active; its `wios` over five seconds grows by no more than 2,600 | `local-vs-network-disk` |

**Lazy or wrong routes the checks must reject, each as a `wrong/*.sh`:**

- `cores-are-vcpus.sh`: writes the CPU counts. Fails the three `cores.` checks.
- `halved-arm.sh`: divides every machine by two. Fails `cores.arm-2`.
- `node-by-halves.sh`: says CPU 40 is on node 1 because 40 is past the middle. Fails `node-of-cpu-40.db-2` (the shape is chosen so that it is on node 0).
- `steal-from-one-reading.sh`: uses the second file alone.
- `no-floor.sh`: the credit simulation without the floor at zero.
- `cap-on-reads.sh`: sets `IOReadIOPSMax` instead of `IOWriteIOPSMax`. Fails the state check.
- `stopped-the-db.sh`: stops `shop-db` so nothing exceeds the tier. Fails "active".
- `iops-only.sh`: sets the IOPS cap and not the throughput cap, and answers `disk-1m-binding=iops`.

**Reference solution.** A drop-in for `shop-db` with the two write caps, `daemon-reload`, `restart`; the pipelines from the worked examples for the rest; `fio` under `systemd-run` with the same two properties for the two disk numbers. The numbers may also be worked by hand; that is still the skill.

### 8.2 Debug: `debug-crawling-db` (systemd lab), skills `stolen-or-capped`, `local-vs-network-disk`, `vcpu-to-core`

**The prompt, in full, is this and no more:**

> `shop-db` is the shop's database on this server. Its data disk, `/dev/lab/data`, is provisioned for 500 IOPS and 8 MiB a second, and the database is meant to be able to use all of that. It may use up to 256 MB of memory and no more, because `shop-batch`, the nightly batch job on the same server, needs the rest. `shop-batch` is kept on CPU 0 on purpose and must keep running there.
>
> Checkout is slow. The database's own log (`journalctl -u shop-db`) prints how much work it gets through each second, and it is a small fraction of what it managed last week. Three things are wrong with how this server treats `shop-db`. Find them and put them right without stopping either service and without giving `shop-db` more than it is meant to have. Then run the checks.

It gives the purpose, the symptom and the count. It does not say that the faults are settings, which settings, or where.

**The three planted faults** (for the writer only):

1. `IOWriteIOPSMax=/dev/lab/data 20` in a drop-in: a twenty-fifth of the disk's allowance.
2. `MemoryHigh=48M` while the database's working set is about 150 MB: it is throttled and paging, alive and crawling. `MemoryMax=256M` is correct and must stay.
3. `AllowedCPUs=0`: pinned onto the one CPU the batch job is kept on, while the other CPUs idle.

`shop-db` logs `passes N writes M` each second, so each fault shows in its log and all three must go for the numbers to recover. **A caution for the writer:** build it as two processes in the one service, a writer (4 KiB direct writes) and a memory worker (the page-toucher), so that each rate depends on one fault. Then prove it before writing the checks: with only the I/O fault fixed, only `disk-allowance` and `disk-rate` should turn green; with only the memory fault fixed, only `memory-not-squeezed`. Whether a memory throttle on the cgroup also slows a process that only does direct writes was not tried; if it does, change `disk-rate` to "the write rate is at least ten times what it was when the lab started" and let `disk-allowance` carry the skill.

**Checks.** The descriptions shown to the learner state the end state, never the bug.

| Check id | Description shown | Command, in outline | Rejects |
| --- | --- | --- | --- |
| `both-running` | "shop-db and shop-batch are both running, and shop-db has not been restarted by a crash." | both `is-active`; `NRestarts` 0 | stopping the batch job; a fix that gets the database killed |
| `disk-allowance` | "shop-db may use the data disk's full allowance and no more." | `systemctl show` gives write caps of 500 IOPS and 8388608 bytes on `/dev/lab/data` | the cap left at 20; the cap deleted, which the real disk would never allow |
| `disk-rate` | "shop-db's writes have picked up." | `wios` in `io.stat` grows by at least 1,500 in five seconds | a cap that is right on paper but not applied (no `daemon-reload`, no restart) |
| `memory-ceiling` | "shop-db can still never use more than 256 MB." | `MemoryMax` is 268435456 | removing or raising the hard limit to stop the paging |
| `memory-not-squeezed` | "shop-db is no longer being slowed for memory." | the `high` count in `memory.events` is the same after eight seconds, and `memory.swap.max` is not 0 | `MemoryHigh` still below the working set; forbidding swap, which turns paging into stalling |
| `own-cpus` | "shop-db is free to run on CPUs the batch job is not using." | `cpuset.cpus.effective` of `shop-db` includes at least one CPU other than 0 | still pinned to CPU 0 |
| `batch-still-pinned` | "shop-batch is still kept on CPU 0." | `systemctl show shop-batch -p AllowedCPUs` is 0 | unpinning the batch job instead, which lets the noisy job loose on every CPU |

**Known-wrong fixes** (`wrong/`, one fault left or one shortcut taken each): `io-cap-removed.sh`, `io-cap-still-20.sh`, `memory-max-raised.sh`, `swap-forbidden.sh`, `still-on-cpu-0.sh`, `batch-unpinned.sh`, `batch-stopped.sh`.

**What makes this checkable.** Tried on the owner's machine: `AllowedCPUs=` sets `cpuset.cpus` and `cpuset.cpus.effective` under systemd in a privileged container, `systemctl set-property` changes it live, and `taskset -cp` agrees. The checks read settings, counters and structure. They do not read `cpu.pressure`, `mpstat` or a throughput figure for CPU, because those belong to the whole machine: during the trial the host was busy with other containers (load 14 on 8 CPUs) and a service moved off the shared CPU sped up by only 30%.

### 8.3 Explain

**Prompt.**

> A team moved a database from a physical server with 16 cores to a cloud VM with 16 vCPUs of a burstable type, and put its data on the VM's local disk because "it's the fast one". A week later the database is slow every afternoon, a colleague blames "noisy neighbours", and after the VM was stopped over a weekend the data was gone. Explain, in your own words: what 16 vCPUs usually are and how you would check; how a burstable instance's credits work and why the slowdown took a week to show; how you would tell stolen CPU from a cap of the machine's own from a machine that is simply too small, and what a neighbour can and cannot take from you; why the data disappeared and what a network disk would have cost in speed; and how the three clouds differ on any two of these.

**Rubric.**

| Id | Required | Description |
| --- | --- | --- |
| `vcpu` | yes | On most x86 instance types a vCPU is one hardware thread and two share a core, so 16 vCPUs are 8 cores; Arm types and some AMD types give a core per vCPU; `lscpu`'s threads per core, cores per socket and sockets, or the provider's table, say which. |
| `credits` | yes | A burstable instance earns credits at a fixed rate set by its baseline and spends them in proportion to CPU use; below the baseline the balance grows to a limit, above it the balance falls; a steady load a little above the baseline takes days to empty the bucket, and then the instance is held to its baseline (or, in AWS's unlimited mode, billed for the surplus). |
| `stolen-capped-busy` | yes | Steal (`st`, the eighth number in `/proc/stat` over an interval) is CPU the host withheld and points at a burstable or shared-core instance out of credits or an overcommitted host; throttled periods in `cpu.stat`, a memory throttle or a disk at its allowance are caps of the machine's own and show no steal; a run queue longer than the CPU count with no steal and no throttling is a machine that is too small. Each has a different remedy. |
| `neighbours` | yes | On fixed-size instances the provider dedicates cores to the instance (AWS documents pinning and that two customers never share a core at once), so a neighbour cannot take CPU time; shared caches, memory bandwidth, disks and the network can still be contended. Dedicated hosts or sole-tenant nodes remove other tenants altogether. |
| `disks` | yes | A local (instance store, temporary, Local SSD) disk is physically in the host: fast, and erased when the instance stops or moves; a network disk persists but has an IOPS and a throughput allowance, and the VM has its own, and you get the smaller; throughput is IOPS times block size until the throughput cap binds. |
| `clouds-differ` | yes | Any two correct differences, for example: AWS T instances default to unlimited mode and bill surplus credits while Azure B-series is throttled to its base; Google's shared-core types have no visible bank and burst for seconds; Google bills all vCPUs when SMT is off; which sizes have a local disk at all. |
| `numa` | no | Large instances span NUMA nodes; memory on the far node is slower; keep a process's CPUs and memory on one node. |

**Model answer.** To be written with the topic, about 350 words, following the rubric rows in order with the numbers from the lesson (t3.large at 35%: six days).

## 9. Review pool

Short, mixed, mostly a judgement or a sum on real numbers. At least two of every skill, at least one `predict_shell` (the validator's rule until `estimate` counts as "code or predict").

From the practice ladder: `est-cores-from-vcpus`, `slice-siblings`, `est-minutes-to-empty`, `credits-bucket-trace`, `steal-from-proc-stat`, `mcq-stolen-or-capped`, `numa-which-node`, `mcq-numa-remote-memory`, `est-vm-or-disk-cap`, `mcq-queue-depth-at-a-cap`.

Review-only items (fresh numbers and stories, so a come-back question is never the one just missed):

| Id | Kind | Skill | Scenario | Right answer | Mistakes or wrong answers |
| --- | --- | --- | --- | --- | --- |
| `est-cores-three-rows` | estimate | `vcpu-to-core` | AWS's table (read 2026-11-11): `m7i.large` 2 vCPUs, 2 threads per core; `m7g.large` 2 vCPUs, 1 thread per core. You run 8 of each. How many physical cores in all? Exact | 24. Working: `8 * 2 / 2 + 8 * 2 / 1` | 32 ("every vCPU counted as a core"); 16 ("every machine halved") |
| `mcq-which-vcpu-is-a-core` | mcq | `vcpu-to-core` | You need 8 physical cores for a compute-bound job and want to pay for no idle threads. Each cloud's pages (read 2026-11-10 and 11) say which sizes give a core per vCPU. Which choice gives 8 cores from 8 vCPUs? | "An Arm size such as AWS `m8g.2xlarge`, where each vCPU is one core" | "An Intel size such as AWS `m7i.2xlarge`, where each vCPU is one core"; "A burstable size such as AWS `t3.2xlarge`, where each vCPU is one core"; "Any 8-vCPU size, because providers count vCPUs in cores, not threads" |
| `est-hours-to-empty` | estimate | `burst-credits` | AWS (read 2026-11-10): `t3.large`, 2 vCPUs, earns 36 credits an hour, holds at most 864. A service runs it steadily at 35% from a full bucket, in standard mode. After how many hours is the bucket empty? ±1 | 144. Working: `full / (vcpus * util / 100 * 60 - earn)` | 20.6 ("ignores what it earns"); 24 ("the bucket holds a day's earnings, but it is draining at 6 an hour, not 36") |
| `est-unlimited-bill` | estimate | `burst-credits` | AWS (read 2026-11-10): surplus credits on T3 cost $0.05 a vCPU-hour; `t3.large` has 2 vCPUs and a 30% baseline. It runs at 100% for a 730-hour month in unlimited mode. What is the surplus charge? ±1% | $51.10. Working: `vcpus * (100 - baseline) / 100 * hours * rate` | $73.00 ("the baseline's share is already paid for"); $25.55 ("one vCPU") |
| `mpstat-steal-per-cpu` | predict_shell | `stolen-or-capped` | `mpstat.txt` is `mpstat -P ALL 5 1` on a 2-vCPU VM, in Ubuntu 24.04's layout, with `%steal` 61.20 on CPU 0 and 58.80 on CPU 1. Command: `awk '$1 != "Average:" && $2 ~ /^[0-9]+$/ {print "cpu" $2, $9}' mpstat.txt` (the file also has `mpstat`'s `Average:` lines, which the first test skips) | `cpu0 61.20` then `cpu1 58.80` | Both vCPUs robbed alike: a whole-VM limit, not one unlucky core |
| `mcq-remedy-for-spent-credits` | mcq | `stolen-or-capped` | A reporting job runs flat out for six hours a night on a `B2s_v2` (Azure, base 40%, read 2026-11-10). By the second hour its "CPU Credits Remaining" is 0 and it takes three times as long as on a laptop. Which change addresses the cause? | "Move the job to a fixed-size VM of the same vCPUs, since it needs sustained CPU" | "Raise the job's priority with `nice`, since a higher priority gets more of the CPU"; "Remove the CPU quota on the job's service, since the quota is what throttles it"; "Add a second data disk to the VM, since the job is waiting on its disk allowance" |
| `mcq-slow-not-dead` | mcq | `stolen-or-capped` | A cache service answers a hundred times slower than yesterday. It is `active`, there is no OOM line in the kernel log, `st` is 0, and its `memory.events` shows `high` rising by hundreds a minute with `memory.current` level at 64 MB. What is happening? | "It is over its `memory.high` throttle, so the kernel keeps slowing it and paging it out" | "It has hit its `memory.max` wall, so the kernel keeps killing it and systemd restarts it"; "It has used its CPU quota, so the kernel stops it for the rest of each 100 ms period"; "It is losing CPU to the host, so the kernel can only run it when a neighbour is idle" |
| `numa-distance` | predict_shell | `numa` | `numactl.txt` ends with the distance table for two nodes (10, 21, 21, 10). Command: `awk '/^ *0:/ {print "from node 0 to node 1:", $3}' numactl.txt` | `from node 0 to node 1: 21` | 10 is local; 21 is the kernel's rough "about twice as costly" |
| `mcq-numa-when` | mcq | `numa` | Two VMs run the same in-memory database. `lscpu` on the first says `NUMA node(s): 1` (8 vCPUs); on the second, `NUMA node(s): 2` (96 vCPUs). For which is binding CPUs and memory to one node worth doing? | "Only the second: it spans two nodes, so memory can land on the far one" | "Only the first: it is small, so each remote access costs it relatively more"; "Both: every VM has remote memory, and binding always shortens the path"; "Neither: the hypervisor hides the nodes, so binding has no effect in a VM" |
| `est-throughput-bound-iops` | estimate | `local-vs-network-disk` | AWS gp3 includes 3,000 IOPS and 125 MiB/s (read 2026-11-10). A backup writes 256 KiB at a time. How many writes a second does the volume allow? Exact | 500. Working: `min(iops, mib * 1024 / kib)` | 3,000 ("at this block size 3,000 writes would be 750 MiB/s, over the throughput cap"); 750 ("that is the MiB/s the IOPS cap would allow, not a rate of writes") |
| `mcq-local-disk-three-clouds` | mcq | `local-vs-network-disk` | A VM's host fails and the provider restarts the VM on another host. What has become of the files on its local disk, on any of the three clouds (pages read 2026-11-10)? | "They are gone: the local disk was in the failed host and does not follow the VM" | "They are intact: the provider copies the local disk to the new host first"; "They are intact: local disks are network disks under a different name"; "They are gone on AWS only: Azure and Google keep local disks across hosts" |
| `mcq-tiers-order` | mcq | `local-vs-network-disk` | A lookup makes 10,000 small random reads one after another. Using the lesson's rough figures (RAM 100 ns, a local NVMe disk 20 µs, a network SSD 1 ms a read), about how long does it take from each? | "1 ms from RAM, 0.2 s from the local disk, 10 s from the network disk" | "1 ms from RAM, 2 ms from the local disk, 10 ms from the network disk"; "1 s from RAM, 20 s from the local disk, 100 s from the network disk"; "0.1 ms from RAM, 0.2 s from the local disk, 1 s from the network disk" |

`review_pool:` in `topic.yaml`: the ten ladder items above plus these twelve.

## 10. What needs platform work first

| Need | Why | Smallest version that would do |
| --- | --- | --- |
| The `estimate` recall type | Ten items here ask for a number. As multiple choice they still work, but the learner picks rather than produces, and the choices give away the size of the answer. | As specified in `estimate-questions.md`. Until it exists every estimate above ships as `mcq` built from its answer and mistakes; nothing in this topic waits for it. |
| Nothing in `tools/labcheck.py` | Every lab uses the existing plain and systemd modes, numeric `expect` operators and the storage labs' loop-device pattern. | None. Add `fio numactl sysstat` to this topic's `tail-common`. |
| A check that `io.max` and `memory.high` behave on CI's runners | They were tried only on Docker Desktop's WSL2 kernel. GitHub's Ubuntu runners should have block-layer throttling and swap, but nobody has run it there. | Open the first lab's pull request early and read the Labs job; if `io.max` is unsupported there, the disk steps fall back to recorded `fio` output and the debug loses its first fault. |
| Recordings from real cloud VMs (authors, once) | The three machine trees and every `vmstat`, `mpstat` and `/proc/stat` fixture are built to the real formats but with invented numbers and a placeholder model name. One question is open and only a real VM can settle it: what a Linux guest on an Azure B-series VM shows when its credits are gone (steal, or nothing). | One capture run in the owner's subscription, after a budget alert is in place: three small VMs for about fifteen minutes (an Intel D2s_v5, an Arm D2ps_v6, an AMD D2as_v5) to copy `/proc/cpuinfo` and `/sys/devices/system/cpu`; and one B2ts_v2 driven flat out for 90 minutes while `vmstat 60` and `/proc/stat` are saved. Cost at the prices read: about $0.03 for the burstable VM with its disk and address, under $0.10 for the three others, so well under $0.25 in all. The topic can be `ready` before this run; the fixtures say "representative" until then. |
| An optional real-cloud lab (not recommended for now) | "Drain a burstable VM and watch it slow" would be memorable. | See Open questions. It would be an Azure lab with a stated cost of about $0.03, a budget alert first, auto-shutdown, a tag and a teardown check. It needs the cloud mode of the lab checker (ADR-0014), which does not exist, and it needs the learner to know how to create a VM, which the track teaches in Module 8. |

## 11. Cost and time

**Cost to the learner: nothing.** Every lab is a container on their own machine; every question runs in the browser. The only money is the Claude API's few cents for grading the explanation.

**Time, counted honestly.**

| Part | Minutes |
| --- | --- |
| Lesson intro and recap | 15 |
| Reading (resources 0 to 5, 8 to 11, 13 to 16, the named sections only) | 60 |
| 22 quick questions at about 1.5 minutes | 35 |
| `example-read-the-slice` | 20 |
| `fill-credit-bucket` | 20 |
| `write-steal-pct` | 30 |
| `example-cap-and-squeeze` | 30 |
| Build | 60 |
| Debug | 45 |
| Explain | 15 |
| **Total** | **330** |

`estimated_minutes: 330`. The outline's 240 is a placeholder; Module 1's topics are 90 to 120. This is the widest row in the module's table (nine ideas in one line of the spec), which is why it is the longest.

## 12. Open questions, each with a recommendation

Under the owner's rule: the best learning and retention that is free or inside the Azure budget.

1. **Split the topic?** At five and a half hours it is three times a Module 1 topic. It divides cleanly: `csa.hw.cores-memory` keeps the CPU side (`vcpu-to-core`, `burst-credits`, `stolen-or-capped`, `numa`: about 3.5 hours) and a new topic, say `csa.hw.disks` ("Local and network disks"), takes `local-vs-network-disk`, which would grow to three skills (the tiers, what survives, which cap binds) with `example-cap-and-squeeze`'s disk half as its worked example. Shorter topics mean more proofs and more reviews for the same material, which is what retention wants. It changes the spec (one more row, 21 topics in the module) and needs a second build, debug and explain. **Recommendation: split, when the module is written.** This brief is laid out so the disk material lifts out; if the owner prefers the spec as it stands, write it as one topic exactly as above.
2. **Two worked examples in one ladder.** The validator requires at least one and the app shows a list, so two should work, but no topic has done it. **Recommendation: keep both;** a worked example before each new kind of task is the "worked examples, then fading" rule. Check the topic page with two before marking it `ready`.
3. **What "memory tiers" means in the spec.** Read here as the hierarchy from cache to network disk. **Recommendation: keep that reading** and leave memory-optimised instance families to Module 12.
4. **A real burstable VM for the learner.** Draining a B2ts_v2 costs about three cents and takes 40 minutes of waiting. It would need the learner to create and delete an Azure VM six modules before the track teaches that, and the cloud checker. **Recommendation: no required cloud lab in this topic.** The arithmetic and the recorded numbers teach the same thing; the authors' capture run (section 10) makes the recordings genuine. Offer the real thing in Module 12 (Compute), where the VM skills exist.
5. **Should the main resource be the Nitro chapter?** It is the best single text but its subject on the page is security. **Recommendation: yes,** with the Intro telling the learner what to read it for; fall back to AWS's "CPU options" page if the owner's first pass finds it too hard.
6. **PSI and `memory.high` inside `stolen-or-capped`, or a sixth skill?** They are two more witnesses in one diagnosis, not a separate ability. **Recommendation: keep five skills.**
7. **A fixed percentage for what Hyper-Threading gains.** No provider page read gives one, and Intel's page gives none. **Recommendation: teach "more than one, well short of two, and it depends on the work"** with Google's sentence as the source, and never ask for a number.

## For the checkpoint designer: Checkpoint 2, part 2, "Diagnose a slow VM"

The spec line is "Diagnose a slow VM: CPU steal, throttling and memory pressure." This is the design, ready to be made the checkpoint's `debug`.

### The constraint that shapes it

Steal cannot be produced in a container: the learner's machine decides it, and on Docker Desktop it is zero. Throttling and memory pressure can be produced for real (both were tried). So the part has a **recorded half**, which is the only honest way to include steal, and an optional **live half**.

### Recommended form: one lab, `debug-slow-vms` (systemd lab; a plain lab if the live half is dropped)

**Half A: four tickets (required).** `/srv/tickets/vm-a` to `vm-d` hold what an on-call script saved from four slow VMs at the moment of the complaint. Every folder has the same files, so nothing about the file list hints at the cause:

- `ticket.txt`: what the user said ("the nightly report takes three times as long"), the instance's size in neutral terms (vCPUs, memory, "burstable: baseline 20%" or "fixed size"), and, for a burstable one, the credit balance at the time.
- `lscpu.txt`, `uptime.txt`, `free.txt`.
- `vmstat.txt`: sixty lines of `vmstat 1`, in Ubuntu 24.04's layout (with the `gu` column).
- `mpstat.txt`: one `mpstat -P ALL 60 1`.
- `stat-before.txt`, `stat-after.txt`: `/proc/stat`'s first line, sixty seconds apart.
- `pressure/cpu`, `pressure/memory`, `pressure/io`.
- `cgroup/` for the VM's main service: `cpu.max`, `cpu.stat.before`, `cpu.stat.after`, `memory.max`, `memory.high`, `memory.current`, `memory.events.before`, `memory.events.after`, `io.max`, `io.stat.before`, `io.stat.after`.
- `dmesg.txt`.

`seed.sh` writes all of it from fixed numbers, so the checks compute every right answer from the files.

| VM | The truth | What the evidence shows | The decoys in the same folder |
| --- | --- | --- | --- |
| `vm-a` | steal, from spent credits | burstable, credit balance 0; `st` about 80 on both vCPUs; `us` + `sy` about 20, the baseline; `cpu.max` is `max`, no throttled periods; memory fine | a load average of 2.4 on 2 CPUs, which looks like "too small" |
| `vm-b` | the service's CPU quota | fixed size; `st` 0; `id` about 70; `nr_throttled` grows by 330 of 600 periods in the minute (and by far less as a share since boot, so the totals mislead); `cpu.pressure` raised | `free` shows little free memory but plenty `available` |
| `vm-c` | memory pressure | fixed size; `st` 0; `available` under 3% of memory; `si` and `so` in the thousands of KiB a second; `wa` about 35; `pressure/memory` `some avg10` about 45 and `full` about 30; `memory.events` `high` rising; no OOM line in `dmesg` | `wa` and a raised `pressure/io`, which look like a slow disk but are the swapping |
| `vm-d` | none of the three: one thread at its limit | fixed size; `st` between 0 and 1; no throttling; memory fine; all pressure near 0; `mpstat` shows one CPU at 99% `usr` and the rest idle | an average CPU of 25%, which looks healthy |

The fourth VM matters. Without it the answer is a permutation of three known causes; with it the learner has to be willing to say "none of these".

**What the learner writes:** `~/diagnosis/vm-a.txt` and so on, three lines each.

```text
cause=steal
evidence=80.0
fix=fixed-size-or-unlimited
```

- `cause` is one of `steal`, `cpu-quota`, `memory-pressure`, `disk-cap`, `too-few-cpus`, `single-thread`, `healthy`. The list is longer than the truths on purpose.
- `evidence` is one number, and the lab's README says which number goes with which cause: for `steal`, the steal percentage over the sixty seconds from the two `stat` files; for `cpu-quota`, the percentage of periods throttled between the two `cpu.stat` files; for `memory-pressure`, `some avg10` from `pressure/memory`; for `single-thread`, the busiest CPU's `%usr`; for `disk-cap`, writes a second from the two `io.stat` files; for `too-few-cpus`, the average of `vmstat`'s `r`; for `healthy`, 0.
- `fix` is one of `fixed-size-or-unlimited`, `dedicated-host`, `raise-cpu-quota`, `more-memory-or-raise-throttle`, `faster-disk-tier`, `more-vcpus`, `fix-the-program`, `nothing`.

**Checks, three per VM,** each with `test_skills`:

| Check | Passes when | `test_skills` |
| --- | --- | --- |
| `vm-a-cause`, `vm-a-evidence`, `vm-a-fix` | cause is `steal`; evidence within 1.0 of the check's computation; fix is `fixed-size-or-unlimited` | `csa.hw.cores-memory/stolen-or-capped`, `csa.hw.cores-memory/burst-credits` |
| `vm-b-*` | `cpu-quota`; within 1.0 of 55.0; `raise-cpu-quota` | `csa.linux.cpu/throttling`, `csa.hw.cores-memory/stolen-or-capped` |
| `vm-c-*` | `memory-pressure`; within 0.5 of the file's value; `more-memory-or-raise-throttle` | `csa.linux.memory/swap-paging`, `csa.hw.cores-memory/stolen-or-capped` |
| `vm-d-*` | `single-thread`; within 1.0 of the busiest CPU; `fix-the-program` | `csa.linux.triage/first-minute`, `csa.hw.cores-memory/stolen-or-capped` |

**Wrong answers to ship as `wrong/*.sh`,** each an honest mistake: `everything-is-steal.sh`; `vm-a-too-few-cpus.sh` (believed the load average); `vm-b-since-boot.sh` (throttled share from the totals, not the minute); `vm-c-disk-cap.sh` (believed `wa`); `vm-d-healthy.sh` (believed the average); `dedicated-host-for-credits.sh` (the right cause for vm-a with a remedy that costs ten times more and does not address credits).

**Half B: the live VM (recommended if the checkpoint's time allows; drop it without touching half A).** The lab machine itself is the fifth VM. `shop-api` on it is slow now. The prompt gives the purpose (what it serves, that it may use at most one CPU's worth and 256 MB), the symptom (its own log's rate) and the count: **two** things are wrong. Planted: a CPU quota far below its bursts (Module 1's skill) and a `MemoryHigh` below its working set (this topic's worked example). Checks as in section 8.2 of this brief: throttled periods stop rising; the `high` count stops rising; the quota is still finite and no more than one CPU; `MemoryMax` is unchanged; the service was not stopped or restarted by a crash. `test_skills`: `csa.linux.cpu/throttling`, `csa.hw.cores-memory/stolen-or-capped`.

**Why recorded evidence is a fair "debug".** ADR-0002's third proof is finding and fixing faults in work you did not make. For three of these machines the fix is a decision (resize, change the credit mode, add memory), which is what an architect does with a slow VM; the fix vocabulary records the decision and the checks reject the expensive wrong ones. The live half adds a fix made with the learner's own hands.

### What to tell the learner, and what not to

The prompt names the system (four customer VMs and this one), the symptom of each (in `ticket.txt`, in the user's words), and the number of faults on the live VM. It does not say which VM has which cause, that one has none of the three, or where to look. Check descriptions say "vm-b's cause is right", never what the cause is.

### Standards

- **Time.** The spec's checkpoints have time limits; lab exercises have no time-limit field today (the audit noted this for Checkpoint 1). Suggested target, stated in the prompt and not enforced: 40 minutes for half A, 15 for half B.
- **Tolerances** are in the table above and in the lab's README, so the learner knows how exact to be.

### Getting unstuck (ADR-0012)

- **A solved sibling:** `example-ticket`: one more VM, a disk at its I/O allowance (`disk-cap`), worked in labelled steps in the fixed order the module teaches: is CPU being stolen (`st`)? is something capped (`cpu.stat`, `memory.events`, `io.stat` against `io.max`)? is something simply full (`r`, `available`)? is it one thread (`mpstat`)? The order is the lesson's decision table.
- **Fresh versions:** the same four truths under other names with other numbers, and the causes on different letters. Because `seed.sh` writes the evidence from a small table of numbers, a version is a new table; two are cheap.

### What stays unproven

- The fixtures are built to the real file formats (checked on Ubuntu 24.04 in a container) with invented numbers. They become genuine after the capture run in section 10 of this brief.
- Whether an Azure B-series VM out of credits shows steal is not known. `vm-a` is therefore described as a burstable VM in neutral terms with AWS's numbers (baseline 20%), where AWS's own support article is reported to list a depleted balance as a cause of steal. If the capture run shows that Azure reports no steal, that is itself worth a fifth ticket in a later revision: a VM whose CPU is pinned at exactly its baseline with `st` 0.
- Half B's mechanics were tried on Docker Desktop only, not on CI's runners.

## Appendix: what was tried in Docker

All on 2026-11-10 and 2026-11-11, in throwaway `ubuntu:24.04` containers that were removed afterwards. The scripts are in `experiments/` beside this file.

| Tried | Script | Result |
| --- | --- | --- |
| `lscpu --sysroot` on generated machine trees | `sysroot3.sh` | Works. Three shapes read back correctly, including two NUMA nodes and sibling threads. Needs the hexadecimal mask files. Prints the host's `Architecture:` line. |
| `io.max` on a loop device, raw cgroup files | `cg.sh` | 400 direct 4 KiB writes at a 100 IOPS cap took 3.89 s; 4 MiB at a 1 MiB/s cap took 4.01 s. |
| The same through systemd with `fio` | `sysd/t1.sh` | No cap: 6,758 IOPS. 500 IOPS cap: 499 IOPS, 2.0 ms. Depth 16: 503 IOPS, 31.8 ms. With an 8 MiB/s cap and 1 MiB blocks: 7 IOPS, 7,809 KiB/s. A capped service's `io.stat` grew by exactly 200 writes a second. |
| `MemoryHigh` on a service that touches 150 MB | `sysd/t2.sh` | No limit: 745 passes in 12 s. `MemoryHigh=64M`: 1 pass, 88 MB in swap, `high` 1,075, still active. With swap forbidden as well: still allocating after 12 s, `memory.pressure` 33%. `MemoryMax=64M` without swap: OOM-killed, as in Module 1. |
| `AllowedCPUs=` for two services on CPU 0 | `sysd/t3.sh` | `cpuset.cpus.effective` is 0 for both; `taskset -cp` agrees; `set-property` moves one live. Throughput and `cpu.pressure` were too noisy to check on a busy host. |
| Output layouts | inline | `vmstat` has a `gu` column on 24.04; `mpstat`, `sar -u ALL`, `numactl --hardware` and `/proc/pressure/*` as quoted in the facts table. |
