# Wrong: doesn't filter to public addresses, so the loopback-only database
# on 5432 is listed as if it were exposed.
cat > ~/bin/exposed-ports <<'EOF'
#!/bin/bash
set -euo pipefail
sudo ss -ltnpH | while read -r line; do
  laddr=$(awk '{print $4}' <<<"$line")
  port=${laddr##*:}
  proc=$(grep -oP '\("\K[^"]+' <<<"$line" | head -1)
  if [ "$port" = 22 ]; then verdict=allowed; else verdict=unexpected; fi
  echo "$port ${proc:-?} $verdict"
done | sort -un
EOF
chmod +x ~/bin/exposed-ports
