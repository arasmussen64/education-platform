# Wrong: only ever reports SSH, so it never notices the debug port at all.
cat > ~/bin/exposed-ports <<'EOF'
#!/bin/bash
set -euo pipefail
if sudo ss -ltnH | awk '{print $4}' | grep -qE ':22$'; then
  echo "22 sshd allowed"
fi
EOF
chmod +x ~/bin/exposed-ports
