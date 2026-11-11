#!/bin/bash
# Lays down the worked example: what an on-call script saved from one GPU
# server, box-1, during a training run. Everything is constructed, not
# captured: no GPU was used. The nvidia-smi summary follows the layout that
# NVIDIA's Multi-Instance GPU User Guide (Release 620, 2026-11-04) shows for
# driver 580.65.06, and its card name, power cap and memory total are the
# ones that guide shows for an H100 80GB HBM3; every other number is
# invented, from arithmetic on the second, so the checks can work out each
# answer from the same files.
set -euo pipefail

box=/srv/gpu/box-1
mkdir -p "$box"

cat > "$box/nvidia-smi.txt" <<'EOF'
Wed Nov  4 14:03:11 2026
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.65.06              Driver Version: 580.65.06      CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA H100 80GB HBM3          On  |   00000000:04:00.0 Off |                    0 |
| N/A   34C    P0            182W /  700W |   12450MiB /  81559MiB |     54%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A            2817      C   python3                               12440MiB |
+-----------------------------------------------------------------------------------------+
EOF

# A minute of the card, one line a second: two idle seconds and one at 54%,
# over and over (a mean of 18, 40 idle seconds), and the memory the model
# holds, which doesn't change. The summary above was taken in a busy second.
{
  echo "second,gpu_util_pct,mem_used_mib"
  for ((s = 1; s <= 60; s++)); do
    if ((s % 3 == 0)); then util=54; else util=0; fi
    echo "$s,$util,12450"
  done
} > "$box/gpu.csv"

# mpstat -P ALL 60 1 over the same minute: all 26 vCPUs flat out in %usr,
# nothing waiting on the disk, nothing stolen.
{
  printf 'Linux 6.8.0-1015-gcp (gpu-box-1) \t11/04/26 \t_x86_64_\t(26 CPU)\n\n'
  for label in 14:03:11 Average:; do
    printf '%-11s  CPU    %%usr   %%nice    %%sys %%iowait    %%irq   %%soft  %%steal  %%guest  %%gnice   %%idle\n' "$label"
    printf '%-11s  all   98.41    0.00    1.49    0.00    0.00    0.08    0.00    0.00    0.00    0.02\n' "$label"
    for ((cpu = 0; cpu < 26; cpu++)); do
      tenths=$(((cpu * 7) % 9))
      printf '%-11s %4d   98.%d0    0.00    1.%d0    0.00    0.00    0.08    0.00    0.00    0.00    0.02\n' \
        "$label" "$cpu" "$tenths" $((9 - tenths))
    done
    echo
  done
} > "$box/mpstat.txt"

# iostat -xz 60 1, shortened to the columns this topic reads: the boot disk
# and the data disk the training data is read from, both far from busy.
cat > "$box/iostat.txt" <<'EOF'
Linux 6.8.0-1015-gcp (gpu-box-1) 	11/04/26 	_x86_64_	(26 CPU)

Device            r/s     rkB/s  r_await     w/s     wkB/s  w_await  aqu-sz  %util
nvme0n1          0.40      6.10     0.52    3.10     41.20     0.88    0.01   0.30
nvme0n2        212.50  27200.00     0.84    0.00      0.00     0.00    0.18  11.40
EOF

cat > "$box/README" <<'EOF'
What an on-call script saved from box-1, a training server with one GPU and
26 vCPUs, during one minute of a training run.

  nvidia-smi.txt   what nvidia-smi printed, once, during the minute
  gpu.csv          a monitoring export: one line a second for the minute,
                   the card's utilisation (%) and the memory in use (MiB)
  mpstat.txt       mpstat -P ALL 60 1: each vCPU over the same minute
  iostat.txt       iostat -xz 60 1, shortened to the columns the lesson
                   reads; nvme0n2 is the disk the training data is on

Constructed, not captured: no GPU was used to make these. Each file follows
the layout of the tool it is named after (nvidia-smi as NVIDIA's own guide
prints it for driver 580.65.06), with invented numbers. There is no
nvidia-smi command on this machine.
EOF

chmod -R a+rX /srv/gpu

# The checksum of the evidence, for the check that it is as the lab laid it
# down (the learner has sudo). Root's alone.
(cd /srv/gpu && find . -type f | sort | xargs sha256sum | sha256sum | cut -d' ' -f1) > /usr/local/lib/lab/evidence.sha256
chmod 600 /usr/local/lib/lab/evidence.sha256
