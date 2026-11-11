# Writing brief: Hypervisors (`csa.hw.hypervisors`, topic 15)

Module 2, "Virtualization, hardware and Windows", of the Cloud Solutions Architect track. Designed 2026-11-10 to 2026-11-11. Nothing here is written into the repository yet; this is the brief a writer builds the topic from.

**Decisions in one paragraph.** The topic is proven entirely on the learner's machine, at no cost. The learner does three hands-on things: reads what a Linux guest reveals about the hypervisor under it (live, on the lab machine, and in recordings of real cloud VMs); boots a small virtual machine with QEMU and chooses its hardware, so "emulated" and "paravirtual" are things they typed and saw; and classifies a fleet of recorded servers. There is no cloud lab: the track's budget guardrails don't exist until Module 8, and nothing here needs one. Recorded output is honest when it is really recorded, labelled and scrubbed, and it can be obtained for nothing (see [Where the recordings come from](#where-the-recordings-come-from)).

Words used in this brief: a **capture** is a folder of small text files holding what one machine printed for a fixed list of commands. **TCG** is QEMU's built-in emulator, which runs a guest with no help from the CPU.

## What the learner will be able to do

- Say what a hypervisor does, tell a type 1 from a type 2, and place KVM with QEMU, Hyper-V, Xen and AWS Nitro.
- From inside a Linux guest, work out what it is running on and how its disk and network card reach the hardware.
- Tell an emulated device from a paravirtual one and from an SR-IOV virtual function, and say what each costs.
- Say how AWS, Azure and Google Cloud build their hosts, what a guest sees on each, and what host maintenance does to a running VM on each.
- Say what a hypervisor isolates and what it doesn't, and what dedicated tenancy, an isolated size, a sole-tenant node or bare metal changes.

### The six-month core

What should still be there half a year later, and what the review pool is built to keep:

1. In two minutes on any Linux server: is this a VM, on what, and are its NIC and disk on the fast path? (`systemd-detect-virt --vm`, `lscpu`, the driver behind each device.)
2. The three device paths and their trade-off in one sentence each.
3. One line per cloud: what the host is built from, what the guest sees, what maintenance does.
4. The list of things a hypervisor does not protect a VM from, and the product on each cloud that closes each gap.
5. Why "KVM isn't available" inside a cloud VM, and what nested virtualization is.

Names of side-channel attacks, Nitro version numbers and PCI IDs are not in the core. They appear in fixtures, never as the thing asked.

## Prerequisites

Real ones, by topic:

| Needs | From | Why |
| --- | --- | --- |
| "hypervisor" and "VM" in one clause each, steal time, vCPU, `top`, `nproc` | `csa.linux.cpu` | the lesson starts from steal time: someone took the CPU away |
| virtual memory, RSS, exit status 128 + signal | `csa.linux.memory` | guest memory is a second layer of the same idea; a VM's memory is its process's RSS |
| a container is not a VM; namespaces; one shared kernel | `csa.linux.containers` | `systemd-detect-virt` answers "container" before "VM", and the lab machine is a container on a VM |
| firmware, bootloader, kernel, initramfs, `dmesg`, serial console | `csa.linux.boot` | the QEMU labs boot a kernel and an initramfs and read the serial console |
| block devices, `lsblk`, NVMe device names | `csa.linux.storage` | disks are half of the device story |
| interfaces, `ip`, a veth pair | `csa.linux.net-tools` | NICs are the other half; the lab container's own `eth0` is a veth, which the lesson must say |
| scripts with arguments, `chmod +x`, unset variables | `csa.linux.scripting` | the fill-in, the build and the debug are scripts |
| `grep`, `awk`, `sort`, pipes | `csa.linux.shell` | every recall item and check |
| ownership and modes | `csa.linux.permissions` | the debug's last fault is a disk image any user can read |

Recommended `prerequisites:` line: `[csa.linux.containers, csa.linux.boot, csa.linux.storage, csa.linux.net-tools, csa.linux.scripting, csa.linux.permissions]`. The others follow from these (containers needs cpu and memory; all need shell). See open question 7 on whether to keep `csa.m1.checkpoint` as the gate.

### Terms this topic must define itself

Module 1 used none of these, or used them in passing without a definition. Each needs one plain sentence at first use:

- **guest**, **host**, **virtual CPU (vCPU)** (used in `csa.linux.cpu`, never defined), **virtual machine monitor**
- **privileged instruction** and **kernel mode against user mode** (Module 1 says "the kernel" 11 lessons over without this split)
- **hardware virtualization extensions** (Intel VT-x, AMD-V; on Arm, EL2), **emulation**, **QEMU**, **TCG**, **KVM**, `/dev/kvm`
- **type 1**, **type 2**, **bare metal**
- **device driver** (the boot lesson says "drivers" once), **PCI device** and what `lspci` lists, **DMI** (the name plate a machine's firmware reports: vendor, product)
- **paravirtual**, **virtio**, **VMBus** and **synthetic device**, **enlightened guest**
- **SR-IOV**, **physical function**, **virtual function (VF)**, **passthrough**
- **offload card** (Nitro card, Azure Boost)
- **nested virtualization**, **live migration**, **host maintenance**
- **side channel**, **hyperthread / SMT** in one clause (topic 17 teaches it), **tenant**, **dedicated host**, **confidential VM** in one clause (taught in `csa.secarch.confidential`)
- Commands new to the learner: `systemd-detect-virt`, `lscpu`, `lspci`, `tee`, `qemu-system-x86_64`, `qemu-img`

## Skills

| Skill | What it covers |
| --- | --- |
| `hypervisor-types` | What a hypervisor does (shares CPU, memory and devices between guests and traps what a guest may not do itself); type 1 against type 2; emulation against hardware-assisted virtualization (QEMU alone against QEMU with KVM); nested virtualization |
| `read-the-guest` | Work out from inside a Linux guest what it runs on: `systemd-detect-virt` and its innermost-only rule, `lscpu`'s hypervisor lines, the `hypervisor` CPU flag, the DMI vendor, the boot log |
| `device-paths` | Tell emulated, paravirtual and SR-IOV or passthrough devices apart by driver and bus, and say what each costs in speed, drivers and mobility |
| `cloud-hypervisors` | How the three clouds build it and what a guest sees: Nitro (a KVM-based hypervisor plus offload cards: NVMe and ENA), Azure (Hyper-V: VMBus devices, an Accelerated Networking VF), Google (KVM: virtio or gVNIC); what host maintenance does on each |
| `isolation-limits` | What a hypervisor isolates and what it can't: performance, side channels on shared hardware, the host failing, the host's operator; what dedicated tenancy and bare metal change |

## Lesson plan

The order of ideas, each with the resource section that carries it. The lesson's own text supplies the three explanations marked **lesson must supply**.

1. **Start from steal time.** `csa.linux.cpu` showed `st` in `top`: the host took our CPU away. Who is "the host"? A hypervisor has three jobs: share the CPUs (each vCPU is a thread the host schedules), share the memory (each guest gets its own "physical" memory, mapped a second time), and hand out devices. The third is the hard one and most of this topic. *Resource: Red Hat, "What is a hypervisor?", whole page (4 minutes).*
2. **Lesson must supply: what "trap" means, without assembly.** A guest's kernel believes it owns the machine. Some instructions only an owner may run (switch off interrupts, talk to a disk controller). With the CPU's virtualization extensions switched on, the CPU itself stops at each of those and hands control to the hypervisor, which does the safe equivalent for that guest only and hands back. Everything else runs directly on the real CPU at full speed. Without the extensions every instruction has to be imitated in software, which is emulation. Give the measured number: the same 300,000-step loop took 0.89 s on the host and 12.76 s in an emulated guest, 14 times slower (see [Evidence](#evidence-from-trying-it)).
3. **Type 1 and type 2, honestly.** Type 2 runs as a program on an ordinary operating system (VirtualBox, QEMU on its own). Type 1 owns the hardware (ESXi, Hyper-V, Xen). KVM blurs the line: it turns the Linux kernel into the hypervisor, and is counted as type 1. The question worth keeping: *what else runs with full control of the hardware?* Hyper-V has a root partition running Windows; Xen has dom0; KVM has the whole Linux host; Nitro has nothing but a small hypervisor. *Resources: Red Hat page; Microsoft, "Hyper-V architecture", the first three sections (5 minutes).*
4. **Lesson must supply: three ways to give a guest a network card, as one picture in words.** A restaurant with one kitchen (the physical card). *Emulated:* a waiter pretends to be a 1996 Intel card, and the guest speaks to him in that card's language, register by register; any guest can do it and it is slow. *Paravirtual:* the guest knows it is in a restaurant and uses an order pad both sides agreed on (virtio on KVM, VMBus on Hyper-V); fast, but the guest needs that driver, and the host's software still carries every plate. *SR-IOV:* the kitchen has many hatches, and the guest is given one of its own (a virtual function of the physical card); nearly bare-metal speed, but the guest is now tied to that card, which is awkward when the host needs maintenance. Then Nitro: the kitchen moved out of the building onto its own cards, and the hypervisor only hands out hatches. *Resource (the main one): Brendan Gregg, "AWS EC2 Virtualization 2017: Introducing Nitro" (10 to 15 minutes with its diagram). The lesson intro must gloss its vocabulary first: PV, HVM, PVHVM, dom0, SR-IOV.*
5. **The three clouds. Mark the differences.** One table, three rows, filled only from the verified facts below:

   | | AWS | Azure | Google Cloud |
   | --- | --- | --- | --- |
   | Hypervisor | Nitro hypervisor, built on KVM; Xen on T2 | Hyper-V | KVM-based |
   | What else is on the host | Nothing in the I/O path: Nitro cards do network, storage and management | A root partition; Azure Boost moves network and storage to hardware on newer sizes | Not stated in the documentation that could be opened (see Not confirmed) |
   | NIC the guest sees | ENA, a PCI device | `hv_netvsc` on VMBus, plus a Mellanox or MANA virtual function when Accelerated Networking is on | virtio-net, or gVNIC (`gve`), which newer and Arm series require |
   | Disk the guest sees | NVMe | SCSI on VMBus; NVMe on Boost sizes | SCSI or NVMe (NVMe only on the Arm T2A series) |
   | Host maintenance | hypervisor replaced live, in place | VM paused for up to 30 s; the VF is taken away and traffic falls back to the synthetic NIC for about 30 s | live migration to another host; a blackout typically well under a second, the clock may jump up to 5 s |
   | Nested virtualization | M7i, M8i, C7i, C8i, R7i, R8i and relatives, and bare metal | not on the Arm Dpsv6 sizes | most Intel series and N4D; not E2, memory-optimized or Arm |
   | No other tenant on the host | Dedicated Instances, Dedicated Hosts | isolated sizes (about 10% dearer), Dedicated Host | sole-tenant nodes |

   *Resources: AWS whitepaper "The components of the Nitro System" (12 minutes); Microsoft, "How Accelerated Networking works in Linux and FreeBSD VMs", as far as "Azure host servicing" (8 minutes); Google, "Live migration process during maintenance events" (6 minutes).*
6. **Reading the guest.** Five places, in the order to try them: `systemd-detect-virt` (and why it says `docker` or `wsl` until you add `--vm`: it reports the innermost layer only), `lscpu`'s `Hypervisor vendor` and `Virtualization type`, the `hypervisor` word in the CPU flags, the DMI vendor under `/sys/class/dmi/id/`, and the first lines of the boot log. Then the driver behind each NIC and disk. Say plainly what the lab machine is: a container, on a Linux VM, on the learner's laptop, so its own `eth0` is a veth and tells nothing; that is what the recordings are for. *Resource: `systemd-detect-virt(1)`.*
7. **Lesson must supply: what it can't isolate, as a list a person can say from memory.** A hypervisor keeps guests out of each other's memory and devices. It does not, by itself, give you: (a) *steady speed*: neighbours can share the processor's largest cache, and on burstable sizes the core itself, in turns; (b) *freedom from side channels*: hardware shared at the same moment can leak, which is why AWS never runs two customers on one core at the same time and why `lscpu` lists a `Vulnerability` line per known attack; (c) *a host that doesn't fail*: when it stops, every guest on it stops; (d) *privacy from the operator*, unless the platform is built without operator access (Nitro) or the memory is encrypted from the host (confidential VMs, a later topic); (e) *immunity from a hypervisor bug*, which is the argument for a small hypervisor. Then what you can buy: a host to yourself removes other tenants and nothing else on that list. *Resources: AWS whitepaper, "The EC2 approach to preventing side-channels" (10 minutes); Microsoft, "Isolation for VMs in Azure" (3 minutes).*

Recap bullets follow the seven steps. The "Read now" paragraph names the labs as Module 1's lessons do.

## Verified facts

Every specific claim the topic may make. "Read" is the date the page was fetched. Where a page carries its own date it is given.

| # | Claim | Source | Read |
| --- | --- | --- | --- |
| 1 | The Nitro System has three parts: Nitro cards, the Nitro security chip, the Nitro hypervisor | https://docs.aws.amazon.com/whitepapers/latest/security-design-of-aws-nitro-system/the-components-of-the-nitro-system.html | 2026-11-10 |
| 2 | The Nitro hypervisor is "a lightweight hypervisor that manages memory and CPU allocation"; by design it has no networking stack, no general-purpose file system, no peripheral drivers, no shell and no interactive access | https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-nitro-instances.html and the whitepaper page above | 2026-11-10 |
| 3 | The Nitro hypervisor is based on core KVM technology | https://aws.amazon.com/ec2/faqs/ (the High Memory entry: "lightweight Nitro Hypervisor that is based on core KVM technology"); systemd's manual lists `amazon` as Amazon EC2 Nitro using Linux KVM | 2026-11-10 |
| 4 | Nitro cards present NVMe for block storage and ENA for networking over PCIe; under the hypervisor each function is split into SR-IOV virtual functions assigned directly to VMs | whitepaper page above | 2026-11-10 |
| 5 | "Instances built on the AWS Nitro System use ENA for enhanced networking, and storage volumes exposed as NVMe block devices" | https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-nitro-instances.html | 2026-11-10 |
| 6 | Nitro versions and families: M5, T3, T4g, M6g are v2; M7g, M7i, M7a are v4; M8g is v5; M8i, M8a, M9g are v6 | same page | 2026-11-10 |
| 7 | T2 is the only general-purpose family whose hypervisor is listed as Xen | https://docs.aws.amazon.com/ec2/latest/instancetypes/gp.html | 2026-11-11 |
| 8 | A bare metal instance can take 20 minutes or more to become reachable; the security chip, not a hypervisor, protects its firmware | Nitro instances page; whitepaper page | 2026-11-10 |
| 9 | Nitro has no operator access: no mechanism to log in to a host or read an instance's memory | https://docs.aws.amazon.com/whitepapers/latest/security-design-of-aws-nitro-system/no-aws-operator-access.html | 2026-11-11 |
| 10 | On EC2, fixed-performance instances get pinned cores; cores are never shared between customers at the same time through SMT; instances come in multiples of 2 vCPUs where the hardware uses SMT and of 1 where it doesn't (Graviton); burstable types (T3, T3a, T4g) may run one after another on a core, with state flushed between; memory pages are never shared across instances; Dedicated Instances and Dedicated Hosts opt out of sharing hardware | https://docs.aws.amazon.com/whitepapers/latest/security-design-of-aws-nitro-system/the-ec2-approach-to-preventing-side-channels.html | 2026-11-11 |
| 11 | The Nitro hypervisor is updated live, in place, with instances running | whitepaper components page | 2026-11-10 |
| 12 | AWS nested virtualization runs on virtual (not only bare metal) instances of M7i, M7i-flex, M8i, M8id, M8i-flex, C7i, C7i-flex, C8i, C8id, C8i-flex, R7i, R7iz, R8i, R8id, R8i-flex, X8i, I7i, I7ie; KVM and Hyper-V are the supported inner hypervisors; no extra charge | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/amazon-ec2-nested-virtualization.html | 2026-11-11 |
| 13 | "The Azure hypervisor system is based on Windows Hyper-V"; the host OS in the root partition has direct access to the physical devices and exposes virtual devices to guest partitions | https://learn.microsoft.com/en-us/azure/security/fundamentals/hypervisor (page dated 2022-11-10, updated 2026-07-21) | 2026-11-10 |
| 14 | Hyper-V: partitions; a root partition running Windows; child partitions reach devices over VMBus; enlightened I/O bypasses device emulation and needs a guest that knows about the hypervisor; needs Intel VT or AMD-V | https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/architecture (dated 2026-01-21) | 2026-11-10 |
| 15 | Accelerated Networking is SR-IOV. Without it all traffic crosses the host and its virtual switch; with it traffic goes straight to the VM and policy is applied in hardware. It can't be switched on while the VM runs. Most general-purpose and compute-optimized sizes with 2 or more vCPUs support it (4 or more where hyperthreaded). The cards are NVIDIA/Mellanox ConnectX and Microsoft's MANA | https://learn.microsoft.com/en-us/azure/virtual-network/accelerated-networking-overview (dated 2026-08-11) | 2026-11-10 |
| 16 | In a Linux guest the synthetic NIC is a VMBus device on the `hv_netvsc` driver; the VF is a PCI device on `mlx4`, `mlx5` or `mana`; both carry the same MAC; the IP address is on the synthetic one; applications use the synthetic one. During host servicing the VF is removed and traffic continues on the synthetic path, typically for about 30 seconds, sometimes a few minutes, several times a year. The boot log prints `Data path switched to VF` and `from VF` | https://learn.microsoft.com/en-us/azure/virtual-network/accelerated-networking-how-it-works (dated 2026-07-16) | 2026-11-10 |
| 17 | Dpsv6 (Arm): Accelerated Networking required, nested virtualization not supported, generation 2 only | https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/dpsv6-series (updated 2026-10-27) | 2026-11-10 |
| 18 | Azure Boost "offloads server virtualization processes traditionally performed by the hypervisor and host OS onto purpose-built software and hardware": networking (MANA) and storage (an FPGA, NVMe interfaces) | https://learn.microsoft.com/en-us/azure/azure-boost/overview (dated 2025-03-18) | 2026-11-11 |
| 19 | During memory-preserving maintenance Azure VMs "are paused for up to 30 seconds" | https://learn.microsoft.com/en-us/azure/virtual-machines/linux/time-sync | 2026-11-11 |
| 20 | Azure has deployed mitigations so one customer can't attack another through the speculative-execution flaws; a customer running untrusted code inside a VM should take further steps, including a size without hyperthreading; `lscpu`'s `Thread(s) per core: 2` means hyperthreading | https://learn.microsoft.com/en-us/azure/virtual-machines/mitigate-se (dated 2024-02-26) | 2026-11-11 |
| 21 | Azure isolated sizes are dedicated to one customer and cost roughly 10% more; a Dedicated Host reserves a host for several of one customer's VMs; a confidential VM encrypts without physical isolation | https://learn.microsoft.com/en-us/azure/virtual-machines/isolation (dated 2026-09-25) | 2026-11-11 |
| 22 | Compute Engine VMs run on "Google's security-hardened, KVM-based hypervisor". Nested virtualization (L0, L1, L2) isn't supported on E2, memory-optimized or Arm VMs, nor on AMD except N4D; only KVM may be the inner hypervisor; expect 10% or more lost on CPU-bound work | https://docs.cloud.google.com/compute/docs/instances/nested-virtualization/overview | 2026-11-10 |
| 23 | Live migration moves a running VM to another host in the same zone for maintenance, security updates or a predicted hardware failure, in three stages (source brownout, blackout, target brownout); disruption is "typically much less than 1 second"; the clock may appear to jump up to 5 seconds; VMs with GPUs and bare metal instances are stopped instead | https://docs.cloud.google.com/compute/docs/instances/live-migration-process | 2026-11-11 |
| 24 | gVNIC is "a virtual network interface designed specifically for Compute Engine", driver `gve`; third-generation and later series support only gVNIC; Arm and Confidential VMs need it | https://docs.cloud.google.com/compute/docs/networking/using-gvnic | 2026-11-11 |
| 25 | A sole-tenant node is "a physical Compute Engine server that is dedicated to hosting only your project's VMs", billed with a premium | https://docs.cloud.google.com/compute/docs/nodes/sole-tenant-nodes | 2026-11-11 |
| 26 | KVM is "a full virtualization solution for Linux on x86 hardware containing virtualization extensions (Intel VT or AMD-V)": `kvm.ko` plus `kvm-intel.ko` or `kvm-amd.ko`, in the mainline kernel since 2.6.20, with its userspace part in QEMU | https://linux-kvm.org/page/Main_Page | 2026-11-11 |
| 27 | QEMU's accelerators: KVM (Linux), Xen, HVF (macOS), WHPX (Windows), and TCG, a JIT "capable of emulating many CPUs"; the default is pure emulation. VirtIO devices are "specifically tuned for efficient operation under virtualisation" | https://www.qemu.org/docs/master/system/introduction.html | 2026-11-10 |
| 28 | SR-IOV "makes one physical device appear as multiple virtual devices": a physical function and virtual functions, which the kernel treats as hot-plugged PCI devices | https://docs.kernel.org/PCI/pci-iov-howto.html | 2026-11-11 |
| 29 | `systemd-detect-virt` identifies `qemu`, `kvm`, `amazon`, `microsoft`, `google`, `xen`, `vmware`, `apple` and others, and the containers `docker`, `podman`, `lxc`, `wsl`; with several layers only the innermost is reported; exit status is non-zero when nothing is detected | https://www.freedesktop.org/software/systemd/man/latest/systemd-detect-virt.html | 2026-11-10 |
| 30 | Ubuntu 24.04 ships systemd 255, whose `systemd-detect-virt --list` includes `amazon`, `google` and `apple` | run in `ubuntu:24.04` on this machine | 2026-11-11 |
| 31 | On a Nitro instance `/sys/devices/virtual/dmi/id/board_asset_tag` holds the instance ID; the system UUID often, not always, starts with `ec2` | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/identify_ec2_instances.html | 2026-11-11 |
| 32 | On Compute Engine `dmidecode -s system-product-name` prints `Google Compute Engine` | https://docs.cloud.google.com/compute/docs/instances/detect-compute-engine | 2026-11-11 |
| 33 | On an Azure Linux VM `/sys/class/ptp/ptp0/clock_name` reads `hyperv`, and `lsmod` shows `hv_utils` and `hv_vmbus` | https://learn.microsoft.com/en-us/azure/virtual-machines/linux/time-sync | 2026-11-11 |
| 34 | PCI IDs: `1d0f` Amazon (`8061` NVMe EBS Controller, `ec20` ENA); `1ae0` Google (`0042` gVNIC); `1af4` Red Hat virtio (`1000`/`1041` network, `1001`/`1042` block); `1414` Microsoft (`00ba` Azure Network Adapter); `15b3:1016` Mellanox ConnectX-4 Lx Virtual Function | https://pci-ids.ucw.cz/v2.2/pci.ids, version 2026.11.09 | 2026-11-11 |
| 35 | Type 1 runs on the hardware, type 2 as an application on an operating system; KVM is listed as type 1 and has been in Linux since 2007 | https://www.redhat.com/en/topics/virtualization/what-is-a-hypervisor | 2026-11-11 |
| 36 | The stages from full emulation through Xen PV, HVM, SR-IOV networking (2013) and storage, to Nitro (2017, KVM without QEMU) and bare metal; Nitro's overhead "often less than 1%" (one engineer's measurement) | https://www.brendangregg.com/blog/2017-11-29/aws-ec2-virtualization-2017.html | 2026-11-11 |
| 37 | GitHub-hosted runners are free on public repositories, with x64 and arm64 Linux labels (4 CPUs, 16 GB). Since 2026-10-28 an eligible Linux job may run on AWS or on Azure | https://docs.github.com/en/actions/reference/runners/github-hosted-runners ; https://github.blog/changelog/2026-10-28-github-actions-adds-multi-cloud-compute-to-improve-reliability/ | 2026-11-10, 2026-11-11 |

Where sources disagree: Red Hat calls KVM type 1 without comment; QEMU's own documentation treats KVM as one accelerator among several under a program that runs on a host OS. The lesson says both and moves to the practical question in step 3.

## Evidence from trying it

Run on this machine (Windows 11, Docker Desktop 29.8.2, kernel `6.18.33.2-microsoft-standard-WSL2`, Intel Core Ultra (model masked)) on 2026-11-10 and 2026-11-11. Everything started was removed afterwards, except as noted in the summary.

- **What a container here reveals.** `systemd-detect-virt` printed `wsl`; with `--vm`, `microsoft`. `lscpu` printed `Hypervisor vendor: Microsoft` and `Virtualization type: full`; the CPU flags include `hypervisor` and `vmx`. `/sys/bus/vmbus/devices` holds 43 devices and `/sys/bus/virtio/devices` 2. There is **no DMI** (`/sys/class/dmi/id` doesn't exist under WSL2), **no `/dev/kvm`** even in a privileged container, and **`dmesg` no longer holds the boot messages** (the buffer had rotated; an unprivileged container can't read it at all). The container's `eth0` has no driver: it is a veth.
- **Consequence for checks.** A live check may rely on `systemd-detect-virt --vm`, `lscpu`, the CPU flags and the bus folders, and must compute the right answer on the machine it runs on (the owner's laptop is a Hyper-V guest; a CI runner is an Azure or an AWS VM; a Linux laptop is bare metal and prints `none` with a non-zero exit status). Nothing may depend on `dmesg`, DMI or KVM being there.
- **A VM boots in a plain lab container, as the `learner` user.** `qemu-system-x86` 8.2.2 from Ubuntu 24.04, the stock `linux-image-virtual` kernel (6.8.0-149) and an initramfs made from `busybox-static`: 16 to 27 seconds per boot under TCG with other containers busy. The image is 381 MB.
- **The guest sees what it was given.** Default: 1 CPU, `nic: eth0 driver=e1000`, DMI vendor `QEMU`, product `Ubuntu 24.04 PC v2 (i440FX + PIIX, arch_caps fix, 1996)`. With `-smp 2 -m 512 -nic user,model=virtio-net-pci -drive ...,if=virtio`: 2 CPUs, `MemTotal` 468,880 kB, `driver=virtio_net`, `vda driver=virtio_blk`. With `model=e1000` and `if=ide`: `driver=e1000`, `sda driver=sd`. The stock kernel has virtio and the IDE controller built in; `e1000` is a module the initramfs must carry.
- **Emulation costs 14 times here.** A 300,000-step shell loop: 0.89 s on the host, 12.76 s in the guest.
- **KVM is refused here**, with the exact text `Could not access KVM kernel module: No such file or directory` and `qemu-system-x86_64: -accel kvm: failed to initialize kvm: No such file or directory`.
- **A VM is a process.** While the 2-vCPU, 512 MB guest ran: one `qemu-system-x86` process (the name is cut to 15 characters), 4 threads, 267 MB resident, 113% CPU, two of the threads busy.
- **The draft capture script works**: `<design folder>/experiments/hv/lab-capture`, and one real capture made with it is in `<design folder>/experiments/hv/captures/this-laptop-docker-desktop-wsl2/`. Two things to change before use: read the boot log from `journalctl -k -b` first and `dmesg` second, and record each disk's and NIC's full `/sys` device path (`readlink -f /sys/block/sda`), which names the bus (`VMBUS`, `virtio0`, `nvme`) even where the driver name alone doesn't.

## Where the recordings come from

A recording is honest if four things hold: it was captured, not typed; it is labelled with the cloud, the instance type, the image, the kernel and the date; it is stored as captured, with only identifying values masked (instance IDs, UUIDs, MAC and IP addresses, hostnames, serials); and the learner also runs the same commands on a live machine, so the reading skill is never exercised on recordings alone.

| Capture | How to get it | Cost | Status |
| --- | --- | --- | --- |
| `laptop-wsl2` (Hyper-V under Windows 11) | `lab-capture` in a privileged container | free | done, 2026-11-11 |
| `qemu-emulated`, `qemu-virtio` (a QEMU guest with emulated, then paravirtual devices) | the guest's own report, converted to the capture layout by the lab's `seed.sh` | free | reports exist from the trial; conversion to write |
| `runner-x64-a`, `runner-x64-b` (GitHub-hosted Linux runners: Azure, and since 2026-10-28 possibly AWS) | a manually started workflow in the public repository that runs `sudo lab-capture` on the runner itself and uploads the folder; run it until both clouds have turned up | free | to do; needs no cloud account |
| `runner-arm64` (an Arm runner) | the same workflow on `ubuntu-24.04-arm` | free | to do |
| `runner-kvm-guest` (a QEMU guest with KVM) | the same workflow boots the lab's guest with `-accel kvm`, which a runner's `/dev/kvm` should allow | free | to do; unproven |
| `gcp-e2-micro` | the owner starts the always-free `e2-micro` in `us-central1`, `us-west1` or `us-east1`, runs the script, deletes the VM | free tier | owner, about 20 minutes |
| `azure-an-on`, `azure-an-off` (one VM, Accelerated Networking on then off) | the owner, on a size where the feature is optional (on the Arm D-series it is required; check the size's page), such as a `Standard_D2s_v5` at $0.096 an hour, for about 30 minutes | about $0.05 from the Azure credit | optional; owner approves |

The topic can go `ready` on the first five rows. Until the Google capture exists, Google appears only in multiple-choice items built on the documentation, never as "captured output".

**What stays unproven until the runner workflow has run once:** what a GitHub runner's capture actually contains (whether DMI is readable, whether the NIC is `hv_netvsc` with a VF or an ENA, whether `/dev/kvm` is usable, whether a job from this repository ever lands on AWS), and so the exact text of the recall fixtures marked *(after capture)* below and of the capture folders the labs read.

## Resources

All fetched and read on the date shown. Minutes are reading time at about 200 words a minute, or the video's running time.

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (main) | AWS EC2 Virtualization 2017: Introducing Nitro, by Brendan Gregg (eight stages from emulation to bare metal, with a diagram; about 1,900 words) | https://www.brendangregg.com/blog/2017-11-29/aws-ec2-virtualization-2017.html | reading, link | Copyright Brendan Gregg; linked, not copied | 15 | `device-paths`, `hypervisor-types`, `cloud-hypervisors` | 2026-11-11 |
| 1 | What is a hypervisor? (Red Hat; about 950 words) | https://www.redhat.com/en/topics/virtualization/what-is-a-hypervisor | reading, link | Copyright Red Hat; linked, not copied | 4 | `hypervisor-types` | 2026-11-11 |
| 2 | Hyper-V architecture (Microsoft Learn; 999 words) | https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/architecture | reading, link | CC BY 4.0 | 5 | `hypervisor-types`, `device-paths` | 2026-11-10 |
| 3 | The components of the Nitro System, from "The Security Design of the AWS Nitro System" (AWS whitepaper) | https://docs.aws.amazon.com/whitepapers/latest/security-design-of-aws-nitro-system/the-components-of-the-nitro-system.html | reading, link | Copyright Amazon Web Services; linked, not copied | 12 | `cloud-hypervisors`, `device-paths` | 2026-11-10 |
| 4 | The EC2 approach to preventing side-channels, from the same whitepaper | https://docs.aws.amazon.com/whitepapers/latest/security-design-of-aws-nitro-system/the-ec2-approach-to-preventing-side-channels.html | reading, link | Copyright Amazon Web Services; linked, not copied | 10 | `isolation-limits` | 2026-11-11 |
| 5 | How Accelerated Networking works in Linux and FreeBSD VMs (Microsoft Learn; 2,728 words, read as far as "Azure host servicing") | https://learn.microsoft.com/en-us/azure/virtual-network/accelerated-networking-how-it-works | reading, link | CC BY 4.0 | 8 | `device-paths`, `cloud-hypervisors` | 2026-11-10 |
| 6 | Live migration process during maintenance events (Google Cloud) | https://docs.cloud.google.com/compute/docs/instances/live-migration-process | reading, link | CC BY 4.0 | 6 | `cloud-hypervisors` | 2026-11-11 |
| 7 | Isolation for VMs in Azure (Microsoft Learn; 649 words) | https://learn.microsoft.com/en-us/azure/virtual-machines/isolation | reading, link | CC BY 4.0 | 3 | `isolation-limits` | 2026-11-11 |
| 8 | `systemd-detect-virt(1)` | https://www.freedesktop.org/software/systemd/man/latest/systemd-detect-virt.html | reading, link | LGPL-2.1-or-later (systemd documentation) | 3 | `read-the-guest` | 2026-11-10 |
| 9 | Introduction, from the QEMU documentation (accelerators and device models) | https://www.qemu.org/docs/master/system/introduction.html | reading, link | GPL-2.0 (QEMU documentation) | 4 | `hypervisor-types` | 2026-11-10 |
| 10 (optional) | AWS re:Invent 2023: Deep dive into the AWS Nitro System (CMP306), on the AWS Events channel, 33 min 30 s | https://www.youtube.com/watch?v=Cxie0FgLogg | video, embed | Standard YouTube licence, Amazon Web Services; official embed | 34 | `cloud-hypervisors`, `device-paths` | 2026-11-11 (title, length and description; not watched) |
| 11 (optional) | AWS re:Invent 2017: C5 Instances and the Evolution of Amazon EC2 Virtualization (CMP332), 59 min 56 s | https://www.youtube.com/watch?v=LabltEXk0VQ | video, link | Standard YouTube licence, Amazon Web Services | 60 | `device-paths` | 2026-11-11 (title, length and description; not watched) |
| 12 (optional) | Overview of Azure Boost (Microsoft Learn; read the first screen) | https://learn.microsoft.com/en-us/azure/azure-boost/overview | reading, link | CC BY 4.0 | 3 | `cloud-hypervisors` | 2026-11-11 |

Core reading: 70 minutes. The QEMU documentation's licence is taken from the project's own statement and should be confirmed when the topic is written.

Considered and not used: the virtual-machine chapter of *Operating Systems: Three Easy Pieces* (not opened; it assumes an operating-systems course), and Google's Titanium page (it would not render, so nothing in this topic rests on it).

## Practice ladder

Fixture rule for every `predict_shell` item: the files are excerpts of real output, each named with where and when it was captured; the command is portable to Git Bash (no `jq`, nothing machine-dependent); the answer is short. Fixtures marked *(after capture)* wait for the runner workflow. Multiple-choice rule: four choices of similar length, the right one never the longest by more than a few words, the teaching in `explanation`.

### One image for all the topic's labs

A plain lab (no systemd). The first `RUN`, identical in all five: `ubuntu:24.04` with `qemu-system-x86 qemu-utils linux-image-virtual busybox-static cpio zstd systemd util-linux pciutils sudo nano less procps file`, and the `learner` user. `systemd` is installed for the `systemd-detect-virt` program only. `seed.sh` then:

- copies the kernel to `/opt/vm/vmlinuz` (mode 644; the package installs it readable by root only) and builds `/opt/vm/initramfs.cpio.gz` from busybox, the decompressed `e1000.ko`, and an `/init` that mounts `/proc` and `/sys`, prints a fixed **guest report** between `=== guest report` and `=== end`, and powers off. The report's lines: `cpus:`, `memory_kb:`, `hypervisor_flag:`, `dmi_vendor:`, one `nic: NAME driver=DRIVER` per interface, one `disk: NAME driver=DRIVER` per disk, `virtio_devices:`. With `lab.shell` on the kernel command line it starts a shell instead, for the worked example.
- lays down `/srv/captures/<name>/` for each capture, in the layout of `lab-capture`: `about.txt`, `detect-virt.txt`, `lscpu.txt`, `cpu-flags.txt`, `dmesg-boot.txt`, `dmi/sys_vendor` and `dmi/product_name`, `lspci.txt`, `net-drivers.txt`, `block-drivers.txt`, `buses.txt`, `vulnerabilities.txt`.
- installs `lab-capture` in `/usr/local/bin`.

### The ladder

| # | Item | Type | Skill | Design |
| --- | --- | --- | --- | --- |
| 1 | `example-whats-under-me` | worked example (lab) | `read-the-guest`, `cloud-hypervisors` | Below |
| 2 | `mcq-what-a-hypervisor-does` | mcq | `hypervisor-types` | A 96-core server is sold as 24 four-vCPU VMs. One guest's kernel runs an instruction that would switch off interrupts on a real machine. What happens? **Right:** the CPU stops at that instruction and hands it to the hypervisor, which applies it to that guest's virtual CPU only. Wrong: it runs on the real CPU and stalls every guest; the hypervisor has already rewritten the guest's kernel on disk so it never tries; every guest instruction is interpreted in software one at a time |
| 3 | `hv-detect-innermost` | predict_shell | `read-the-guest` | File: `detect-virt.txt` from `laptop-wsl2` (`any: wsl`, `vm: microsoft`, `container: wsl`). Command: `awk -F': ' '$1 == "vm" {print $2}' detect-virt.txt`. Prints `microsoft`. Explanation: the tool names the innermost layer unless asked for the VM |
| 4 | `hv-lscpu-vendor` | predict_shell | `read-the-guest` | File: seven real lines of `lscpu` from `laptop-wsl2` (`Model name`, `Thread(s) per core`, `Virtualization: VT-x`, `Hypervisor vendor: Microsoft`, `Virtualization type: full`, two others). Command: `grep -e '^Hypervisor vendor' -e '^Virtualization type' lscpu.txt \| awk -F': *' '{print $2}'`. Prints `Microsoft` then `full` |
| 5 | `mcq-type1-type2` | mcq | `hypervisor-types` | VirtualBox on a Windows laptop; Hyper-V under Azure; KVM on a Linux server. Which sentence is right? **Right:** VirtualBox is a program on an OS that owns the hardware (type 2); Hyper-V owns the hardware itself (type 1); KVM makes the Linux kernel the hypervisor and is counted with type 1. Wrong answers swap one pair each |
| 6 | `hv-guest-nic-driver` | predict_shell | `device-paths` | Files: the real guest reports `emulated.log` and `virtio.log` from the trial. Command: `grep -h '^nic:' emulated.log virtio.log \| awk '{print $3}'`. Prints `driver=e1000` then `driver=virtio_net` |
| 7 | `mcq-emulated-vs-paravirtual` | mcq | `device-paths` | The same guest, restarted with its NIC changed from `e1000` to `virtio-net`. What changed? **Right:** the host stopped imitating a real Intel card register by register; guest and host now pass packets through queues designed for a VM, so the guest must have the virtio driver. Wrong: the guest now owns a slice of the physical card; nothing but the name, since both are software; the host now encrypts the traffic |
| 8 | `hv-kvm-refused` | predict_shell | `hypervisor-types` | Files: `accel-help.txt` (the real three lines: `Accelerators supported in QEMU binary:`, `tcg`, `kvm`) and `kvm-try.txt` (the two real error lines). Command: `tail -n +2 accel-help.txt \| tr '\n' ' '; echo; grep -c 'KVM kernel module' kvm-try.txt`. Prints `tcg kvm ` then `1`. Explanation: QEMU can use KVM only where the machine exposes it; inside a cloud VM that is nested virtualization |
| 9 | `hv-tcg-slowdown` | predict_shell | `hypervisor-types` | File: `loop-times.txt` with `host 0.89` and `guest-tcg 12.76` (seconds for one loop, measured 2026-11-11). Command: `awk '{t[$1] = $2} END {printf "%d times slower\n", t["guest-tcg"] / t["host"]}' loop-times.txt`. Prints `14 times slower` |
| 10 | `mcq-nested-virtualization` | mcq | `hypervisor-types` | A team runs Android emulators in CI on cloud VMs and gets "KVM not available". **Right:** the VM's CPU doesn't expose the virtualization extensions; pick an instance type with nested virtualization (on AWS the M7i, M8i, C8i and R8i families, or bare metal) or accept emulation. Wrong: install the `kvm` package; switch the region; raise the vCPU quota |
| 11 | `mcq-nitro-pieces` | mcq | `cloud-hypervisors` | On a current EC2 host, what runs where? **Right:** a small KVM-based hypervisor on the main board divides CPU and memory; networking, EBS and management run on separate Nitro cards. Wrong: a Linux host OS with QEMU per instance; a Windows root partition with a virtual switch; Xen with a control domain doing the I/O |
| 12 | `hv-azure-two-nics` *(after capture)* | predict_shell | `cloud-hypervisors`, `device-paths` | File: `net-drivers.txt` of the Azure runner capture (expected: `eth0 hv_netvsc` and a second interface on `mlx5_core` or `mana`). Command prints the drivers. Explanation: one synthetic NIC, one virtual function, the same MAC |
| 13 | `mcq-vf-revoked` | mcq | `device-paths`, `cloud-hypervisors` | An Azure VM's log shows `Data path switched from VF`, and 30 seconds later `Data path switched to VF`. Latency rose in between; no connection dropped. **Right:** the host was serviced, the SR-IOV function was taken away and traffic ran through the host's virtual switch on the synthetic NIC until it came back. Wrong: the VM was live-migrated to another region; the NIC driver crashed and reloaded; the VM ran out of CPU credits |
| 14 | `hv-nitro-devices` *(after capture)* | predict_shell | `cloud-hypervisors` | File: `lspci.txt` of the AWS runner capture. Command: `grep -c 'Amazon.com' lspci.txt`. Explanation names the NVMe EBS controller and ENA lines |
| 15 | `mcq-which-cloud` | mcq | `cloud-hypervisors` | A Linux guest shows `eth0` on `hv_netvsc`, a second interface on `mlx5_core` with the same MAC, and `systemd-detect-virt --vm` prints `microsoft`. **Right:** Azure, with Accelerated Networking on. Wrong: AWS Nitro with ENA; Google Cloud with gVNIC; a laptop running VirtualBox |
| 16 | `mcq-maintenance` | mcq | `cloud-hypervisors` | A service on Compute Engine stalled once for 400 ms with no reboot, and its log shows the clock stepping. **Right:** a live migration's blackout; design for a sub-second pause. Wrong: a noisy neighbour; the disk filling; steal time from a burstable type |
| 17 | `mcq-what-is-shared` | mcq | `isolation-limits` | Two customers' VMs are on one host. What can one do to the other? **Right:** slow it, through hardware they still share, such as the processor's largest cache; reading its memory is what the hypervisor prevents. Wrong: read its disk unless it is encrypted; nothing at all; kill its processes if it has more vCPUs |
| 18 | `hv-vulnerabilities` | predict_shell | `isolation-limits` | File: eight real `Vulnerability` lines of `lscpu` from `laptop-wsl2`. Command: `grep -c 'Mitigation' vulnerabilities.txt`. Prints `4`. Explanation: a guest sees its own mitigations; cross-tenant ones are the provider's job (fact 10) |
| 19 | `mcq-dedicated` | mcq | `isolation-limits` | A regulator asks that no other customer share the hardware. What does a Dedicated Host, an isolated size or a sole-tenant node remove? **Right:** other tenants, so noisy neighbours and cross-tenant side channels; not the hypervisor, the provider's staff or the host as a single point of failure. Each wrong answer adds one thing it doesn't remove |
| 20 | `mcq-host-failure` | mcq | `isolation-limits` | "The hypervisor isolates our VM, so the outage can't have been the provider." **Right:** isolation is between guests; when the host fails every guest on it stops, which is why instances are spread over hosts and zones. Three plausible wrong readings |
| 21 | `fill-under-me` | fill-in (lab) | `read-the-guest`, `device-paths` | Below |
| 22 | `write-boot-vm` | write (lab) | `hypervisor-types`, `device-paths` | Below |

### `example-whats-under-me` (worked example, about 25 minutes)

- **The container holds** the shared image.
- **The learner types** seven labelled lines: (1) `systemd-detect-virt`, then with `--vm`: the innermost layer, then the machine under it; (2) `lscpu | grep -E 'Hypervisor|Virtualization'`; (3) `grep -m1 -o -w hypervisor /proc/cpuinfo`; (4) `ls /sys/bus/vmbus/devices /sys/bus/virtio/devices 2>/dev/null | head` : which paravirtual buses this kernel sees; (5) the same questions asked of a recording: `cat /srv/captures/runner-x64-a/detect-virt.txt` and `grep -i -E 'hypervisor detected|DMI:' /srv/captures/runner-x64-a/dmesg-boot.txt`; (6) its devices: `cat /srv/captures/runner-x64-a/net-drivers.txt /srv/captures/runner-x64-a/block-drivers.txt`; (7) save `~/example/under-me.txt`: line 1 this machine's `--vm` answer, line 2 the recording's; (8) a first look at a VM from the outside in: `/opt/vm/boot-default | tee ~/example/boot.log`, a ready-made launcher that prints the QEMU command it runs, boots the guest with QEMU's default hardware and lets it report on itself (1 CPU, an `e1000` card, DMI vendor `QEMU`). The write exercise is then not the learner's first sight of a VM.
- **Checks.** `this-machine`: line 1 equals `$(systemd-detect-virt --vm || true)`, computed in the check (so `none` on bare metal is right). `the-recording`: line 2 equals the `vm:` value in the capture. `guest-reported`: `~/example/boot.log` holds a guest report whose NIC line says `driver=e1000`.
- **Wrong fixes.** `no-vm-flag.sh` writes the answer without `--vm` (`docker` or `wsl`); `both-the-same.sh` writes this machine's answer twice. Seed at least one capture whose VM answer differs from any plausible CI host, or the second passes on a lucky runner: use `qemu-virtio` (`qemu`) for line 2 if both runner captures turn out to be `microsoft`.

### `fill-under-me` (fill-in, about 20 minutes)

- **The container holds** `~/bin/under-me`, which takes a capture folder and prints four lines, with `...` in four places:

  ```text
  hypervisor: Microsoft          (lscpu's "Hypervisor vendor", or "none")
  vm: microsoft                  (the vm: line of detect-virt.txt)
  nics: hv_netvsc mlx5_core      (the drivers in net-drivers.txt, sorted, on one line)
  disks: sd                      (the same for block-drivers.txt, without repeats)
  ```

- **The learner** fills the gaps with `nano` and tries it on three captures, then captures the lab machine itself (`sudo lab-capture ~/captures/here`) and runs the script on that.
- **Checks**, each comparing the script's line with the same question answered directly in the check: `no-gaps`; `hypervisor-line`, `vm-line`, `nics-line`, `disks-line` on `runner-x64-a`; `works-on-another` on `qemu-emulated`, which the prompt doesn't name; `works-live` on a capture the check makes itself with `lab-capture` in a temporary folder.
- **Wrong fixes.** `any-not-vm.sh` reads the `any:` line; `model-name.sh` prints the CPU's model name as the hypervisor; `hard-coded.sh` echoes the first capture's four lines; `unsorted-dupes.sh` prints `sd sd sd`.

### `write-boot-vm` (write, about 30 minutes)

- **The container holds** `/opt/vm` and an empty `~/vm/`.
- **The learner writes** `~/bin/boot-vm`: create `~/vm/disk.img` (64 MB, raw, with `qemu-img`) if it isn't there, then start the guest with 2 vCPUs, 512 MB, a paravirtual NIC and the disk on a paravirtual interface, using the kernel and initramfs in `/opt/vm`, the serial console on the terminal (`-nographic`), `-no-reboot`, and TCG. Run it as `~/bin/boot-vm | tee ~/vm/boot.log`. The hints give the fixed part of the command (kernel, initramfs, `-append "console=ttyS0 quiet panic=-1"`); the hardware options are the learner's.
- **Checks**, all read from the log the learner's own run left: `log-is-fresh` (`boot.log` is newer than `boot-vm`); `two-cpus` (`cpus: 2`); `memory-512` (`memory_kb` between 440,000 and 524,288; the trial gave 468,880); `nic-paravirtual` (`driver=virtio_net`); `disk-paravirtual` (a `vd` disk on `virtio_blk`); `vm-gone` (no `qemu-system-x86` left running, matched as `qemu-system-x8[6]`).
- **Wrong fixes.** `default-nic.sh` (no `model=`, so `e1000`); `ide-disk.sh`; `one-cpu.sh`; `left-running.sh` (starts the guest with `lab.shell` and never powers it off).
- **Why read a log instead of booting in the check:** a check has 30 seconds, and a boot took up to 27 here. See platform work 1 for the cleaner alternative.

## Proofs

### Build: `build-fleet-report` (about 45 minutes)

**Brief the learner gets.** "The shop is taking stock of where its servers run. `/srv/fleet-a/` holds a recording of each of six servers. Write `~/bin/fleet-report FLEET_DIR`, which prints one line per server, sorted by name: the server's name, what it runs on, and how its network card reaches the hardware:

```text
api-1 hyperv sriov
db-1 kvm paravirtual
legacy-1 qemu emulated
```

The second word is `kvm`, `hyperv`, `xen`, `qemu` (emulation, no hardware help) or `none` (bare metal), taken from the recording's `vm:` line (`microsoft` is hyperv; `kvm`, `amazon` and `google` are kvm). The third is `emulated`, `paravirtual` or `sriov`, taking the fastest path the server has. Then save `~/report/slow.txt`: the names of the servers in `/srv/fleet-a` whose network card is emulated, one per line."

The lesson's table of drivers is the reference: `e1000`, `e1000e`, `8139cp`, `pcnet32` are emulated; `virtio_net`, `hv_netvsc`, `xen_netfront`, `vmxnet3`, `gve` are paravirtual; `mlx4_core`, `mlx5_core`, `mana`, `ena`, `ixgbevf`, `iavf` are a virtual function or a card-backed device.

- **The container holds** `/srv/fleet-a/<server>/` (six of the real captures under server names) and `/usr/local/share/lab/fleet-b/` (the same recordings recombined under other names, with one the first fleet lacks).
- **Checks.** `report-fleet-a`: the script's output for `/srv/fleet-a` equals the truth the check computes from the same files with its own classifier. `report-fleet-b`: the same for the second fleet, which the brief doesn't mention. `sorted`. `slow-list`: `~/report/slow.txt` equals the check's own list. `fastest-path-wins`: the server with both `hv_netvsc` and a virtual function reads `sriov`.
- **Shortcuts the checks must reject, each a `wrong/*.sh`.** Typing the six lines into a file and `cat`-ing it (fails `report-fleet-b`); classifying by cloud name instead of driver ("Azure means sriov": fails on the Azure capture without a VF); taking the first driver listed rather than the fastest path; using `systemd-detect-virt`'s `any:` line (prints `docker` for a container capture); listing every server in `slow.txt`.

### Debug: `debug-slow-guest` (about 35 minutes)

**Prompt, in full, to the house rule (purpose, symptom, count).** "The shop's test database runs in a small VM on this machine, started with `~/bin/shop-vm`. It is meant to match `~/vm/README`: 2 CPUs, 1 GiB of memory, its disk and its network card both on the fast, paravirtual path, and its data private to the `learner` account. People who use it say it is slow, and an audit found that another user on this machine could read the shop's data. Start it with `~/bin/shop-vm | tee ~/vm/boot.log`, read what the guest says about itself, and put it right. There are four faults. Don't change the guest in `/opt/vm`, and don't give the VM more than the README asks for."

- **The container holds** the launcher, its settings file `~/vm/shop-vm.conf`, and `~/vm/shop-disk.img`. The four faults, for the writer only: the launcher reads a variable the settings file doesn't set and falls back to one CPU; the settings file names an emulated NIC model; the launcher attaches the disk with an emulated interface; the disk image is mode 666. Memory is correct, as a decoy.
- **Checks**, described to the learner as end states: `log-is-fresh`; `two-cpus`; `memory-1g` (between 900,000 and 1,048,576 kB); `nic-paravirtual`; `disk-paravirtual`; `data-private` (the image is owned by `learner` with mode 600 or 640); `guest-untouched` (the checksums of `/opt/vm` match the image's); `vm-gone`.
- **Shortcuts the checks must reject.** Fixing three of four (four `wrong/*.sh`, one per fault left in). Oversizing to be safe, `-smp 8 -m 4096` (fails `two-cpus` and `memory-1g`). Editing `boot.log` by hand (fails `log-is-fresh` once the launcher is touched; add a check that the log's kernel version line matches `/opt/vm/vmlinuz`). The security-weakening ones: `chmod 644` instead of 600 (still world-readable), and `sudo chown root` then running the VM with `sudo` (fails `data-private`'s owner test).

### Explain

**Prompt.** "A colleague says: 'Our database VM in the cloud is basically a dedicated server. So last night's slowdown can't have come from the provider, and nobody else could ever see our data.' Explain, in your own words: what a hypervisor does, and how the VM's disk and network card differ from physical ones (emulated, paravirtual, SR-IOV); how you'd check from inside the Linux guest what it runs on and which path its devices use; how AWS, Azure and Google Cloud build this differently, and what each does to a running VM during host maintenance; and what a hypervisor does and doesn't isolate, with what you could buy or change to close each gap."

| Rubric id | Required | The answer says |
| --- | --- | --- |
| `role` | yes | A hypervisor shares one machine's CPUs, memory and devices among guests and steps in when a guest tries something only the machine's owner may do; hardware extensions make that fast, and without them everything is emulated |
| `device-paths` | yes | Emulated: software imitates real hardware, any guest works, slow. Paravirtual (virtio, VMBus): guest and host cooperate through a driver the guest must have. SR-IOV: the guest gets a virtual function of the physical card, near bare-metal speed, tied to that card |
| `read-guest` | yes | `systemd-detect-virt --vm` (and why without `--vm` it may name a container), `lscpu`'s hypervisor vendor, the driver behind each NIC and disk |
| `three-clouds` | yes | AWS: KVM-based Nitro hypervisor with I/O on cards (NVMe, ENA), updated live. Azure: Hyper-V; a synthetic NIC with an optional virtual function, removed for about 30 seconds during servicing. Google: KVM; virtio or gVNIC; live migration with a sub-second pause |
| `limits` | yes | Not isolated: performance (a shared cache, steal), the host failing, in principle side channels on shared hardware, the operator. A dedicated host, isolated size or sole-tenant node removes other tenants only |
| `types` | no | Type 1 owns the hardware, type 2 runs on an OS; KVM makes Linux the hypervisor |
| `nested` | no | KVM inside a cloud VM needs nested virtualization, offered on some instance types only |

The model answer is written with the topic, from the verified facts only.

## Review pool

Short, mostly judgement and reading real output. `review_pool:` gets the ten marked ●.

| Skill | Come-back questions (recall items, plus the fill-in and write labs, which also count) |
| --- | --- |
| `hypervisor-types` | `mcq-what-a-hypervisor-does` ●, `mcq-type1-type2`, `hv-kvm-refused`, `hv-tcg-slowdown` ●, `mcq-nested-virtualization` ●, `write-boot-vm` |
| `read-the-guest` | `hv-detect-innermost` ●, `hv-lscpu-vendor` ●, `fill-under-me`; add `mcq-detect-none` (a physical server in a rack prints `none` with a non-zero exit status, and `lscpu` has no hypervisor line: bare metal, nothing under the kernel) |
| `device-paths` | `hv-guest-nic-driver` ●, `mcq-emulated-vs-paravirtual`, `mcq-vf-revoked` ●, `hv-azure-two-nics` |
| `cloud-hypervisors` | `mcq-nitro-pieces`, `mcq-which-cloud` ●, `mcq-maintenance` ●, `hv-nitro-devices` |
| `isolation-limits` | `mcq-what-is-shared` ●, `hv-vulnerabilities`, `mcq-dedicated`, `mcq-host-failure` |

Every skill has at least four candidates that don't need a lab, so a missed question always has a different quick one to come back as.

## Platform work

None is required to write this topic. Three small things would make it better:

1. **A check that may run longer than 30 seconds.** `checks.yaml` gains an optional `timeout:` in seconds (default 30, capped at 300), read by `tools/labcheck.py` where it calls `exec_in`. With it, the VM labs' checks boot the learner's launcher themselves and read the guest's report, instead of trusting a log the learner's run left. Smallest version: about ten lines in the checker, one in the validator's schema, a sentence in `content/README.md`.
2. **A capture workflow and script.** `tools/lab-capture` (the draft is in the scratch folder) and a manually started workflow that runs it on `ubuntu-latest` and `ubuntu-24.04-arm` and uploads the result. This is authoring tooling, not learner-facing.
3. **The validator's warning for a longest-by-far right answer** that the audit asked for, before this module's multiple-choice items are written.

A note for the checker's documentation, not a change: a program's name is cut to 15 characters, so the VM is `qemu-system-x86` to `ps -C` and `pgrep -x`.

## Cost and time

**Cost to the learner: nothing.** No cloud account is used. **Cost to write it:** nothing for the first five captures; the Google one is inside the always-free tier; the optional Azure pair is about five cents of the monthly credit and needs the owner's yes.

**Time, from the resources' real length:**

| Part | Minutes |
| --- | --- |
| Lesson intro and recap | 12 |
| Core reading (resources 0 to 9) | 70 |
| 20 recall items at about 90 seconds | 30 |
| Worked example, fill-in, write | 75 |
| Build, debug | 80 |
| Explain | 15 |
| **Total: `estimated_minutes: 280`** | **282** |

The optional talk adds 34. On the owner's machine each lab also builds a 381 MB image once (under two minutes here).

## Not confirmed

- **How the pages were read.** Microsoft's and most of AWS's pages came back in full. The pages on brendangregg.com, redhat.com, docs.cloud.google.com, qemu.org, linux-kvm.org and freedesktop.org came back as extracts made by the fetching tool, with quotations; the quotations in this brief are as that tool returned them. Read each in full before quoting it in a lesson.
- **The two talks were not watched.** Title, length, channel, description and that embedding is allowed were read; what they cover is from the description.
- **DMI strings on AWS and Azure** (`Amazon EC2`, `Microsoft Corporation`) are what a capture is expected to show; no provider page opened states them. The Google one is documented (fact 32).
- **Azure's disk driver in a real guest** (`hv_storvsc`) is inferred from the Hyper-V architecture page and from this laptop, where the disks sit on VMBus; no Azure VM has been captured yet.
- **Google's offload hardware (Titanium)** is left out: its page would not render.
- **What `systemd-detect-virt` prints on a cloud's bare metal instance** is not known. It recognises EC2 partly by the machine's name plate, which a bare metal instance may share. No item should claim an answer until one has been captured.
- **Nothing in the practice ladder or the proofs has been built or run under `labcheck test`.** The trials prove the parts work (the tools, the VM, the capture script), not the labs.
- **Boot time on a CI runner** is unmeasured. Here it was 16 to 27 seconds with other containers busy; four labs at once on a shared runner will be slower, which is one more reason the checks read a log.
- **The QEMU documentation's licence** is recorded from the project's general licence, not from the page.

## What Checkpoint 2 can draw on

Part 2 of the checkpoint ("diagnose a slow VM: CPU steal, throttling and memory pressure") can name `csa.hw.hypervisors/isolation-limits` and `/read-the-guest` in `test_skills`. The QEMU image gives the checkpoint a real VM to be slow in.

## Open questions, each with a recommendation

Under the owner's rule: best learning and retention, free or inside the Azure credit.

1. **Recorded cloud output, or a cloud VM the learner starts?** Recorded, plus the live lab machine. A cloud VM would teach the same reading at the price of an account, a budget alert and a teardown that the track doesn't teach until Module 8. *Recommend: no cloud lab in this topic.*
2. **Is booting a VM with QEMU worth a 381 MB image and 20-second boots?** Yes. It is the only free way to make "emulated against paravirtual" something the learner caused, and it makes KVM and QEMU concrete. It works unprivileged and without KVM. *Recommend: keep it.*
3. **Who makes the AWS and Google captures?** The builder adds the runner workflow, which costs nothing and needs no account; the owner makes the Google capture once on the free tier. *Recommend: add "run `lab-capture` on a free `e2-micro`" to `docs/owner-queue.md`, and write the topic without waiting for it.*
4. **The main resource.** Gregg's post is the best short account of the device story but assumes vocabulary. *Recommend: keep it as main, with the lesson glossing five terms before it; the 2023 talk stays optional.*
5. **How much of type 1 against type 2?** Two sentences and one question, because the textbook split doesn't survive KVM. *Recommend: as in step 3 of the lesson plan.*
6. **How deep on side channels?** Judgement only: shared hardware can leak, providers avoid sharing cores, a dedicated host removes other tenants. No attack names are asked. *Recommend: as designed.*
7. **Prerequisites.** Topic ids, as listed, would let a learner start this topic before Packages, Performance triage and Hardening; keeping `csa.m1.checkpoint` holds the module order of the spec's map. *Recommend: list the topic ids and drop the checkpoint, since nothing here needs those three; say so in the devlog as an author note.*
8. **The spec's row.** It reads "tell type 1 from type 2 hypervisors; explain KVM/QEMU, Hyper-V and AWS Nitro, paravirtualization and SR-IOV; say what a hypervisor can and can't isolate". The design adds reading the guest and the three clouds' maintenance behaviour. *Recommend: add "read from inside a guest what it runs on" to the row, so the outline and the topic agree.*
9. **The laptop capture in a public repository.** It names the CPU model and kernel of the owner's machine, and nothing that identifies a person; the script masks addresses, UUIDs and serials. *Recommend: publish it as it is, labelled "a Windows 11 laptop running Docker Desktop", because a recording of the learner's own kind of machine is the most convincing one; mask the model name if the owner prefers.*
