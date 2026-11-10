# Wrong: sorted ascending (+%cpu), so the first line is the most idle
# process, not the busiest.
cat > ~/bin/top-cpu <<'EOF'
#!/bin/bash
set -euo pipefail
n="${1:-5}"
ps -eo comm,%cpu --sort=%cpu | awk -v n="$n" 'NR > 1 && NR <= n + 1 {print $1, $2 "%"}'
EOF
chmod +x ~/bin/top-cpu
