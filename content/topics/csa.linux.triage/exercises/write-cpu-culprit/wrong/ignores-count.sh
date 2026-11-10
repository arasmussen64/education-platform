# Wrong: the count is hard-coded to five, so top-cpu 3 still prints five.
cat > ~/bin/top-cpu <<'EOF'
#!/bin/bash
set -euo pipefail
ps -eo comm,%cpu --sort=-%cpu | awk 'NR > 1 && NR <= 6 {print $1, $2 "%"}'
EOF
chmod +x ~/bin/top-cpu
