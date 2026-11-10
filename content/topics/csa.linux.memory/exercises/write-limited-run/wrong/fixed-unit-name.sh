# Wrong: every run is a unit called "limited", so the journal can't tell
# one run from another and two at once would collide.
mkdir -p ~/bin
cat > ~/bin/limited-run <<'EOF'
#!/bin/bash
name="$1"
limit="$2"
shift 2
out=$(sudo systemd-run --wait --collect --unit=limited -p MemoryMax="$limit" -p MemorySwapMax=0 "$@" 2>&1 || true)
result=$(echo "$out" | awk -F': ' '/Finished with result/ {print $2}')
if [ "$result" = oom-kill ]; then
  echo "$name: killed: out of memory at $limit"
  exit 137
fi
echo "$name: finished"
EOF
chmod +x ~/bin/limited-run
