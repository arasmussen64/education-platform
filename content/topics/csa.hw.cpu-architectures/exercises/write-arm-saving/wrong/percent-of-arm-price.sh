# Wrong: the percentage is taken of the Arm price instead of the x86 price,
# so 0.0192 saved on 0.1008 comes out as 23.5% instead of 19.0%. A saving
# is a share of what you pay now.
mkdir -p ~/bin
cat > ~/bin/arm-saving <<'EOF'
#!/bin/bash
set -euo pipefail
x86_price=$(awk -F, -v t="$2" '$2 == t {print $5}' "$1")
arm_price=$(awk -F, -v t="$3" '$2 == t {print $5}' "$1")
awk -v x="$x86_price" -v a="$arm_price" -v n="$4" 'BEGIN {
  hour = x - a
  printf "per hour: %.4f\n", hour
  printf "percent: %.1f\n", hour * 100 / a
  printf "per month for %d: %.2f\n", n, hour * 730 * n
}'
EOF
chmod +x ~/bin/arm-saving
