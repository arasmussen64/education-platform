# The reference audit, written in one go; in the lab you'd use nano.
cat > ~/bin/exposed-ports <<'EOF'
#!/bin/bash
# Usage: exposed-ports
# TCP ports listening on a public address, each with its process and a
# verdict: allowed for SSH (22), unexpected for anything else. Loopback-only
# sockets are not exposed and aren't listed.
set -euo pipefail
sudo ss -ltnpH | while read -r line; do
  laddr=$(awk '{print $4}' <<<"$line")
  case "$laddr" in
    0.0.0.0:* | "[::]:"* | "*:"*) ;;
    *) continue ;;
  esac
  port=${laddr##*:}
  proc=$(grep -oP '\("\K[^"]+' <<<"$line" | head -1)
  if [ "$port" = 22 ]; then verdict=allowed; else verdict=unexpected; fi
  echo "$port ${proc:-?} $verdict"
done | sort -un
EOF
chmod +x ~/bin/exposed-ports
~/bin/exposed-ports
