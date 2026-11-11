#!/bin/bash
# Lays down the GPU plan under /srv/plan. gpus.csv is a dated table of real
# list prices and sizes (its README, below, gives every source). The trial
# servers' evidence is constructed, not captured: no GPU was used. Their
# nvidia-smi summaries follow the layout NVIDIA's Multi-Instance GPU User
# Guide (Release 620, 2026-11-04) shows for driver 580.65.06, with the card
# name, power cap and memory total it shows for an H100 80GB HBM3; every
# other number is invented, from arithmetic on the second, so the checks
# work out each answer from the same files.
set -euo pipefail

plan=/srv/plan
mkdir -p "$plan/boxes/box-4" "$plan/boxes/box-5"
cp /usr/local/lib/lab/gpus.csv "$plan/gpus.csv"
rm /usr/local/lib/lab/gpus.csv

cat > "$plan/gpus-README.txt" <<'EOF'
gpus.csv: GPU instances on three clouds, one row each, read on 2026-11-11.

  as_of               the day the row was read
  cloud, region       aws us-east-1 (N. Virginia), azure eastus (East US),
                      gcp us-central1 (Iowa)
  instance            the provider's name for the size
  gpu                 the card
  gpu_count           how many cards the instance has
  gpu_mem_as_stated   one card's memory, in the provider's own figure and
                      unit: AWS in GiB, Azure and Google Cloud in GB
  gpu_mem_gib         the same figure converted to GiB: a GiB as stated is
                      kept, and a GB (1,000,000,000 bytes) is divided by
                      1.073741824, to two places
  vcpus               the instance's vCPUs
  hourly_usd          the on-demand price for Linux, US dollars an hour

The providers disagree about the same cards. AWS lists the L4 as 22 GiB and
Google Cloud as 24 GB, which is 22.35 GiB; AWS lists the T4 as 16 GiB and
Azure as 16 GB, which is 14.90 GiB. This table takes every figure at its
word and converts it, so it never pretends one unit is the other; on a real
machine, nvidia-smi's own total settles it. Work only with gpu_mem_gib.

Where each column came from, all read on 2026-11-11:
  AWS sizes and card memory  https://docs.aws.amazon.com/ec2/latest/instancetypes/ac.html
  AWS prices                 AWS's public price file for US East (N. Virginia),
                             Linux, on-demand, published 2026-11-10; today's are
                             at https://aws.amazon.com/ec2/pricing/on-demand/
  Azure sizes and memory     the size-series pages under
                             https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/
  Azure prices               https://prices.azure.com/api/retail/prices (East US,
                             pay-as-you-go); today's are at
                             https://azure.microsoft.com/pricing/details/virtual-machines/linux/
  Google Cloud sizes         https://docs.cloud.google.com/compute/docs/gpus
  Google Cloud prices        https://cloud.google.com/products/compute/pricing/accelerator-optimized
                             (Iowa)
Prices change. These are for this plan; today's will differ.
EOF

cat > "$plan/jobs.txt" <<'EOF'
The four jobs the shop wants a GPU plan for.

chat   Serve a chat model of 11 billion parameters, stored in 16 bits,
       round the clock, on one card, with 25% headroom on top of its
       weights.

tune   Train a model of 6 billion parameters, stored in 16 bits, on one
       card. Training keeps several working copies of the weights: plan for
       four times the weights, with no further headroom on top. One
       training run takes 9 hours on the card the plan chooses. The team
       that runs it already rents a g6.12xlarge for its nights and asks
       whether tune could run on that instead.

big    Serve a model of 90 billion parameters with 20% headroom on top of
       its weights, on A100 80GB cards like the one in NC24ads_A100_v4's
       row of gpus.csv: stored in 16 bits, or, as the alternative, in 4
       bits. A model too big for one card is split evenly over several.

embed  Six small services, each needing 6 GB of card memory, which must not
       be able to disturb one another: each has memory of its own, and a
       crash in one can't reach the others. They are to share A100 40GB
       cards, partitioned with MIG (mig-a100-40gb.txt).
EOF

cat > "$plan/mig-a100-40gb.txt" <<'EOF'
# GPU instance profiles on the A100-SXM4-40GB, from NVIDIA's Multi-Instance
# GPU User Guide, Release 620 (2026-11-04), Table 15. The card is cut into
# 8 memory slices of about 5 GB and 7 compute slices; a profile takes so
# many of each, and the last column is how many of that profile alone one
# card can hold. (The guide's 1g.5gb+me, with a media engine, is left out.)
profile  memory_slices  compute_slices  most_on_one_card
1g.5gb   1              1               7
1g.10gb  2              1               4
2g.10gb  2              2               3
3g.20gb  4              3               2
4g.20gb  4              4               1
7g.40gb  8              7               1
EOF

cat > "$plan/layouts.txt" <<'EOF'
Four layouts proposed for one A100 40GB, by number. Each one either breaks
the card's slice sums or is a layout NVIDIA's guide shows working.

1  4g.20gb, 4g.20gb
2  1g.10gb, 1g.10gb, 1g.10gb, 1g.10gb
3  3g.20gb, 3g.20gb, 1g.5gb
4  3g.20gb, 3g.20gb
EOF

# --- Two trial servers, each with one H100 80GB and 26 vCPUs ---------------------
# box-4 reads its training data from a network disk that is at its limit:
# the card works at a quarter, the CPUs wait on reads, the disk is full up.
# box-5 is the GPU working flat out with the CPUs and the disk to spare.
cat > "$plan/boxes/box-4/nvidia-smi.txt" <<'EOF'
Thu Nov  5 10:12:11 2026
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.65.06              Driver Version: 580.65.06      CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA H100 80GB HBM3          On  |   00000000:04:00.0 Off |                    0 |
| N/A   38C    P0            236W /  700W |   30210MiB /  81559MiB |     31%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A            3391      C   python3                               30200MiB |
+-----------------------------------------------------------------------------------------+
EOF
cat > "$plan/boxes/box-5/nvidia-smi.txt" <<'EOF'
Thu Nov  5 16:40:02 2026
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.65.06              Driver Version: 580.65.06      CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA H100 80GB HBM3          On  |   00000000:04:00.0 Off |                    0 |
| N/A   63C    P0            641W /  700W |   66180MiB /  81559MiB |    100%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A            1204      C   python3                               66170MiB |
+-----------------------------------------------------------------------------------------+
EOF

# gpu.csv: a minute, one line a second. box-4 sits between 18% and 34%,
# idle one second in ten (a mean of 23.6); box-5 between 96% and 100%.
{
  echo "second,gpu_util_pct,mem_used_mib"
  for ((s = 1; s <= 60; s++)); do
    if ((s % 10 == 0)); then util=0; else util=$((18 + (s * 7) % 17)); fi
    echo "$s,$util,30210"
  done
} > "$plan/boxes/box-4/gpu.csv"
{
  echo "second,gpu_util_pct,mem_used_mib"
  for ((s = 1; s <= 60; s++)); do echo "$s,$((96 + s % 5)),66180"; done
} > "$plan/boxes/box-5/gpu.csv"

# mpstat MACHINE USR SYS IOWAIT IDLE: mpstat -P ALL 60 1 for 26 vCPUs that
# all spend the minute the same way.
mpstat_file() {
  local machine=$1 usr=$2 sys=$3 iowait=$4 idle=$5 label cpu
  printf 'Linux 6.8.0-1015-gcp (%s) \t11/05/26 \t_x86_64_\t(26 CPU)\n\n' "$machine"
  for label in 10:12:11 Average:; do
    printf '%-11s  CPU    %%usr   %%nice    %%sys %%iowait    %%irq   %%soft  %%steal  %%guest  %%gnice   %%idle\n' "$label"
    printf '%-11s  all  %6s    0.00  %6s  %6s    0.00    0.10    0.00    0.00    0.00  %6s\n' "$label" "$usr" "$sys" "$iowait" "$idle"
    for ((cpu = 0; cpu < 26; cpu++)); do
      printf '%-11s %4d  %6s    0.00  %6s  %6s    0.00    0.10    0.00    0.00    0.00  %6s\n' "$label" "$cpu" "$usr" "$sys" "$iowait" "$idle"
    done
    echo
  done
}
mpstat_file box-4 21.40 3.10 44.80 30.60 > "$plan/boxes/box-4/mpstat.txt"
mpstat_file box-5 33.20 2.40 0.10 64.20 > "$plan/boxes/box-5/mpstat.txt"

cat > "$plan/boxes/box-4/iostat.txt" <<'EOF'
Linux 6.8.0-1015-gcp (box-4) 	11/05/26 	_x86_64_	(26 CPU)

Device            r/s     rkB/s  r_await     w/s     wkB/s  w_await  aqu-sz  %util
nvme0n1          0.30      4.80     0.61    2.80     36.40     0.92    0.01   0.30
nvme0n2       2400.00 307200.00    86.40    0.00      0.00     0.00  207.36 100.00
EOF
cat > "$plan/boxes/box-5/iostat.txt" <<'EOF'
Linux 6.8.0-1015-gcp (box-5) 	11/05/26 	_x86_64_	(26 CPU)

Device            r/s     rkB/s  r_await     w/s     wkB/s  w_await  aqu-sz  %util
nvme0n1          0.20      3.20     0.58    2.60     33.80     0.90    0.01   0.30
nvme0n2        410.00  52480.00     0.91    0.00      0.00     0.00    0.37  14.20
EOF

for b in box-4 box-5; do
  cat > "$plan/boxes/$b/README" <<EOF
What an on-call script saved from $b, a trial training server with one GPU
and 26 vCPUs, during one minute of the same training job.

  nvidia-smi.txt   what nvidia-smi printed, once, during the minute
  gpu.csv          a monitoring export: one line a second, the card's
                   utilisation (%) and the memory in use (MiB)
  mpstat.txt       mpstat -P ALL 60 1: each vCPU over the same minute
  iostat.txt       iostat -xz 60 1, shortened to the columns the lesson
                   reads; nvme0n2 is the network disk the data is on

Constructed, not captured: no GPU was used to make these. Each file follows
the layout of the tool it is named after, with invented numbers.
EOF
done

cat > "$plan/README.txt" <<'EOF'
The GPU plan: what goes in ~/plan/answers.txt
=============================================

One key=value line for each key below; ~/plan/answers.txt lists the keys.
The jobs are in jobs.txt, the instances in gpus.csv (gpus-README.txt says
what each column is and where it came from), and the trial servers'
evidence under boxes/.

The rules of the plan:
  - A model's weights take its parameters x its bits / 8 bytes; a GiB is
    1,073,741,824 bytes. Work with gpu_mem_gib, never gpu_mem_as_stated.
  - A job runs on one card unless jobs.txt says otherwise, and a card holds
    what the job needs only if its gpu_mem_gib is at least that much.
  - A month is 730 hours. Prices are gpus.csv's hourly_usd, in US dollars.
  - Don't round a number before you have used it.

chat
  weights-gib.chat        chat's weights, in GiB
  instance.chat           the cheapest instance in gpus.csv that can run
                          chat as jobs.txt says
  monthly.chat            what that instance costs for a month, in dollars
tune
  needed-gib.tune         what tune's card must hold, in GiB
  instance.tune           the cheapest instance in gpus.csv that can run tune
  job-cost.tune           what one training run costs on it, in dollars
  tune-fits.g6.12xlarge   yes or no: can tune run on the team's g6.12xlarge?
big
  cards-needed.big-16bit  how many A100 80GB cards big needs in 16 bits
  cards-needed.big-4bit   how many it needs in 4 bits
embed
  cards.embed             how many A100 40GB cards the six services need
  valid-layouts           the numbers of the layouts in layouts.txt that one
                          A100 40GB can hold, separated by commas (for
                          example 1,3), or none
The trial servers
  starved-by.box-4        what kept box-4's card waiting: one of cpu, disk,
                          never-loaded, too-small, sharing, none
  starved-by.box-5        the same for box-5
  avg-util.box-4          box-4's mean utilisation over its minute, in %

Numbers may be written with or without decimals. weights-gib.chat is
checked to within 0.1, needed-gib.tune to within 0.5, avg-util.box-4 to
within 1, monthly.chat and job-cost.tune to within 1%; the rest exactly.
EOF

mkdir -p /home/learner/plan
cat > /home/learner/plan/answers.txt <<'EOF'
weights-gib.chat=
instance.chat=
monthly.chat=
needed-gib.tune=
instance.tune=
job-cost.tune=
tune-fits.g6.12xlarge=
cards-needed.big-16bit=
cards-needed.big-4bit=
cards.embed=
valid-layouts=
starved-by.box-4=
starved-by.box-5=
avg-util.box-4=
EOF
chown -R learner:learner /home/learner/plan
chmod -R a+rX "$plan"

# The checksum of everything under /srv/plan, for the check that keeps the
# plan's files as they were (the learner has sudo). Root's alone.
(cd "$plan" && find . -type f | sort | xargs sha256sum | sha256sum | cut -d' ' -f1) > /usr/local/lib/lab/plan.sha256
chmod 600 /usr/local/lib/lab/plan.sha256
