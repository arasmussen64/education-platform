# Wrong: measures properly, but only the three services the prompt names,
# typed into a list, instead of every shop-*.service the machine has. A
# service added later is never measured.
cat > ~/bin/busiest-service <<'EOF'
#!/bin/bash
set -euo pipefail
base=/sys/fs/cgroup/system.slice
read_usage() { awk '/^usage_usec/ {print $2}' "$base/$1.service/cpu.stat"; }
services=(shop-api shop-db shop-worker)
declare -A before
for s in "${services[@]}"; do before[$s]=$(read_usage "$s"); done
sleep 1
lines=""
for s in "${services[@]}"; do
  after=$(read_usage "$s")
  lines+="$(( (after - before[$s]) / 1000 )) $s"$'\n'
done
sorted=$(printf '%s' "$lines" | sort -rn)
printf '%s\n' "$sorted" | awk '{printf "  %s: %s ms\n", $2, $1}'
echo "busiest: $(printf '%s\n' "$sorted" | head -1 | awk '{print $2}')"
EOF
chmod +x ~/bin/busiest-service
