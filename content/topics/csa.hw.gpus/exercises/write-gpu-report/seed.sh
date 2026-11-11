#!/bin/bash
# Lays down the lab: two GPU servers' monitoring exports, a minute each.
# Constructed, not captured: no GPU was used. The memory totals are what
# NVIDIA's Multi-Instance GPU User Guide (Release 620) shows an H100 80GB
# HBM3 (81559 MiB, driver 580.65.06) and an A100-SXM4-40GB (40537 MiB,
# driver 450.80.02) reporting; every other number is invented, from
# arithmetic on the second, so the checks can work out each answer from the
# same files. The checks also make up a third box of their own as they run.
set -euo pipefail

# box DIR TOTAL: writes DIR/gpu.csv from util(s) and mem(s) below.
box() {
  local dir=$1 total=$2 s
  mkdir -p "$dir"
  {
    echo "second,gpu_util_pct,mem_used_mib,mem_total_mib"
    for ((s = 1; s <= 60; s++)); do echo "$s,$(util "$s"),$(mem "$s"),$total"; done
  } > "$dir/gpu.csv"
}

# box-2: a training run on an H100. Idle one second in four while the next
# batch arrives; the memory rises and falls a little with each batch, and
# the last second isn't the fullest. Mean 52.0%, 15 idle seconds.
util() { if (($1 % 4 == 0)); then echo 0; else echo $((55 + ($1 * 7) % 31)); fi; }
mem() { echo $((61000 + ($1 % 10) * 120)); }
box /srv/gpu/box-2 81559

# box-3: a service answering requests on an A100 40GB, idle two seconds in
# five. Mean 17.7%, which rounds to 18 and not 17; 24 idle seconds.
util() { if (($1 % 5 < 2)); then echo 0; else echo $((22 + ($1 * 3) % 17)); fi; }
mem() { echo $((38800 + ($1 % 7) * 90)); }
box /srv/gpu/box-3 40537

cat > /srv/gpu/README <<'EOF'
Two GPU servers' monitoring exports, one minute each: box-2/gpu.csv and
box-3/gpu.csv. Each has a heading line and then one line a second:

  second          1 to 60
  gpu_util_pct    nvidia-smi's GPU-Util for that second, in %
  mem_used_mib    the card's memory in use, in MiB
  mem_total_mib   the card's memory, in MiB, as the card reports it

Constructed, not captured: no GPU was used to make these. The totals are
the ones NVIDIA's own guide shows an H100 80GB and an A100 40GB reporting;
the rest is invented. There is no nvidia-smi command on this machine.
EOF

chmod -R a+rX /srv/gpu
mkdir -p /home/learner/bin
chown learner:learner /home/learner/bin
