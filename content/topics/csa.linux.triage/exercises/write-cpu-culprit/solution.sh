# The reference script, written in one go; in the lab you'd use nano.
cat > ~/bin/top-cpu <<'EOF'
#!/bin/bash
# Usage: top-cpu [N]  (default 5)
# The N processes using the most CPU, busiest first, as "name pct%".
set -euo pipefail
n="${1:-5}"
ps -eo comm,%cpu --sort=-%cpu | awk -v n="$n" 'NR > 1 && NR <= n + 1 {print $1, $2 "%"}'
EOF
chmod +x ~/bin/top-cpu
echo "--- top-cpu (default five):"
~/bin/top-cpu
echo "--- top-cpu 3:"
~/bin/top-cpu 3
