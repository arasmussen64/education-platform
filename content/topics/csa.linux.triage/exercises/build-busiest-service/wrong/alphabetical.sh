# Wrong: names the first service alphabetically as busiest, without
# measuring anything, so it blames shop-api.
cat > ~/bin/busiest-service <<'EOF'
#!/bin/bash
set -euo pipefail
base=/sys/fs/cgroup/system.slice
services=()
for d in "$base"/shop-*.service; do services+=("$(basename "$d" .service)"); done
echo "services: ${services[*]}"
echo "busiest: ${services[0]}"
EOF
chmod +x ~/bin/busiest-service
