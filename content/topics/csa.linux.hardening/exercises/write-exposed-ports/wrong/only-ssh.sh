# Wrong: only ever reports SSH, so it never notices the debug port at all.
cat > ~/bin/exposed-ports <<'EOF'
#!/bin/bash
set -euo pipefail
if sudo ss -ltnH | awk '{print $4}' | grep -E ':22$' > /dev/null; then
  echo "22 sshd allowed"
fi
EOF
chmod +x ~/bin/exposed-ports
