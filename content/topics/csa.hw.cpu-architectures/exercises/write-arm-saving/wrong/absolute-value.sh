# Wrong: the difference is always taken as a positive number, so a move
# that costs more money is reported as a saving.
mkdir -p ~/bin
cat > ~/bin/arm-saving <<'EOF'
#!/bin/bash
set -euo pipefail
x86_price=$(awk -F, -v t="$2" '$2 == t {print $5}' "$1")
arm_price=$(awk -F, -v t="$3" '$2 == t {print $5}' "$1")
awk -v x="$x86_price" -v a="$arm_price" -v n="$4" 'BEGIN {
  hour = x - a
  if (hour < 0) hour = -hour
  printf "per hour: %.4f\n", hour
  printf "percent: %.1f\n", hour * 100 / x
  printf "per month for %d: %.2f\n", n, hour * 730 * n
}'
EOF
chmod +x ~/bin/arm-saving
