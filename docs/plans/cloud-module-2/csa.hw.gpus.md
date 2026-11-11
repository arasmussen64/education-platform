# Writing brief: `csa.hw.gpus` (topic 18), GPU basics

Design only. Nothing here is written into the repository yet. Sources were read on 2026-11-10 and 2026-11-11; each fact below carries its date.

**The fact that shapes this topic:** there is no GPU to practise on. The owner's PC has no NVIDIA GPU (`nvidia-smi` is not installed), CI has none, and no cloud's free tier includes one. So this brief settles what can honestly be taught and checked without one: reading recorded `nvidia-smi` output, memory arithmetic for a model of a given size and precision, choosing an instance from dated provider tables, and partition arithmetic. Nothing in the topic pretends to run on a GPU.

**No machine-learning knowledge is assumed.** The ML track is a separate track and its learners are other people (or the same person later). Every ML word the topic uses is on the "terms this topic must define" list below, each in a sentence.

It leans on two notes by the other Module 2 designers, in the same folder: `estimate-questions.md` (the proposed `estimate` recall type and its multiple-choice fallback) and `price-fixture-2026-11.md` and `.csv` (the dated prices).

## 1. What the learner will be able to do

1. Say in plain words why a GPU is fast at some work and useless at other work, what CUDA is, what the two kinds of arithmetic unit in an NVIDIA GPU are for (CUDA cores and Tensor Cores), and what "precision" trades.
2. Work out whether a model fits a card: parameters × bytes each, in the units `nvidia-smi` uses, plus the headroom the job needs. Say why this comes before any question of speed.
3. Read `nvidia-smi`: which card, how much of its memory is in use and by which process, and what "GPU-Util" does and does not mean.
4. From a GPU's utilisation and the host's own numbers, say what is starving it: the CPUs preparing its input, the disk, its own memory, work that is too small, or another tenant.
5. Choose a GPU instance from the three clouds' current tables for a described job: a card with enough memory, the number of cards, enough vCPUs, the price for an hour and for the job.
6. Say how one large GPU is shared: MIG's partitions and their arithmetic, time-slicing and what it does not isolate, the fractional GPUs clouds sell, and when a GPU-to-GPU link (NVLink) matters.

**The six-month core.**

- Memory first. Parameters × bytes each; it all has to fit in the card's own memory at once. Halving the precision halves the memory.
- A card's label is a name. `nvidia-smi` gives the real figure, in MiB.
- "100% utilisation" means something was running, not that the card is full. Low utilisation means the card is waiting, and the question is "for what?"
- The GPU is the last station on a line: disk, CPU, GPU. It can be starved by either station before it.
- Price the job, not the hour: a faster card can be cheaper.
- MIG builds walls (memory and faults stay inside each partition); taking turns does not.

## 2. Prerequisites and terms

**Prerequisites (topic ids).**

| Topic | What this topic uses from it |
| --- | --- |
| `csa.hw.cores-memory` | vCPU against core; reading an instance table row; local NVMe against network disks and their caps (a GPU starved by its disk is that topic's material met again); noisy neighbours and what isolation means; GiB against GB |
| `csa.hw.hypervisors` | Host and guest; a device handed straight to one VM (the hypervisors topic covers SR-IOV; if it does not use the words "pass-through", this topic defines them in a sentence) |
| `csa.linux.triage` | The USE method; `mpstat -P ALL` and one CPU at 100%; `iostat -xz` and a saturated disk; `wa` |
| `csa.linux.shell`, `csa.linux.scripting` | `grep`, `awk`, `sort`, `$(( ))`, writing a small script |

Recommended `prerequisites:` line: `[csa.hw.cores-memory]`. That topic already requires the Module 1 checkpoint and `csa.hw.hypervisors`.

**Terms this topic must define itself.** None is taught earlier in this track.

- **GPU**; **CUDA** (NVIDIA's software layer that lets ordinary programs use the GPU for arithmetic; also the name on the general arithmetic units).
- **Streaming multiprocessor (SM)**, **CUDA core**, **Tensor Core**.
- **Model, parameter, weight:** a model is a very large table of numbers; the numbers are its parameters, also called weights; running the model is multiplying inputs by that table.
- **Training and inference:** training adjusts the numbers and keeps several working copies of them; inference only uses them.
- **Batch:** many inputs pushed through together.
- **Precision; FP32, FP16 and BF16, INT8, 4-bit:** how many bytes store each number (4, 2, 2, 1, a half). Fewer bytes is less exact and smaller.
- **Mixed precision** and **quantisation**, one clause each: doing most of the arithmetic in 16 bits; storing the weights in 8 or 4.
- **VRAM, GPU memory:** the card's own memory, separate from the VM's RAM.
- **MiB and GiB** as `nvidia-smi` prints them, against the "GB" on a card's label.
- **Kernel, in NVIDIA's sense:** a program running on the GPU. It is not the Linux kernel, and the lesson must say so, because NVIDIA's definition of utilisation uses the word.
- **Input pipeline:** reading, decoding and preparing the data a GPU works on, which the CPUs do.
- **Out of memory on a GPU:** the program stops with an error; there is no swap to fall back on.
- **Pass-through, virtual GPU (vGPU), fractional GPU.**
- **MIG (Multi-Instance GPU), GPU instance, profile** (`2g.10gb`: two compute slices, 10 GB); **time-slicing**.
- **NVLink; PCIe** (the ordinary slot a card plugs into, in a clause).
- **Quota** (a per-account limit on how many GPU vCPUs you may start) and **Spot** (a cheaper price for capacity that can be taken back), a clause each; Module 8 and Module 12 teach them properly.

## 3. Skills

| Skill | What it covers |
| --- | --- |
| `gpu-vs-cpu` | Why a GPU: the same arithmetic on many numbers at once; CUDA cores against Tensor Cores; precision and what lower precision buys |
| `vram-fit` | Memory arithmetic: parameters × bytes per parameter, GB against GiB against MiB, headroom, training against inference, and whether a model fits a card |
| `read-nvidia-smi` | Read the card, memory used and total, utilisation and the process list from `nvidia-smi`; say what GPU-Util does and does not measure |
| `gpu-starvation` | From utilisation and the host's CPU and disk numbers, say what is starving a GPU (input preparation, storage, memory, work too small, sharing) and what would help |
| `gpu-instance-choice` | Choose an instance from a provider's GPU table: memory per card, number of cards, vCPUs, local disk, price for an hour and for a job; how the three clouds' families differ |
| `gpu-sharing` | MIG partition arithmetic and what it isolates; time-slicing; fractional cloud GPUs; pass-through; NVLink and when more than one GPU is needed |

Six skills, the most the rules allow. Each has at least four questions that can come back (the count is at the end of section 7).

## 4. Lesson plan

**1. What a GPU is for.** *Main resource:* NVIDIA Blog, "CPU vs GPU: What's the Difference?" (6 minutes, written for a general reader). *The lesson supplies* the picture and the limit of it:

> A CPU is a kitchen with eight very good chefs: each can cook anything, one dish at a time, quickly. A GPU is a hall with thousands of people who can each do one small sum, all doing the *same* sum on different numbers at the same moment. Give the hall a million multiplications and it is done at once. Give it a recipe with steps that depend on each other and it is no help at all.

One sentence on **CUDA**: the software that lets a program hand its arithmetic to the hall; it is NVIDIA's, which is why "a CUDA GPU" means an NVIDIA one.

**2. Inside the card: CUDA cores and Tensor Cores.** *Resource:* NVIDIA, "GPU Performance Background User's Guide", the first two sections only (stop at "Understanding Performance"). It says a GPU is a number of streaming multiprocessors, a cache and its own fast memory; that an A100 has 108 of them; and that 16-bit work can run on either Tensor Cores or CUDA cores. *The lesson supplies* the beginner's version:

> Each group of workers in the hall (a streaming multiprocessor) has two kinds of desk. The general desks (CUDA cores) do any arithmetic at full precision. The special desks (Tensor Cores) do one thing, multiplying grids of numbers, and do it several times faster when the numbers are stored in fewer bytes. A job that multiplies big grids in 16 bits uses the special desks. A physics simulation that needs every digit uses the general ones and gains nothing from the special ones.

and **precision** as bytes per number: 4 (FP32), 2 (FP16 or BF16), 1 (INT8), a half (4-bit). Fewer bytes: less exact, half the memory, and faster where Tensor Cores can be used (NVIDIA: up to 3 times overall on the most arithmetic-heavy models).

**3. Memory is the first question.** *Resources:* Hugging Face, "Optimizing LLMs for Speed and Memory" (the opening and the first paragraphs of "Lower Precision"; stop at the first block of code, which is Python); Hugging Face Accelerate, "Model memory estimator" (the tables). *The lesson supplies* the sum in words, the units, and the honest limits of the sum, because the resources assume the reader is a Python programmer:

> A model with 7 billion parameters is 7 billion numbers. At 2 bytes each that is 14 billion bytes: 14 GB, which is 13.0 GiB as `nvidia-smi` counts. All of it has to be in the card's own memory at the same time, or the model does not load; a GPU has no swap. That is why memory decides first and speed second.

> The sum gives the floor, not the bill. Hugging Face measured a 15.5-billion-parameter model at 4 bits: the sum says 7.75 GB, the card showed 9.5 GB. Inputs, working space and layers that are not shrunk all add to it. Training needs far more than running: the estimator's own table shows about four times the model's size with the usual training method. So a plan states its headroom.

> The label on a card is a name. An "A100 40GB" reports 40,537 MiB (39.6 GiB); an "H100 80GB" reports 81,559 MiB (79.6 GiB). Provider tables disagree too: AWS lists the L4 as 22 GiB and Google lists the same card as 24 GB. Read `memory.total` when you can and plan against the smaller figure when you cannot.

**4. Reading `nvidia-smi`.** *Resource:* the `nvidia-smi` manual, only the definitions of the utilisation and memory fields. *The lesson supplies* an annotated recording (ours, built to the layout in NVIDIA's own guide) with five things pointed at: the card's name, memory used and total, GPU-Util, the process list, and power. And the sentence that matters most:

> NVIDIA defines GPU-Util as the share of the last sample period in which *one or more kernels was executing*. A kernel here is a program on the GPU, not the Linux kernel. So 100% means "something was running the whole time". It is a shop being open, not a shop being full. A card can show 100% while most of it idles, and a card with its memory full can show 0% because a model is loaded and nobody is asking it anything.

**5. What is starving it.** *Resources:* TensorFlow, "Better performance with the tf.data API" (the opening and the two timeline pictures in "The naive approach" and "Prefetching"; the code is Python and can be skipped); PyTorch's "Performance Tuning Guide" (the two paragraphs under "Enable asynchronous data loading"). Both say the same thing from the makers' side: while the CPUs fetch and prepare the next input, the GPU sits idle. *The lesson supplies* the line and the table, because neither resource is written for someone deciding what machine to buy:

> A conveyor with three stations: the disk hands over raw data, the CPUs prepare it, the GPU does the arithmetic. The GPU is last. It runs only as fast as the slowest station before it.

| What you see | What is starving the GPU | What helps | What does not |
| --- | --- | --- | --- |
| GPU-Util low or sawtooth; every vCPU near 100% `usr`; `wa` near 0 | the CPUs preparing its input | more vCPUs per GPU; more preparation workers; preparing the data ahead of time | a bigger GPU |
| GPU-Util low; CPUs mostly idle; `wa` high; the data disk at its allowance in `iostat` | the disk | a local NVMe disk for the dataset; a higher disk tier | more vCPUs |
| GPU-Util near 0; no process in the list; an out-of-memory error in the application's log | nothing: the model never loaded | lower precision; a card with more memory | waiting; more vCPUs |
| GPU-Util low and steady; CPUs idle; disk idle; memory barely used | the work is too small (one input at a time) | bigger batches; a smaller, cheaper card | more of anything |
| GPU-Util near 100%; CPUs and disk with room to spare | nothing: the GPU is the limit, which is what it was bought for | a faster card or a second one, if it must go faster | more vCPUs, a faster disk |
| GPU-Util swinging; two owners in the process list | another tenant taking turns on the card | a partition of its own (MIG) or a card of its own | tuning the job |

**6. Choosing an instance.** *Resources:* Google Cloud, "About GPU instances"; the three providers' tables (AWS "Specifications for accelerated computing instances"; Azure's NCasT4_v3 and NVadsA10_v5 pages; Google's "GPU machine types"). *The lesson supplies* the order of questions (does the model fit one card with headroom; if not, how many cards; enough vCPUs to feed them; a local disk for the data; then price for the job) and one worked choice from a dated table. It also does the look-up once with the learner, ungraded: open one provider's price page, find one named instance, compare with the lesson's table.

**Where the clouds differ:**

| | AWS | Azure | Google Cloud |
| --- | --- | --- | --- |
| Families | G (one to eight mid-size cards: T4, A10G, L4, L40S); P (eight large cards: A100, H100, H200, B200) | NC (compute: T4, A100, H100); NV (graphics and shared: A10). Azure has further GPU families whose pages were not read for this brief | G2 (L4), A2 (A100), A3 (H100, H200), A4 (B200), and N1 machines with a T4 attached |
| Smallest single modern card in the fixture | `g6.xlarge`, L4, $0.8048 an hour | `NC4as_T4_v3`, T4 16 GB, $0.526; a whole A10 24 GB is `NV36ads_A10_v5` at $3.20 | `g2-standard-4`, L4, $0.706832 |
| Part of a card | `g6f.large`: an eighth of an L4, 2.79 GiB | `NV6ads_A10_v5`: a sixth of an A10, 4 GiB | fractional sizes for virtual workstations on G4 |
| How the table states card memory | GiB, and lower than the label (L4: 22 GiB) | the label (T4: 16 GB) | the label (L4: 24 GB) |
| Free tier | none for GPUs | none | "GPUs and TPUs are not included in the Free Tier"; a free-trial account cannot add GPUs at all |

The lesson notes two things that will go stale and says so: Google's page marks the T4 as approaching end of support, and the largest cards change every year (a "Rubin" row already heads Google's table). The method outlives the table.

**7. Sharing a card.** *Resources:* NVIDIA, "Multi-Instance GPU User Guide" (the Introduction and the Concepts chapter with its table of profiles); NVIDIA, "Time-Slicing GPUs in Kubernetes" (the two paragraphs "Understanding Time-Slicing GPUs" and the comparison with MIG; the word "pod" is from Module 1's memory topic); NVIDIA's NVLink page. *The lesson supplies:*

> **Walls or turns.** MIG cuts a large card into up to seven smaller ones with walls between them: each has its own memory and its own share of the arithmetic, and a crash or a memory blow-out in one stays in that one. Time-slicing has no walls: the programs take turns on the whole card, share all its memory, and one that fills the memory takes the others down with it. MIG exists only on the large data-centre cards (A30, A100, H100, H200, B200 in NVIDIA's list); a T4 or an L4 can only take turns.

> **The arithmetic.** An A100 40GB is eight slices of 5 GB of memory and seven slices of compute. A profile's name says what it takes: `2g.10gb` is two compute slices and 10 GB. A layout can never use more than eight memory slices or seven compute slices. That rule rejects bad layouts; it does not prove a good one, because profiles also have fixed positions on the card, so for a real layout the last word is NVIDIA's table.

> **More than one card.** A model too big for one card is split across several, and then the cards talk to each other constantly. NVLink is a direct card-to-card link far faster than the ordinary slot. It matters when one job spans cards; it does nothing for eight separate jobs on eight cards. (Its speed changes every generation; look it up rather than remember it.)

**Recap.** Seven bullets: the six-month core plus the clouds' families.

## 5. Verified facts

| # | Claim | Source | Read |
| --- | --- | --- | --- |
| 1 | "The CPU is composed of just a few cores with lots of cache memory that can handle a few software threads at a time. In contrast, a GPU is composed of hundreds of cores that can handle thousands of threads simultaneously"; CUDA, "First released in 2007... lets coders take advantage of the computing power of GPUs for general purpose processing" | https://blogs.nvidia.com/blog/whats-the-difference-between-a-cpu-and-a-gpu/ | 2026-11-11 |
| 2 | "NVIDIA GPUs consist of a number of Streaming Multiprocessors (SMs), on-chip L2 cache, and high-bandwidth DRAM"; an A100 has 108 SMs, a 40 MB L2 cache and 80 GB of memory; "FP16 operations can be executed in either Tensor Cores or NVIDIA CUDA cores"; "Tensor Cores were introduced in the NVIDIA Volta GPU architecture to accelerate matrix multiply and accumulate operations" | https://docs.nvidia.com/deeplearning/performance/dl-performance-gpu-background/index.html | 2026-11-11 |
| 3 | Lower precision formats "require less memory"; "math operations run much faster in reduced precision, especially on GPUs with Tensor Core support"; "up to 3x overall speedup on the most arithmetically intense model architectures"; FP16 "uses 16 bits, compared to 32 bits for single precision" | https://docs.nvidia.com/deeplearning/performance/mixed-precision-training/index.html | 2026-11-11 |
| 4 | "Tensor cores are specialized hardware designed to compute matrix-matrix multiplication operations"; with the data loader's default "the main training process has to wait for the data to be available" | https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html | 2026-11-11 |
| 5 | "Loading the weights of a model having X billion parameters requires roughly 4 * X GB of VRAM in float32 precision" and "roughly 2 * X GB of VRAM in bfloat16/float16 precision"; for inputs under 1,024 tokens "the memory requirement for inference is very much dominated by the memory requirement to load the weights"; Llama-2-70b needs 2 × 70 = 140 GB; a 15.5-billion-parameter model is 31 GB in bfloat16, "just a bit over 15 GBs" at 8 bits and 9.5 GB measured at 4 bits | https://huggingface.co/docs/transformers/llm_tutorial_optimization | 2026-11-11 |
| 6 | The estimator's table for `bert-base-cased`: float32 418.18 MB total and 1.61 GB "Training using Adam"; float16 206.59 MB and 826.36 MB; int8 103.29 MB; int4 51.65 MB. Training is about four times the model's size in each row | https://huggingface.co/docs/accelerate/usage_guides/model_size_estimator | 2026-11-11 |
| 7 | GPU utilisation: "Percent of time over the past sample period during which one or more kernels was executing on the GPU. The sample period may be between 1 second and 1/6 second depending on the product." Memory utilisation: "Percent of time over the past sample period during which global (device) memory was being read or written." `--query-gpu=` takes a comma-separated list of properties; `nvidia-smi dmon` prints one line per monitoring cycle | https://docs.nvidia.com/deploy/nvidia-smi/index.html | 2026-11-10 |
| 8 | The layout of `nvidia-smi`'s summary table (driver 580.65.06: name, `Pwr:Usage/Cap`, `Memory-Usage`, `GPU-Util`, `Compute M.`, `MIG M.`) and two real totals: an A100-SXM4-40GB shows `40537MiB`; an "NVIDIA H100 80GB HBM3" shows `81559MiB` and a 700 W cap | NVIDIA Multi-Instance GPU User Guide, Release 620, PDF created 2026-11-04: https://docs.nvidia.com/datacenter/tesla/pdf/MIG_User_Guide.pdf (converted to text and read) | 2026-11-11 |
| 9 | MIG "allows GPUs (starting with NVIDIA Ampere architecture) to be securely partitioned into up to seven separate GPU Instances"; each instance has "separate and isolated paths through the entire memory system"; it gives "a defined quality of service (QoS) with fault isolation" | same guide, chapter 2 | 2026-11-11 |
| 10 | "the A100-40GB GPU can be thought of having 8x5GB memory slices and 7 SM slices"; a memory slice is "roughly one eighth" and an SM slice "roughly one seventh" | same guide, section 6.2 | 2026-11-11 |
| 11 | A100-40GB profiles and how many of each fit: `1g.5gb` 7; `1g.10gb` 4; `2g.10gb` 3; `3g.20gb` 2; `4g.20gb` 1; `7g.40gb` 1. H100 80GB: `1g.10gb` 7; `1g.20gb` 4; `2g.20gb` 3; `3g.40gb` 2; `4g.40gb` 1; `7g.80gb` 1. A valid combination is one where "no two profiles overlap"; all supported combinations and placements are listed in the guide's chapter on supported profiles | same guide, Table 2 and Table 13 | 2026-11-11 |
| 12 | Cards that support MIG, with memory and the most instances: B200 180 GB, 7; H200 141 GB, 7; H100 80 GB and 94 GB, 7; A100 40 GB and 80 GB, 7; A30 24 GB, 4; the RTX PRO Blackwell cards. The T4, L4, A10 and L40S are not in the list | same guide, "Supported GPUs" | 2026-11-11 |
| 13 | NVIDIA's comparison: MPS shares by percentage with memory protection but no error isolation and no memory-bandwidth guarantee; MIG is a physical partition with error isolation, at most 7, and can be reconfigured only "When Idle" | same guide, Table 3 | 2026-11-11 |
| 14 | Time-slicing: "Unlike Multi-Instance GPU (MIG), there is no memory or fault-isolation between replicas"; "The GPU simply provides an equal share of time to all GPU processes" | https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/gpu-sharing.html | 2026-11-11 |
| 15 | NVLink "is a... direct GPU-to-GPU interconnect that scales multi-GPU input and output (IO) within a server". The page's figure for the current generation (3 TB/s per GPU on the Vera Rubin platform) changes with each generation; do not teach a number | https://www.nvidia.com/en-us/data-center/nvlink/ | 2026-11-11 |
| 16 | AWS rows (vCPUs, memory, cards, card memory as AWS states it): `g4dn.xlarge` 4, 16 GiB, 1 × T4, 16 GiB; `g4dn.12xlarge` 48, 192 GiB, 4 × T4, 64 GiB (4 × 16); `g5.xlarge` 4, 16 GiB, 1 × A10G, 22 GiB; `g6.xlarge` 4, 16 GiB, 1 × L4, 22 GiB; `g6e.xlarge` 4, 32 GiB, 1 × L40S, 44 GiB; `g6f.large` 2, 8 GiB, 0.125 × L4, 2.79 GiB; `p4d.24xlarge` 96, 1,152 GiB, 8 × A100, 320 GiB (8 × 40); `p5.48xlarge` 192, 2,048 GiB, 8 × H100, 640 GiB (8 × 80); `p5en.48xlarge` 8 × H200, 1,128 GiB; `p6-b200.48xlarge` 8 × B200, 1,432 GiB. Each has local NVMe instance store (`g4dn.xlarge` 1 × 125 GB; `g5.xlarge` 1 × 250 GB) | https://docs.aws.amazon.com/ec2/latest/instancetypes/ac.html | 2026-11-11 |
| 17 | **Disagreement:** the price fixture took "24 GB" for the A10G and L4 from AWS's marketing pages; AWS's specification table (fact 16) says 22 GiB. Both describe the same cards (24 × 10^9 bytes is 22.35 GiB). A question must say which figure and unit it uses | `price-fixture-2026-11.md` against fact 16 | 2026-11-11 |
| 18 | Azure: NCasT4_v3 has "up to 4 NVIDIA T4 GPUs with 16 GB of memory each"; `NC4as_T4_v3` 4 vCPUs, 28 GiB; `NC8as_T4_v3` 8, 56 GiB; `NC16as_T4_v3` 16, 110 GiB; `NC64as_T4_v3` 64, 440 GiB. NVadsA10_v5 offers "partial NVIDIA GPUs... starting at 1/6th of a GPU with 4-GiB frame buffer to a full A10 GPU with 24-GiB"; `NV6ads_A10_v5` has 6 vCPUs and 55 GiB. NC_A100_v4 has "up to 4 NVIDIA A100 PCIe GPUs with 80 GB memory each"; `NC24ads_A100_v4` 24 vCPUs, 220 GiB. NCads_H100_v5 has "up to 2 NVIDIA H100 NVL GPUs with 94GB memory each"; `NC40ads_H100_v5` 40 vCPUs, 320 GiB | `.../sizes/gpu-accelerated/ncast4v3-series`, `nvadsa10v5-series`, `nca100v4-series`, `ncadsh100v5-series` on learn.microsoft.com | 2026-11-11 |
| 19 | Google Cloud rows: `g2-standard-4` 4 vCPUs, 16 GB, 1 × L4, 24 GB; `a2-highgpu-1g` 12, 85 GB, 1 × A100, 40 GB; `a2-ultragpu-1g` 12, 170 GB, 1 × A100, 80 GB; `a3-highgpu-1g` 26, 234 GB, 1 × H100, 80 GB; `a3-highgpu-8g` 208, 1,872 GB, 8 × H100, 640 GB; `a3-ultragpu-8g` 8 × H200, 1,128 GB; `a4-highgpu-8g` 8 × B200, 1,440 GB. "NVIDIA T4 is approaching end of support" | https://docs.cloud.google.com/compute/docs/gpus | 2026-11-11 |
| 20 | Google Cloud provides GPUs "in pass-through mode, which provides your instances with direct control over GPUs and their memory"; fractional GPU sizes exist for virtual workstations on G4; GPUs can be added to Spot VMs | https://docs.cloud.google.com/compute/docs/gpus/about-gpus | 2026-11-11 |
| 21 | "GPUs and TPUs are not included in the Free Tier offer. You are always charged for GPUs"; on a free-trial account you cannot "Add GPUs to your VM instances" | https://docs.cloud.google.com/free/docs/free-cloud-features | 2026-11-10 |
| 22 | Prices per hour, Linux, on demand: `g4dn.xlarge` $0.526; `g6.xlarge` $0.8048; `g5.xlarge` $1.006 (AWS, N. Virginia). `NC4as_T4_v3` $0.526; `NC8as_T4_v3` $0.752; `NV36ads_A10_v5` $3.20; `NC24ads_A100_v4` $3.673 (Azure, East US). `g2-standard-4` $0.706832; `a2-highgpu-1g` $3.673385 (Google Cloud, Iowa) | `price-fixture-2026-11.csv`; the Azure figures were also read independently from the Azure Retail Prices API | 2026-11-10, 2026-11-11 |
| 23 | Also read from the Azure API and not in the fixture: `NV6ads_A10_v5` $0.454; `NC40ads_H100_v5` $6.98; `NC4as_T4_v3` Spot $0.164 | https://prices.azure.com/api/retail/prices | 2026-11-10 |
| 24 | In a naive input pipeline, "while your pipeline is fetching the data, your model is sitting idle"; prefetching makes the step take the larger of the two times instead of their sum | https://www.tensorflow.org/guide/data_performance | 2026-11-11 |
| 25 | Google's monitoring agent reads GPU utilisation and memory from NVIDIA's management library, per GPU and per process | https://docs.cloud.google.com/compute/docs/gpus/monitor-gpus | 2026-11-11 |

**Could not be confirmed.**

- The MIG guide's web pages below its index (for example `.../mig-user-guide/latest/supported-mig-profiles.html`) answered both tools with an endless redirect on 2026-11-11. The index page loaded and the official PDF of the same guide was read in full, so the facts stand; the writer should open the web pages in a browser before linking to a sub-page, and link the PDF or the index otherwise.
- The exact header of `nvidia-smi --query-gpu=... --format=csv` output, the MiB total a T4 or an L4 reports, and the wording of a GPU out-of-memory error from an application. None was found on a page that could be read. Until a capture run supplies them (section 10), fixtures use only the two cards whose totals are confirmed, time series are labelled as a monitoring export with our own column names, and the out-of-memory line is described in words.
- Whether new accounts start with a GPU quota of zero. Commonly said; not found on a page read.

## 6. Resources

| # | Title | URL | Type | Licence | Minutes | Skills | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 (main) | CPU vs GPU: What's the Difference? (NVIDIA Blog) | https://blogs.nvidia.com/blog/whats-the-difference-between-a-cpu-and-a-gpu/ | reading | Copyright NVIDIA; linked, not copied | 6 (1,112 words) | `gpu-vs-cpu` | 2026-11-11 |
| 1 | GPU Performance Background User's Guide (NVIDIA): the first two sections | https://docs.nvidia.com/deeplearning/performance/dl-performance-gpu-background/index.html | reading | Copyright NVIDIA; linked | 6 (of 15; 3,061 words in all) | `gpu-vs-cpu` | 2026-11-11 |
| 2 | Optimizing LLMs for Speed and Memory (Hugging Face): the opening and the start of "Lower Precision", to the first block of code | https://huggingface.co/docs/transformers/llm_tutorial_optimization | reading | Apache-2.0 (the file's header was read) | 4 (of 36) | `vram-fit` | 2026-11-11 |
| 3 | Model memory estimator (Hugging Face Accelerate): the tables | https://huggingface.co/docs/accelerate/usage_guides/model_size_estimator | reading | Apache-2.0 | 3 (932 words) | `vram-fit` | 2026-11-11 |
| 4 | NVIDIA Multi-Instance GPU User Guide: Introduction, and Concepts with its table of profiles | https://docs.nvidia.com/datacenter/tesla/pdf/MIG_User_Guide.pdf (82 pages; the web edition's index is https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/) | reading | Copyright NVIDIA; linked | 12 (about 8 pages) | `gpu-sharing`, `read-nvidia-smi` (it has real output) | 2026-11-11 |
| 5 | Time-Slicing GPUs in Kubernetes (NVIDIA GPU Operator): "Understanding Time-Slicing GPUs" and the comparison with MIG | https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/gpu-sharing.html | reading | Copyright NVIDIA; linked | 4 (of 14) | `gpu-sharing` | 2026-11-11 |
| 6 | nvidia-smi documentation: the definitions of the utilisation and memory fields | https://docs.nvidia.com/deploy/nvidia-smi/index.html | reading | Copyright NVIDIA; linked | reference, 5 (the page is 27,000 words) | `read-nvidia-smi` | 2026-11-10 |
| 7 | About GPU instances (Google Cloud) | https://docs.cloud.google.com/compute/docs/gpus/about-gpus | reading | CC BY 4.0 (the page footer was read) | 11 (2,166 words) | `gpu-instance-choice`, `gpu-sharing` | 2026-11-11 |
| 8 | GPU machine types (Google Cloud): find the G2, A2 and A3 tables | https://docs.cloud.google.com/compute/docs/gpus | reading | CC BY 4.0 | 8 (of 31) | `gpu-instance-choice` | 2026-11-11 |
| 9 | Specifications for Amazon EC2 accelerated computing instances: find five named rows in the first table | https://docs.aws.amazon.com/ec2/latest/instancetypes/ac.html | reading | Copyright AWS; linked | 5 (of 61) | `gpu-instance-choice` | 2026-11-11 |
| 10 | NCasT4_v3 size series, and NVadsA10_v5 size series (Azure) | https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/ncast4v3-series , `.../nvadsa10v5-series` | reading | CC BY 4.0 (Microsoft Learn) | 6 + 3 (the opening of the second) | `gpu-instance-choice`, `gpu-sharing` | 2026-11-11 |
| 11 | Better performance with the tf.data API (TensorFlow): the opening, "The naive approach" and "Prefetching", for the prose and the timeline pictures | https://www.tensorflow.org/guide/data_performance | reading | CC BY 4.0 (footer read); the code samples are Apache-2.0 | 5 (of 21) | `gpu-starvation` | 2026-11-11 |
| 12 | Performance Tuning Guide (PyTorch): "Enable asynchronous data loading and augmentation" | https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html | reading | BSD-3-Clause (the tutorials' licence file was read) | 2 (of 15) | `gpu-starvation` | 2026-11-11 |
| 13 | NVLink and NVLink Switch (NVIDIA) | https://www.nvidia.com/en-us/data-center/nvlink/ | reading | Copyright NVIDIA; linked | 4 (853 words) | `gpu-sharing` | 2026-11-11 |
| 14 | Monitoring GPU performance on Linux VMs (Google Cloud) | https://docs.cloud.google.com/compute/docs/gpus/monitor-gpus | reading | CC BY 4.0 | 5 | `read-nvidia-smi` | 2026-11-11 |

Reading the lesson asks for: about 65 minutes (resources 0 to 5, 7, 9 or 10, 11). The rest are "more resources".

**About the main resource.** It is the only beginner-level text by the maker, and it covers one skill of six. The topic's weight is carried by the lesson's own explanations and by the tables; that is a property of the subject (the good texts assume a programmer or an ML engineer), and the Intro should say so. The product page for Tensor Cores (https://www.nvidia.com/en-us/data-center/tensor-cores/) was read and is not used: it is about the newest product line and explains nothing a beginner can use.

**No video is listed.** None was opened and checked.

## 7. Practice ladder

Every lab is a **plain** lab (no systemd, no privileges): a small Ubuntu image with recorded evidence and a dated table. Shared first `RUN`: `ubuntu:24.04` with `sudo nano less procps` and the `learner` user.

**How recorded evidence is presented.** As files that say what they are: `nvidia-smi.txt` is "what `nvidia-smi` printed on this server", `gpu.csv` is "a monitoring export: one line a second". There is no fake `nvidia-smi` command in the image. The track's rule against simulators (ADR-0017) is about never passing a model off as the tool, and a file is honest where a stand-in command would not be.

**The predict commands were run.** Every `predict_shell` command quoted in this brief was run over its fixture in Git Bash on the owner's PC and in bash on `ubuntu:24.04` (whose `awk` is mawk), and printed the stated answer in both: `experiments/predict-check.sh` in this folder.

**Fixtures until the capture run.** The summary table follows the layout in NVIDIA's guide (fact 8) and uses only the A100-SXM4-40GB (40,537 MiB) and the H100 80GB (81,559 MiB), whose totals are confirmed. Numbers for use and utilisation are invented to tell each story. Every fixture's README says "representative, built to the documented layout".

### 7.1 `example-read-a-gpu-box` (worked example), skills `read-nvidia-smi`, `gpu-starvation`, `vram-fit`

**Holds** `/srv/gpu/box-1/`: `nvidia-smi.txt` (one A100-SXM4-40GB, `6150MiB / 40537MiB`, GPU-Util 18%, one process holding 6,140 MiB); `gpu.csv` (`second,gpu_util_pct,mem_used_mib` for 60 seconds, written by `seed.sh` as a repeating pattern of two idle seconds and one at 54%, so the mean is 18); `mpstat.txt` (4 vCPUs, each about 99% `usr`, `%iowait` 0); `iostat.txt` (the data disk quiet).

**Steps:**

1. *Which card, how much memory.* `cat nvidia-smi.txt`, then `grep -o '[0-9]*MiB / *[0-9]*MiB' nvidia-smi.txt`.
2. *In GiB and as a share.* `echo "$(( 40537 / 1024 )) GiB total, $(( 6150 * 100 / 40537 ))% used"`: 39 GiB, 15%.
3. *Who holds it.* The process table at the bottom: one program, 6,140 MiB.
4. *How busy, over a minute.* `awk -F, 'NR > 1 {s += $2; n++} END {print s / n}' gpu.csv`: 18.
5. *How often idle.* `awk -F, 'NR > 1 && $2 == 0 {n++} END {print n}' gpu.csv`: 40 of 60 seconds.
6. *What the host was doing.* `cat mpstat.txt`: every CPU flat out in `usr`, nothing waiting on disk.
7. *The verdict.* The card is idle two seconds in three while four CPUs cannot prepare its input fast enough. Save `~/example/verdict.txt`: `avg-util=18`, `idle-seconds=40`, `mem-used-pct=15`, `starved-by=cpu`.

**Checks:** each of the four lines against the check's own computation from the files (the verdict against the fixed truth). **Wrong:** `wrong/blamed-the-gpu.sh` (`starved-by=none`), `wrong/last-sample.sh` (the last line's utilisation instead of the mean).

### 7.2 Recall on why a GPU, and on memory

| Id | Kind | Skill | Scenario | Right answer | Wrong answers or mistakes |
| --- | --- | --- | --- | --- | --- |
| `mcq-what-suits-a-gpu` | mcq | `gpu-vs-cpu` | Four jobs. Which gains most from a GPU? | "Multiplying two tables of ten million numbers each, over and over" | "Parsing a log file line by line where each line depends on the last"; "Serving a thousand small web requests that each read one database row"; "Compressing one large file with a method that works through it in order" |
| `mcq-cuda-or-tensor-cores` | mcq | `gpu-vs-cpu` | NVIDIA's guide (read 2026-11-11) says 16-bit work can run on Tensor Cores or CUDA cores and that Tensor Cores speed up matrix multiplication. Two jobs share an A100: a weather simulation that must stay in 64-bit numbers, and a model that multiplies grids in 16 bits. Which units does each mostly use? | "The simulation runs on the CUDA cores; the 16-bit model's multiplying runs on the Tensor Cores" | "The simulation runs on the Tensor Cores; the 16-bit model's multiplying runs on the CUDA cores"; "Both run on the Tensor Cores, because the CUDA cores only handle drawing graphics"; "Both run on the CUDA cores, because Tensor Cores only work while a model is training" |
| `est-precision-gb` | estimate | `gpu-vs-cpu` | Hugging Face's rule (read 2026-11-11): X billion parameters take about 4 × X GB at 32 bits and 2 × X GB at 16 bits. A model has 3 billion parameters. About how many GB do its weights take at 16 bits? Exact | 6. Working: `params_billion * bytes` | 12 ("that is the 32-bit size"); 3 ("one byte each is the 8-bit size") |
| `mcq-what-lower-precision-buys` | mcq | `gpu-vs-cpu` | A team moves a model from 32-bit to 16-bit numbers. What do they get? | "About half the memory and faster multiplying on Tensor Cores, for slightly less exact numbers" | "About half the memory and slower multiplying on Tensor Cores, for slightly more exact numbers"; "About twice the memory and faster multiplying on CUDA cores, for slightly less exact numbers"; "About the same memory and faster multiplying on Tensor Cores, for exactly the same numbers" |
| `est-weights-gib` | estimate | `vram-fit` | A model has 7 billion parameters stored in 16 bits. `nvidia-smi` counts memory in MiB (1 GiB = 1,073,741,824 bytes). How many GiB do the weights take? ±0.2 | 13.0. Working: `params * bytes / 2**30` | 14.0 ("that is GB of a thousand million bytes; `nvidia-smi` will show less than the label suggests is free"); 26.1 ("4 bytes each is 32-bit") |
| `mcq-fits-which-card` | mcq | `vram-fit` | A model's weights are 24.2 GiB at 16 bits. The only cards on offer report 22 GiB each (AWS's table lists the L4 so, read 2026-11-11). The team needs it running this week on one card. What works? | "Store the weights in 8 bits, about 12 GiB, and check the answers are still good enough" | "Rent an instance with two of the cards, since 44 GiB in total is more than enough"; "Add more RAM to the VM, since the card borrows from it when its own memory runs out"; "Keep 16 bits and wait, since the card frees memory once the model has warmed up" |
| `smi-memory-free` | predict_shell | `read-nvidia-smi`, `vram-fit` | `smi.txt` is the data line of `nvidia-smi` for an H100: `\| N/A   41C    P0            268W /  700W \|   61250MiB /  81559MiB \|     97%      Default \|`. Command: `awk -F'\|' '/MiB/ {split($3, m, "/"); gsub(/[^0-9]/, "", m[1]); gsub(/[^0-9]/, "", m[2]); print "free MiB:", m[2] - m[1]}' smi.txt` | `free MiB: 20309` | About 19.8 GiB left: a 13 GiB model fits beside what is loaded, a 24 GiB one does not |
| `est-training-memory` | estimate | `vram-fit` | Hugging Face's estimator (read 2026-11-11) shows a 418 MB model needing 1.61 GB to train with the usual method: about four times its size. A team wants to train a model whose weights are 5 GiB. About how much card memory should they plan for? ±10% | 20. Working: `weights * 4` | 5 ("that is enough to run it, not to train it"); 10 ("training keeps more than one extra copy") |
| `mcq-floor-not-bill` | mcq | `vram-fit` | Hugging Face measured a 15.5-billion-parameter model stored in 4 bits (read 2026-11-11): the sum says 7.75 GB; the card showed 9.5 GB in use. What should a plan take from that? | "The sum is the least it can need, so add stated headroom before choosing a card" | "The sum is wrong for 4-bit models, so use the 16-bit figure whenever in doubt"; "The card over-reports memory in use, so trust the sum and ignore the reading"; "The sum is the most it can need, so a card that fits the sum is always enough" |

### 7.3 `fill-vram-fit` (fill-in), skill `vram-fit`

- *Script:* `~/bin/vram-fit PARAMS_BILLION BITS CARD_GIB HEADROOM_PCT` prints three lines: `weights: 13.0 GiB`, `needed: 16.3 GiB`, `fits: no`. Three gaps: bytes per parameter (`bits / 8`); GiB from bytes (`/ 1073741824`); the headroom (`* (100 + headroom) / 100`).
- *Checks:* no `...`; three cases, the third never shown to the learner: `7 16 16 25` (13.0, 16.3, no); `7 16 22 25` (yes); `70 4 40 20` (32.6, 39.1, yes: a hair under the card).
- *Wrong fixes to reject:* `wrong/decimal-gb.sh` (divides by 10^9: prints 14.0); `wrong/bits-as-bytes.sh`; `wrong/no-headroom.sh` (says `7 16 16 25` fits).
- *Hints:* "8 bits to a byte"; "a GiB is 1,024 × 1,024 × 1,024 bytes"; "25% headroom means the card must hold the weights and a quarter again".

### 7.4 Recall on reading the card, and on starvation

| Id | Kind | Skill | Scenario | Right answer | Wrong answers |
| --- | --- | --- | --- | --- | --- |
| `mcq-what-gpu-util-means` | mcq | `read-nvidia-smi` | NVIDIA defines GPU-Util as the share of the sample period in which "one or more kernels was executing on the GPU" (read 2026-11-10). `nvidia-smi` shows 100%. What do you know? | "Some GPU program was running throughout; it says nothing of how much of the card it used" | "Every arithmetic unit on the card was busy throughout; there is no capacity left to use"; "All of the card's memory was in use throughout; the next program to load will not fit"; "The card ran at its rated speed throughout; adding work will slow every program on it" |
| `smi-csv-average` | predict_shell | `read-nvidia-smi` | `gpu.csv` has the header `second,gpu_util_pct,mem_used_mib` and six lines with utilisation 0, 0, 60, 0, 0, 60. Command: `awk -F, 'NR > 1 {s += $2; n++} END {print "average util:", s / n "%"}' gpu.csv` | `average util: 20%` | One reading would have said 0 or 60; the mean says the card is idle four seconds in six |
| `smi-biggest-process` | predict_shell | `read-nvidia-smi` | `procs.csv` is a saved list of the programs on a card, `pid,name,used_mib`: `4411,python,18250`; `4630,python,9120`; `5102,triton,11840`. Command: `sort -t, -k3 -rn procs.csv \| head -n 1` | `4411,python,18250` | Three programs share one card's memory; the total, 39,210 MiB, is nearly all of an A100 40GB |
| `mcq-memory-full-util-zero` | mcq | `read-nvidia-smi` | `nvidia-smi` shows `39900MiB / 40537MiB` and GPU-Util 0% for ten minutes, with one process listed. What is the likeliest state of this server? | "A model is loaded and waiting for requests: memory is held while nothing is being computed" | "The card has run out of memory and stopped: nothing can be computed until it is restarted"; "The card is being starved by slow disks: memory fills up while the data is still arriving"; "A model is training at full speed: memory in use is what the utilisation figure reports" |
| `starve-idle-seconds` | predict_shell | `gpu-starvation` | The same six-line `gpu.csv`. Command: `awk -F, 'NR > 1 && $2 == 0 {n++} END {print n, "of", NR - 1, "seconds idle"}' gpu.csv` | `4 of 6 seconds idle` | An idle GPU is a waiting GPU; the next question is what it waits for |
| `mcq-starved-by-cpu` | mcq | `gpu-starvation` | A training job on a 4-vCPU, one-GPU instance: GPU-Util swings between 0 and 50%, averaging 20%. `mpstat -P ALL` shows all four CPUs at 99% `usr`; `wa` is 0; the card's memory is a third used. What would help most? | "The same card with more vCPUs, so the input is prepared as fast as the card can take it" | "A larger card with more memory, so more of the input can be held on the card at one time"; "The same card with a faster disk, so the input is read as fast as the card can take it"; "A second card of the same kind, so the two cards can share the input between them" |
| `mcq-starved-by-disk` | mcq | `gpu-starvation` | Another job: GPU-Util steady near 15%. CPUs are 60% idle with `wa` at 35%. `iostat -xz` shows the dataset's network disk at 100% `%util` with `await` 40 ms. What would help most? | "Put the dataset on a local NVMe disk or a higher disk tier, so reads stop being the limit" | "Add vCPUs to the instance, so more of them are free to prepare input for the card"; "Move to a card with Tensor Cores, so each step of the arithmetic takes less time"; "Lower the model's precision to 8 bits, so each batch of input needs less memory" |
| `mcq-not-starved` | mcq | `gpu-starvation` | A job shows GPU-Util at 98 to 100%, CPUs at 30%, no disk wait, card memory 80% used. The team asks what to change so it finishes sooner. | "Nothing is starving it: only a faster card or a second one would shorten the run" | "The CPUs are starving it: doubling the vCPUs would roughly halve the time it takes"; "The disk is starving it: moving the data to local NVMe would shorten the run"; "The memory is starving it: a card with more memory would run the same job faster" |
| `mcq-never-loaded` | mcq | `gpu-starvation` | A service was moved to a cheaper GPU instance and now answers nothing. `nvidia-smi` shows 0% and no processes; the application's log ends with an out-of-memory error from the GPU a few seconds after start. What happened? | "The model does not fit this card's memory, so it never loaded: lower the precision or use a bigger card" | "The model loaded but the CPUs cannot feed it, so it sits idle: move to an instance with more vCPUs"; "The model loaded but the disk is too slow, so it sits idle: put its files on a local NVMe disk"; "The model is loading slowly from the disk, so it is not ready: wait for the load to complete" |

### 7.5 `write-gpu-report` (write), skills `read-nvidia-smi`, `gpu-starvation`

- *Holds:* `/srv/gpu/box-2/` and `/srv/gpu/box-3/`, each with `gpu.csv` (60 seconds; the card's total in a `total_mib` column) and `mpstat.txt`. A third box is hidden for the checks.
- *The learner writes* `~/bin/gpu-report DIR` from a blank file. It prints three lines: `average util: N%` (a whole number, rounded), `peak memory: X of Y MiB`, `idle seconds: N`.
- *Checks:* each line, on both boxes and the hidden one, against the check's own `awk`.
- *Wrong fixes to reject:* `wrong/last-line.sh` (reports the last second, not the minute); `wrong/header-counted.sh` (the header row counted as a sample, so the mean is low and idle seconds are one too many); `wrong/peak-is-last.sh`.

### 7.6 Recall on choosing and sharing

Every question that uses a price carries its own small table with the caption "On-demand, Linux, per hour; AWS N. Virginia, Azure East US, Google Cloud Iowa; read 2026-11-10 and 11", copied from the price fixture, and the fields `prices_as_of` and `prices_source`.

| Id | Kind | Skill | Scenario | Right answer | Wrong answers or mistakes |
| --- | --- | --- | --- | --- | --- |
| `mcq-cheapest-that-fits` | mcq | `gpu-instance-choice` | A model needs 18 GiB on one card. The table: `g4dn.xlarge` T4 16 GiB $0.526; `g2-standard-4` L4 24 GB $0.706832; `g6.xlarge` L4 22 GiB $0.8048; `g5.xlarge` A10G 22 GiB $1.006; `NC24ads_A100_v4` A100 80 GB $3.673. Which is the cheapest that fits? | "`g2-standard-4` at $0.706832" | "`g4dn.xlarge` at $0.526" (the cheapest; too small); "`g6.xlarge` at $0.8048" (fits; not the cheapest); "`NC24ads_A100_v4` at $3.673" (fits five times over) |
| `est-job-cost` | estimate | `gpu-instance-choice` | A team timed one job on two instances: 20 hours on `g4dn.xlarge` ($0.526 an hour) and 2 hours on `NC24ads_A100_v4` ($3.673 an hour). How much cheaper, in dollars, is the run on the A100? ±2% | 3.17. Working: `t4_hours * t4_price - a100_hours * a100_price` | −3.15 ("compared the hourly prices; the job is not an hour long"); 7.35 ("that is what the A100 run costs, not the saving") |
| `mcq-count-is-not-size` | mcq | `gpu-instance-choice` | AWS's table (read 2026-11-11): `g4dn.12xlarge` has 4 × T4 and "64 GiB (4 x 16 GiB)". A model's weights are 40 GiB and the software runs it on one card. Does this instance work? | "No: each card holds 16 GiB, and a model that runs on one card needs one card of 40 or more" | "Yes: the four cards pool their memory, so the instance offers the model all 64 GiB"; "Yes: the model loads onto the first card and overflows to the others as it needs to"; "No: four cards can never be used together, so only one card's worth is ever usable" |
| `mcq-vcpus-per-gpu` | mcq | `gpu-instance-choice` | A job on `NC4as_T4_v3` (4 vCPUs, one T4, $0.526) is starved by its CPUs. Azure's table (read 2026-11-11) also has `NC8as_T4_v3` (8 vCPUs, one T4, $0.752) and `NC64as_T4_v3` (64 vCPUs, four T4s). Which change fits the diagnosis? | "`NC8as_T4_v3`: the same card with twice the vCPUs to prepare its input" | "`NC64as_T4_v3`: four cards, so each card needs only a quarter of the input"; "`NC4as_T4_v3` twice over: two small instances share the preparation work"; "`NC24ads_A100_v4`: a larger card needs less input prepared for each step" |
| `est-weekend-bill` | estimate | `gpu-instance-choice` | An `NC24ads_A100_v4` ($3.673 an hour, read 2026-11-10) was left running from Friday 18:00 to Monday 06:00 by mistake. What did the weekend cost? ±1% | 220.38. Working: `hours * price` with 60 hours | 176.30 ("48 hours is Saturday and Sunday; Friday evening and Monday morning add 12"); 3.67 ("that is one hour") |
| `mcq-no-free-gpu` | mcq | `gpu-instance-choice` | A learner wants to try a GPU without spending anything and has a new Google Cloud account on its free trial. Google's page (read 2026-11-10) says what? | "Free-trial accounts cannot add GPUs at all, and the Free Tier never includes them" | "Free-trial accounts get one small GPU for ninety days, and then it is billed hourly"; "The Free Tier includes one T4 each month in three US regions, as it does an `e2-micro`"; "Free-trial accounts can add any GPU, and the trial credit covers the first hundred hours" |
| `est-mig-per-card` | estimate | `gpu-sharing` | NVIDIA's guide (read 2026-11-11): an A100 40GB has 8 memory slices of 5 GB and 7 compute slices. A `2g.10gb` instance takes 2 compute slices and 10 GB. How many fit on one card? Exact | 3. Working: `min(mem_slices // 2, compute_slices // 2)` | 4 ("the memory would allow four; seven compute slices allow only three pairs"); 7 ("that is the count for the smallest profile") |
| `mcq-mig-valid-layout` | mcq | `gpu-sharing` | Same card: 8 memory slices of 5 GB, 7 compute slices. Which layout can one card hold? | "One `4g.20gb`, one `2g.10gb` and one `1g.5gb`" | "One `4g.20gb` and two `2g.10gb`" (8 compute slices); "Three `3g.20gb`" (60 GB); "Eight `1g.5gb`" (8 compute slices). Each option is the same form, so length gives nothing away |
| `mcq-walls-or-turns` | mcq | `gpu-sharing` | Two teams must share one A100, and one team's experiments often run out of GPU memory and crash. NVIDIA's pages (read 2026-11-11) compare the two ways to share. Which protects the other team? | "MIG: each team gets its own memory and faults stay inside its partition" | "Time-slicing: each team gets its own memory and faults stay inside its turn"; "MIG: the teams share all the memory but each is limited to half the time"; "Time-slicing: the card restarts a crashed program without the other noticing" |
| `mcq-which-cards-have-mig` | mcq | `gpu-sharing` | A design shares cheap T4 cards between tenants "with MIG for isolation". NVIDIA's list of supported cards (read 2026-11-11) has the A30, A100, H100, H200 and B200. What follows? | "A T4 cannot be partitioned with MIG; tenants on it can only take turns, without isolation" | "A T4 can be partitioned with MIG into two halves; each tenant gets 8 GB of its own memory"; "A T4 can be partitioned with MIG, but only into seven equal parts of about 2 GB each"; "A T4 cannot be shared at all; each tenant needs an instance with a whole card" |
| `mcq-fraction-for-what` | mcq | `gpu-sharing` | Azure sells `NV6ads_A10_v5`: a sixth of an A10 with 4 GiB of card memory, $0.454 an hour (read 2026-11-10 and 11). For which job is it the right buy? | "A remote desktop for one engineer using a 3D drawing program" | "A service answering questions with a 7-billion-parameter model"; "A nightly job training a model whose weights are 5 GiB in size"; "A batch job that needs a whole A10 for two hours each morning" |
| `mcq-when-nvlink-matters` | mcq | `gpu-sharing` | Hugging Face's example (read 2026-11-11): a 70-billion-parameter model needs about 140 GB at 16 bits, and the largest single cards in the tables hold 80 to 94 GB. Where does a fast card-to-card link earn its price? | "Running that one model across two or more cards, which then exchange data constantly" | "Running eight separate small models, one on each of the eight cards in the server"; "Running that one model on a single card, with the other seven cards left switched off"; "Running eight copies of a web server, each using one card to draw its own pages" |

### 7.7 Ladder order for `topic.yaml`

`example-read-a-gpu-box`, `mcq-what-suits-a-gpu`, `mcq-cuda-or-tensor-cores`, `est-precision-gb`, `mcq-what-lower-precision-buys`, `est-weights-gib`, `mcq-fits-which-card`, `smi-memory-free`, `est-training-memory`, `mcq-floor-not-bill`, `fill-vram-fit`, `mcq-what-gpu-util-means`, `smi-csv-average`, `smi-biggest-process`, `mcq-memory-full-util-zero`, `starve-idle-seconds`, `mcq-starved-by-cpu`, `mcq-starved-by-disk`, `mcq-not-starved`, `mcq-never-loaded`, `write-gpu-report`, `mcq-cheapest-that-fits`, `est-job-cost`, `mcq-count-is-not-size`, `mcq-vcpus-per-gpu`, `est-weekend-bill`, `mcq-no-free-gpu`, `est-mig-per-card`, `mcq-mig-valid-layout`, `mcq-walls-or-turns`, `mcq-which-cards-have-mig`, `mcq-fraction-for-what`, `mcq-when-nvlink-matters`.

**Questions that can come back, by skill** (practice plus the review-only items of section 9): `gpu-vs-cpu` 4 + 2; `vram-fit` 6 + 2; `read-nvidia-smi` 6 + 2; `gpu-starvation` 6 + 2; `gpu-instance-choice` 6 + 2; `gpu-sharing` 6 + 2.

## 8. Proofs

### 8.1 Build: `build-gpu-plan` (plain lab), all six skills

**The brief the learner gets** (no starter, no hints, tutor off): the shop wants a one-page GPU plan for four jobs. Everything needed is in `/srv/plan/`. Write `~/plan/answers.txt`, one `key=value` line for each item in the README's list. The README states the rules of the plan: every figure in `gpus.csv` is to be treated as GiB as the provider states it; a job runs on one card unless it says otherwise; a month is 730 hours.

**What the container holds.**

- `jobs.txt`: four jobs in plain words. *chat*: serve a model of 7 billion parameters at 16 bits, 25% headroom. *tune*: train a model of 5 billion parameters at 16 bits; plan four times the weights. *big*: a model of 70 billion parameters, at 16 bits and, as an alternative, at 4 bits with 20% headroom. *embed*: seven small services of under 5 GB each that must not be able to disturb one another.
- `gpus.csv`: `as_of,cloud,instance,gpu,gpu_count,gpu_mem,vcpus,hourly`, eleven rows from the fixture and facts 16, 18 and 19, with the date. A checksum check confirms it has not been edited (the learner has `sudo`).
- `mig-a100-40.txt`: the profile table of fact 11, and `layouts.txt` with four proposed layouts.
- `boxes/box-4`, `boxes/box-5`: recorded evidence from two trial servers (one starved by its disk, one not starved).

**Keys and checks** (one check per key; the right values are computed by the check from the files):

| Key | Right value (for the writer to confirm when the files exist) | Skill |
| --- | --- | --- |
| `weights-gib.chat` | 13.0 (±0.1) | `vram-fit` |
| `instance.chat` | the cheapest row whose single card holds 16.3 GiB: `g2-standard-4` | `gpu-instance-choice` |
| `monthly.chat` | 730 × its price: 515.99 (±1%) | `gpu-instance-choice` |
| `needed-gib.tune` | 9.31 × 4 = 37.3 (±0.5) | `vram-fit` |
| `instance.tune` | the cheapest single card of 37.3 GiB or more. `NC24ads_A100_v4` ($3.673) beats `a2-highgpu-1g` ($3.673385) by four hundredths of a cent, and has twice the memory | `gpu-instance-choice` |
| `job-cost.tune` | a 6-hour run on it: 22.04 (±1%) | `gpu-instance-choice` |
| `cards-needed.big-16bit` | 130.4 GiB over cards of 80: 2 | `vram-fit`, `gpu-sharing` |
| `fits-one-a100-40.big-4bit` | 32.6 × 1.2 = 39.1 against 40: `yes` | `vram-fit` |
| `cards.embed` | seven `1g.5gb` instances on one A100 40GB: 1 | `gpu-sharing` |
| `valid-layouts` | the numbers of the layouts in `layouts.txt` that respect 8 memory and 7 compute slices, for example `1,3` | `gpu-sharing` |
| `starved-by.box-4`, `starved-by.box-5` | `disk`, `none` | `gpu-starvation`, `read-nvidia-smi` |
| `avg-util.box-4` | the mean from its `gpu.csv` (±1) | `read-nvidia-smi` |

**Lazy or wrong routes the checks must reject, each as a `wrong/*.sh`:** `cheapest-row.sh` (the cheapest instance regardless of memory: the T4 for *chat*); `no-headroom.sh` (also picks the T4, because 13.0 fits in 16); `decimal-gb.sh` (14.0 for the weights); `summed-cards.sh` (a four-T4 instance for *tune*, counting 64 GiB as one card); `one-big-card.sh` (`cards-needed.big-16bit=1`); `memory-only-mig.sh` (calls a layout valid that fits in memory and needs eight compute slices); `blamed-the-gpu.sh` (`starved-by.box-4=none`).

**A caution for the writer.** *tune*'s answer rests on a price difference of $0.000385 an hour. That is deliberate (two clouds, the same card class, the same price, and one has twice the memory), but the check must compare the prices as numbers with all their decimals, and the README must tell the learner not to round before comparing.

### 8.2 Debug: `debug-fit-check` (plain lab), skills `vram-fit`, `gpu-instance-choice`

**The prompt, in full:**

> `~/bin/fit-check` was written by a colleague who has left. Given a model's size in billions of parameters, its bits per parameter and a headroom percentage, it is meant to print the cheapest instance in `/srv/plan/gpus.csv` on which the model runs **on one card** with that headroom to spare, as `instance price`.
>
> The team followed its advice twice last month. One model would not load: the GPU ran out of memory at start-up. For another, the invoice was several times what a neighbouring team paid for the same job on a different instance. Three things are wrong with the script. Find them and fix them, without changing what it is meant to do. Then run the checks.

It gives the purpose, the symptoms and the count. It does not say which lines, or what kind of mistake.

**The three planted faults** (for the writer only), in a script of about 25 lines of bash and `awk`:

1. It compares the model with `gpu_count × gpu_mem`, the instance's total, instead of one card's memory.
2. The headroom is applied backwards: `needed = weights * (100 - headroom) / 100`.
3. Among the rows that fit it takes the last in the file, not the cheapest (`tail -n 1` where a numeric sort and `head -n 1` belong).

Fault 2 makes the 7-billion-parameter model "fit" a 16 GiB card; fault 1 recommends a four-T4 instance for a 26 GiB model; fault 3 returns the A100 when an L4 would do.

**Checks.** The script is run on five cases, two shown in the README as usage examples and three never shown, and each printed line is compared with the answer the check computes from the same CSV with its own `awk`. Descriptions read "prints the right instance for a model of 7 billion parameters at 16 bits with 25% headroom", and so on: the end state, never the bug. One check confirms the CSV's checksum.

**Known-wrong fixes:** `wrong/still-sums-cards.sh`, `wrong/headroom-still-backwards.sh`, `wrong/still-not-cheapest.sh` (each leaves one fault and fails at least one hidden case), and `wrong/hard-coded.sh` (prints the right answers for the two README cases and nothing sensible otherwise).

**Why a script and not a broken GPU server.** There is no server to break. A sizing script with the three classic sizing mistakes in it is unfamiliar work whose fix can be checked exactly, and the mistakes are the topic's own (card against instance, headroom, price), not shell trivia.

### 8.3 Explain

**Prompt.**

> A team asks for "a GPU server". They want to serve a model with 7 billion parameters and, once a week, train a smaller one. Their trial server shows 20% GPU utilisation, and a second team would like to share the card. Explain, in your own words: why this work suits a GPU at all, and what CUDA cores and Tensor Cores each do; why you would ask about memory before speed, and how you would work out whether the model fits a card; what `nvidia-smi`'s utilisation figure does and does not tell you, and what 20% might mean; how you would choose an instance, and one way the three clouds differ; and how one card can be shared safely, and when a link between cards matters.

**Rubric.**

| Id | Required | Description |
| --- | --- | --- |
| `why-gpu` | yes | A GPU has thousands of simple arithmetic units that do the same operation on many numbers at once, which suits multiplying large tables of numbers; CUDA cores do general arithmetic at any precision, Tensor Cores are specialised for matrix multiplication and are fastest at reduced precision (16-bit and below). |
| `memory-first` | yes | The model's parameters must all be in the card's own memory: parameters × bytes each (7 billion at 2 bytes is 14 GB, about 13 GiB); lower precision halves or quarters it; the sum is a floor, so headroom is added; training needs several times the weights; if it does not fit it does not run. |
| `utilisation` | yes | GPU-Util is the share of time some GPU program was running, not the share of the card in use; 20% means the card mostly waits, and the cause is found from the host: CPUs flat out preparing input, a disk at its limit, work too small, or another tenant; near 100% with the host idle means the GPU itself is the limit. |
| `choosing` | yes | Pick the card whose memory holds the model with headroom, then the number of cards, enough vCPUs to feed it and a local disk if the data is large, then compare the cost of the whole job rather than the hourly price; one correct difference between clouds (families and card models, fractional cards, how card memory is stated, no free tier). |
| `sharing` | yes | MIG partitions a supported large card into up to seven instances with their own memory and fault isolation, sized in fixed profiles; time-slicing shares the whole card in turns with no memory or fault isolation; small cards such as the T4 cannot use MIG. |
| `multi-gpu` | no | A model larger than one card's memory is spread over several, which then need a fast card-to-card link (NVLink); independent jobs on separate cards do not. |

**Model answer.** To be written with the topic, about 350 words, in the rubric's order with the lesson's numbers.

## 9. Review pool

From the ladder: `est-weights-gib`, `mcq-fits-which-card`, `smi-memory-free`, `mcq-what-gpu-util-means`, `smi-csv-average`, `mcq-starved-by-cpu`, `mcq-starved-by-disk`, `mcq-cheapest-that-fits`, `est-job-cost`, `est-mig-per-card`, `mcq-walls-or-turns`, `mcq-cuda-or-tensor-cores`.

Review-only items:

| Id | Kind | Skill | Scenario | Right answer | Mistakes or wrong answers |
| --- | --- | --- | --- | --- | --- |
| `mcq-gpu-or-not` | mcq | `gpu-vs-cpu` | A team wants a GPU instance "to make the nightly export faster". The export reads rows one at a time and writes each to a file; a profile shows one CPU core at 100% and the rest idle. What do you tell them? | "A GPU will not help: the work is one step after another, not one sum over many numbers" | "A GPU will help: it has thousands of cores, so the export can use one for each row it reads"; "A GPU will help once the rows are stored in 16 bits, so that the Tensor Cores can be used"; "A GPU will not help yet: the export first needs a card with more memory than its file size" |
| `est-bytes-for-precision` | estimate | `gpu-vs-cpu` | A model has 2 billion parameters. Stored in 8 bits each, about how many GB is that? Exact | 2. Working: `params_billion * bits / 8` | 16 ("bits, not bytes"); 4 ("that is 16-bit") |
| `est-fit-with-headroom` | estimate | `vram-fit` | A model has 13 billion parameters at 16 bits. The team wants 20% of headroom on top of the weights. How many GiB must the card report? ±0.3 | 29.1. Working: `params * bytes / 2**30 * 1.2` | 24.2 ("the weights alone"); 31.2 ("worked in GB of a thousand million bytes") |
| `mcq-train-or-serve` | mcq | `vram-fit` | A model's weights are 9 GiB at 16 bits. It is served comfortably from a 22 GiB card. The team now wants to train it on the same card, and Hugging Face's estimator (read 2026-11-11) puts training at about four times the weights. What should they expect? | "It will not fit: training wants about 36 GiB, so a 40 GiB card or larger is needed" | "It will fit: training uses the same memory as serving, plus a little for each batch"; "It will fit: the card moves what does not fit into the VM's RAM while it is training"; "It will not fit: training always needs two cards, whatever the size of the model" |
| `smi-used-pct` | predict_shell | `read-nvidia-smi` | A one-line file: `9800MiB / 40537MiB`. Command: `awk '{gsub(/MiB/, ""); print "used:", int($1 * 100 / $3) "%"}' mem.txt` | `used: 24%` | A quarter of the card: three more jobs of this size would fill it |
| `mcq-two-owners` | mcq | `read-nvidia-smi` | The process list on one card shows two programs from two different users, 18,000 MiB and 21,000 MiB, on an A100 40GB (40,537 MiB) with MIG disabled. A third user wants to load a 4 GiB model. What will happen? | "It will fail for lack of memory, and nothing stops the first two from failing the same way" | "It will load into its own partition, since the card divides its memory evenly between users"; "It will load after the others finish their turn, since the card queues programs for memory"; "It will fail for lack of compute slices, since two users already hold all seven of them" |
| `mcq-batch-of-one` | mcq | `gpu-starvation` | A service sends its model one request at a time. GPU-Util sits at 8%; CPUs, disk and card memory all have room. The team proposes a larger card. What is the better reading? | "The work arrives too small to fill the card: group requests into batches, or use a smaller card" | "The card is too slow for the work: a larger card will raise the utilisation figure to normal"; "The CPUs are too few for the work: more vCPUs will feed the card and raise its utilisation"; "The disk is too slow for the work: a local NVMe disk will feed the card and raise utilisation" |
| `mcq-which-station` | mcq | `gpu-starvation` | Three trial runs of one job, same card. Run A: GPU 20%, CPUs 99% busy, `wa` 0. Run B, after doubling the vCPUs: GPU 45%, CPUs 50% busy, `wa` 40. What is the limit in run B? | "The disk: the CPUs now have room to spare and are waiting on reads" | "The CPUs: they are still the limit, since the GPU is under half used"; "The GPU: its figure more than doubled, so it is now what limits the job"; "The memory: more vCPUs load more data, so the card's memory is full" |
| `est-monthly-serving` | estimate | `gpu-instance-choice` | A model is served round the clock from one `g2-standard-4` at $0.706832 an hour (Google Cloud, Iowa, read 2026-11-11). Use 730 hours a month. What does a month cost? ±1% | 515.99. Working: `price * 730` | 508.92 ("720 hours"); 16.96 ("one day") |
| `mcq-same-card-three-clouds` | mcq | `gpu-instance-choice` | One job needs one card of about 24 GB. The dated table: AWS `g6.xlarge` (L4, listed as 22 GiB) $0.8048; Google `g2-standard-4` (L4, listed as 24 GB) $0.706832; Azure's nearest whole card `NV36ads_A10_v5` (A10 24 GB, 36 vCPUs) $3.20. What is the fair conclusion? | "The same class of card costs very different amounts by cloud, because of what is bundled with it" | "The AWS card is smaller than Google's, because 22 is less than 24, so it suits smaller models"; "Azure's card is four times as fast, because its price is about four times the other two"; "The three are equivalent offers, because every cloud prices one card of a kind the same" |
| `est-mig-cards-for-teams` | estimate | `gpu-sharing` | Ten teams each need an isolated `2g.10gb` instance. NVIDIA's table (read 2026-11-11): three `2g.10gb` fit on one A100 40GB. How many cards? Exact | 4. Working: `ceil(teams / per_card)` | 3 ("ten 10 GB instances are 100 GB, which is two and a half cards of memory; the compute slices allow only three to a card"); 10 ("a card each ignores partitioning") |
| `mcq-pass-through-or-part` | mcq | `gpu-sharing` | Google's page (read 2026-11-11) says GPUs are attached "in pass-through mode". What does that mean for the VM that has one? | "The VM controls the whole card and its memory directly; no other VM uses that card" | "The VM receives a time-share of the card; other VMs on the host use it in between"; "The VM sees a software copy of the card; the real card stays with the hypervisor"; "The VM controls one seventh of the card; six other VMs hold the other partitions" |

`review_pool:` in `topic.yaml`: the twelve ladder items above plus these twelve. Three are `predict_shell`, which satisfies the validator's rule today.

## 10. What needs platform work first

| Need | Why | Smallest version that would do |
| --- | --- | --- |
| The `estimate` recall type | Twelve items ask for a number (memory, cost, counts). | As in `estimate-questions.md`. Until it exists they ship as `mcq` from the answer and its mistakes. Nothing waits for it. |
| Nothing in `tools/labcheck.py` or the validator | All five labs are plain labs with files and `awk`. | None. |
| A look at how the topic page shows a wide fixture | `nvidia-smi`'s table is about 91 characters wide. The page's code box already scrolls sideways (`overflow-x-auto` in `web/src/components/styles.ts`), so nothing should be needed; look at one fixture on a phone-width screen before marking the topic `ready`. | None expected. |
| Genuine recordings (authors, once) | Every `nvidia-smi` fixture is built to the documented layout with invented numbers, and three formats could not be confirmed (section 5). | One capture run on a single-T4 VM in the owner's Azure subscription, about an hour: `NC4as_T4_v3` at $0.526 an hour plus a disk and an address, about $0.55 in all (about $0.20 on Spot). It needs the budget alert that Module 2's first cloud step sets up, a quota for the NCasT4_v3 family (which may have to be requested first), auto-shutdown, a tag, and deletion at the end. Save `nvidia-smi`, `nvidia-smi --query-gpu=... --format=csv -l 1` and `mpstat` under four conditions: idle; a GPU kept busy; the same held back by one pinned CPU; a program that asks for more memory than the card has. The topic can be `ready` before this; the fixtures say "representative" until then. |

## 11. Cost and time

**Cost to the learner: nothing.** No lab touches a cloud. The only money is the Claude API's few cents for grading the explanation.

**Why there is no cloud lab.** A real GPU for an hour costs about fifty cents, well inside the budget. But what the hour would add is watching `nvidia-smi` print live what the recordings already show; the learner cannot write GPU programs (Python comes in Module 6, GPU code never in this track), so there is nothing for them to *do* on the card that a check could verify. The first lab that needs a real GPU is where the track deploys one for a purpose: Module 12 (Compute) or Module 27 (AI and ML platforms). The spec's own rule points the same way: large GPU work is "designed and reviewed" and practised with "a single GPU" as a stand-in, later.

**Time.**

| Part | Minutes |
| --- | --- |
| Lesson intro and recap | 15 |
| Reading (the named sections of resources 0 to 5, 7, one provider's table, 11) | 65 |
| 28 quick questions at about 1.3 minutes | 36 |
| `example-read-a-gpu-box` | 20 |
| `fill-vram-fit` | 20 |
| `write-gpu-report` | 25 |
| Build | 50 |
| Debug | 40 |
| Explain | 15 |
| **Total** | **286** |

`estimated_minutes: 290`.

## 12. Open questions, each with a recommendation

1. **Is a topic with no GPU honest?** Yes, if it says so and is exact about what it proves: reading, arithmetic, choosing and sharing. It does not prove that the learner can operate a GPU, and the explain rubric does not ask for that. **Recommendation: ship it as designed,** say "there is no GPU here; everything is read or counted" in the Intro (the ML track's GPU topic says the same), and give the learner their first real card where the track has a use for one.
2. **Six skills or five?** `read-nvidia-smi` and `gpu-starvation` could be one. They fail differently (misreading a figure against choosing the wrong cause), and a missed question should bring back the kind that was missed. **Recommendation: six.**
3. **How much ML to explain.** Only what sizing needs: parameter, precision, training against inference, batch. **Recommendation: hold that line.** Anything more belongs to the ML track, and Module 27 can assume this topic.
4. **Which unit does a lab's table use for card memory?** Providers disagree (fact 17). **Recommendation:** the lab's CSV keeps each provider's figure as stated, the README says "treat every figure as GiB for this plan", and the lesson explains why real planning takes the smaller figure. The alternative, converting everything to one unit, would hide the disagreement the learner will meet.
5. **The MIG sum rule.** "At most 8 memory slices and 7 compute slices" rejects bad layouts but cannot prove a good one. **Recommendation:** questions offer only layouts that are either documented by NVIDIA or break the sums, and the lesson says the table is the last word.
6. **Debug as a script.** The alternative is a recorded-evidence diagnosis, as in Checkpoint 2's part 2. **Recommendation: the script.** The build and the recall already ask for diagnosis from recordings; the debug should ask for something else, and three sizing mistakes in someone else's tool is the mistake an architect inherits.
7. **Named cards go stale.** Google already marks the T4 as near the end of support. **Recommendation:** keep the T4 for now as "the small, older card" (it is still the cheapest on AWS and Azure), date every table, and review the topic's tables once a year with the price fixture.
8. **The main resource is thin.** **Recommendation: accept it** for this topic and let the lesson carry more than usual; revisit if a maker's beginner-level text on GPU memory appears.
