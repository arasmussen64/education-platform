# Wrong: marks every port allowed, so the open debug door isn't flagged.
cat > ~/bin/exposed-ports <<'EOF'
#!/bin/bash
set -euo pipefail
sudo ss -ltnpH | while read -r line; do
  laddr=$(awk '{print $4}' <<<"$line")
  case "$laddr" in
    0.0.0.0:* | "[::]:"* | "*:"*) ;;
    *) continue ;;
  esac
  port=${laddr##*:}
  proc=$(grep -oP '\("\K[^"]+' <<<"$line" | head -1)
  echo "$port ${proc:-?} allowed"
done | sort -un
EOF
chmod +x ~/bin/exposed-ports
