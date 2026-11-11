# Writing brief: Checkpoint 2, the right machine (`csa.m2.checkpoint`)

The checkpoint that ends Module 2, "Virtualization, hardware and Windows". The spec gives it three parts:

1. Right-size five described workloads across the three clouds, including a move to Arm and a GPU job. Code checks the estimates.
2. Diagnose a slow VM: CPU steal, throttling and memory pressure.
3. Stand up a small Active Directory domain, join a Windows and a Linux VM to it, and explain how Entra ID would differ.

**Part 1 is designed here in full.** Parts 2 and 3 belong to the designers of `csa.hw.cores-memory` and `csa.hw.windows-ad`, whose briefs I haven't seen. This brief gives each a checkpoint-level design and says plainly what it assumes about their topics, so the two can be reconciled. Every assumption is marked **Assumed**.

Companion files: [price-fixture-2026-11.md](price-fixture-2026-11.md) and its CSV, [estimate-questions.md](estimate-questions.md), and the topic 20 brief, [csa.hw.windows-licensing.md](csa.hw.windows-licensing.md).

## What the checkpoint proves

That the learner can look at a workload and a machine and say whether they fit: pick the size, the processor, the GPU and the licence; tell from a machine's own numbers why it is slow; and stand up the directory that Windows estates hang on.

### The six-month core

A checkpoint has no review pool; its parts bring topic skills back through `test_skills` (ADR-0012). What it should leave behind:

1. **Size on the busy hours, not the average and not the worst second,** then check four things in order: does it fit (CPU, memory, GPU memory), may it run there (processor, operating system, licence), is anything smaller enough, what does it cost for the hours it runs.
2. **A slow machine has a reason you can read:** the hypervisor took the CPU, your own limit stopped the process, or memory is being reclaimed. Each has its own number, and each has a different fix.
3. **A domain is DNS, Kerberos and a directory,** and a machine joins it by getting an account in it. Entra ID is a different thing with a similar job.

## Three parts, and a platform with two slots

A checkpoint's `prove` holds one `build`, one `debug` and one `explain` (`tools/content_model.py`, `Prove`). `web/src/progress/progress.ts` counts the build (or any of `unstuck.versions`) and the debug. Checkpoint 1 met the same wall: the spec gave it two parts and only one was built, which the audit recorded as "narrower than the spec".

| Spec part | Slot | Kind |
| --- | --- | --- |
| 1, the right machine | `prove.build`, with `unstuck.example`, `steps` and `versions` | a plain lab |
| 2, the slow VM | `prove.debug` | a systemd lab |
| 3, the domain | **no slot today** | an Azure lab (or a local one; see part 3) |
| 3, "how Entra ID would differ", and the module as a whole | `prove.explain` | graded by AI |

**Recommended: add `prove.more`.** A list of further exercises a checkpoint requires, each a build or a debug, all of which must pass. It is the smallest change that lets a checkpoint have as many parts as its spec: one field in `Prove`; the validator checks each is a build or debug with `test_skills`; `progress.ts` requires each; the checkpoint page shows them as "Part 3". Checkpoints 3, 5 and 7 have two or three parts each and will need it too, and Checkpoint 1's unbuilt second part could use it.

**If that isn't built before this module is written:** part 1 is the build, part 2 the debug, the explain covers Entra ID, and the hands-on half of part 3 lives only in topic 19's own build. Then the spec's text for Checkpoint 2 must be amended in the same pull request to say so, and the devlog must record it, so that what is built and what is specified don't drift apart again.

## Prerequisites

`csa.hw.hypervisors`, `csa.hw.cpu-architectures`, `csa.hw.cores-memory`, `csa.hw.gpus`, `csa.hw.windows-ad`, `csa.hw.windows-licensing`. All six must be `ready` before the checkpoint can be.

From Module 1 the labs use: `csa.linux.shell` (reading CSV files with `sort`, `cut` and `awk`), `csa.linux.cpu` (cgroup quota and throttling, steal in `top`), `csa.linux.memory` (cgroup memory limits), `csa.linux.services` (drop-ins, `systemctl`), `csa.linux.triage` (the first-minute checklist), `csa.linux.permissions` (SSH keys, for part 3). `test_skills` may name their skills, since they come before this checkpoint.

**Terms the checkpoint may use without defining:** only those the six topics define. In particular part 1's brief must not use "p95" or "95th percentile" unless `csa.hw.cores-memory` teaches it. **Assumed:** it does, as part of right-sizing from metrics. If it doesn't, that topic must, because the spec's right-sizing drill ("from a week of metrics") can't be done without it.

## What this brief assumes about the other topics

| Topic | Assumed skills (ids are placeholders; replace with the real ones) | Assumed machinery |
| --- | --- | --- |
| `csa.hw.cores-memory` | `vcpu-vs-core`; `burstable-credits` (baseline, credits, what happens at zero); `noisy-neighbours` (steal, and that nothing inside the VM fixes it); `right-size` (percentiles, headroom, choosing a size from a week of metrics); `memory-pressure` (reclaim and stall, apart from the OOM kill of Module 1); `disk-kinds` | A lab pattern for steal, which a container can't produce for real: a stand-in for the cloud console (`lab-instance show` and `lab-instance resize SIZE`, always exiting 0, like the boot labs' `lab-launch`) and a `vmstat` stand-in, first in `PATH`, whose `st` column follows the instance's credit state (the README's rule for numbers that belong to the whole machine). Real cgroup throttling and real memory pressure, as in Module 1. |
| `csa.hw.cpu-architectures` | `instruction-sets`; `arm-savings` (what the price difference is and isn't); `rebuild-for-arm` (what must be rebuilt, and what can't be) | none needed here |
| `csa.hw.gpus` | `vram-fit` (GPU memory decides whether a job runs at all); `read-gpu-utilisation`; `gpu-sharing` (MIG, fractions) | none needed here; part 1 gives GPU numbers as a file |
| `csa.hw.windows-ad` | `domain-basics`; `kerberos`; `group-policy`; `domain-join`; `entra-vs-adds` | One of two shapes, see part 3: a real Windows Server domain built in the learner's Azure subscription, or a Samba domain controller in a local container. The budget alert, the auto-shutdown, the tag and the teardown are taught there first, because that topic holds the track's first real-cloud lab. |
| `csa.hw.hypervisors` | `what-is-isolated` | none |
| `csa.hw.windows-licensing` | `core-counting`, `licence-included`, `bring-your-own`, `dedicated-hosts`, `sql-editions`, `look-it-up` (these are real; see that brief) | plain labs |

## Part 1, the build: `build-the-right-machine`

A plain lab (no systemd), free, local.

### What the container holds

Under `/srv/sizing/`:

- `README.txt`: the date and region of the prices, the source pages, "a month is 730 hours", the SQL Server rates, and the company's sizing policy (below).
- `prices.csv`: 43 rows from the fixture: per cloud one x86 general-purpose family in several sizes, one Arm family, a memory-optimised family, burstable sizes with their baselines, and GPU sizes with the GPU's memory. Mostly one family per kind per cloud (the fixture's `m6i`, `m7a`, `D4as_v5`, `Dsv6`, `n2`, `e2-standard` and `t2a` rows are left out), so that "the cheapest that fits" is rarely a near-tie between look-alikes.
- `workloads/w1` to `w5`, each with `brief.txt` (five to eight lines: what it is, where it runs now, what it must run on, which cloud) and `metrics.csv` (a week of 5-minute samples, 2,016 rows: CPU as a percentage of the current machine, memory in GiB, and for the GPU job the GPU's utilisation and memory).
- `answers.csv`, with a header and five empty rows: `workload,instance,monthly_usd`, and a last line `saving,,` for the monthly saving against today.
- `metric-summary FILE`: a small tool that prints the average, the median, the 95th percentile and the maximum of each column, as a cloud's monitoring page would. The raw file is there for anyone who wants to check it with `sort` and `awk`.

`seed.sh` builds every metric from arithmetic on a row counter (a daily wave, a weekly wave, a few spikes), never from randomness, so the checks can recompute everything. This was tried: 2,016 rows generate in one `awk` call, and the default `awk` in `ubuntu:24.04` (mawk) handles all of it.

### The policy the brief states

So that "right-sized" has one meaning and a check can hold the learner to it, the README gives the company's rule. It is the answer's definition, not a hint: applying it is the work.

- **CPU:** the busy hours must fit with room to spare: the 95th percentile of CPU must be no more than 60% of the new machine's vCPUs.
- **Memory:** the peak must be no more than 80% of the new machine's memory.
- **GPU memory:** the peak must be no more than 90% of the GPU's memory.
- **Burstable sizes** are allowed only when the average CPU per vCPU is at or under the size's baseline and the brief says the peaks are short.
- **Among the machines that fit, on the clouds the brief allows,** take the cheapest for the hours it runs. Anything within 15% of the cheapest is accepted.

### The five workloads

Numbers here are the design; `seed.sh` produces them and the checks recompute them. Prices are the fixture's.

| | Workload | Runs now on | What the numbers say | Constraint in the brief | Right answer (accepted) | A month |
| --- | --- | --- | --- | --- | --- | --- |
| w1 | `orders-api`, a Linux web API on Google Cloud | `n4-standard-8` (8 vCPUs, 32 GiB), $264.84 | 95th percentile CPU 27% (2.16 vCPUs; needs 3.6, so 4). Peak memory 11.2 GiB (needs 14, so 16). Average CPU 14%. | A vendor's monitoring agent is x86 only. Stay on Google Cloud. | `n4-standard-4` | $132.42 |
| w2 | `ledger-db`, Windows Server with SQL Server Standard on Azure | `D8s_v5` (8 vCPUs, 32 GiB), $1,132.96 with both licences | 95th percentile CPU 18% (1.44 vCPUs; needs 2.4, so the 4-vCPU size). Peak memory 24.6 GiB (needs 30.75, so 32). | No Software Assurance: licences included. Stay on Azure. | `E4s_v5` (4 vCPUs, 32 GiB) | $610.28: (0.436 + 4 × 0.10) × 730 |
| w3 | `thumbnailer`, a stateless Linux service on AWS, to be moved to Arm | `m7i.xlarge`, $147.17 | 95th percentile CPU 55% (2.2 vCPUs; needs 3.67, so 4). Peak memory 9.0 GiB (needs 11.25, so 16). | Built from source in CI; its images are already built for both architectures; a load test on Arm served the same requests per vCPU. Stay on AWS. | `m7g.xlarge` (`m8g.xlarge` is 10% more: accepted) | $119.14 |
| w4 | `caption-model`, a nightly GPU batch job, 180 hours a month | Azure `NC24ads_A100_v4`, $661.14 | Peak GPU memory 19.4 GiB (needs 21.6, so a 24 GB card). GPU utilisation at the 95th percentile 41%: one GPU is plenty. CPU needs 4 vCPUs, memory 16 GiB. | Any of the three clouds. | Google Cloud `g2-standard-4` (AWS `g6.xlarge` is 14% more: accepted) | $127.23: 0.706832 × 180 |
| w5 | `wiki`, a small internal Linux tool | `m7i.large`, $73.58 | Average CPU 7%, short peaks to 85%, 95th percentile 30%. Peak memory 2.9 GiB (needs 3.6, so 4). | Ships as an x86 image only. Peaks last a few minutes. AWS or Azure. | `t3.medium` or `B2s` (the same price) | $30.37 |

Today the five cost $2,279.70 a month; right-sized, $1,019.44; the saving is $1,260.26, 55%.

What each one is there to catch:

- **w1:** sizing on the average (2 vCPUs: too small); leaving it alone; taking the Arm size that is a cent cheaper and can't run the agent.
- **w2:** sizing only on CPU and choosing the 4-vCPU general-purpose size (16 GiB: the database doesn't fit); keeping 8 vCPUs for the memory and paying SQL Server for 8; costing it without SQL Server ($318.28) or without any licence ($183.96).
- **w3:** staying on x86; choosing a burstable Arm size (two vCPUs, and the average is above its baseline).
- **w4:** choosing by the GPU's speed and not its memory (a T4 has 16 GB: the job doesn't load); keeping the A100; costing 730 hours ($515.99).
- **w5:** sizing a quiet tool on its peak; refusing a burstable size out of habit.

A prototype of these rules was run over the fixture: for every workload the accepted set is exactly the one in the table, and the next-cheapest wrong choice is at least 31% over.

### The prompt

It gives the story (a company reviewing five workloads before its cloud bill is renewed), where the files are, the format of `answers.csv`, and "the checks hold you to the policy in the README". It does not name the traps, the right families, or which workload is the Arm move beyond what the workload's own brief says.

### Checks

Each computes its truth from `prices.csv` and the workload's `metrics.csv` inside the check. Each must finish inside the checker's 30 seconds; the prototype's percentile over 2,016 rows takes none of it.

| Check | Tests | `test_skills` (**assumed** ids in italics) |
| --- | --- | --- |
| `sheet-complete` | Five rows and the saving, every instance a name from `prices.csv`. | `csa.linux.shell/sed-awk` |
| `data-untouched` | Checksums of `prices.csv`, the README and the five metric files. The learner has `sudo`; this keeps the sheet honest. | `csa.linux.shell/navigate` |
| `w1-fits` | The instance meets the policy and the brief: enough vCPUs and memory, x86, Google Cloud. | *`csa.hw.cores-memory/right-size`*, *`csa.hw.cpu-architectures/rebuild-for-arm`* |
| `w1-not-oversized` | Its monthly cost is within 15% of the cheapest that fits. | *`csa.hw.cores-memory/right-size`* |
| `w2-fits` | Enough vCPUs and memory, a size with a Windows price, Azure. | *`csa.hw.cores-memory/right-size`* |
| `w2-not-oversized` | Within 15% of the cheapest that fits, both licences counted. | `csa.hw.windows-licensing/sql-editions` |
| `w3-fits` | Arm, enough vCPUs and memory, not a burstable size its average rules out, AWS. | *`csa.hw.cpu-architectures/arm-savings`*, *`csa.hw.cpu-architectures/rebuild-for-arm`* |
| `w3-not-oversized` | Within 15%. | *`csa.hw.cores-memory/right-size`* |
| `w4-fits` | A GPU with enough memory; enough vCPUs and memory. | *`csa.hw.gpus/vram-fit`* |
| `w4-not-oversized` | Within 15% of the cheapest that fits, on any cloud. | *`csa.hw.gpus/read-gpu-utilisation`* |
| `w5-fits` | Fits; if burstable, the average is under the baseline; AWS or Azure; x86. | *`csa.hw.cores-memory/burstable-credits`* |
| `w5-not-oversized` | Within 15%. | *`csa.hw.cores-memory/burstable-credits`* |
| `estimates-right` | For each row, `monthly_usd` is within 15% of the true cost of **the instance the learner chose**, for the hours it runs, licences included. All five must be. | `csa.hw.windows-licensing/licence-included` |
| `saving-right` | The saving is within 15% of today's total minus the true cost of the learner's five choices. | `csa.hw.windows-licensing/licence-included` |

The 15% on the estimates is the spec's own figure for cost drills. It is wide enough to forgive rounding and a 720-hour month, and every mistake in the list above is far outside it.

### Wrong fixes the contract needs

One `wrong/*.sh` each; each writes an `answers.csv` and must fail the named check.

| File | The mistake | Fails |
| --- | --- | --- |
| `left-as-they-are.sh` | Every workload stays where it is, costed correctly. The lazy answer. | every `not-oversized`, `w3-fits` |
| `sized-on-averages.sh` | Sizes from the average column. | `w1-fits` (2 vCPUs and 8 GiB: too small on both counts) |
| `one-size-up-to-be-safe.sh` | The right family, a size larger everywhere. | every `not-oversized` |
| `arm-everywhere.sh` | Moves w1 and w5 to Arm too. | `w1-fits`, `w5-fits` |
| `gpu-by-speed.sh` | A T4 for w4. | `w4-fits` |
| `gpu-kept-big.sh` | An A100 for w4. | `w4-not-oversized` |
| `forgot-the-licences.sh` | Right instances; w2 costed at the Linux price. | `estimates-right`, `saving-right` |
| `gpu-all-month.sh` | Right instances; w4 costed at 730 hours. | `estimates-right`, `saving-right` |
| `db-by-cpu.sh` | `D4s_v5` for w2. | `w2-fits` |
| `no-burstable.sh` | `D2s_v5` for w5. | `w5-not-oversized` |
| `edited-the-prices.sh` | Lowers a price in `prices.csv` to make a favourite fit. | `data-untouched` |

### Where this departs from the spec's drill, and why

The drills table says right-sizing is "within one size". As a check that is too loose for a proof: the current size is often within one size of the right one, so doing nothing would pass. Here the size must meet a stated policy and the cost must be within 15% of the cheapest that fits. One size up doubles the price, so it fails; a neighbouring family or another cloud at nearly the same price passes. "Within one size" stays the tolerance for the quick review questions in `csa.hw.cores-memory`, where the learner reads numbers by eye (an estimate with `factor: 2`, on a question written so that the current size is at least two sizes out).

## Part 2, the debug: `debug-the-slow-vm`

A systemd lab, free, local. **Assumed** throughout: the machinery in the table above exists in `csa.hw.cores-memory`'s own labs, and this lab is that machinery with three causes planted at once.

**The prompt, and nothing more than this:** "This VM runs the shop's API and its nightly report. Customers say the API has been slow in bursts since Monday, and the on-call engineer says the machine 'looks half idle'. There are three separate causes. Find each from the machine's own numbers and fix it, without stopping either service and without throwing away the limits that protect them. `lab-instance show` is your cloud console for this VM, and `lab-instance sizes` lists what it could be resized to, with prices."

Purpose, symptom, the number of causes. Not what they are, not where. The checkpoint's `objectives` and `summary` in `topic.yaml` must not undo that: the spec's sentence names all three ("CPU steal, throttling and memory pressure") and the outline copied it. Write the objective as "Find out why a VM is slow from its own numbers, and fix each cause where it lives."

**What is planted** (for the writer):

1. **Steal.** The VM is a burstable size whose credits are spent: the workload's average CPU is above the size's baseline. The `vmstat` stand-in shows a high `st`; `lab-instance show` shows a credit balance of zero. Nothing inside the VM fixes it. The fix is `lab-instance resize` to a size whose baseline covers the average, or to a non-burstable one.
2. **Throttling.** The API's unit has a CPU quota far below what its bursts need. Real: `cpu.stat`'s `nr_throttled` climbs. The fix is a higher quota or none, in a drop-in. (This is `csa.linux.cpu`'s skill, brought back on purpose.)
3. **Memory pressure.** The API's unit has `MemoryHigh=` set just under its working set, so the kernel reclaims from it constantly and it stalls, without ever being killed. Real: the cgroup's `memory.events` counts `high`, and `memory.pressure` shows a non-zero `some avg10`. The fix is a `MemoryHigh` (or only a `MemoryMax`) above what the service really uses. This is deliberately not an OOM kill, which Module 1 already proved.

**Checks, and the shortcuts each rejects:**

| Check | Tests | Rejects | `test_skills` |
| --- | --- | --- | --- |
| `steal-gone` | The instance (the stand-in's state) is non-burstable, or its baseline is at or above the workload's average CPU. | Leaving the size; restarting things. | *`csa.hw.cores-memory/burstable-credits`*, *`csa.hw.cores-memory/noisy-neighbours`* |
| `not-oversized` | The new size costs no more than twice the cheapest size that passes `steal-gone`, from the lab's own price list. | "Give it the biggest machine." | *`csa.hw.cores-memory/right-size`* |
| `api-not-throttled` | `nr_throttled` for the API's cgroup doesn't rise over 5 seconds while the API is under its usual load. | A restart that only resets the counter. | `csa.linux.cpu/throttling` |
| `api-not-stalling` | `memory.events` `high` doesn't rise over 5 seconds, read twice with the same `MainPID`. | A restart. | *`csa.hw.cores-memory/memory-pressure`* |
| `limits-kept` | The API still has a finite `MemoryMax`, no more than four times its measured peak. The report still has its CPU quota. | Deleting every limit to make the numbers go quiet. The audit found a Module 1 lab that accepted exactly that. | `csa.linux.memory/container-memory`, `csa.linux.cpu/cgroups-v2` |
| `both-running` | Both services are active and enabled, read twice a second apart. | Stopping or disabling the report to free the CPU. | `csa.linux.services/systemctl` |

`wrong/*.sh`: one for each cause left in place (three files); `removed-every-limit.sh`; `stopped-the-report.sh`; `biggest-instance.sh`; `just-restarted.sh`.

**Tried on this machine:** Docker Desktop's kernel (6.18, WSL2) exposes `/proc/pressure/memory` and a per-cgroup `memory.pressure`, so the memory-pressure cause can be real here. Its `/proc/stat` shows no steal, as expected, which is why steal is a stand-in. **Not tried:** whether GitHub's Ubuntu runners expose the pressure files. The `api-not-stalling` check reads `memory.events`, which doesn't depend on them, so CI is safe either way; only a learner-facing hint that mentions `memory.pressure` would be affected.

## Part 3, the domain: `build-the-domain`

The spec: "Stand up a small Active Directory domain, join a Windows and a Linux VM to it." The windows-ad designer decides how topic 19 does this. The checkpoint's version depends on that, so here are both shapes.

### Shape A (recommended): a timed rebuild in Azure

**Assumed:** topic 19's build is a real Windows Server domain in the learner's own Azure subscription, and that topic has already made the learner set a budget with an alert, auto-shutdown, and a tag on everything.

Under the owner's rule this is the better learning: an architect will meet Active Directory on real Windows Server VMs in a cloud network, and nothing local is Windows. A second, timed build some weeks after the first is also the spec's own idea of spaced review for a key lab ("now and then a timed rebuild").

- **What the learner builds:** a resource group tagged `topic=csa.m2.checkpoint`; a small network; a Windows Server VM promoted to a domain controller for a new domain; a second Windows Server VM and an Ubuntu VM, both joined; one domain user who can log in to the Linux VM.
- **Smallest sizes that should work** (the windows-ad brief confirms them): two `B2ms` with Windows ($0.0912 an hour each) and one `B2s` with Linux ($0.0416), East US.
- **Estimated cost, from prices read 2026-11-10:** VMs $0.224 an hour; two 128 GiB Standard SSD disks at $9.60 a month each and one 32 GiB at $2.40, about $0.03 an hour together; one public IP address at $0.005 an hour. **About $0.26 an hour: $0.78 for a three-hour sitting, under $2 with a second attempt.** Left running: $6.21 a day, $189 a month, which alone is more than the $150 credit. That is the reason auto-shutdown, the budget alert and the teardown check are not optional.
- **How it is checked.** `tools/labcheck.py` can only reach a local container today. The smallest addition that would check this lab is two more places a check may run, named per check in `checks.yaml`:
  - `where: ssh`: the command runs on the Linux member over SSH (the learner gives the address and key). From there one machine can prove the whole domain: the domain's service records resolve; `realm list` shows the machine joined; `adcli testjoin` proves its machine account works; `id` resolves the domain user; and a directory search made with the machine's own Kerberos ticket lists the Windows member's computer account, which proves the Windows VM joined without ever logging in to Windows.
  - `where: host`: the command runs on the learner's own machine with the `az` command they are signed in to, read-only: the budget and its alert exist; auto-shutdown is set on each VM; everything in the resource group carries the tag; no network rule lets the whole internet reach remote desktop or SSH; and, as the last check after teardown, nothing with the tag is left.
- **Shortcuts the checks must reject:** opening port 3389 or 22 to `0.0.0.0/0` to make connecting easy; joining only the Linux VM; a domain controller with no second Windows machine; leaving everything running; deleting the VMs and leaving the disks and the address (still billed).
- **CI can't run it** (ADR-0014). The checks are tested against recordings: the saved output of every check command from a correct build, which must pass, and from each wrong build, which must fail.
- **What stays unproven until the owner runs it once:** every check command against real output (the shape of `az`'s JSON, what `realm` and `adcli` print on the image chosen); whether `B2ms` is enough for a domain controller; how long it takes (promoting a domain controller and two joins are mostly waiting); the real cost; and the recordings themselves, which until then are written from documentation.

### Shape B: a local domain

**If** topic 19 proves the domain locally (a Samba domain controller in a container, a Linux member joined with `realmd` and SSSD), the checkpoint's part 3 is the same lab in a new story, free, checked by `labcheck` as it is. It can't join a Windows VM: there is no Windows in a container on this platform. The spec's words "join a Windows and a Linux VM" would then be unmet, and the spec must be amended to say what is proved.

### Which, and when

Shape A if topic 19 has an Azure lab; the local lab then serves as the practice for it and as the support step here. If the cloud checks (`where: ssh`, `where: host`) aren't built in time, ship the checkpoint with parts 1 and 2 and the explain, leave part 3's hands-on in topic 19, and amend the spec, as under "Three parts" above.

## The explain

Opens after the build passes, as every checkpoint's does (ADR-0012, amended 2026-11-10).

**Prompt.** "A team's 4-vCPU Linux VM is slow at busy times. Their plan: move it to an 8-vCPU Arm instance with a GPU 'to be safe', and put the company's new Windows domain controller on the same machine to save money. In your own words: what a vCPU on a cloud VM really is and what the hypervisor does and doesn't keep apart; how you would tell from the VM's own numbers whether it is short of CPU, being held back by a limit, losing CPU to the host, or short of memory; what moving to Arm needs and what it saves; what a GPU would and wouldn't change here; what a domain controller is for, and how Entra ID differs from Active Directory Domain Services; and what Windows on that machine would cost and whether licences the company owns could be used."

**Rubric** (ids are for the grader; all but the last required):

| Id | The point |
| --- | --- |
| `slice` | A vCPU is a share of a physical core (usually one of its two threads) handed out by a hypervisor; neighbours are kept apart in memory and devices but still share the hardware, which is where steal and noisy neighbours come from. |
| `diagnose` | Four different numbers for four different causes: load and CPU use for real shortage; `cpu.stat` throttling for a limit; steal for the host or spent burst credits; reclaim and pressure (or swap activity) for memory. More vCPUs fix only the first. |
| `arm` | Arm needs software built for it: compiled code and images rebuilt, anything closed-source checked. The saving is in price for the same work, not speed for free. |
| `gpu` | A GPU helps only work written to use one, and its memory, not its speed, decides whether a job fits. It does nothing for a web service. |
| `directory` | A domain controller holds accounts and policy and proves identity with Kerberos; Entra ID is a cloud identity service that speaks web sign-in protocols and has no domain join or Group Policy of the same kind. Putting a domain controller on an application's server is a risk, not a saving. |
| `licence` | Windows adds a per-vCPU charge; the Arm sizes have no Windows price; owned licences help on Azure with Software Assurance and mostly not on AWS or Google Cloud. |
| `method` (not required) | Measure first, change one thing, measure again. |

The model answer is assembled from the six topics' own model answers once they exist. **Assumed:** the windows-ad brief's explain covers Entra ID against Active Directory Domain Services in more depth; this rubric's `directory` point should use its wording.

## Getting unstuck (ADR-0012)

For part 1, the build:

- **`unstuck.example`: `example-the-right-machine-clinic`.** A solved sibling in another story: a clinic's three workloads (an oversized booking API, a Windows records server with SQL Server Standard, a GPU job that reads scans). Labelled steps: read the brief for what it must run on; read `metric-summary` and say which numbers matter; apply the policy to get the vCPUs and memory needed; filter the price sheet to what fits; take the cheapest; cost it for the hours it runs; write the row.
- **`unstuck.steps`**, four fill-in labs with hints, each the whole sheet with the other rows already filled in, and each checked by the build's own checks:
  1. `step-size-from-the-metrics`: only w1's row is empty.
  2. `step-count-the-licence`: only w2's row.
  3. `step-arm-and-gpu`: w3's and w4's rows.
  4. `step-the-whole-sheet`: every row empty, with the method as five comment lines at the top of `answers.csv`.
- **`unstuck.versions`**: `build-the-right-machine-bakery` and `build-the-right-machine-print-shop`. The same five kinds of workload with other numbers and the clouds rotated: the Arm move on Azure (`D4s_v6` to `D4ps_v6`), the Windows and SQL Server database on AWS (so AWS's SQL Server rate is used), a GPU job that needs more than 24 GB, a burstable candidate whose average is *over* the baseline, so the burstable size is the wrong answer this time. Their checks are the build's, with the checksums changed. One `seed.sh` with a story number makes all three, so the versions cost little to write.

For part 2: a second debug waits until learners are seen to get stuck, as ADR-0012 says. The topic labs of `csa.hw.cores-memory`, `csa.linux.cpu` and `csa.linux.memory` are the practice, and each failed check brings its skill back on Today.

For part 3: topic 19's own lab is the worked example.

## Time

The spec wants checkpoints to have time limits. No lab has a time field today, and Checkpoint 1 dropped its 45 minutes without saying so.

| Part | Target |
| --- | --- |
| 1, the right machine | 60 minutes |
| 2, the slow VM | 30 minutes (the spec's figure for a three-fault break-fix) |
| 3, the domain | 90 minutes, most of it waiting for Windows |
| The explain | 20 minutes |

**Recommended: show the time, don't fail on it, the first time through.** A beginner's first pass at a module gate should be judged on being right. The smallest way: an optional `advisory: true` on a lab check. The checker runs it and prints it, the page shows it, and it doesn't count towards passing. The check itself needs nothing new: `ps -o etimes= -p 1` inside the container is the seconds since the lab started (tried here). Without that field, the prompt states the target and nothing measures it. A hard limit belongs to the later timed rebuild, when one is built.

`estimated_minutes`: **210** (the outline's 480 was a placeholder; Checkpoint 1 says 120).

## Platform work, smallest version of each

| Need | Smallest version | If it isn't built |
| --- | --- | --- |
| A third required part | `prove.more`: a list of extra builds or debugs, all required. | Part 3's hands-on stays in topic 19; amend the spec. |
| Checks that reach a cloud VM and the learner's `az` | `where: ssh` and `where: host` on a check, and recordings for CI. This is ADR-0014's cloud mode at its smallest, and topic 19 needs it first. | Shape B, or part 3 deferred. |
| A time target that is measured | `advisory: true` on a check. | State the target in the prompt. |
| Nothing for part 1 | Plain labs exist. | |
| Nothing for part 2 beyond topic 17's stand-ins | **Assumed** to be designed there. | Part 2 drops the steal cause and becomes two real causes; the spec is amended. |

The `estimate` question type isn't needed by the checkpoint itself.

## Cost

- Parts 1 and 2, the example, the steps and the versions: nothing. Eight plain labs and one systemd lab in CI.
- Part 3, shape A: about $0.78 a sitting, under $2 with a retry, inside the Azure credit, with the guardrails above. Shape B: nothing.
- No AI cost beyond the one explain grading.

## Open questions, each with a recommendation

1. **Three parts in a model with two slots.** Recommended: `prove.more`. It makes this checkpoint match its spec and unblocks four later ones.
2. **Part 3 in Azure or local.** Recommended: Azure, as a timed rebuild, if topic 19 has an Azure lab. It is the real thing, it costs about a dollar, and it is the track's first practice of tearing down what you built.
3. **Should the time targets fail the checkpoint?** Recommended: not on the first pass; show them.
4. **A stated sizing policy, and 15% of the cheapest, where the spec says "within one size".** Recommended, for the reason given under part 1. The spec's drills table should gain a line saying proofs use a stated policy.
5. **A `metric-summary` tool in the lab, or make the learner compute the percentile with `sort` and `awk`?** Recommended: provide the tool. The proof is about sizing judgement; a percentile by hand is a shell exercise that Module 1 already proved.
6. **The checkpoint's public objectives name the debug's three causes** (they are copied from the spec). Recommended: reword them when `topic.yaml` is written, as shown under part 2.
7. **Checkpoint ids by position** (`csa.m2.checkpoint`). The spec's open question says to decide before anything is built, and Module 1 already uses a positional id. Recommended: keep positional ids; they cost the learner nothing, and renaming would touch saved events.
8. **The spec says Arm "saves 20–40%".** The fixture shows 9% to 31% on list price. Recommended: the CPU architectures brief says which figure it teaches; this checkpoint only uses the prices.
