# Wrong: sorts the deltas smallest first, so the busiest line names the
# idlest service.
cat > ~/bin/busiest-service <<'EOF'
#!/bin/bash
set -euo pipefail
base=/sys/fs/cgroup/system.slice
read_usage() { awk '/^usage_usec/ {print $2}' "$base/$1.service/cpu.stat"; }
services=()
for d in "$base"/shop-*.service; do services+=("$(basename "$d" .service)"); done
declare -A before
for s in "${services[@]}"; do before[$s]=$(read_usage "$s"); done
sleep 1
lines=""
for s in "${services[@]}"; do
  after=$(read_usage "$s")
  lines+="$(( (after - before[$s]) / 1000 )) $s"$'\n'
done
sorted=$(printf '%s' "$lines" | sort -n)
printf '%s\n' "$sorted" | awk '{printf "  %s: %s ms\n", $2, $1}'
echo "busiest: $(printf '%s\n' "$sorted" | head -1 | awk '{print $2}')"
EOF
chmod +x ~/bin/busiest-service
