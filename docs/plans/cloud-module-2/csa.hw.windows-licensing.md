# Writing brief: Windows licensing in the cloud (`csa.hw.windows-licensing`, topic 20)

Module 2 of the Cloud Solutions Architect track. This brief is what a writer needs to build the topic without redesigning it. Two companion files: [price-fixture-2026-11.md](price-fixture-2026-11.md) holds every price used here with its source, and [estimate-questions.md](estimate-questions.md) designs the `estimate` question type that most of the quick questions use.

Marks used below: **[E]** an `estimate` question (a typed number, checked within a tolerance), **[M]** multiple choice, **[S]** `predict_shell`. Every [E] has a fallback as [M] if the type isn't built: its choices are the answer and the listed mistakes.

## What the learner will be able to do

- **Count the licences.** For a VM, a physical server or a whole inventory, say how many Windows Server and SQL Server core licences it needs, with the minimums applied.
- **Price a Windows or SQL Server machine three ways:** with the licence included in the hourly price, with a licence the company already owns, and on a dedicated host. On each of the three clouds, say whether the second and third are even allowed.
- **Say when a dedicated host is cheaper,** with the arithmetic: how full it must be, and how the licence count changes.
- **Choose the SQL Server edition and the number of cores,** knowing that the licence is most of the bill.
- **Check before signing.** Name the page that settles a licensing question, and tell a rule that has held for years from a number that will have moved.

### The six-month core

Six months on, without the lesson open, the learner should still be able to:

1. Count core licences with the floors: 8 for a Windows VM, 16 for a Windows server, 4 for SQL Server.
2. Estimate what Windows adds to a VM from its vCPUs (about $34 a vCPU a month in 2026), and know SQL Server adds several times that.
3. Answer "can we bring our licences?" with three questions: which product, does it have Software Assurance, which cloud. And know the shape of the answer: Azure takes both products with Software Assurance; on AWS and Google Cloud, SQL Server moves and Windows Server mostly doesn't.
4. Explain that a dedicated host is a whole server at a small premium, so it only pays when it is nearly full or when licences are counted on its physical cores.
5. Reach for the Microsoft Product Terms and a dated price table, not memory.

The review pool is built for exactly these five.

## Prerequisites

| Topic | What this topic uses from it |
| --- | --- |
| `csa.hw.hypervisors` | A VM is a slice of a physical host shared with other customers; what "shared" and "dedicated" hardware mean. |
| `csa.hw.cores-memory` | vCPU against physical core, and that two vCPUs are usually one core's two threads. Counting licences "by physical core" or "by vCPU" depends on it. **Assumed:** that brief teaches these under some skill; reconcile the wording. |
| `csa.linux.shell` | `awk -F,` over a CSV: filtering rows, adding up a column (skills `sed-awk`, `count-and-sort`). The labs use them. |
| `csa.linux.scripting` | A small script with arguments, made executable (skill `quoting-vars`). The fill-in and write labs are scripts. |

Not prerequisites: `csa.hw.cpu-architectures` (one sentence here says the Arm sizes have no Windows price), `csa.hw.windows-ad` (CALs are defined here in a sentence), `csa.hw.gpus`.

### Terms this topic must define itself

None of these is taught earlier in the track. Each needs a plain sentence at first use.

- **Licence**, and **perpetual** (bought once) against **subscription** (rented by the year).
- **Core licence:** a licence for one processor core; server software is sold by the core, in packs.
- **Edition:** Windows Server Standard and Datacenter; SQL Server Enterprise, Standard, Developer and Express.
- **SQL Server:** Microsoft's database server. The track hasn't taught databases yet, so one sentence: a program that stores an application's data and answers queries about it, usually the most expensive software on the machine.
- **CAL (client access licence):** a licence per user or device that connects to a server, needed on top of the server's own licences when you own them, and not needed with a cloud's licence-included Windows.
- **Software Assurance (SA):** a yearly add-on to a licence bought through a volume agreement, which brings upgrade rights and, what matters here, the right to use the licence in more places.
- **Volume licensing** and **Enterprise Agreement:** how a company buys Microsoft licences in bulk; one sentence.
- **Product Terms:** Microsoft's published contract terms for every product, and the final word on any rule in this topic.
- **Licence included** (AWS), **pay-as-you-go** (Azure) and **on-demand licence** (Google Cloud): the cloud rents you the licence by the hour inside the VM's price.
- **Bring your own licence (BYOL).**
- **Azure Hybrid Benefit**, **License Mobility**, **Listed Provider**.
- **Tenancy:** shared (the default) against dedicated. **Dedicated host** (AWS, Azure) and **sole-tenant node** (Google Cloud).
- **OSE (operating system environment):** the Product Terms' word for one running copy of an operating system, a VM or the physical machine. The lesson says "VM" and mentions the word once so the Product Terms can be read.
- **A month is 730 hours.**

## Skills

| Skill | What it covers |
| --- | --- |
| `core-counting` | Count the core licences a VM, a server or an inventory needs. Windows Server: 8 per processor and 16 per server on hardware, 8 per VM when licensing by VM; Standard covers two VMs per fully licensed server and Datacenter any number. SQL Server: 4 per VM or processor, sold in packs of two. |
| `licence-included` | Read and work out licence-included prices: what Windows and SQL Server add per vCPU-hour on each cloud, the 4-vCPU floor for SQL Server, and how much of a bill is licence. |
| `bring-your-own` | Decide whether a licence the company owns may be used on a given cloud and tenancy: Azure Hybrid Benefit, License Mobility, the 1 October 2019 rule, and what Software Assurance changes. |
| `dedicated-hosts` | Price a dedicated host or sole-tenant node against shared VMs, find the break-even, and say when counting licences on physical cores makes the host cheaper. |
| `sql-editions` | Choose the SQL Server edition and core count that fit a workload, and cut the bill by cutting cores. |
| `look-it-up` | Find the page that settles a licensing rule or a price, and tell stable rules from facts that go stale. |

Every skill has at least five questions that can come back (the count is under "Review pool").

## Lesson plan

The lesson is `<Intro>`, the main resource, `<Recap>`, in the Module 1 voice: short paragraphs, each led by a bold term, a "Read now" paragraph that says which resource to read for what.

| # | Idea | Taught from | Where the clouds differ |
| --- | --- | --- | --- |
| 1 | **The licence can cost more than the machine.** Open with one VM's bill in four layers. | The lesson's own picture (A). | |
| 2 | **What a licence is:** perpetual and subscription, core licences, CALs, Software Assurance, the Product Terms. | Resource 4, "What qualifies you" and the FAQ on Software Assurance. | |
| 3 | **Counting Windows Server cores.** On your own hardware: every core, at least 8 a processor and 16 a server; Standard runs two VMs per fully licensed server and can be stacked; Datacenter runs any number. By VM: one licence per virtual core, at least 8 a VM, only with Software Assurance or a subscription. | Resource 7 (the edition table) and resource 8. | |
| 4 | **Licence included:** the cloud rents the licence by the vCPU-hour. Windows Server is $0.046 a vCPU-hour on all three (as read). No CALs. | The lesson, with the fixture's rows; resource 2, "License included options". | Azure shows a "Windows" price and a "Linux" price for a size. AWS does the same and also prints the rate per vCPU. Google Cloud bills the licence as a separate "premium image" line. |
| 5 | **Bringing your own to Azure: Azure Hybrid Benefit.** Needs Software Assurance or a subscription. The VM then costs the Linux price. 8 licences a VM at least. Standard licences may run on-premises and in Azure together for 180 days; Datacenter, when licensing by VM, indefinitely. | **Resource 1 (the main one)**, chapters 1:19 to 6:50; resource 4. | Azure only. |
| 6 | **Bringing your own to AWS and Google Cloud.** Two doors. License Mobility: needs Software Assurance, works on shared hardware, covers SQL Server and not Windows Server. Dedicated hardware: for products without License Mobility, and only licences bought before 1 October 2019 for versions released before then. So Windows Server 2022 and 2025 are licence-included there, always. | Resource 2, "BYOL options"; resource 3, "Bring Your Own License". Then the lesson's picture (B). | AWS: Dedicated Hosts. Google Cloud: sole-tenant nodes. Microsoft calls Alibaba, Amazon, Google and itself "Listed Providers"; the rule is Microsoft's, which is why Azure has its own, kinder, benefit. |
| 7 | **SQL Server.** Editions; core licences in packs of two; at least 4 per VM, and the floor shows in every cloud's price list. The licence is 3 to 8 times the machine, so the cheapest core is the one you don't license: size by memory, pick a memory-optimised size, check whether Standard is enough, use Developer for test and Express for small. | Resource 5 (sections named in the resources table); resource 9 for the limits. The lesson's own worked comparison. | The rates differ a little (see the fixture). AWS lets you switch off vCPUs on a licence-included instance to pay for fewer ("Optimize CPUs"). Azure Hybrid Benefit has its own exchange rates for SQL Server (one Enterprise core licence covers 4 vCPUs of a Standard VM). |
| 8 | **Dedicated hosts.** You rent the whole server and pay for it full or empty; in the prices read it costs 10% more than the same capacity as shared VMs. It pays when (a) the licences you own are only allowed there, or (b) licences are counted on the host's physical cores and you run many VMs on it. Then the break-even sum. | Resource 6, "Overview" to "Cost optimization scenarios"; resource 1, chapter 6:50; the lesson's picture (C). | Azure: Datacenter licences with Software Assurance on every physical core of a host give unlimited Windows VMs; the same for SQL Server Enterprise. AWS and Google Cloud: only the pre-October-2019 licences qualify for Windows. Google Cloud states its 10% premium; the others don't. |
| 9 | **What holds and what moves.** A two-column table: rules to remember, facts to look up, and where. Then the look-up, done once: open one price page, find one instance, compare with the lesson's dated table. | The lesson. Resource 8 as the place. | |
| 10 | **The method, as five steps:** list the servers; count cores with the floors; ask the three questions (product, Software Assurance, cloud); price each allowed option at 730 hours; compare, and write down what you assumed. | The lesson; the worked example lab follows it step for step. | |

### Three explanations the lesson must supply itself

No resource does these for a beginner, because each vendor only describes itself.

**(A) The bill in layers.** One AWS `m7i.xlarge` (4 vCPUs, 16 GiB) for a 730-hour month, prices read 2026-11-10:

| What runs on it | Per hour | Per month | The machine's share |
| --- | --- | --- | --- |
| Linux | $0.2016 | $147.17 | 100% |
| Windows Server | $0.3856 | $281.49 | 52% |
| Windows Server and SQL Server Standard | $0.8656 | $631.89 | 23% |
| Windows Server and SQL Server Enterprise | $1.8856 | $1,376.49 | 11% |

The words to go with it: the hardware didn't change between the rows. Everything after the first row is rent for software, and it is charged per vCPU, which is why this topic keeps counting cores.

**(B) "Can we bring it?" on one page.**

| | Azure | AWS | Google Cloud |
| --- | --- | --- | --- |
| Windows Server, with Software Assurance | Yes: Azure Hybrid Benefit. Pay the Linux price. 8 licences a VM at least. | Not on shared instances, whatever the Software Assurance. | The same as AWS. |
| Windows Server, bought before 1 October 2019, version 2019 or older | Without Software Assurance: no. | Only on Dedicated Hosts. | Only on sole-tenant nodes. |
| Windows Server 2022 or 2025 | With Software Assurance: yes. | Licence included only. | Licence included only. |
| SQL Server, with Software Assurance | Yes: Azure Hybrid Benefit. | Yes, on shared instances: License Mobility. 4 licences a VM at least. | Yes, on regular VMs: License Mobility. |
| SQL Server, without Software Assurance | No. | Only on Dedicated Hosts, bought before 1 October 2019, version 2017 or older. | Check the Product Terms; Google's page gives the Windows Server conditions and sends other products to Microsoft's list. |

The words: three questions decide every cell. Which product (Windows Server has no License Mobility; SQL Server does). Is Software Assurance active. Which cloud (Microsoft's rule for "Listed Providers" applies to AWS and Google Cloud; Azure has its own benefit).

**(C) Why a full host needs fewer licences.** A picture in words of one Azure host (Dasv5-Type1: 64 physical cores, 112 vCPUs, $5.298 an hour) filling up with 4-vCPU Windows VMs:

| VMs on the host | Licences if counted per VM (8 each) | Licences if the host's cores are licensed (Datacenter) |
| --- | --- | --- |
| 4 | 32 | 64 |
| 8 | 64 | 64 |
| 16 | 128 | 64 |
| 28 (full) | 224 | 64 |

And the money beside it: 28 such VMs with Windows included cost 28 × $0.356 = $9.968 an hour; with Hybrid Benefit on shared hardware 28 × $0.172 = $4.816 an hour and 224 licences; on the host $5.298 an hour and 64 licences. The host costs a tenth more in Azure fees and needs 160 fewer licences. Below 8 VMs it needs more licences and wastes most of the server. The break-even depends on what a licence costs you, which is why the answer to "is a dedicated host cheaper?" always starts with "how full will it be?"

### What holds and what moves

For idea 9, and for the writer to keep the two apart in every question.

| Teach as a rule (it is in the Product Terms today and is the structure everything else hangs on) | Teach as "look it up", with the place |
| --- | --- |
| Server software is licensed per core, with floors: Windows Server 8 a processor and 16 a server on hardware, 8 a VM by VM; SQL Server 4 a VM or processor. | Every price, including the $0.046. Each cloud's price page; a dated table in the question. |
| Standard covers two VMs per fully licensed server; Datacenter any number. | Which versions may be brought to AWS and Google Cloud, and the 1 October 2019 date. Product Terms; each cloud's licensing FAQ. |
| Software Assurance is what lets a licence move: by VM, to Azure, or through License Mobility. | The list of Listed Providers ("subject to change", Microsoft's document says). |
| SQL Server has License Mobility; Windows Server doesn't. | SQL Server's editions and their limits. They changed with SQL Server 2025: Standard went from 24 to 32 cores, and the 2025 editions page lists no Web edition and two Developer editions. |
| Licence included means paying per vCPU-hour and needing no CALs. | Azure Hybrid Benefit's exchange rates for SQL Server and its 180-day allowance. Product Terms, "Microsoft Azure". |
| A dedicated host is billed whole, full or empty. | The host premium (10% in the prices read; only Google states it). Product names: Azure Stack HCI is now Azure Local; Azure AD is now Entra ID. |

How long the left column has held was not checked today; the lesson should say "as the Product Terms stand in November 2026", not "always".

## Verified facts

Every specific claim the topic may make, where it was read, and when. Quotation marks are the source's own words.

| # | Claim | Source | Read |
| --- | --- | --- | --- |
| 1 | Windows Server on hardware: "The number of Licenses required equals the number of Physical Cores on the Licensed Server, subject to a minimum of 8 Licenses per Physical Processor and a minimum of 16 Licenses per Server." | https://www.microsoft.com/licensing/terms/productoffering/WindowsServerStandardDatacenterEssentials/EAEAS | 2026-11-10 |
| 2 | "Datacenter edition permits use of the server software in any number of OSEs on the Licensed Server." "Standard edition permits use of the server software in two OSEs on the Licensed Server." More Standard licences, the same number again, allow two more. | same | 2026-11-10 |
| 3 | Licensing by individual VM is "available for subscription licenses or licenses with active Software Assurance only"; "the number of Licenses required equals the number of Virtual Cores in the Virtual OSE, subject to a minimum of 8 Licenses per Virtual OSE." | same | 2026-11-10 |
| 4 | Windows Server's Software Assurance benefits list "License Mobility: External Connector only". Server licences have none. | same | 2026-11-10 |
| 5 | CALs: "all server software access requires CALs or CAL Equivalent Licenses", with exceptions listed. | same | 2026-11-10 |
| 6 | Windows Server 2025 list prices: Standard $1,176 and Datacenter $6,771, each "for 16 core licenses". Standard: "2 virtual machines, plus one Hyper-V host per license". Datacenter: "unlimited virtual machines". Pay-as-you-go through Azure Arc: $33.58 per core per month, or $0.046 per hour. | https://www.microsoft.com/en-us/windows-server/pricing | 2026-11-10 |
| 7 | Azure Hybrid Benefit for Windows Server needs "core licenses for Windows Server ... with active Software Assurance or qualifying subscription licenses". With it "you only need to pay for the base compute rate of the VM. The base compute rate is equal to the Linux rate". | https://learn.microsoft.com/en-us/windows-server/get-started/azure-hybrid-benefit (last updated 2025-09-03) | 2026-11-10 |
| 8 | "You need a minimum of 8 core licenses (Datacenter or Standard edition) per VM. For example, 8 core licenses are still required if you run a 4-core instance ... 12 core licenses are required for a 12-core instance." A processor licence counts as 16 core licences. | same; and Product Terms, Microsoft Azure: "The minimum number of core licenses required per VM is 8." | 2026-11-10 |
| 9 | Standard: "Licenses must be used either on-premises or in Azure, but not at the same time", except once, for up to 180 days, to migrate. Datacenter, licensing by VM: "simultaneous usage on-premises and in Azure indefinitely". | same | 2026-11-10 |
| 10 | Dedicated host: "You can use any number of Windows Server VMs on an Azure dedicated host if you allocate Windows Server Datacenter licenses with active Software Assurance or subscription for all the available physical cores". Standard has no such right. | same; Product Terms, https://www.microsoft.com/licensing/terms/productoffering/MicrosoftAzure/EAEAS | 2026-11-10 |
| 11 | "Workloads using Azure Hybrid Benefit can run only during the Software Assurance or subscription license term." "The Microsoft Product Terms for your program take precedent over this article." | https://learn.microsoft.com/en-us/windows-server/get-started/azure-hybrid-benefit | 2026-11-10 |
| 12 | Turning the benefit on or off "changes a metadata licensing flag only" and doesn't restart the VM; `az vm update ... --set licenseType=Windows_Server`. | https://learn.microsoft.com/en-us/azure/virtual-machines/windows/hybrid-use-benefit-licensing (last updated 2025-01-02) | 2026-11-10 |
| 13 | SQL Server per core, on hardware: "a minimum of four Licenses per Physical Processor". By VM: "the number of Licenses required equals the number of Virtual Cores in the Virtual OSE, subject to a minimum of four Licenses per Virtual OSE." | https://www.microsoft.com/licensing/terms/productoffering/SQLServer/EAEAS | 2026-11-10 |
| 14 | "SQL Server core SKUs are sold in packs of two-core licenses each." Licensing by VM: "Only licenses with Software Assurance or subscription licenses are eligible for this license model." "License Mobility is available with Software Assurance only." | https://www.microsoft.com/licensing/guidance/SQL | 2026-11-10 |
| 15 | SQL Server's Software Assurance benefits: "License Mobility: All editions of SQL Server". Enterprise, licensed by physical core with Software Assurance: "any number of instances of the server software in any number of OSEs on any Licensed Server." | Product Terms, SQL Server (URL in 13) | 2026-11-10 |
| 16 | SQL Server 2025 editions: Enterprise, Standard, Enterprise Developer, Standard Developer, Evaluation, Express. Standard is "limited to lesser of 4 sockets or 32 cores" (24 cores "in SQL Server 2022 and earlier") with a 256 GB buffer pool; Express to 1 socket or 4 cores, 1,410 MB and a 50 GB database. The Developer editions are "licensed for use as a development and test system, not as a production server". The page lists no Web edition. | https://learn.microsoft.com/en-us/sql/sql-server/editions-and-components-of-sql-server-2025 (dated 2025-11-19) | 2026-11-10 |
| 17 | SQL Server 2025 list prices: Enterprise $15,123 and Standard $3,945 per 2-core pack; Standard server $989 with CALs at $230; Developer and Express free; subscriptions $5,434 and $1,418 a year per 2-core pack. | the pricing PDF (URL in the fixture; dated 2025-11-03) | 2026-11-10 |
| 18 | Azure Hybrid Benefit for SQL Server on VMs: an Enterprise core licence covers 1 vCPU of an Enterprise VM or 4 vCPUs of a Standard VM; a Standard core licence covers 1 vCPU of a Standard VM; "subject to a minimum of four Core Licenses per Virtual Machine". 180 days to migrate. On a dedicated host: "allocate enough SQL Server Enterprise core licenses to cover all Physical Cores ... and run unlimited Virtual Machines on that host." | Product Terms, Microsoft Azure (URL in 10) | 2026-11-10 |
| 19 | Listed Providers: "Beginning October 1, 2019, on-premises licenses purchased without Software Assurance and mobility rights cannot be deployed with dedicated hosted cloud services offered by Listed Providers." They are "Alibaba, Amazon, Google, Microsoft"; "this list is subject to change". | https://www.microsoft.com/licensing/docs/view/Listed-Providers and the October 2019 document it links | 2026-11-11 |
| 20 | The Flexible Virtualization Benefit (October 2022) lets licences with Software Assurance or a subscription run at an "Authorized Outsourcer", which is "any Outsourcer that is not a Listed Provider". So it doesn't reach AWS or Google Cloud. | https://www.microsoft.com/licensing/guidance/Flexible-Virtualization-Benefit ; AWS says the same of itself (source in 21) | 2026-11-10 |
| 21 | AWS: products with License Mobility and active Software Assurance "can be brought to AWS on shared or dedicated tenant environments"; SQL Server is "licensed per vCPU on shared-tenancy (default) EC2 instances, with a minimum ... of four vCPUs per EC2 instance". Windows Server and others "don't have License Mobility rights ... even if the licenses have SA", so they need dedicated infrastructure, perpetual licences bought before 1 October 2019 (or within an Enterprise Agreement term that began before it), and a version "publicly available prior to October 1, 2019". | https://docs.aws.amazon.com/prescriptive-guidance/latest/migration-microsoft-workloads-aws/licensing-microsoft-workloads.html | 2026-11-11 |
| 22 | AWS: "Windows Server 2022 is not eligible for BYOL"; "Windows Server 2025 is not eligible for BYOL". SQL Server without Software Assurance on Dedicated Hosts: "The version deployed must be version 2017 or earlier". | https://aws.amazon.com/windows/faq/ | 2026-11-10 |
| 23 | AWS licence included: Windows Server AMIs "require no Client Access Licenses" and "include two Microsoft Remote Desktop Services licenses for administrative purposes". | https://aws.amazon.com/windows/resources/licensing/ | 2026-11-10 |
| 24 | AWS licence rates per vCPU-hour: Windows Server $0.046; with SQL Server Standard $0.166; with Enterprise $0.421; with Web $0.063. Optimize CPUs lets you "customize the number of vCPUs" on licence-included instances "while maintaining the same memory, storage, and network". | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/optimize-cpu.html | 2026-11-11 |
| 25 | AWS Dedicated Hosts "are billed on a per-host basis ... regardless of how many instances are running". An M6i host has 2 sockets and 64 physical cores and holds 32 `m6i.xlarge`. Windows Server from Amazon's images on a host: "$0.046 per hour per vCPU". | https://docs.aws.amazon.com/prescriptive-guidance/latest/optimize-costs-microsoft-workloads/byol-ded-hosts.html ; https://aws.amazon.com/ec2/dedicated-hosts/pricing/ | 2026-11-10 and 11 |
| 26 | Google Cloud: Windows Server images cost "$0.046 USD/hour per visible vCPU" ($0.023 flat on `f1-micro` and `g1-small`). SQL Server: "$0.399 USD per core/hour" Enterprise, "$0.1200" Standard, "$0.011" Web, Express no charge; "a four core minimum for each instance". | https://cloud.google.com/compute/disks-image-pricing | 2026-11-10 |
| 27 | Google Cloud: "Windows Server licenses are typically not eligible for BYOL using License Mobility"; SQL Server and SharePoint Server "are typically eligible". A Windows Server licence may come under outsourcing rights if the version was released before 1 October 2019 ("Windows Server 2022 is not eligible"), it was acquired before then (or by true-up under an earlier enrolment), and it runs on sole-tenant nodes. A licence moved to a region can't move again for 90 days. | https://cloud.google.com/compute/docs/instances/windows/ms-licensing (last updated 2026-11-10) | 2026-11-10 |
| 28 | Google Cloud sole-tenant nodes: "you are billed for all of the vCPU and memory resources on the sole-tenant nodes, plus a sole-tenancy premium, which is 10% of the cost". | https://cloud.google.com/compute/sole-tenant-pricing | 2026-11-11 |
| 29 | Azure dedicated hosts: "Users are charged per dedicated host, regardless how many VMs are deployed"; "Software licensing, storage and network usage are billed separately". Dasv5-Type1 has 64 physical cores and 112 vCPUs. | https://learn.microsoft.com/en-us/azure/virtual-machines/dedicated-hosts and `/dedicated-host-general-purpose-skus` (both last updated 2026-09-27) | 2026-11-11 |
| 30 | Azure's SQL Server licence meters are $0.10 (Standard) and $0.375 (Enterprise) per vCPU-hour, and the smallest meter is named "1-4 vCPU VM" ($0.40 and $1.50). | Azure Retail Prices API | 2026-11-10 |
| 31 | Every price in this brief. | [price-fixture-2026-11.md](price-fixture-2026-11.md) | 2026-11-10 and 11 |

**Where sources disagree.** AWS's guidance (21) names three Listed Providers, "Alibaba, Amazon, and Google Cloud". Microsoft's own document (19) names four, with Microsoft. Use Microsoft's.

## Resources

All free to read. Linked, never copied. "Minutes" is for the part the lesson assigns, at about 200 words a minute for dense text; the word counts are of the fetched page.

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 (main) | "An Overview of Azure Hybrid Benefit", John Savill's Technical Training (published 2022-11-22). Chapters: Windows Server 1:19, 8 core minimum per VM 3:58, hybrid rights 5:42, Azure Dedicated Host use 6:50, SQL Server licences 9:59. | https://www.youtube.com/watch?v=dt4LDm-ptQk | video | Standard YouTube licence (linked, not copied) | 14 (855 seconds) | `core-counting`, `bring-your-own`, `dedicated-hosts` | 2026-11-11: the watch page opened; title, length and chapters read from it. **Not watched.** |
| 2 | "Microsoft licensing on AWS", AWS Prescriptive Guidance | https://docs.aws.amazon.com/prescriptive-guidance/latest/migration-microsoft-workloads-aws/licensing-microsoft-workloads.html | reading | Copyright Amazon Web Services; linked, not copied | 15 (about 3,000 words) | `licence-included`, `bring-your-own` | 2026-11-11, read |
| 3 | "Microsoft licenses", Compute Engine documentation | https://cloud.google.com/compute/docs/instances/windows/ms-licensing | reading | CC BY 4.0 (stated in the page footer) | 7 (about 1,300 words of body) | `bring-your-own`, `licence-included` | 2026-11-10, read |
| 4 | "Azure Hybrid Benefit for Windows Server", Microsoft Learn (the Azure tab and the FAQ) | https://learn.microsoft.com/en-us/windows-server/get-started/azure-hybrid-benefit | reading | CC BY 4.0 (the `MicrosoftDocs/windowsserverdocs` repository's licence) | 6 | `bring-your-own`, `core-counting`, `dedicated-hosts` | 2026-11-10, read |
| 5 | "SQL Server licensing guidance", Microsoft Licensing (the sections on the per-core model, licensing by virtual machine, License Mobility and Azure Hybrid Benefit) | https://www.microsoft.com/licensing/guidance/SQL | reading | Copyright Microsoft; linked, not copied | 10 of about 22 | `core-counting`, `sql-editions`, `bring-your-own` | 2026-11-10, read through a summary; the writer picks the exact headings |
| 6 | "Bring licenses for Windows and SQL Server workloads", AWS Prescriptive Guidance ("Overview" to "Cost optimization scenarios") | https://docs.aws.amazon.com/prescriptive-guidance/latest/optimize-costs-microsoft-workloads/byol-ded-hosts.html | reading | Copyright Amazon Web Services; linked, not copied | 15 (about 3,700 words in all) | `dedicated-hosts`, `bring-your-own` | 2026-11-11, first half read |
| 7 | "Windows Server 2025 licensing and pricing" | https://www.microsoft.com/en-us/windows-server/pricing | reading | Copyright Microsoft; linked, not copied | 3 | `core-counting` | 2026-11-10, read |
| 8 | Microsoft Product Terms (the reference: Windows Server, SQL Server, and Microsoft Azure for the Hybrid Benefit) | https://www.microsoft.com/licensing/terms/ | reading | Copyright Microsoft; linked, not copied | reference | `look-it-up` | 2026-11-10, three entries read |
| 9 | "Editions and supported features of SQL Server 2025", Microsoft Learn (the editions table and "Scale limits" only) | https://learn.microsoft.com/en-us/sql/sql-server/editions-and-components-of-sql-server-2025 | reading | CC BY 4.0 (the `MicrosoftDocs/sql-docs` repository's licence) | 3 | `sql-editions` | 2026-11-10, read |
| 10 | "Your Guide to Saving with Azure Hybrid Benefit", Microsoft Developer, Azure Essentials Show (published 2025-08-19) | https://www.youtube.com/watch?v=1LgV-kfnUAA | video | Standard YouTube licence (linked, not copied) | 8 (475 seconds), optional | `bring-your-own` | 2026-11-11: watch page opened. Not watched. |
| 11 | "Enterprise software licensing and optimization on AWS (MAM315)", AWS re:Invent 2025 | https://www.youtube.com/watch?v=4HSY9Cc3U1w | video | Standard YouTube licence (linked, not copied) | 57, optional | `bring-your-own`, `dedicated-hosts` | 2026-11-11: watch page opened. Not watched. |

Assigned reading and watching: 14 + 15 + 7 + 6 + 10 + 15 + 3 + 3 = **73 minutes**.

**Before the topic is written, a writer must watch resource 1.** It is the only resource found that teaches the Azure side to a beginner in a quarter of an hour, and its chapters match three skills. But it is four years old and its content was not checked against facts 7 to 10. If it states the older rule (16 licences cover two VMs of up to 8 cores), make resource 4 the main resource and resource 1 an extra, and say in the lesson which rule is current.

## Practice ladder

In order. The lab image is a plain lab (no systemd): `ubuntu:24.04` with `sudo nano less`, a `learner` user, and a `seed.sh` that writes `/srv/licensing/`. Every lab of the topic shares the first `RUN`, as the scripting labs do.

**Lab data, common to the labs.** `/srv/licensing/README.txt` gives the date of the prices, the region, the source pages and "a month is 730 hours". An estate file has one server a row and carries its own prices, so no lab needs to join two files (the track hasn't taught that):

```text
server,vcpus,os,sql,win_sa,sql_sa,linux_hourly,windows_hourly
web-1,2,windows,none,yes,no,0.096,0.188
db-2,2,windows,standard,no,no,0.096,0.188
rpt-1,16,windows,enterprise,yes,yes,0.768,1.504
cache-1,4,linux,none,no,no,0.192,0.192
```

SQL Server's rates are in the README and in each prompt: Standard $0.10 and Enterprise $0.375 per vCPU-hour, at least 4 vCPUs. One idiom is new in this topic and the worked example teaches it: a floor in `awk`, written as two rules (`$2 >= 8 {n += $2}` and `$2 < 8 {n += 8}`), which uses only what Shell essentials taught.

| # | Id | Type | Skill | What it is |
| --- | --- | --- | --- | --- |
| 1 | `example-price-one-estate` | worked example, lab | `core-counting`, `licence-included`, `bring-your-own` | Seven servers on Azure. Steps, each labelled: (1) read the inventory and the README; (2) count the Windows core licences Hybrid Benefit would need, with the 8 floor, in `awk`; (3) count SQL Server core licences with the 4 floor; (4) the month's cost with every licence included; (5) the same with the benefit where `win_sa` or `sql_sa` is `yes`; (6) the saving, written to `~/example/answer.txt` as three `name=value` lines. Checks: each line against the same sum done by the check over the data. Wrong: `no-floor.sh`, `benefit-for-everyone.sh`. |
| 2 | `count-windows-small-vm` | [E] | `core-counting` | A 4-vCPU Azure VM will use Hybrid Benefit. Core licences? **8**, exact. Mistakes: 4 (the vCPUs), 16 (the per-server floor). |
| 3 | `count-windows-three-vms` | [E] | `core-counting` | VMs of 2, 8 and 12 vCPUs. **28**, exact. Mistakes: 22 (no floor), 24 (8 each). |
| 4 | `count-windows-server` | [E] | `core-counting` | A server you own: 1 processor, 4 cores, Windows Server Standard. Core licences? **16**, exact. Mistakes: 4 (the cores), 8 (the per-processor floor only). |
| 5 | `lic-awk-floor` | [S] | `core-counting` | A 5-row CSV of VMs and vCPUs (2, 4, 8, 16, 32); the command is the two-rule floor in `awk` with `END {print n}`. Output `72`. The explanation walks the two rules. |
| 6 | `standard-or-datacenter` | [E] | `core-counting` | A 32-core server (2 × 16). Standard at $1,176 and Datacenter at $6,771 per 16 core licences. Standard covers 2 VMs per full set. From how many VMs is Datacenter cheaper? **11**, exact. Working: Datacenter 2 × 6,771 = 13,542; Standard 2,352 a set; 5 sets (10 VMs) 11,760; 6 sets (11 or 12 VMs) 14,112. Mistakes: 6 (price ratio, forgetting two VMs a set), 12 (the first VM count where both VMs of the sixth set are used), 13. |
| 7 | `count-sql-packs` | [E] | `core-counting` | SQL Server on VMs of 2, 4 and 6 vCPUs, licensed by VM. How many 2-core packs? **7**, exact. Mistakes: 6 (no floor), 14 (licences, not packs). |
| 8 | `li-windows-month` | [E] | `licence-included` | Table: AWS `m7i.xlarge` Linux $0.2016, Windows $0.3856. What does the Windows licence add in a month? **$134.32**, within 2%. Mistakes: $281.49 (the whole Windows price), $33.58 (one vCPU). |
| 9 | `li-rate-per-vcpu` | [E] | `licence-included` | Table: Azure `D8s_v5` Linux $0.384, Windows $0.752. Licence per vCPU-hour? **$0.046**, within 0.001. Mistakes: 0.368 (the whole VM), 0.094 (the Windows price over 8). |
| 10 | `mcq-sql-floor-in-prices` | [M] | `licence-included`, `core-counting` | Table: AWS `m7i.large` (2 vCPUs) $0.1928 with Windows, $0.6728 with SQL Server Standard too; `m7i.xlarge` (4 vCPUs) $0.3856 and $0.8656. SQL Server adds $0.48 to both. Why? Right: "SQL Server is charged for at least 4 vCPUs". Wrong, same length: "SQL Server is priced per instance, not per vCPU" (then the 8-vCPU size wouldn't cost $0.96); "The smaller size is discounted for Windows" (the Windows prices are in proportion); "SQL Server needs 4 vCPUs to start" (it runs; you pay for 4). |
| 11 | `li-share-of-bill` | [E] | `licence-included` | Table: `m7i.xlarge` Linux $0.2016; with Windows and SQL Server Enterprise $1.8856. What percentage of the bill is licence? **89.3**, within 2 points. Mistakes: 10.7 (the machine's share), 79.6 (leaving Windows out). |
| 12 | `li-from-memory` | [E] | `licence-included` | No table. About how much does licence-included Windows Server add in a month to a 16-vCPU VM? **$537**, within 30%. Mistakes: $33.58 (one vCPU, not 16), $17.66 (a day, not a month). The prompt says "from memory; within 30% is right". |
| 13 | `mcq-rule-of-thumb-fails` | [M] | `licence-included`, `look-it-up` | Table: Azure `B2s` Linux $0.0416, Windows $0.0496. A colleague budgets 2 × $0.046 for the Windows licence. Right: "The table shows $0.008 for the whole VM; small burstable sizes are priced apart, so read the price". Wrong: "The table must be out of date"; "Burstable sizes need no Windows licence"; "The rate is per core, and this VM has one core". |
| 14 | `mcq-byol-windows-aws` | [M] | `bring-your-own` | Windows Server 2022 Datacenter, bought 2023, Software Assurance active. The team wants it on ordinary AWS instances. Right: "Not allowed; use licence-included on AWS, or use the licences in Azure". Wrong: "Allowed, because Software Assurance is active"; "Allowed on Dedicated Hosts only" (2022 is too new for that door too); "Allowed after sending Microsoft a form" (that is License Mobility, which Windows Server lacks). |
| 15 | `mcq-byol-sql-gcp` | [M] | `bring-your-own` | SQL Server Enterprise core licences, Software Assurance active, to regular Google Cloud VMs. Right: "Allowed through License Mobility; 4 licences a VM at least". Wrong: "Needs sole-tenant nodes"; "Not allowed since October 2019"; "Allowed only for versions before 2019". |
| 16 | `mcq-benefit-needs-sa` | [M] | `bring-your-own` | 30 Azure VMs run with Hybrid Benefit; finance lets Software Assurance lapse to save money. What must happen? Right: "Turn the benefit off or renew; the VMs then cost the Windows price". Wrong: "Nothing; licences are perpetual"; "The VMs stop at the end of term"; "Buy CALs for each VM". |
| 17 | `ahb-saving-year` | [E] | `bring-your-own`, `licence-included` | Table: `D4s_v5` Linux $0.192, Windows $0.376. Ten such VMs run all year (8,760 hours) with Hybrid Benefit. What is saved? **$16,118**, within 2%. Mistakes: $1,612 (one VM), $32,938 (the whole Windows price). A second line in the explanation: it takes 80 core licences. |
| 18 | `mcq-migration-overlap` | [M] | `bring-your-own` | 40 Windows VMs move to Azure over nine months; old and new run side by side. Standard or Datacenter licences, with Software Assurance? Right: "Datacenter by VM may run in both places with no time limit; Standard has 180 days". Wrong: "Both have 180 days"; "Neither may run in two places"; "Standard has no limit; Datacenter has 180 days". |
| 19 | `dh-ten-percent` | [E] | `dedicated-hosts` | Table: an AWS M7i Dedicated Host is $10.644 an hour and holds 48 `m7i.xlarge`; one `m7i.xlarge` (Linux) is $0.2016. How many percent more does the full host cost than the 48 instances? **10.0**, within half a point. Mistakes: 110 (the ratio), 9.1 (the difference over the host's price, not the instances'). The half point is what keeps 9.1 out. |
| 20 | `dh-break-even` | [E] | `dedicated-hosts` | You own Windows licences that are allowed on that host. A licence-included `m7i.xlarge` is $0.3856. From how many Windows VMs is the host ($10.644) cheaper than licence-included instances? **28**, exact. Mistakes: 27 (rounded down), 53 (the Linux price), 48 (a full host). |
| 21 | `dh-fewer-licences` | [E] | `dedicated-hosts`, `core-counting` | An Azure Dasv5 host: 64 physical cores. 28 Windows VMs of 4 vCPUs. How many fewer core licences if the host is licensed (Datacenter) than if each VM is? **160**, exact. Mistakes: 48 (112 − 64, no floor), 224 (per VM, not the difference). |
| 22 | `mcq-half-empty-host` | [M] | `dedicated-hosts` | Which estate is a dedicated host cheaper for? Right: "40 steady SQL Server Enterprise VMs whose licences can be counted on the host's cores". Wrong: "6 Windows VMs that run in office hours"; "40 Linux VMs that must be fast"; "40 Windows VMs with licence included". |
| 23 | `sql-size-by-memory` | [E] | `sql-editions`, `licence-included` | A database needs 32 GiB and 4 vCPUs. Table: Azure `D8s_v5` (8 vCPUs, 32 GiB) Windows $0.752; `E4s_v5` (4 vCPUs, 32 GiB) Windows $0.436; SQL Server Standard $0.10 a vCPU-hour, 4 at least. What does the `E4s_v5` save in a month? **$522.68**, within 2%. Mistakes: $230.68 (the VM only), $292.00 (the licence only). |
| 24 | `mcq-sql-edition-fit` | [M] | `sql-editions` | Three databases on SQL Server 2025: a 6 GB internal tool, a test copy of the sales system, a 400 GB warehouse on 48 cores. Which editions? Right: "Express, Developer, Enterprise". Wrong: "Express, Express, Standard"; "Standard, Developer, Standard"; "Developer, Developer, Enterprise" (Developer may not run production). |
| 24b | `sql-fewer-active-vcpus` | [E] | `sql-editions`, `licence-included` | A database needs 64 GiB and little CPU. Table: AWS `r7i.2xlarge` (8 vCPUs, 64 GiB) is $0.5292 as Linux and $3.8972 with Windows and SQL Server Enterprise; the licences are $0.421 a vCPU-hour, and AWS lets you run the instance with fewer active vCPUs and pay licences only for those. What is saved in a month by running 4 active vCPUs? **$1,229.32**, within 2%. Mistakes: $1,422.48 (half the whole price, machine included), $307.33 (one vCPU). The explanation checks the table first: 0.5292 + 8 × 0.421 = 3.8972. |
| 25 | `mcq-who-settles-it` | [M] | `look-it-up` | A reseller's blog says Windows Server 2025 can be brought to AWS Dedicated Hosts. Where is that settled? Right: "Microsoft's Product Terms, then AWS's licensing FAQ". Wrong: "The AWS price list"; "The Windows Server download page"; "The reseller's quote, once signed". |
| 26 | `mcq-what-goes-stale` | [M] | `look-it-up` | Which of four statements from a two-year-old design note is most likely still true? Right: "SQL Server needs at least 4 core licences a VM". Wrong: "Windows adds $0.046 a vCPU-hour"; "SQL Server Standard uses at most 24 cores"; "The newest Windows Server we can bring is 2019". The explanation: the last three are a price, a version limit and a date-bound rule; check each. |
| 27 | `fill-licence-count` | fill-in, lab | `core-counting` | `~/bin/licence-count ESTATE` prints `windows core licences: N`, `sql core licences: N` and `sql 2-core packs: N` for an estate where every Windows VM would use Hybrid Benefit. Four `...` gaps: the two floors, the row filter for SQL Server, the division into packs. Checks run it on `estate.csv` and on `estate-b.csv` and compare each line with the check's own `awk`. Wrong: `no-floor.sh`; `floor-of-16.sh`; `sql-on-every-row.sh`; `typed-in.sh` (prints the first estate's numbers, which the second estate catches). Hints as in Module 1's fill-ins. |
| 28 | `write-monthly-cost` | write, lab | `licence-included`, `bring-your-own` | Write `~/bin/monthly-cost ESTATE`: three lines, `licence-included: 1234.56`, `with-hybrid-benefit: 987.65`, `saving: 246.91`, at 730 hours. The benefit applies to Windows only where `win_sa` is `yes` and to SQL Server only where `sql_sa` is `yes`. Checks: two estates, each line within one cent of the check's own sum; the script is executable. Wrong: `hours-720.sh`; `no-sql-floor.sh` (the 2-vCPU SQL Server row shows it); `benefit-for-everyone.sh`; `forgot-sql.sh`. |

Item ids carry no type prefix for [E] items, so an item keeps its id whether it ships as multiple choice now or becomes an estimate later. Changing its `type` is a meaningful change: bump its `rev`.

**The look-up, done once (not graded).** After item 13 the lesson asks the learner to open one price page (https://azure.microsoft.com/pricing/details/virtual-machines/windows/), find `D4s v5` in East US, and compare it with the lesson's dated table. It is a step in the lesson, not an item: today's number can't be checked.

## Proofs

### Build: `build-price-the-estate` (lab, from a blank file)

**The brief the learner gets.** Fenwick Tools is moving 14 servers. `/srv/licensing/estate.csv` lists them: eight are going to Azure and six to AWS (a `cloud` column), with each server's vCPUs, operating system, SQL Server edition, whether its Windows and SQL Server licences have Software Assurance, when the Windows licence was bought and for which version, and the hourly prices. The six AWS servers are identical Windows VMs the size of an `m7i.xlarge`. The README gives the SQL Server rates, the price of an M7i Dedicated Host and how many such VMs it holds. Write `~/report/estate.txt` with these lines, money in whole dollars a month at 730 hours:

```text
azure_windows_licences=      core licences to set aside for Hybrid Benefit
sql_licences=                SQL Server core licences brought under Software Assurance, both clouds
monthly_licence_included=    everything with the licence included
monthly_best=                every server on its cheapest allowed option, on shared hardware
host_break_even_vms=         from how many of the AWS Windows VMs a Dedicated Host would be cheaper than licence included
host_cheaper=                yes or no, for the six
```

The prompt states the purpose and the format and nothing about the rules: no floors, no "Windows can't move to AWS". Those are what is being proved.

**The data is built so each rule moves a number.** Among the Azure servers: two Windows VMs under 8 vCPUs with Software Assurance; one without; a 2-vCPU SQL Server Standard VM with Software Assurance; a 16-vCPU Enterprise one. The AWS six carry Windows Server 2019 Datacenter licences bought in 2018, with Software Assurance. On shared instances that Software Assurance buys nothing, so Windows is licence included there; on a Dedicated Host those licences may be brought, so the host's price is the whole cost and the break-even is the host's price over a licence-included instance's. For six VMs the host loses. (The README says Fenwick owns enough Datacenter core licences to cover a host's 96 physical cores, so the question is only about money.) Two of the six run SQL Server under Software Assurance, which does move (License Mobility), and one runs it without. The README gives each cloud's SQL Server rates (they differ: Standard is $0.10 on Azure and $0.12 on AWS).

**Checks,** each computing the truth from `estate.csv` inside the check:

| Check | Tests | Tolerance |
| --- | --- | --- |
| `report-complete` | The six lines are there, each with a value. | |
| `azure-windows-licences` | The count with the 8 floor, only for `win_sa=yes`. | exact |
| `sql-licences` | The count with the 4 floor, only for `sql_sa=yes`, on both clouds. | exact |
| `licence-included-total` | The sum over all 14. | 1% |
| `best-total` | Azure: benefit where there is Software Assurance. AWS: Windows always licence included; SQL Server brought where `sql_sa=yes`. | 1% |
| `break-even` | The host's price over the licence-included price, rounded up. | exact |
| `host-verdict` | `no` for six VMs. | exact |
| `data-untouched` | The checksum of `estate.csv` and the README. | |

**Shortcuts the checks must reject,** each as a `wrong/*.sh` that fails at least one check:

- `no-floors.sh`: counts vCPUs. Fails both licence counts.
- `licence-included-everywhere.sh`: the lazy answer, `monthly_best` equal to `monthly_licence_included`. Compliant, and too dear. Fails `best-total`.
- `benefit-for-everyone.sh`: the benefit on every Windows VM. Looks cheapest; not allowed without Software Assurance. Fails `best-total` and the count.
- `windows-moves-to-aws.sh`: treats Software Assurance as making Windows free on AWS. Fails `best-total`.
- `hours-744.sh`: a 31-day month. At 1%, fails both totals (744 is 1.9% more than 730).
- `break-even-on-linux-price.sh`: divides by the Linux price. Fails `break-even`.
- `host-per-slot.sh`: prices the host as six forty-eighths of its hourly price, so it "wins". Fails `host-verdict`.

The 1% tolerance is deliberate: with the table in hand this is a calculation, and 1% is tight enough that every wrong rule above shows.

### Debug: `debug-the-quote` (lab)

**The prompt, in full, is this and no more:** "Harbour Dental is moving nine servers. A colleague wrote `~/quote/make-quote`, a script that reads an inventory and prints a monthly quote, and ran it on `~/quote/inventory.csv`. The quote should be the cheapest option the licences allow, and no cheaper. Finance compared it with the cloud's own calculator and the script's total is lower. There are three faults in the script. Find and fix them, then run the checks. `inventory-b.csv` is a second customer's inventory you can try it on."

It gives the system's purpose, the symptom and the number of faults. It does not say what they are or where. Check descriptions state an end state ("The quote for the first inventory is right"), never a bug. Hints are off, as for every proof.

**What is planted** (for the writer only): the script is about 30 lines of bash and `awk`, commented in the colleague's voice with what each part is meant to do.

1. SQL Server is charged on the VM's vCPUs with no floor of 4. (`core-counting`)
2. The Windows line uses the Linux price for every Windows server, not only those with Software Assurance. (`bring-your-own`)
3. The dedicated host line charges the host's hourly price times the share of its slots in use, not the whole host. (`dedicated-hosts`)

Each makes the quote too low, which is the symptom. Each is one or two lines to fix. A comment may be wrong in the way the code is wrong; none may say so.

**Checks:**

| Check | Tests |
| --- | --- |
| `quote-a-right` | The total for `inventory.csv` is the true total, to the cent. |
| `quote-b-right` | The same for `inventory-b.csv`. |
| `quote-fresh-right` | The check writes a third inventory to `/tmp` from arithmetic on a counter, runs the script on it, compares, and removes it. A total typed into the script can't pass. |
| `sql-lines-right`, `windows-lines-right`, `host-line-right` | Each kind of line, over the three inventories, so a failure points at one skill. |
| `benefit-still-used` | A Windows server with Software Assurance is still charged the Linux price. |
| `host-still-quoted` | The host line is still there for the inventory that has a host. |

**Shortcuts the checks must reject:**

- Fixing two of the three: three files, `left-sql-floor.sh`, `left-benefit.sh`, `left-host.sh`.
- `removed-the-benefit.sh`: charges every Windows server the Windows price. The total stops being too low and becomes too high; fails `benefit-still-used` and the totals.
- `deleted-the-host.sh`: drops the host line. Fails `host-still-quoted`.
- `typed-the-total.sh`: appends an `echo` of the right total for the first inventory. Fails `quote-b-right` and `quote-fresh-right`.

### Explain

**Prompt.** "A company runs 40 Windows Server VMs and 6 SQL Server VMs in its own data centre. Half the licences have Software Assurance. One vendor says 'bring your licences to any cloud'; another says 'you'll need dedicated hosts'. In your own words: what decides the licence bill for these servers on Azure, on AWS and on Google Cloud; when the company may use the licences it owns, and where; when a dedicated host would be the cheaper choice; and what you would check, and where, before anyone signs."

**Rubric.**

| Id | Required | The point |
| --- | --- | --- |
| `per-core` | yes | Licences are counted in cores with floors (8 a Windows VM, 4 for SQL Server); licence included means paying per vCPU-hour, and SQL Server costs several times what Windows does. |
| `who-may-bring` | yes | Software Assurance is what lets a licence move. Azure takes Windows Server and SQL Server through Hybrid Benefit. On AWS and Google Cloud, SQL Server moves to shared VMs through License Mobility and Windows Server doesn't: it is licence included, or old licences on dedicated hardware. So both vendors are partly right. |
| `host-economics` | yes | A dedicated host is paid for whole, full or empty, at a small premium; it is cheaper when it is nearly full and licences are counted on its physical cores, or when the licences owned are only allowed there. |
| `fewer-cores` | yes | For SQL Server the licence is most of the bill, so fewer cores, the right edition and a memory-optimised size matter more than the VM's price. |
| `verify` | yes | Names what to check and where: the Product Terms for the rule, the cloud's licensing page, the purchase dates and Software Assurance status of the licences, and current prices with their date. |
| `allowance` | no | The 180-day overlap for Standard, or Datacenter's right to run in both places. |

The model answer is written from the lesson's three pictures. It must name the three clouds and must not state a price without "as of".

## Review pool

Short, quick, mostly a sum or a judgement, on real numbers. Review-only items have numbers that appear nowhere in practice, so a remembered answer is no help.

| Id | Type | Skill | The question and the right answer |
| --- | --- | --- | --- |
| `rev-count-fleet` | [E] | `core-counting` | Hybrid Benefit for VMs of 4, 4, 16 and 32 vCPUs. **64**, exact. Mistakes: 56, 32. |
| `rev-count-stacked` | [E] | `core-counting` | A server with 2 processors of 10 cores, Windows Server Standard, 6 VMs. Core licences? **60** (20 a set, 3 sets), exact. Mistakes: 20, 48. |
| `rev-count-packs` | [E] | `core-counting` | SQL Server VMs of 2, 2, 8 and 12 vCPUs. Packs? **14**, exact. Mistakes: 12, 28. |
| `rev-awk-floor` | [S] | `core-counting` | The two-rule floor over a different CSV, floor 4, SQL Server rows only. One number. |
| `rev-li-month` | [E] | `licence-included` | Table: `D8s_v5` Linux $0.384, Windows $0.752. The Windows licence for a month? **$268.64**, 2%. |
| `rev-li-memory` | [E] | `licence-included` | From memory: Windows on an 8-vCPU VM, a month. **$269**, 30%. |
| `rev-li-sql-floor` | [E] | `licence-included` | Google Cloud charges $0.12 a core-hour for SQL Server Standard. What does it add per hour to a 2-vCPU VM? **$0.48**, within $0.005. Mistake: $0.24. |
| `rev-li-share` | [E] | `licence-included` | Table: `r7i.xlarge` Linux $0.2646; with Windows and SQL Server Standard $0.9286. Licence share? **71.5%**, 2 points. |
| `rev-old-windows-aws` | [M] | `bring-your-own` | Windows Server 2019 Datacenter, bought 2018, no Software Assurance, to AWS. Right: "On Dedicated Hosts only". Wrong: "On any instance"; "Nowhere on AWS"; "Only after buying Software Assurance". |
| `rev-new-sql-no-sa` | [M] | `bring-your-own` | SQL Server 2022 Standard, bought 2023, no Software Assurance, to any of the three clouds. Right: "Licence included on all three; nothing lets it move". Wrong: "Hybrid Benefit on Azure only"; "License Mobility on AWS and Google Cloud"; "Dedicated hosts on AWS and Google Cloud". |
| `rev-three-questions` | [M] | `bring-your-own` | Which three facts decide whether a licence may be brought? Right: "The product, its Software Assurance, the cloud". Wrong sets swap in "the region", "the VM size", "the edition's price". |
| `rev-dh-break-even-azure` | [E] | `dedicated-hosts` | Table: Dasv5 host $5.298; `D4as_v5` with Windows $0.356. Break-even count of Windows VMs? **15**, exact. Mistakes: 14, 31. |
| `rev-dh-sql-packs` | [E] | `dedicated-hosts`, `core-counting` | An Azure Dsv6 host: 96 physical cores. 48 SQL Server Enterprise VMs of 4 vCPUs. How many fewer 2-core packs if the host's cores are licensed? **48**, exact. Mistakes: 96 (licences), 24. The explanation prices it: 48 × $15,123 = $725,904 at list. |
| `rev-dh-when` | [M] | `dedicated-hosts` | A host is 35% full. What follows? Right: "You pay for the empty 65% too; shared VMs are cheaper unless the licences force the host". Wrong: "The host is billed for what runs on it"; "It is cheaper once Windows is included"; "It can be resized to fit". |
| `rev-sql-memory` | [E] | `sql-editions` | Table: AWS `m7i.2xlarge` (8 vCPUs, 32 GiB) with Windows and SQL Server Standard $1.7312; `r7i.xlarge` (4 vCPUs, 32 GiB) $0.9286. A database needs 32 GiB and 3 vCPUs. Monthly saving on the second? **$585.90**, 2%. |
| `rev-sql-edition` | [M] | `sql-editions` | A test copy of production, 200 GB, used by five developers. Right: "Developer: free, and not for production". Wrong: "Express: free up to any size"; "Standard: the cheapest that fits"; "Enterprise: it must match production". |
| `rev-sql-small-production` | [M] | `sql-editions` | A 30 GB database for a small production app on SQL Server 2025, two cores. Right: "Express: free, and 30 GB is under its limit". Wrong: "Developer: free, and has every feature" (not for production); "Standard: Express stops at 10 GB" (50 GB in 2025; the explanation says the limit moved, so name the version); "Enterprise: production needs it". |
| `rev-precedence` | [M] | `look-it-up` | A Microsoft Learn article and the Product Terms differ on a licence count. Right: "The Product Terms; the article says so itself". Wrong: "The newer of the two"; "The article; it is written for engineers"; "Whichever the reseller confirms". |
| `rev-stale-table` | [M] | `look-it-up` | A design note prices a migration from a table dated 14 months ago. Right: "Keep the method, read today's prices, and date the new table". Wrong: "Use it; list prices don't change"; "Add 10% for inflation"; "Drop the cost section". |

Follow-up candidates per skill, counting practice and review (an item with two skills counts for both): `core-counting` 14, `licence-included` 14, `bring-your-own` 9, `dedicated-hosts` 7, `sql-editions` 6, `look-it-up` 5. `topic.yaml`'s `review_pool` lists the 19 above plus practice items 5, 10, 13 and 22.

**Rules for the multiple-choice items** (the audit found the right answer was the longest choice in 102 of 108 cloud questions): the four choices are within a few words of each other in length; the right one is the longest in at most a quarter of the items; the teaching goes in `explanation`; the right answer's position varies; no explanation names a choice by position.

## Platform work this topic needs

| Need | Smallest version | Without it |
| --- | --- | --- |
| The `estimate` question type | As designed in [estimate-questions.md](estimate-questions.md): one model, one validator check, one component. | Every [E] becomes [M] with its mistakes as the choices. The topic can still be `ready`: it has two `predict_shell` items for the review-pool rule. |
| A validator warning when a multiple-choice answer is the longest choice by half again | A few lines in `tools/validate_content.py`, as the audit suggested. | The rule above is kept by hand. |

Nothing else. The five labs are plain labs, which exist.

## Cost and time

- **Cost: nothing.** No cloud account is touched. The labs are containers on the learner's machine.
- **CI:** five plain labs, each a small image; they build in the Labs job like the scripting labs.
- **Time: about 285 minutes.** Assigned reading and watching 73; the lesson's own text 12; 25 quick questions at about a minute and a half, 40; the worked example 20; the fill-in 20; the write 30; the build 45; the debug 30; the explain 15. The outline's 240 was a placeholder; Module 1's topics claim 90 to 120 and the audit found that low.

## Open questions, each with a recommendation

1. **Is a four-year-old video the right main resource?** Recommended: yes, if a writer watches it and finds it matches facts 7 to 10; it is the best beginner's explanation found and it is short. Otherwise resource 4 becomes the main one. Either way the lesson's three pictures carry the cross-cloud part, which no resource has.
2. **Is 285 minutes too long for one topic?** Recommended: keep it one topic, as the spec has it. The practice ladder splits cleanly after item 18 (counting and bringing licences) for a learner doing it in two sittings. Cutting the dedicated-host skill would take the topic under four hours and remove half of what the spec asks for.
3. **Labs in the shell, or everything in the browser?** Recommended: labs. Pricing an inventory export with `awk` is the real job, it reuses Module 1 on purpose, and a script can be checked on an inventory the learner hasn't seen. If the owner finds starting a container gets in the way of a topic that is mostly arithmetic, the fill-in and write could become long estimate questions later.
4. **Should the build be a script or an answers file?** Recommended: an answers file. The build proves judgement (which option is allowed), and the debug already proves reading and fixing a script.
5. **Should the lesson give a price for Software Assurance?** No. Microsoft publishes none. Questions that need one state it as part of the story.
6. **Six skills, with `look-it-up` as one of them?** Recommended: yes. It is the habit most worth keeping in six months, and making it a skill is the only way it gets review questions.
7. **Which SQL Server version do questions name?** Recommended: always "SQL Server 2025" where a limit is quoted, because the limits changed with it.
