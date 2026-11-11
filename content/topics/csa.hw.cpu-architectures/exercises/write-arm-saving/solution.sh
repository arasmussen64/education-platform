# One way to write it: awk finds each type's price in the file, then one
# awk program does the three sums and prints them with the decimals asked
# for. Comma-separated files are split with -F, and the type is the second
# field, the price the fifth.
mkdir -p ~/bin
cat > ~/bin/arm-saving <<'EOF'
#!/bin/bash
# Usage: arm-saving CSV X86_TYPE ARM_TYPE COUNT
# What moving COUNT machines from X86_TYPE to ARM_TYPE saves, at the prices
# in CSV: per hour for one machine, as a percentage of the x86 price, and
# per month for all of them (730 hours a month). Negative when Arm costs more.
set -euo pipefail
csv="$1"
x86="$2"
arm="$3"
count="$4"
x86_price=$(awk -F, -v t="$x86" '$2 == t {print $5}' "$csv")
arm_price=$(awk -F, -v t="$arm" '$2 == t {print $5}' "$csv")
awk -v x="$x86_price" -v a="$arm_price" -v n="$count" 'BEGIN {
  hour = x - a
  printf "per hour: %.4f\n", hour
  printf "percent: %.1f\n", hour * 100 / x
  printf "per month for %d: %.2f\n", n, hour * 730 * n
}'
EOF
chmod +x ~/bin/arm-saving
~/bin/arm-saving /srv/prices/2026-11.csv m7i.large m7g.large 40
~/bin/arm-saving /srv/prices/2026-11.csv e2-standard-2 n4a-standard-2 5
