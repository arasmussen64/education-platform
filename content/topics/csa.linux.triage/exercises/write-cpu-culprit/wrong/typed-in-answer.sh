# Wrong: prints the answer for this machine, typed in, as many times as
# asked. The count and the format are right, but it never looks at the
# machine, so a process that wasn't there when it was written is missing.
cat > ~/bin/top-cpu <<'EOF'
#!/bin/bash
set -euo pipefail
n="${1:-5}"
for i in $(seq 1 "$n"); do
  echo "shop-worker 99.4%"
done
EOF
chmod +x ~/bin/top-cpu
