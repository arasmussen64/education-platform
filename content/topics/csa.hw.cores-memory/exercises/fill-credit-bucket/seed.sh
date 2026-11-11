#!/bin/bash
# Lays down the lab: two burstable instances' numbers, built from arithmetic
# on the minute number so the checks can work out the truth from the same
# files, and the learner's script with its gaps.
set -euo pipefail

# usage FILE then "FROM TO PERCENT" lines on stdin: a usage.csv with one
# line a minute, the CPU the workload asked for in that minute.
usage() {
  local file=$1 from to pct minute
  echo "minute,cpu_pct" > "$file"
  while read -r from to pct; do
    for ((minute = from; minute <= to; minute++)); do echo "$minute,$pct" >> "$file"; done
  done
}

# shop-web: a t3.small (AWS's table, read 2026-11-11: 2 vCPUs, a baseline of
# 20% a vCPU, 24 credits an hour, at most 576), with 100 credits at the
# start of the four hours. Quiet for an hour, busy for two, then quiet.
mkdir -p /srv/burst/shop-web
cat > /srv/burst/shop-web/instance.conf <<'EOF'
# shop-web's instance: a t3.small in standard mode
vcpus=2
baseline_pct=20
start_credits=100
max_credits=576
EOF
usage /srv/burst/shop-web/usage.csv <<'EOF'
1 60 5
61 180 90
181 240 10
EOF

# shop-batch, for the checks only: a t3.micro (2 vCPUs, 10%, 12 an hour, at
# most 288) that idles long enough to fill its bucket to the top, so a
# script without the ceiling gets the wrong minute. Root's alone, so its
# answers can't be copied.
hidden=/usr/local/lib/lab/hidden/shop-batch
mkdir -p "$hidden"
cat > "$hidden/instance.conf" <<'EOF'
# shop-batch's instance: a t3.micro in standard mode
vcpus=2
baseline_pct=10
start_credits=250
max_credits=288
EOF
usage "$hidden/usage.csv" <<'EOF'
1 240 0
241 420 95
421 480 5
EOF
chmod -R go-rwx /usr/local/lib/lab/hidden

chmod -R a+rX /srv/burst
mkdir -p /home/learner/bin
cp /usr/local/lib/lab/credit-bucket.starter /home/learner/bin/credit-bucket
chmod 755 /home/learner/bin/credit-bucket
chown -R learner:learner /home/learner/bin
rm /usr/local/lib/lab/credit-bucket.starter
