# Wrong: only compares the last line's hash with the anchor, and never
# works a hash out, so an edited record goes unnoticed.
cat > ~/bin/chain-verify << 'EOF'
#!/bin/bash
set -euo pipefail
log=$1
anchor=$2
last=$(tail -n 1 "$log" | cut -d' ' -f1)
if [ "$last" != "$anchor" ]; then
  echo "anchor mismatch"
  exit 1
fi
echo "ok $(wc -l < "$log")"
EOF
chmod +x ~/bin/chain-verify
