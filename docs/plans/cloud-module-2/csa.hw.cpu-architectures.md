# Writing brief: CPU architectures (`csa.hw.cpu-architectures`, topic 16)

Module 2, "Virtualization, hardware and Windows", of the Cloud Solutions Architect track. Designed 2026-11-10 to 2026-11-11. Nothing here is written into the repository yet; this is the brief a writer builds the topic from.

**Decisions in one paragraph.** The topic is proven on the learner's machine, at no cost. The "what has to be rebuilt" exercise is real: in a lab container the learner finds every part of a deployment that can't run on Arm, rebuilds the in-house programs for Arm with a cross-compiler, and proves they run on the oldest Arm CPU in the fleet through an emulator. The costed comparison uses price lists read from the three providers on 2026-11-10 and is checked by code within a stated tolerance. Building a multi-architecture container image with `docker buildx` works on this machine, but it is **not** a checked lab here: it depends on an emulator that Docker Desktop installs and a CI runner doesn't, the track doesn't teach Docker until Module 6, and the checker can't run a lab on the host. The learner reads real image indexes instead, and builds one in `csa.auto.containers`.

Words used in this brief: an **instruction set** is the list of operations a family of CPUs understands. **x86-64** (also written amd64) is Intel's and AMD's; **arm64** (also written aarch64) is Arm's 64-bit one. An **emulator** is a program that runs programs built for another instruction set by translating them as it goes.

## What the learner will be able to do

- Say what an instruction set is, and why a compiled program runs on one architecture only.
- Read the architecture of a machine, a program file and a container image.
- Recognise the two failures: wrong architecture, and right architecture with a missing feature.
- Sort an application's parts into "runs as it is", "rebuild", "get it from the vendor" and "can't move".
- Name the Arm families on AWS, Azure and Google Cloud and read an instance name.
- Cost a move from x86 to Arm from price lists, and say what must be measured before promising a saving.

### The six-month core

1. Look at a server, a binary or an image and say which architecture it is for, in seconds (`uname -m`, `file`, the image's platform list).
2. Asked "can we move this to Arm?", produce the inventory: unchanged, rebuild, vendor, blocked, and the order to try them in.
3. From a price list, work out the percentage saved, the monthly saving for a fleet and the months to pay back the work, and name what the price list can't tell you.
4. Know `Exec format error` from `Illegal instruction` on sight.
5. Read `m8g`, `D4ps_v6` and `c4a` as Arm, and not be fooled by the `a` in `m7a`.

Core names, feature flags and prices are not in the core. They are in the fixtures, dated.

## Prerequisites

| Needs | From | Why |
| --- | --- | --- |
| emulation, QEMU, vCPU, nested virtualization | `csa.hw.hypervisors` | this topic uses an emulator for single programs and leans on "a vCPU is a thread the host schedules" |
| signals, and exit status 128 + the signal's number | `csa.linux.processes`, `csa.linux.memory` | `Illegal instruction` is signal 4, exit status 132, read the way 137 was |
| `apt`, `dpkg`, packages | `csa.linux.packages` | `dpkg --print-architecture`; a package is built per architecture |
| images, layers, tags, reading a Dockerfile | `csa.linux.containers` | an image is per architecture; a tag can point at several |
| scripts, arguments, strict mode, `chmod +x` | `csa.linux.scripting` | four of the five labs are scripts |
| `find`, `grep`, `awk`, `sort`, pipes | `csa.linux.shell` | every recall item and check; the price arithmetic is `awk` |

Recommended `prerequisites:` line: `[csa.hw.hypervisors, csa.linux.packages, csa.linux.containers, csa.linux.scripting]`.

Python is **not** needed. The track asks for Python Foundations from Module 6; every calculation here is `awk` or shell arithmetic, which Module 1 taught.

### Terms this topic must define itself

Module 1 never used the words "architecture", "compile" or "binary" (checked by searching all fourteen lessons). Each of these needs a plain sentence at first use:

- **instruction**, **machine code**, **instruction set** (architecture), **source code**, **compiler**, **to build**, **binary** (executable), **ELF** in one clause (the file format of a Linux program, whose first bytes name its architecture)
- **interpreted language** against **compiled language** (the scripting lesson taught the shebang but not this split), **bytecode** and the **JVM** in one clause
- **shared library** (`.so`), **statically linked** against **dynamically linked**, in one sentence each: the labs build static programs and find `.so` files
- **x86-64 / amd64**, **arm64 / aarch64**, and that each pair is one thing with two names
- **Arm** the company that licenses designs, **Neoverse** as its server designs, and the chips built from them: **Graviton** (AWS), **Cobalt** (Microsoft), **Axion** (Google), **Ampere Altra** (Ampere, rented out by Azure and Google)
- **cross-compile**, **emulator** for a single program, and in one sentence how Linux can be told to hand foreign programs to one
- **vector instructions** in one clause (operations on many numbers at once: AVX2 and AVX-512 on x86, Neon and SVE on Arm), **feature level** (x86-64-v2, v3, v4)
- **instance type**, **family**, **size**, **generation**, and how to read a name; **region** and **on-demand price** in one clause each (the track teaches them in Modules 8 and 12)
- **hyperthread** in one sentence: on most x86 instance types a vCPU is one of a core's two threads; on Arm types it is a whole core (topic 17 goes further)
- **image index** (manifest list), **platform**, **multi-architecture image**, **registry** in one clause
- **native extension** (the compiled part inside a package for an interpreted language), **agent** (a vendor's program installed on every server)
- Commands new to the learner: `uname -m`, `dpkg --print-architecture`, `file`, `gcc` and `aarch64-linux-gnu-gcc` as one command each, `qemu-aarch64-static`, `unzip -l`

## Skills

| Skill | What it covers |
| --- | --- |
| `read-arch` | Read the architecture of a machine (`uname -m`, `dpkg --print-architecture`, `lscpu`), of a file (`file`) and of an image (the platforms in its index); know amd64 is x86-64 and aarch64 is arm64 |
| `instruction-sets` | What an instruction set is; why a binary runs on one architecture (`Exec format error`); what an emulator does and costs; feature levels inside one architecture and `Illegal instruction` |
| `rebuild-inventory` | Sort a deployment into runs-as-is, rebuild, vendor and blocked: scripts and bytecode, compiled programs, native extensions, libraries inside archives, images, agents, licensed software; rebuild for the oldest CPU in the fleet |
| `arm-families` | The Arm families on three clouds and how to read an instance name; what a vCPU is on them; which operating systems they run |
| `price-performance` | Percent saved at equal size, monthly saving for a fleet, months to pay back the work; why price per vCPU isn't price per unit of work; when Arm isn't the cheaper choice |

## Lesson plan

1. **What a CPU runs.** A CPU does one small operation at a time: add, compare, jump. The list of operations it knows, and how each is written as numbers, is its instruction set. A program on disk is those numbers. *Resources: Crash Course Computer Science #7, "The Central Processing Unit" (11 min 38 s), and #8, "Instructions & Programs" (10 min 36 s), embedded. They build a tiny CPU and run a program on it, which is the picture everything else hangs on.*
2. **Lesson must supply: source, compiler, binary, in terms of what the learner has already done.** The scripts written in Module 1 are text; `bash` reads them each time, and `bash` itself is the binary. A compiled program is translated once, ahead of time, into one CPU family's instructions. So a script moves between architectures untouched (as long as its interpreter exists there), and a compiled program does not. Bytecode sits between: a `.jar` is portable, the Java runtime under it is not. One table: language, what you ship, does it need rebuilding.
3. **Two families, four names.** x86-64, also called amd64; arm64, also called aarch64. `uname -m` and `dpkg --print-architecture` on the lab machine; `file` on a program. *No resource carries this for a beginner; the worked example does.*
4. **Wrong architecture.** `Exec format error`: the kernel read the file's header and declined. An emulator can run it anyway, slowly: measured here, 4 to 33 times slower depending on the work. Docker Desktop installs one silently, which is why a build that "works on my laptop" fails on a CI runner or an Arm node. *Resource: Docker, "Multi-platform builds", the first half.*
5. **Lesson must supply: the second failure, with the fleet as the picture.** Each architecture grows over time. A program built to use newer instructions dies with `Illegal instruction` (signal 4, exit status 132) on an older CPU of the *same* architecture. On x86 the steps are called x86-64-v2, v3 and v4. On Arm the cloud example is SVE: built for Graviton3 or later with SVE switched on, the program dies on Graviton2, which lacks it. The rule for a fleet: build for the oldest CPU you run on. *Resource: Red Hat Developer, "Building Red Hat Enterprise Linux 9 for the x86-64-v2 microarchitecture level" (5 minutes).*
6. **The three clouds. Mark the differences.**

   | | AWS | Azure | Google Cloud |
   | --- | --- | --- | --- |
   | Own Arm chip | Graviton (2, 3, 4, 5) | Cobalt 100 | Axion |
   | Also rents | | Ampere Altra | Ampere Altra |
   | How the name says Arm | a `g` after the generation: `m8g`, `c7g`, `t4g` | a `p` in the size: `D4ps_v6`, `E2ps_v6`, `B2pts_v2` | the series: `C4A`, `N4A`, `T2A` |
   | The trap | `a` means AMD: `m7a` is x86 | `a` means AMD: `D4as_v6` is x86 | `A` means Arm: `C4A` is Arm, `C4D` is AMD |
   | A vCPU is | a whole core | a whole core | a whole core |
   | Runs | Linux only | Linux and Windows 11 client | the public Arm images (the page lists them) |

   *Resources: Microsoft, "Azure Cobalt processor-based Virtual Machines" (2 minutes); Google, "Arm VMs on Compute Engine" (5 minutes); AWS, the Graviton page (3 minutes).*
7. **Images.** A tag can point at an index: a list of images, one per platform. The runtime picks its own. If its platform isn't listed the pull fails; if the image has no index at all, it arrives and then can't start. Three ways to build for two architectures: emulate (slow), build on a machine of each kind, or cross-compile. *Resource: Docker, "Multi-platform builds", the second half; the OCI image index specification for the exact fields.*
8. **The inventory.** Walk a deployment and sort every part. *Resource: AWS, "Considerations when transitioning workloads to AWS Graviton based Amazon EC2 instances" (14 minutes). It is AWS's, and the method holds on all three clouds.*
9. **Lesson must supply: the money, honestly.** One table of list prices for the same size on each cloud (below), then three points no resource makes together. (a) The gap is 7 to 31% at list price, depending on the cloud and what you compare with; "up to 40%" is a vendor's claim about work done per dollar, not about the price. (b) Equal vCPUs are not equal hardware: 2 vCPUs are one core's two threads on `m7i.large` and two whole cores on `m7g.large`, so work that scales with cores can gain more than the price gap, and the only way to know is to measure requests per dollar on your own workload. (c) Arm is not a price class: on Google Cloud the x86 `e2-standard-2` lists below every Arm type, a newer Arm size can list above an older or an AMD one, and a Windows or SQL Server tier can't move at all.

Recap bullets follow the nine steps.

## Verified facts

| # | Claim | Source | Read |
| --- | --- | --- | --- |
| 1 | Graviton generations: Graviton2 is Neoverse N1, Armv8.2, no SVE (M6g, C6g, R6g, T4g); Graviton3 is Neoverse V1, Armv8.4, SVE (M7g, C7g, R7g); Graviton4 is Neoverse V2, Armv9.0, SVE2 (M8g, C8g, R8g); Graviton5 is Neoverse V3, Armv9.2 (M9g) | https://github.com/aws/aws-graviton-getting-started (the table under "Building for Graviton") | 2026-11-11 |
| 2 | M9g's processor is "AWS Graviton5"; M7i is Intel Sapphire Rapids, M7a AMD EPYC 9R14, M8i Intel Granite Rapids, M8a AMD EPYC 9R45, T3 Intel Skylake, T4g Graviton2 | https://docs.aws.amazon.com/ec2/latest/instancetypes/gp.html | 2026-11-10 |
| 3 | "Every vCPU on a Graviton processor maps to a physical core, and there is no Simultaneous Multi-Threading (SMT)" | https://github.com/aws/aws-graviton-getting-started/blob/main/transition-guide.md | 2026-11-11 |
| 4 | Default cores and threads: `m7i.large`, `m8i.large`, `c7i.large`, `t3.micro` are 1 core with 2 threads; `m7a.large`, `m8a.large`, `m7g.large`, `m8g.large`, `m9g.large`, `c7g.large`, `t4g.micro` are 2 cores with 1 thread | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/cpu-options-supported-instances-values.html | 2026-11-10 |
| 5 | AWS's claims: Graviton-based instances "cost up to 20% less than comparable x86-based Amazon EC2 instances" and "use up to 60% less energy"; M6g "up to 40% better price/performance over M5", T4g the same over T3 | https://aws.amazon.com/ec2/graviton/ ; https://aws.amazon.com/ec2/faqs/ | 2026-11-10 |
| 6 | "AWS Graviton processors only support Linux operating systems" | https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-nitro-instances.html | 2026-11-10 |
| 7 | A free trial of `t4g.small` runs "until Dec 31st 2026" | https://aws.amazon.com/ec2/graviton/ | 2026-11-10 |
| 8 | Cobalt 100 is Microsoft's first 64-bit Arm CPU, based on Arm's Neoverse N2, at 3.4 GHz, and "provides an entire physical core for each virtual machine vCPU". Series: Dpsv6, Dpdsv6, Dplsv6, Dpldsv6, Epsv6, Epdsv6. Guest systems listed: Linux distributions and Windows 11 Client | https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/cobalt-overview (dated 2024-11-07, updated 2025-07-03) | 2026-11-10 |
| 9 | Dpsv6 applies to "Linux VMs" and "Windows Client VMs"; sizes D2ps_v6 (2 vCPUs, 8 GiB) to D96ps_v6 | https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/dpsv6-series (updated 2026-10-27) | 2026-11-10 |
| 10 | Google's Arm series: C4A (Axion, on Neoverse V2), N4A (Axion, on Neoverse N3), T2A (64-core Ampere Altra at 3.0 GHz). Each vCPU is one core with no SMT (this page for C4A and T2A; fact 21 for N4A). T2A supports only NVMe and gVNIC | https://docs.cloud.google.com/compute/docs/instances/arm-on-compute | 2026-11-10 |
| 11 | x86-64-v2 adds vector instructions up to SSE4.2 (and SSSE3, POPCNT, CMPXCHG16B); v3 adds up to AVX2, MOVBE and more bit manipulation; v4 adds some of AVX-512. Red Hat chose v2 for RHEL 9. "Programs that use newer CPU instructions might not run on older CPUs" | https://developers.redhat.com/blog/2021/01/05/building-red-hat-enterprise-linux-9-for-the-x86-64-v2-microarchitecture-level (updated 2024-02-05) | 2026-11-11 |
| 12 | A multi-platform image holds "a manifest list, pointing to multiple manifests"; on pull "Docker automatically selects the correct variant based on the host's architecture". Three strategies: QEMU emulation ("can be much slower than native builds"), several native nodes, cross-compilation. Docker Desktop builds under emulation with "the QEMU that's bundled within the Docker Desktop VM"; on plain Linux it is installed with `docker run --privileged --rm tonistiigi/binfmt --install all`. "Docker Desktop and Docker Engine 29.0+ use the containerd image store by default" | https://docs.docker.com/build/building/multi-platform/ | 2026-11-10 |
| 13 | An OCI image index has media type `application/vnd.oci.image.index.v1+json` and a `manifests` list whose entries carry a `platform` with required `architecture` and `os` | https://github.com/opencontainers/image-spec/blob/main/image-index.md | 2026-11-10 |
| 14 | Platforms actually published, read with `docker buildx imagetools inspect --raw`: `ubuntu:24.04` has amd64, arm/v7, arm64/v8, ppc64le, riscv64, s390x, and attestation entries marked `unknown/unknown`; `nginx:1.27`, `postgres:16`, `redis:7`, `python:3.12-slim` all include arm64/v8; `mcr.microsoft.com/mssql/server:2022-latest` is a single amd64 image with no index | read from the registries on this machine | 2026-11-11 |
| 15 | Asked to run that SQL Server image as Arm, Docker 29.8.2 answers: `image with reference mcr.microsoft.com/mssql/server:2022-latest was found but does not provide the specified platform (linux/arm64)` | run on this machine | 2026-11-11 |
| 16 | The transition guide's method: inventory the operating system, images, libraries and runtimes, build tooling, agents and vendor software; interpreted and JIT-compiled languages generally run as they are; C, C++, Go and Rust must be built for arm64; native extensions are the main risk; images are per architecture; roll out with a canary or blue-green on a mixed fleet | https://github.com/aws/aws-graviton-getting-started/blob/main/transition-guide.md | 2026-11-11 |
| 17 | GitHub's hosted Arm runners (`ubuntu-24.04-arm`, 4 CPUs, 16 GB) are free on public repositories | https://docs.github.com/en/actions/reference/runners/github-hosted-runners | 2026-11-10 |
| 18 | Arm VMs on Google can't run nested virtualization; Azure's Dpsv6 can't either | https://docs.cloud.google.com/compute/docs/instances/nested-virtualization/overview ; the Dpsv6 page | 2026-11-10 |
| 19 | In an Azure size name the lower-case letters are features: `a` is "AMD-based processor", `p` is "ARM-based processor", `s` is Premium SSD capable, `d` a local temporary disk, `l` low memory, `t` tiny memory | https://learn.microsoft.com/en-us/azure/virtual-machines/vm-naming-conventions (updated 2026-02-26) | 2026-11-11 |
| 20 | Azure's Dpsv5 series runs on "the Ampere Altra Arm-based processor operating at 3.0 GHz, which provides an entire physical core for each virtual machine vCPU" | https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/dpsv5-series (updated 2026-10-27) | 2026-11-11 |
| 21 | Google's general-purpose series: C4 and N4 are Intel; C4D and N4D are AMD EPYC Turin; C4A is Axion on Neoverse V2 and N4A is Axion on Neoverse N3, and for both "SMT is not supported"; N2 is Intel; N2D and T2D are AMD EPYC Milan, and T2D has SMT disabled, so its vCPU is also a whole core; T2A is Ampere Altra; E2 "offers both Intel and AMD EPYC processors" | https://docs.cloud.google.com/compute/docs/general-purpose-machines | 2026-11-11 |

### Prices, read 2026-11-10

On-demand, Linux, US dollars an hour, 2 vCPUs. Sources: AWS, the data file its own on-demand pricing page loads, stamped 2026-11-10T17:38:52Z, for US East (N. Virginia) (`https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20(N.%20Virginia)/Linux/index.json`, behind https://aws.amazon.com/ec2/pricing/on-demand/). Azure, the Retail Prices API for East US (`https://prices.azure.com/api/retail/prices`, filtered by `armSkuName`). Google, the tables the pricing page serves by default, for Iowa (us-central1) (https://cloud.google.com/products/compute/pricing/general-purpose).

| Cloud | Intel | $/h | AMD | $/h | Arm | $/h | Arm below Intel | Arm below AMD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AWS, generation 7 | `m7i.large` | 0.1008 | `m7a.large` | 0.11592 | `m7g.large` (Graviton3) | 0.0816 | 19.0% | 29.6% |
| AWS, generation 8 | `m8i.large` | 0.10584 | `m8a.large` | 0.12172 | `m8g.large` (Graviton4) | 0.08976 | 15.2% | 26.3% |
| AWS, newest Arm | `m8i.large` | 0.10584 | `m8a.large` | 0.12172 | `m9g.large` (Graviton5) | 0.09784 | 7.6% | 19.6% |
| AWS, burstable | `t3.micro` | 0.0104 | | | `t4g.micro` | 0.0084 | 19.2% | |
| Azure, v5 | `D2s_v5` | 0.096 | `D2as_v5` | 0.086 | `D2ps_v5` (Ampere Altra) | 0.077 | 19.8% | 10.5% |
| Azure, v6 | `D2s_v6` | 0.101 | `D2as_v6` | 0.0908 | `D2ps_v6` (Cobalt 100) | 0.0702 | 30.5% | 22.7% |
| Azure, v7 | `D2s_v7` | 0.132 | `D2as_v7` | 0.0908 | `D2ps_v7` | 0.114 | 13.6% | Arm is 25.6% dearer |
| Azure, burstable | `B2ts_v2` | 0.0104 | | | `B2pts_v2` | 0.0084 | 19.2% | |
| Google, N4 | `n4-standard-2` | 0.0907 | `n4d-standard-2` | 0.0847 | `n4a-standard-2` (Axion) | 0.077 | 15.1% | 9.1% |
| Google, C4 | `c4-standard-2` (7 GiB) | 0.096866 | `c4d-standard-2` (7 GiB) | 0.09168 | `c4a-standard-2` (Axion, 8 GiB) | 0.0898 | 7.3% | 2.1% |
| Google, older | `n2-standard-2` | 0.097118 | `n2d-standard-2` | 0.084492 | `t2a-standard-2` (Ampere Altra) | 0.077 | 20.7% | 8.9% |
| Google, cheapest x86 | `e2-standard-2` | 0.06701 | | | | | Arm is dearer: `n4a` by 14.9%, `c4a` by 34.0% | |

Also read: `m7i.xlarge` 0.2016, `m7g.xlarge` 0.1632, `c7i.large` 0.08925, `c7g.large` 0.0725, `r7i.large` 0.1323, `r7g.large` 0.1071, `D4s_v6` 0.202, `D4as_v6` 0.182, `D4ps_v6` 0.14, `E2s_v6` 0.132, `E2ps_v6` 0.0922.

**What the numbers say.** At equal size the Arm list price is 7 to 31% below the same generation's Intel type and 2 to 30% below AMD's, with two cases where Arm costs more. The spec's "when Arm saves 20–40%" is the vendors' price-performance claim, not a price gap, and the topic should teach the difference (see open question 6).

## Evidence from trying it

On this machine (Windows 11, Docker Desktop 29.8.2, buildx 0.37.2, Intel Core Ultra (model masked)), 2026-11-10 and 2026-11-11.

- **`docker buildx` with emulation works here without setup.** One tag built for `linux/amd64,linux/arm64`; `docker run --platform linux/arm64` printed `hello from aarch64`; `docker image ls --tree` showed both platforms under the tag. The emulated build took 104.6 s against 48.5 s natively, most of both being package downloads.
- **Why it is still not a checked lab.** (1) It worked because Docker Desktop registers an emulator with the Linux kernel (`/proc/sys/fs/binfmt_misc/aarch64`, flags `POCF`). Docker's documentation tells users of plain Linux to install one themselves, so a CI runner should be assumed to have none and the same lab would behave differently there. (2) `tools/labcheck.py` runs checks inside a container; this lab would have to run on the host against the learner's own Docker, a mode that doesn't exist. (3) `docker buildx imagetools inspect` reads registries only, so a checked version needs a local registry as well. (4) The learner has never typed a `docker` command; `csa.auto.containers` teaches that in Module 6.
- **The same registration changes what a lab container does.** In a plain Ubuntu container here, a statically linked arm64 program **ran when started directly** (`hello from aarch64`). On a machine without the registration it fails with `Exec format error`. So no check may depend on what happens when an Arm program is started directly; the labs always name the emulator (`qemu-aarch64-static ./program`), which behaves the same everywhere.
- **Cross-compiling and emulating one program works in a plain container.** `aarch64-linux-gnu-gcc -static` built it; `file` reported `ELF 64-bit LSB executable, ARM aarch64 ... statically linked`; `qemu-aarch64-static` ran it. A dynamically linked one failed with `qemu-aarch64: Could not open '/lib/ld-linux-aarch64.so.1': No such file or directory` (exit status 255). An x86 program given to the Arm emulator: `Invalid ELF image for this architecture` (255).
- **Feature levels fail predictably under the emulator.** The same C file, built four ways and run on named CPU models:

  | Built with | `qemu64` | `Nehalem` | `Haswell` | `max` |
  | --- | --- | --- | --- | --- |
  | default flags | runs | runs | runs | runs |
  | `-march=x86-64-v3` | exit 132 | exit 132 | runs | runs |
  | `-march=x86-64-v4` | exit 132 | exit 132 | exit 132 | exit 132 |

  | Built with | `cortex-a57` | `neoverse-n1` | `neoverse-v1` | `max` |
  | --- | --- | --- | --- | --- |
  | default flags | runs | runs | runs | runs |
  | `-march=armv8.2-a+sve` | exit 132 | exit 132 | runs | runs |

  Each failure printed `qemu: uncaught target signal 4 (Illegal instruction) - core dumped`. Neoverse N1 is Graviton2's core and Neoverse V1 is Graviton3's (fact 1), so the second table is the fleet story with real names. The v4 program also died natively on this laptop, which has no AVX-512, and would run on a CI machine that has it: **never run a feature-level test natively in a check.**
- **What emulation costs here.** One shell loop: 2.01 s native, 67.05 s emulated (33 times). `gzip` of 200 MB: 0.66 s and 2.86 s (4 times). `sha256sum` of 200 MB: 0.17 s and 2.01 s (12 times).
- **`file` tells the parts of a deployment apart**: a shell script, a text file, x86-64 and aarch64 programs and shared objects, and a `.jar` as `Zip archive data`; `unzip -l` lists a native library inside the jar.
- **Price arithmetic agrees in both shells**: the same `awk` lines gave the same integers in Git Bash (gawk) and on Ubuntu 24.04 (mawk).
- **Image size.** The trial image (compiler, cross-compiler, all of `qemu-user-static`) was 891 MB and took 3 min 9 s to build. Deleting every emulator but `qemu-aarch64-static` and `qemu-x86_64-static` in the same `RUN` should take about 200 MB off; that figure is an estimate.

## Resources

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (main) | Instructions & Programs: Crash Course Computer Science #8 (CrashCourse channel) | https://www.youtube.com/watch?v=zltgXvg6r3k | video, embed | Standard YouTube licence, Crash Course; official embed | 11 | `instruction-sets` | 2026-11-11 (title, length, description, embedding allowed; not watched) |
| 1 | The Central Processing Unit (CPU): Crash Course Computer Science #7 | https://www.youtube.com/watch?v=FZGugFqdr60 | video, embed | Standard YouTube licence, Crash Course; official embed | 12 | `instruction-sets` | 2026-11-11 (as above) |
| 2 | Considerations when transitioning workloads to AWS Graviton based Amazon EC2 instances (about 2,500 to 3,000 words) | https://github.com/aws/aws-graviton-getting-started/blob/main/transition-guide.md | reading, link | CC BY-SA 4.0 | 14 | `rebuild-inventory` | 2026-11-11 |
| 3 | Multi-platform builds (Docker documentation) | https://docs.docker.com/build/building/multi-platform/ | reading, link | Apache-2.0 (Docker documentation) | about 10 (not measured) | `read-arch`, `instruction-sets`, `rebuild-inventory` | 2026-11-10 |
| 4 | Building Red Hat Enterprise Linux 9 for the x86-64-v2 microarchitecture level, by Florian Weimer (about 950 words) | https://developers.redhat.com/blog/2021/01/05/building-red-hat-enterprise-linux-9-for-the-x86-64-v2-microarchitecture-level | reading, link | Copyright Red Hat; linked, not copied | 5 | `instruction-sets` | 2026-11-11 |
| 5 | Arm VMs on Compute Engine (Google Cloud) | https://docs.cloud.google.com/compute/docs/instances/arm-on-compute | reading, link | CC BY 4.0 | 5 | `arm-families` | 2026-11-10 |
| 6 | Azure Cobalt processor-based Virtual Machines (Microsoft Learn; 314 words) | https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/cobalt-overview | reading, link | CC BY 4.0 | 2 | `arm-families` | 2026-11-10 |
| 7 | AWS Graviton processor (AWS's product page: the claims, to be read as claims) | https://aws.amazon.com/ec2/graviton/ | reading, link | Copyright Amazon Web Services; linked, not copied | 3 | `arm-families`, `price-performance` | 2026-11-10 |
| 8 | AWS Graviton Technical Guide: the README's "Building for Graviton" table | https://github.com/aws/aws-graviton-getting-started | reading, link | CC BY-SA 4.0 | 3 | `arm-families`, `instruction-sets` | 2026-11-11 |
| 9 | OCI Image Index Specification | https://github.com/opencontainers/image-spec/blob/main/image-index.md | reading, link | Apache-2.0 (the specification's repository; confirm when writing) | 4 | `read-arch` | 2026-11-10 |
| 10 (optional) | Migrate applications to Arm servers (Arm Learning Paths; its stated reading time is 15 minutes; last updated 2026-09-29) | https://learn.arm.com/learning-paths/servers-and-cloud-computing/migration/ | reading, link | CC BY 4.0 | 15 | `rebuild-inventory` | 2026-11-11 |
| 11 (data) | The three price sources named above | | data | prices are facts; each fixture names its source and date | | `price-performance` | 2026-11-10 |

Core reading and watching: about 69 minutes. Which video is `resources[0]` is open question 4.

## Practice ladder

Fixture rule: real output, named with where and when it was captured. Price fixtures hold whole numbers of millionths of a dollar an hour (`m7i.large 100800`), so shell arithmetic is exact and the same in both shells; the item's text gives the dollar figure too. Every price item says "read 2026-11-10" in its prompt. Fixtures marked *(after capture)* wait for a recording of a real Arm machine, from the free GitHub Arm runner described in the hypervisors brief.

### One image for all the topic's labs

A plain lab. First `RUN`, identical in all five: `ubuntu:24.04` with `gcc libc6-dev gcc-aarch64-linux-gnu libc6-dev-arm64-cross qemu-user-static file binutils unzip zip sudo nano less procps`, the `learner` user, and all of `/usr/bin/qemu-*-static` removed except the aarch64 and x86_64 ones. The labs assume an x86-64 host, which the owner's machine and CI both are; the first check of each lab should say so plainly if it isn't.

### The ladder

| # | Item | Type | Skill | Design |
| --- | --- | --- | --- | --- |
| 1 | `example-one-program-two-machines` | worked example (lab) | `read-arch`, `instruction-sets` | Below |
| 2 | `mcq-what-is-an-instruction-set` | mcq | `instruction-sets` | A Go program built on an Intel laptop is copied to a Graviton server and won't start, though both run Ubuntu 24.04. Why? **Right:** the file holds x86-64 instructions, and the server's CPU understands a different set; it must be built again for arm64. Wrong: the two Ubuntus have different library versions; the file lost its execute permission in the copy; Graviton needs programs to be signed |
| 3 | `arch-two-names` | predict_shell | `read-arch` | Files: `names.txt` (`x86_64 amd64`, `aarch64 arm64`) and `uname.txt` (`aarch64`). Command: `awk -v m="$(cat uname.txt)" '$1 == m {print $2}' names.txt`. Prints `arm64` |
| 4 | `arch-file-says` | predict_shell | `read-arch` | File: `files.txt`, six real lines of `file` output from the trial (a script, a text file, two x86-64 files, two aarch64 files). Command: `grep -c 'x86-64' files.txt; grep -c 'aarch64' files.txt`. Prints `2` and `2` |
| 5 | `mcq-script-or-binary` | mcq | `instruction-sets`, `rebuild-inventory` | Which of these moves to an Arm server with no rebuild: a Bash script, a C program, a Go program, a Rust program? **Right:** the script, because it is text and `bash` on the Arm server reads it. The wrong answers each name a compiled program with a plausible reason |
| 6 | `arch-emulation-cost` | predict_shell | `instruction-sets` | File: `times.txt`, the three measured rows (`loop 2.014 67.050`, `gzip 0.664 2.862`, `sha256 0.169 2.009`). Command: `awk '{printf "%s %dx\n", $1, $3 / $2}' times.txt`. Prints `loop 33x`, `gzip 4x`, `sha256 11x` |
| 7 | `mcq-works-on-my-laptop` | mcq | `instruction-sets` | A two-architecture image build passes on a developer's Docker Desktop and fails in CI with `exec format error`. **Right:** Docker Desktop ships an emulator and registers it; the CI machine has none until the pipeline installs one, uses an Arm machine, or cross-compiles. Wrong: CI's Docker is too old for Arm; the base image is missing in CI's region; the registry refused the Arm layers |
| 8 | `arch-signal-four` | predict_shell | `instruction-sets` | File: `runs.txt`, the real results of the v3 build (`qemu64 132`, `Nehalem 132`, `Haswell 0`, `max 0`). Command: `awk '$2 == 132 {n++} END {print n " of " NR " died with signal " 132 - 128}' runs.txt`. Prints `2 of 4 died with signal 4` |
| 9 | `mcq-illegal-instruction` | mcq | `instruction-sets`, `rebuild-inventory` | A service built on a Graviton3 machine with "use everything this CPU has" runs there and dies with `Illegal instruction` on the Graviton2 nodes. **Right:** it uses instructions the older chip lacks; build for the oldest CPU in the fleet. Wrong: Graviton2 is a different architecture; the nodes are short of memory; the binary was corrupted in transfer |
| 10 | `arch-index-platforms` | predict_shell | `read-arch` | File: a trimmed, real index of `ubuntu:24.04` read 2026-11-11 (four entries: amd64, arm64, s390x, one attestation with `unknown`). Command: `grep -o '"architecture": *"[a-z0-9]*"' index.json \| sort \| uniq -c \| awk '{print $1, $3}'`. The writer pins the output with the validator |
| 11 | `mcq-image-wont-start` | mcq | `read-arch`, `rebuild-inventory` | On an Arm node, an image that exists in the registry reports that it "does not provide the specified platform (linux/arm64)". **Right:** the tag has no arm64 image; build and push one, or keep that workload on x86 nodes. Wrong: pull with administrator rights; the node's disk is full; add `--privileged` |
| 12 | `mcq-read-the-name` | mcq | `arm-families` | Which list is all Arm? **Right:** `m8g.large`, `Standard_D4ps_v6`, `c4a-standard-4`, `t2a-standard-2`. Each wrong list swaps in one x86 look-alike: `m7a.large`, `Standard_D4as_v6`, `c4d-standard-4`, `t2d-standard-2` |
| 13 | `mcq-what-is-a-vcpu` | mcq | `arm-families`, `price-performance` | `m7i.large` and `m7g.large` both say 2 vCPUs. What is behind them? **Right:** one core's two threads on the Intel type; two whole cores on the Graviton type. Wrong: two cores on both; two threads on both; half a core each on the Graviton type |
| 14 | `arch-saving-percent` | predict_shell | `price-performance` | File: `prices.txt` (`m7i.large 100800`, `m7g.large 81600`, millionths of a dollar an hour, us-east-1, read 2026-11-10). Command: `x=$(awk '$1 == "m7i.large" {print $2}' prices.txt); g=$(awk '$1 == "m7g.large" {print $2}' prices.txt); echo "$(( (x - g) * 100 / x ))%"`. Prints `19%` |
| 15 | `arch-fleet-month` | predict_shell | `price-performance` | Same file. Command: `awk '{p[$1] = $2} END {printf "$%d a month\n", (p["m7i.large"] - p["m7g.large"]) * 730 * 40 / 1000000}' prices.txt`. Prints `$560 a month` (40 instances, 730 hours) |
| 16 | `mcq-not-cheaper` | mcq | `price-performance` | A batch tier on Google Cloud runs on `e2-standard-2` at $0.0670 an hour. Someone proposes `c4a-standard-2` at $0.0898 "because Arm is cheaper". **Right:** it lists 34% higher; Arm is not a price class, so compare the types you'd really use. Wrong answers each accept the premise |
| 17 | `mcq-what-rebuilds` | mcq | `rebuild-inventory` | A service is a Go program, two Bash scripts, a `.jar`, and a monitoring agent from a vendor. What needs what? **Right:** rebuild the Go program; the scripts run as they are; the jar runs if it has no native library inside; the agent needs the vendor's arm64 build. Three near-misses |
| 18 | `mcq-cant-move` | mcq | `rebuild-inventory`, `arm-families` | Which tier stays on x86 for now? **Right:** the SQL Server database on Windows Server, since the Arm families run Linux (and on Azure, Windows 11 client) and the SQL Server image is amd64 only. Wrong: the nginx tier, the PostgreSQL database, the Python API |
| 19 | `fill-what-arch` | fill-in (lab) | `read-arch` | Below |
| 20 | `write-arm-saving` | write (lab) | `price-performance` | Below |

### `example-one-program-two-machines` (worked example, about 20 minutes)

- **The container holds** `~/src/hello.c` (prints `hello from` and the machine's architecture) and `~/src/count.c` (a loop that counts and prints how long it took).
- **The learner types:** (1) `uname -m; dpkg --print-architecture`: one machine, two names; (2) `gcc -O2 -o hello ~/src/hello.c && file hello && ./hello`; (3) `aarch64-linux-gnu-gcc -O2 -static -o hello-arm64 ~/src/hello.c && file hello-arm64`: the same source, another instruction set; (4) `./hello-arm64`: the note says both things that can happen and why (an error, or it runs because this machine's kernel has been given an emulator); (5) `qemu-aarch64-static ./hello-arm64`: named emulator, same result everywhere; (6) build `count` both ways and run each, natively and under the emulator, and read the two times; (7) save `~/example/arch.txt`: this machine's architecture, then the architecture `file` reports for each of the two `hello` programs.
- **Checks.** `machine-line` equals `$(uname -m)`. `native-is-x86` and `cross-is-arm`: the check runs `file` on the learner's two programs. `file-lines` match what `file` says. `arm-runs-emulated`: `qemu-aarch64-static ~/hello-arm64` prints `hello from aarch64`.
- **Wrong fixes.** `copied-not-cross-built.sh` (copies `hello` to `hello-arm64`); `dynamic.sh` (no `-static`, so the emulated run can't find its loader); `typed-the-answers.sh` (writes `arch.txt` without building).

### `fill-what-arch` (fill-in, about 15 minutes)

- **The container holds** `/srv/samples/` (eight files: two scripts, a text file, x86-64 and aarch64 programs, one shared object of each, a jar) and `~/bin/what-arch` with `...` in four places. It prints one line per file given: `NAME x86-64`, `NAME aarch64` or `NAME not-a-program`.
- **Checks** compare each line with `file`, run in the check, on `/srv/samples` and on a second folder the prompt doesn't name.
- **Wrong fixes.** `by-file-name.sh` (trusts `x86_64` in the name; the seed includes a misnamed file); `elf-means-x86.sh`; `hard-coded.sh`.

### `write-arm-saving` (write, about 30 minutes)

- **The container holds** `/srv/prices/2026-11-10.csv` (the real table: `cloud,type,arch,vcpus,usd_per_hour`) with a header line naming the three sources and the date.
- **The learner writes** `~/bin/arm-saving CSV X86_TYPE ARM_TYPE COUNT`, printing three lines: `per hour: 0.0192`, `percent: 19.0`, `per month for 40: 560.64`. The prompt states the convention: 730 hours in a month, the percentage taken of the x86 price.
- **Checks**, each to a stated tolerance: `percent` within 0.5 of a point; `per-month` within 2%; `per-hour` within 0.0005. Run on three pairs from the real file and on two from `/usr/local/share/lab/prices-test.csv`, a second file with made-up prices, labelled as test data, that the prompt doesn't name. `arm-dearer`: for `D2as_v7` to `D2ps_v7` the percentage is negative (about -25.6).
- **Wrong fixes.** `percent-of-arm-price.sh` (23.5 instead of 19.0); `per-vcpu.sh` (divides by the vCPU count); `hard-coded.sh`; `absolute-value.sh` (hides that Arm is dearer).

## Proofs

### Build: `build-move-to-arm` (about 60 minutes)

**Brief the learner gets.** "The shop wants its service on Arm servers. The oldest Arm machines in the fleet have Neoverse N1 cores. Everything the service is made of is under `/srv/shop/`. (1) Write `~/bin/arm-audit DIR`, which prints, sorted, the path of every file under `DIR` that can't run on arm64 as it is: programs and libraries built for another architecture, and archives with such a library inside. (2) For `/srv/shop`, save `~/report/plan.txt` with one line for each of those files, `PATH rebuild` if the source is in `/srv/shop/src`, `PATH vendor` if it isn't. (3) Save `~/report/images.txt` with one line for each image named in `/srv/shop/images/images.txt`: `IMAGE multi` if its saved index offers linux/arm64, `IMAGE x86-only` if it doesn't. (4) Build the shop's own two programs for arm64 into `~/out/`, statically linked, so they run on the fleet's oldest machines. Don't change the sources."

- **The container holds**, all laid down by `seed.sh`:
  - `/srv/shop/bin/shop-api`, `/srv/shop/bin/shop-thumb` (x86-64, built from `/srv/shop/src/*.c`), `backup.sh`, `report.py`;
  - `/srv/shop/src/` with a `Makefile` whose flags are x86 ones (`-march=x86-64-v3`), so `make CC=aarch64-linux-gnu-gcc` alone fails, and whose comment suggests SVE flags "for speed";
  - `/srv/shop/lib/python/` with a pure-Python package and one whose `.so` is x86-64;
  - `/srv/shop/lib/java/orders.jar`, holding a class file and `native/libcrc-linux-x86_64.so`; and `labels.jar` with no native library;
  - `/srv/shop/agents/metrics-agent`, x86-64, no source;
  - `/srv/shop/images/index/*.json`: the real indexes read 2026-11-11 for `nginx:1.27`, `postgres:16` and `mcr.microsoft.com/mssql/server:2022-latest`, and one written by the seed for the shop's own image, with amd64 only;
  - `/usr/local/share/lab/depot/`, a second tree with a different mix, including an aarch64 program that must not be listed.
- **Checks.**
  - `audit-shop` and `audit-depot`: the script's output equals what the check computes with `find`, `file` and `unzip -l`.
  - `plan`: each line's verdict equals the check's (does a source file of that name exist?).
  - `images`: equals what the check reads from the saved indexes.
  - `api-is-arm64`, `thumb-is-arm64`: `file` says aarch64 and statically linked.
  - `runs-on-the-oldest`: `qemu-aarch64-static -cpu neoverse-n1 ~/out/shop-thumb --selftest` prints the same line as the x86 program run natively.
  - `sources-untouched`: checksums.
- **Shortcuts the checks must reject, each a `wrong/*.sh`.** Listing every file (`audit-lists-everything`); `find` and `file` only, which misses the library inside the jar (`audit-misses-the-jar`); listing the aarch64 program in the second tree (`audit-by-extension`); copying the x86 programs into `~/out` (`renamed-x86`); taking the Makefile's hint and building with `-march=armv8.2-a+sve`, which dies on N1 (`built-for-the-newest`); a dynamically linked build (`not-static`); marking the vendor's agent `rebuild`.

### Debug: `debug-wont-start-on-arm` (about 35 minutes)

**Prompt, to the house rule.** "The shop's thumbnail tool is released from `/srv/release/` by running `/srv/release/build.sh`, which puts the program in `/srv/release/bin/thumb`. It has to run on the fleet's Arm servers, the oldest of which have Neoverse N1 cores, and those servers have nothing installed but the program itself. Test it as they would run it: `qemu-aarch64-static -cpu neoverse-n1 /srv/release/bin/thumb --selftest`. It doesn't run. There are three faults in how the release is built. Put the recipe right and build again. Don't change the program's source."

- **The three faults, for the writer only:** the recipe calls the native compiler, so the program is x86-64; once that is fixed, its flags ask for SVE, so it dies on N1 with `Illegal instruction`; and it links dynamically, so on a bare server the loader isn't found. Each fix exposes the next symptom, so the learner meets three different errors, all recorded in the trial.
- **Checks**, as end states: `is-arm64`; `is-static`; `runs-on-the-oldest` (prints the self-test line); `recipe-rebuilds-it` (the check copies `/srv/release` to a temporary folder, runs `build.sh` there and tests that result, so a hand-built binary beside an unfixed recipe fails); `source-untouched`.
- **Shortcuts the checks must reject.** Two of three fixed (three `wrong/*.sh`); testing with `-cpu max` and calling it done (the check names N1); building by hand and leaving the recipe broken; copying the cross-compiler's libraries next to the program instead of linking statically (fails `is-static`).

### Explain

**Prompt.** "Your manager has read that Arm instances are 40% cheaper and wants the whole estate moved next quarter: a Go API, a Python service that uses packages with compiled parts, a Java application, a monitoring agent bought from a vendor, and a SQL Server database on Windows. Explain, in your own words: what an instruction set is and why a program built for x86-64 won't start on Arm, with the two error messages you'd expect to meet and what each means; which of the five parts run unchanged, which must be rebuilt, which need something from a vendor and which can't move; what the Arm families are called on AWS, Azure and Google Cloud and what a vCPU is on them; and what the saving really is at list price, what you'd measure before promising it, and how you'd roll it out."

| Rubric id | Required | The answer says |
| --- | --- | --- |
| `instruction-set` | yes | A CPU family understands one set of instructions; a compiled program holds those instructions, so an x86-64 file fails on Arm with `Exec format error`; interpreted programs move if their interpreter exists there |
| `inventory` | yes | Go: rebuild. Python: the code runs, the compiled packages need arm64 builds. Java: bytecode runs on an Arm JVM unless a jar carries a native library. Agent: the vendor's arm64 build. SQL Server on Windows: stays on x86 |
| `families` | yes | Graviton on AWS (`g` in the name), Cobalt and Ampere on Azure (`p`), Axion and Ampere on Google (C4A, N4A, T2A); a vCPU there is a whole core, where on most x86 types it is one of a core's two threads |
| `money` | yes | The list price at equal size is roughly 10 to 30% lower, not 40%; the larger figure is a claim about work per dollar; measure throughput per dollar on the real workload; count the cost of the work |
| `feature-level` | no | `Illegal instruction` when a build uses instructions an older chip of the same family lacks; build for the oldest CPU in the fleet |
| `rollout` | no | Start with stateless, open-source parts; run a mixed fleet; canary; images for both architectures |
| `not-always` | no | Cases where Arm costs more or isn't offered |

## Review pool

`review_pool:` gets the ten marked ●.

| Skill | Come-back questions |
| --- | --- |
| `read-arch` | `arch-two-names` ●, `arch-file-says` ●, `arch-index-platforms`, `mcq-image-wont-start`, `fill-what-arch`; *(after capture)* `arch-lscpu-arm`: three lines of `lscpu` from a real Arm machine |
| `instruction-sets` | `mcq-what-is-an-instruction-set` ●, `arch-emulation-cost`, `mcq-works-on-my-laptop` ●, `arch-signal-four` ●, `mcq-illegal-instruction` |
| `rebuild-inventory` | `mcq-script-or-binary`, `mcq-what-rebuilds` ●, `mcq-cant-move` ●; add `arch-jar-native`: a real `unzip -l` listing and `grep -c '\.so$'` |
| `arm-families` | `mcq-read-the-name` ●, `mcq-what-is-a-vcpu`; add `mcq-which-generation`: a build that needs SVE, and three AWS families to place it on (M6g, on Graviton2, can't run it; M7g and M8g can) |
| `price-performance` | `arch-saving-percent` ●, `arch-fleet-month` ●, `mcq-not-cheaper`, `write-arm-saving`; add `arch-pay-back`: work priced at $9,000 against $560 a month, `echo $(( (9000 + 559) / 560 ))`, prints `17` |

## Platform work

None is required to write this topic. Two things are worth doing first:

1. **A `numeric` recall item** (`type: numeric`): a prompt, an `answer`, a `tolerance` (absolute, or a percentage of the answer) and an optional `unit`. The page shows a number box; the answer is right when it is within the tolerance. The validator checks that `answer` and `tolerance` are numbers and the tolerance is positive. This is the honest form of "estimate the saving": today it has to be a `predict_shell` item whose arithmetic the learner follows, or a multiple-choice question. Topics 17, 18 and 20 and Checkpoint 2 ("code checks the estimates") need it more than this topic does, since their learners haven't done Python either.
2. **Price fixtures need a date and a refresh.** A comment line in every price fixture names the source and the day it was read; a note in `content/README.md` says to re-read them yearly. The validator can't check a price.

Not needed now, and recorded so it isn't rediscovered: a checked `docker buildx` lab would need a checker mode that runs checks on the host, a local registry, and an emulator installed on the CI runner. It belongs with `csa.auto.containers`.

## Cost and time

**Cost to the learner: nothing.** No cloud account is used. A real Arm VM is optional and belongs later: AWS offers a `t4g.small` trial until 2026-12-31, and Azure's `B2pts_v2` lists at $0.0084 an hour.

**Time:**

| Part | Minutes |
| --- | --- |
| Lesson intro and recap (longer than Module 1's: about thirty new terms) | 15 |
| Core watching and reading (resources 0 to 9) | 69 |
| 18 recall items at about 90 seconds | 27 |
| Worked example, fill-in, write | 65 |
| Build, debug | 95 |
| Explain | 15 |
| **Total: `estimated_minutes: 290`** | **286** |

The lab image is the largest in the track so far; allow three minutes for its first build.

## Not confirmed

- **How the pages were read.** Microsoft's and AWS's documentation pages came back in full. The GitHub, Red Hat, Docker, Google Cloud and Arm pages came back as extracts made by the fetching tool, with quotations. Read each in full before quoting it in a lesson.
- **The two videos were not watched.** Title, channel, length, description and that embedding is allowed were read.
- **`Exec format error` could not be produced on this machine**, because Docker Desktop's emulator runs foreign programs instead. The message and its exit status (expected 126) must be captured on a machine without one, such as a CI runner.
- **The message for a tag whose index lacks a platform** was not produced. What was produced is the message for an image with no index (fact 15).
- **A real Arm machine's `lscpu`** waits for a capture from the free Arm runner.
- **`D2ps_v7`.** It is in Azure's price list at $0.114 (effective 2026-10-01), and an Azure blog found by search announces Cobalt 200 VMs, but no documentation page for the series could be opened (the expected address returned "not found"). The table shows the price and leaves the chip's name out. Its price is published and may be used as a number, as `write-arm-saving`'s last check does; don't name its chip or say it is generally available until its page exists.
- **Windows Server on Arm.** Azure's Cobalt 100 page lists Windows 11 Client and no Windows Server; that page was last updated 2025-07-03, and the price list carries Windows meters for the v7 Arm series. Check again when writing `mcq-cant-move`.
- **Which chip Ampere Altra is built on, and whether it has SVE,** was not read from Ampere or Arm; no item depends on it.
- **Google's prices are for Iowa** on the evidence that the page's region selector shows Iowa selected and the figures match that region's known prices; the page gives no machine-readable region for its default tables.
- **The lab image's size after trimming the emulators** is an estimate.
- **Nothing in the practice ladder or the proofs has been built or run under `labcheck test`.**

## What Checkpoint 2 can draw on

Part 1 ("right-size five described workloads across the three clouds, including a move to Arm") can name `csa.hw.cpu-architectures/price-performance`, `/rebuild-inventory` and `/arm-families` in `test_skills`. The price file and `arm-saving`'s checks are the pattern for "code checks the estimates" without Python.

## Open questions, each with a recommendation

1. **A checked `docker buildx` lab here, or in Module 6?** It works on this machine. It would not behave the same in CI, needs a checker mode that doesn't exist, and uses commands the track hasn't taught. *Recommend: Module 6. Here, an unchecked "try it" box with one command (`docker run --rm --platform linux/arm64 ubuntu:24.04 uname -m`, which prints `aarch64` on Docker Desktop) and the explanation of why it worked.*
2. **Should the learner start a real Arm VM?** It would add nothing the emulator and a recording don't, and the budget guardrails come in Module 8. *Recommend: no; offer it as an optional extra in `csa.compute.vms`.*
3. **Build the `numeric` item type now?** It serves four topics and the checkpoint of this module. *Recommend: yes, before the review pools of topics 17 to 20 are written; this topic can ship without it.*
4. **Which resource is the main one?** The video teaches the idea the topic stands on and is the only one a beginner can take in cold; the transition guide teaches the job. *Recommend: the video (#8) as `resources[0]`, the guide named in the lesson as the second thing to read.*
5. **Python.** *Recommend: none in this topic; say so in the lesson, since a learner may wonder why prices aren't a spreadsheet or a script in Python.*
6. **The spec says "say when Arm saves 20–40%".** The price lists read on 2026-11-10 show 7 to 31% at equal size, and two cases where Arm costs more. *Recommend: reword the row to "say what Arm saves, from price lists, and what has to be rebuilt to get it", and regenerate the outline.*
7. **Two topics in one?** Instruction sets and the inventory are one story; the cost comparison could be its own short topic. At 290 minutes it is the longest topic in the track so far. *Recommend: keep it whole for now and watch the owner's time on it; if it runs past five hours, move `price-performance` and its three items into topic 17, which is about what a vCPU buys.*
