# Wrong: the header line isn't skipped, so the first line is "COMMAND %CPU"
# and the count is off by one.
cat > ~/bin/top-cpu <<'EOF'
#!/bin/bash
set -euo pipefail
n="${1:-5}"
ps -eo comm,%cpu --sort=-%cpu | awk -v n="$n" 'NR <= n {print $1, $2 "%"}'
EOF
chmod +x ~/bin/top-cpu
