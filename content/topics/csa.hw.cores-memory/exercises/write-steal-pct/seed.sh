#!/bin/bash
# Lays down the lab: three pairs of saved /proc/stat first lines, each taken
# a minute apart on a 2-vCPU VM (12,000 ticks in all: 60 seconds x 100 ticks
# x 2 vCPUs), and a fourth pair for the checks only. They are constructed,
# not captured: the numbers since boot are invented, and the growth over the
# minute is chosen so each pair tells a different story.
set -euo pipefail

# pair DIR "BEFORE NUMBERS" "GROWTH": writes DIR/before.txt and
# DIR/after.txt, the second being the first plus the growth, in the layout
# of /proc/stat's first line ("cpu", two spaces, ten numbers).
pair() {
  local dir=$1 before=($2) growth=($3) after=() i
  for ((i = 0; i < 10; i++)); do after+=($((before[i] + growth[i]))); done
  mkdir -p "$dir"
  echo "cpu  ${before[*]}" > "$dir/before.txt"
  echo "cpu  ${after[*]}" > "$dir/after.txt"
}

# The ten numbers: user nice system idle iowait irq softirq steal guest
# guest_nice. Since boot, every machine has had about 5% stolen.
#
# quiet: busy with its own work, and nothing stolen in the minute (0.0%).
pair /srv/stat/quiet "2104000 1200 401300 7351800 30100 0 18800 512000 0 0" \
  "2400 0 600 8900 100 0 0 0 0 0"
# robbed: 4,500 of the minute's 12,000 ticks stolen (37.5%).
pair /srv/stat/robbed "880500 300 160200 3020400 9100 0 7300 214600 0 0" \
  "1500 0 600 5100 0 0 300 4500 0 0"
# mostly-idle: almost nothing to do, and a little stolen (4.0%).
pair /srv/stat/mostly-idle "301000 0 95500 6203000 12000 0 4100 345000 0 0" \
  "240 0 120 11100 60 0 0 480 0 0"

# For the checks only: a VM that is idle apart from being robbed, half a
# minute apart (6,000 ticks; 39.0%). A script that divides steal by the busy
# time alone gets 97.5. Root's alone, so its answer can't be copied.
pair /usr/local/lib/lab/hidden/idle-robbed "15020 0 8040 902000 300 0 150 44000 0 0" \
  "30 0 30 3600 0 0 0 2340 0 0"
chmod -R go-rwx /usr/local/lib/lab/hidden

cat > /srv/stat/README <<'EOF'
Three pairs of saved copies of the first line of /proc/stat, each pair
taken a minute apart on a 2-vCPU VM: quiet, robbed and mostly-idle.

They are constructed, not captured: written in /proc/stat's layout, with
invented numbers. The ten numbers after "cpu" are ticks (hundredths of a
second) since the machine started, in this order: user, nice, system, idle,
iowait, irq, softirq, steal, guest, guest_nice. The first eight add up to
all the time there was; guest and guest_nice are already counted in user
and nice.
EOF
chmod -R a+rX /srv/stat
mkdir -p /home/learner/bin
chown learner:learner /home/learner/bin
