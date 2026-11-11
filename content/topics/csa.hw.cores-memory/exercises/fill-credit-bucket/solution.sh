# The finished script. In the lab you'd fill the three gaps with nano; here
# it's written in one go. A credit is one vCPU flat out for one minute, so in
# a minute the instance earns vcpus x baseline% and spends vcpus x CPU%.
cat > ~/bin/credit-bucket <<'EOF'
#!/bin/bash
# Usage: credit-bucket DIR
# Follows a burstable instance's CPU credit balance minute by minute, from
# DIR/instance.conf (the instance) and DIR/usage.csv (how much CPU its work
# asked for, minute by minute), and prints three lines: the minute the
# balance first ran out (or never), how many minutes the work was held to
# the baseline, and the balance at the end.
dir="$1"
vcpus=$(grep '^vcpus=' "$dir/instance.conf" | cut -d= -f2)
baseline=$(grep '^baseline_pct=' "$dir/instance.conf" | cut -d= -f2)
start=$(grep '^start_credits=' "$dir/instance.conf" | cut -d= -f2)
max=$(grep '^max_credits=' "$dir/instance.conf" | cut -d= -f2)

awk -F, -v vcpus="$vcpus" -v baseline="$baseline" -v b="$start" -v max="$max" '
  NR == 1 { next }                 # the heading line: minute,cpu_pct
  {
    earned = vcpus * baseline / 100
    spent = vcpus * $2 / 100
    b = b + earned - spent
    if (b <= 0 && empty == "") empty = $1
    if (b < 0) b = 0; if (b > max) b = max
    if (b == 0 && $2 > baseline) held++
  }
  END {
    print "empty at minute: " (empty == "" ? "never" : empty)
    print "minutes held to baseline: " held + 0
    printf "final balance: %.1f\n", b
  }' "$dir/usage.csv"
EOF
~/bin/credit-bucket /srv/burst/shop-web
