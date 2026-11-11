# Price fixture for Module 2, read on 2026-11-10 and 2026-11-11

This is the dated set of list prices the writers of Module 2 should copy from. Every number here was read from the provider's own price source on the date shown; nothing is from memory. The same rows are in [price-fixture-2026-11.csv](price-fixture-2026-11.csv), in a shape a lab's `seed.sh` can copy into an image.

**Why a fixture.** Prices change, so a question that says "look up today's price" has no checkable answer. A question that carries its own dated table is checkable for ever. The table teaches the method; a link beside it teaches where today's number lives. See [estimate-questions.md](estimate-questions.md), "Prices in content".

## Conventions

- **On-demand list prices in US dollars per hour**, before any commitment, credit or negotiated discount. AWS calls this On-Demand, Azure pay-as-you-go, Google Cloud on-demand.
- **One region per cloud:** AWS US East (N. Virginia), `us-east-1`; Azure East US, `eastus`; Google Cloud Iowa, `us-central1`. Each is a large US region that the provider's own price page shows first or by default. Prices differ by region; a question must name the region.
- **A month is 730 hours** (365 × 24 ÷ 12). Google's price pages use 730 in their own examples, and Microsoft's Windows Server page gives $33.58 a core a month beside $0.046 an hour, which is 0.046 × 730. Every question must say "use 730 hours a month", because 720 and 744 are both defensible and give different answers.
- **"Windows" means Windows Server with the licence included in the hourly price.** "Linux" means a free distribution such as Ubuntu, so the Linux price is the price of the machine alone.

## Where each number came from

| Source | What it gave | Read on |
| --- | --- | --- |
| AWS price file behind the EC2 On-Demand pricing page, `https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20(N.%20Virginia)/Linux/index.json` (and `/Windows/`, `/Windows%20with%20SQL%20Std/`, `/Windows%20with%20SQL%20Ent/`). The file says it was published 2026-11-10T17:38:52Z. The page a learner uses: https://aws.amazon.com/ec2/pricing/on-demand/ | AWS instance prices, vCPUs, memory | 2026-11-10 |
| AWS Dedicated Hosts price file, `https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/dedicatedhost-ondemand.json`, and the page https://aws.amazon.com/ec2/dedicated-hosts/pricing/ | Host prices, sockets, physical cores, instances per host, the $0.046 Windows fee on a host | 2026-11-10 |
| https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/optimize-cpu.html | AWS licence rates per vCPU-hour | 2026-11-11 |
| Azure Retail Prices API, `https://prices.azure.com/api/retail/prices` with `armRegionName eq 'eastus'` (public, no sign-in). The page a learner uses: https://azure.microsoft.com/pricing/details/virtual-machines/windows/ | Azure VM prices, SQL Server licence meters, dedicated host prices, disk and IP prices | 2026-11-10 |
| https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/ (the series pages for Dsv5, Dsv6, Dasv5, Dpsv6, Esv5, B, NCasT4_v3, NC_A100_v4, NVadsA10_v5) and https://learn.microsoft.com/en-us/azure/virtual-machines/dedicated-host-general-purpose-skus | Azure vCPUs, memory, GPU memory, burstable baselines, host cores | 2026-11-11 |
| https://cloud.google.com/products/compute/pricing/general-purpose and `/accelerator-optimized` (the tables for Iowa) | Google Cloud machine prices, vCPUs, memory | 2026-11-11 |
| https://cloud.google.com/compute/disks-image-pricing (section "Premium images") | Google Cloud's Windows and SQL Server licence fees | 2026-11-10 |
| https://cloud.google.com/compute/sole-tenant-pricing | Sole-tenant node price and the 10% premium | 2026-11-11 |
| https://cloud.google.com/compute/docs/gpus and https://cloud.google.com/compute/docs/general-purpose-machines | GPU memory, the shared-core (burstable) E2 types | 2026-11-11 |
| https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-credits-baseline-concepts.html | AWS burstable baselines and credits | 2026-11-11 |
| https://aws.amazon.com/ec2/instance-types/g5/ and `/g6/` | AWS GPU memory for A10G and L4 | 2026-11-11 |
| https://www.microsoft.com/en-us/windows-server/pricing | Windows Server 2025 list prices | 2026-11-10 |
| https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/bade/documents/products-and-services/en-us/cloud/SQL-Server-2025-Pricing.pdf (dated 2025-11-03 inside the file) | SQL Server 2025 list prices | 2026-11-10 |

## The comparable set

Four vCPUs and 16 GiB of memory, the size most questions should use.

| What | AWS (N. Virginia) | Azure (East US) | Google Cloud (Iowa) |
| --- | --- | --- | --- |
| General purpose, x86, Linux | `m7i.xlarge` $0.2016 | `D4s_v5` $0.192 | `n4-standard-4` $0.1814 |
| The same with Windows Server included | $0.3856 | $0.376 | $0.3654 (the machine plus 4 × $0.046) |
| What Windows adds, per vCPU-hour | $0.046 | $0.046 | $0.046 |
| General purpose, Arm, Linux | `m7g.xlarge` $0.1632 (Graviton3); `m8g.xlarge` $0.17952 (Graviton4) | `D4ps_v6` $0.140 (Cobalt 100); `D4ps_v5` $0.154 (Ampere Altra) | `c4a-standard-4` $0.1796 (Axion); `t2a-standard-4` $0.154 (Ampere Altra) |
| Arm with Windows Server | no price listed | no price listed | not checked |
| One GPU, Linux | `g4dn.xlarge` $0.526 (T4, 16 GB); `g6.xlarge` $0.8048 (L4, 24 GB); `g5.xlarge` $1.006 (A10G, 24 GB) | `NC4as_T4_v3` $0.526 (T4, 16 GB, 28 GiB RAM); `NC24ads_A100_v4` $3.673 (A100, 80 GB, 24 vCPUs) | `g2-standard-4` $0.706832 (L4, 24 GB); `a2-highgpu-1g` $3.673385 (A100, 40 GB, 12 vCPUs) |
| Burstable, 2 vCPUs, 4 GiB, Linux | `t3.medium` $0.0416 (baseline 20% a vCPU, 24 credits an hour) | `B2s` $0.0416 (baseline 20%, 24 credits an hour) | `e2-medium` $0.033506 (each vCPU sustained at 50%, bursts of about 120 seconds, no credits) |
| Memory optimised, 4 vCPUs, 32 GiB, Linux | `r7i.xlarge` $0.2646 | `E4s_v5` $0.252 | `n4-highmem-4` $0.23804 |

The CSV has 57 rows: these and the neighbouring sizes (2, 8, 16 and 32 vCPUs), so a right-sizing question has wrong sizes to choose.

## Licence rates

All per vCPU, per hour, on top of the Linux price of the machine.

| Licence | AWS | Azure | Google Cloud |
| --- | --- | --- | --- |
| Windows Server | $0.046 | $0.046 (Windows price minus Linux price, D and E series) | $0.046 |
| SQL Server Standard | $0.120 ($0.166 with Windows) | $0.100 | $0.120 |
| SQL Server Enterprise | $0.375 ($0.421 with Windows) | $0.375 | $0.399 |
| SQL Server Web | $0.017 ($0.063 with Windows) | $0.008 | $0.011 |
| The floor for SQL Server | 4 vCPUs | 4 vCPUs (the meter is named "1-4 vCPU VM": $0.40 Standard, $1.50 Enterprise) | 4 vCPUs ("Instances with fewer than 4 vCPUs will be charged for 4 vCPUs") |

The floor shows in real prices, which makes a good question: on AWS, `m7i.large` (2 vCPUs) costs $0.1928 with Windows and $0.6728 with Windows and SQL Server Standard, and `m7i.xlarge` (4 vCPUs) costs $0.3856 and $0.8656. SQL Server adds $0.48 an hour to both.

**The $0.046 rule has exceptions, which is itself worth a question.** Small burstable sizes pay less for Windows: Azure `B2s` $0.0496 against $0.0416 (a difference of $0.008 for the whole VM, not $0.092); AWS `t3.medium` $0.0600 against $0.0416 ($0.0184); Google Cloud charges `f1-micro` and `g1-small` a flat $0.023 an hour.

**SQL Server licence included on AWS, whole instances** (Windows and SQL Server together): `m7i.large` Standard $0.6728; `m7i.xlarge` Standard $0.8656, Enterprise $1.8856; `m7i.2xlarge` Standard $1.7312, Enterprise $3.7712; `r7i.xlarge` Standard $0.9286, Enterprise $1.9486; `r7i.2xlarge` Standard $1.8572, Enterprise $3.8972.

## Dedicated hosts and sole-tenant nodes

| Host | Physical cores | Capacity | Price per hour | The same capacity as shared VMs | Host ÷ shared |
| --- | --- | --- | --- | --- | --- |
| AWS M7i Dedicated Host | 96 (2 sockets) | 48 × `m7i.xlarge` | $10.644 | 48 × $0.2016 = $9.6768 | 1.100 |
| AWS M6i Dedicated Host | 64 (2 sockets) | 32 × `m6i.xlarge` | $6.758 | 32 × $0.192 = $6.144 | 1.100 |
| Azure Dasv5-Type1 | 64 | 112 vCPUs, 768 GiB: 28 × `D4as_v5` | $5.298 | 28 × $0.172 = $4.816 | 1.100 |
| Azure Dsv6-Type1 | 96 | 192 vCPUs, 1,024 GiB: 48 × `D4s_v6` | $10.645 | 48 × $0.202 = $9.696 | 1.098 |
| Google Cloud `n2-node-80-640` | not read | 80 vCPUs, 640 GB | $5.764616 | the price already includes "a sole-tenancy premium, which is 10% of the cost of all of the underlying vCPU and memory resources" | 1.100 |

On AWS, a Windows Server image supplied by Amazon costs $0.046 per vCPU-hour on a Dedicated Host too, "consistent across all regions". On Azure, "users are charged per dedicated host, regardless how many VMs are deployed", and "software licensing, storage and network usage are billed separately from the host and VMs".

**An observation, not a published rule:** on all three clouds a host costs 10% more than the same capacity bought as shared VMs. Google states the 10%. For AWS and Azure it is what the four hosts above work out to; no page read says it is a rule, so a lesson should say "in the prices read on 2026-11-10" and never "always".

## Microsoft's own list prices

| Product | Price | Unit |
| --- | --- | --- |
| Windows Server 2025 Standard | $1,176 | 16 core licences |
| Windows Server 2025 Datacenter | $6,771 | 16 core licences |
| Windows Server 2025 pay-as-you-go through Azure Arc | $33.58 a month, or $0.046 an hour | per core |
| SQL Server 2025 Enterprise | $15,123 | 2-core pack |
| SQL Server 2025 Standard, per core | $3,945 | 2-core pack |
| SQL Server 2025 Standard, server | $989, plus $230 a CAL | per server, per user or device |
| SQL Server 2025 Enterprise subscription | $5,434 a year | 2-core pack |
| SQL Server 2025 Standard subscription | $1,418 a year | 2-core pack |
| SQL Server 2025 pay-as-you-go through Azure Arc | Enterprise $274 a month ($0.375 an hour); Standard $73 a month ($0.100 an hour) | the sheet doesn't print the unit; it matches Azure's per-vCPU meters, so per core |
| SQL Server Developer and Express | free | |

These are "open no-level" or suggested retail prices; the pages say real prices come from a reseller. **The price of Software Assurance is on none of the pages read.** A question that needs it must state it as part of the story ("your reseller quotes Software Assurance at $X a year"), never as a fact.

## What the fixture shows that a lesson can use

- **The bill in layers.** `m7i.xlarge` for a month: $147.17 as Linux, $281.49 with Windows, $631.89 with Windows and SQL Server Standard, $1,376.49 with Windows and SQL Server Enterprise. The machine is 52%, 23% and 11% of those last three.
- **Arm against x86, same size, list price.** AWS `m7g` against `m7i`: 19.0% less; `m8g` against `m7i`: 11.0% less. Azure `D4ps_v6` against `D4s_v6`: 30.7% less; `D4ps_v5` against `D4s_v5`: 19.8% less. Google Cloud `c4a` against `c4`: 9.1% less. The spec's "Arm saves 20–40%" is a price-for-performance claim; on list price alone this fixture shows 9% to 31%. The CPU architectures topic must say which it means.
- **Identical prices across clouds.** `t3.medium` and `B2s` are both $0.0416 with the same credit numbers. `g4dn.xlarge` and `NC4as_T4_v3` are both $0.526. `m6i.xlarge` and `D4s_v5` are both $0.192. A question that asks "which cloud is cheaper" can honestly answer "neither".

## Keeping it current

- A fixture is never edited. When prices are read again, write a new file (`price-fixture-2027-05.md` and its CSV) and leave this one, because questions already published point at it.
- A question copies the rows it needs into its own prompt, with the date and the region. It does not link to this file; this file isn't shipped to learners.
- A lab copies the CSV into its image. Its checks compute the right answer from the CSV, so a lab can move to a newer fixture by replacing the file and bumping `rev`.
- To read the prices again: `_work-licensing-checkpoint/tools/azure_prices.py`, `_work-licensing-checkpoint/tools/aws_prices.py` and `_work-licensing-checkpoint/tools/gcp_rows.py` in this folder are the small scripts used here. They are scratch tools, not part of the repository.

## Not verified

- **Google Cloud's N4A (Arm) series.** The price page lists it ($0.154 for `n4a-standard-4`) but one line of the same page calls N4A "In Preview". It is left out of the CSV.
- **The GPU in AWS `g6e`** and the size of Azure's `NC40ads_H100_v5`. Prices were read ($1.861 and $6.98) but the GPU details weren't, so both are left out of the CSV.
- **T4 memory on AWS.** The G4 page read names the T4 but its table didn't parse; 16 GB is confirmed for the same card on Azure's page.
- **Physical cores of the Google Cloud node type.**
- **Whether 730 hours is what the AWS and Azure calculators use.** Google and Microsoft's Windows Server page use it; the two calculators weren't opened.
- **Windows Server on Arm.** The fixture only shows that no Windows price exists for the Arm sizes read. Whether any cloud offers Windows Server on Arm at all is for the CPU architectures brief to confirm.
