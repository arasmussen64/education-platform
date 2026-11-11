# Wrong: the saving is divided by the number of vCPUs, so it is a saving
# per vCPU, not per machine. The machines are what is being bought.
mkdir -p ~/bin
cat > ~/bin/arm-saving <<'EOF'
#!/bin/bash
set -euo pipefail
x86_price=$(awk -F, -v t="$2" '$2 == t {print $5}' "$1")
arm_price=$(awk -F, -v t="$3" '$2 == t {print $5}' "$1")
vcpus=$(awk -F, -v t="$2" '$2 == t {print $4}' "$1")
awk -v x="$x86_price" -v a="$arm_price" -v n="$4" -v v="$vcpus" 'BEGIN {
  hour = (x - a) / v
  printf "per hour: %.4f\n", hour
  printf "percent: %.1f\n", (x - a) * 100 / x
  printf "per month for %d: %.2f\n", n, hour * 730 * n
}'
EOF
chmod +x ~/bin/arm-saving
