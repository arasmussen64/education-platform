# Wrong: reads a counter that doesn't exist (user_usec), so every delta is
# empty, the measurement is nonsense, and all but one service drops out.
cat > ~/bin/busiest-service <<'EOF'
#!/bin/bash
set -euo pipefail
base=/sys/fs/cgroup/system.slice
read_usage() { awk '/^user_usec/ {print $2}' "$base/$1.service/cpu.stat"; }
services=()
for d in "$base"/shop-*.service; do services+=("$(basename "$d" .service)"); done
declare -A before
for s in "${services[@]}"; do before[$s]=$(read_usage "$s"); done
sleep 1
for s in "${services[@]}"; do
  after=$(read_usage "$s")
  echo "  $s: $(( after - before[$s] )) ms"
done
echo "busiest: ${services[0]}"
EOF
chmod +x ~/bin/busiest-service
