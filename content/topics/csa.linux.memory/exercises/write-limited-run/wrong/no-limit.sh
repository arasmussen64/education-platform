# Wrong: the limit is printed but never set, so nothing is ever killed.
mkdir -p ~/bin
cat > ~/bin/limited-run <<'EOF'
#!/bin/bash
name="$1"
limit="$2"
shift 2
out=$(sudo systemd-run --wait --collect --unit="$name" "$@" 2>&1 || true)
result=$(echo "$out" | awk -F': ' '/Finished with result/ {print $2}')
if [ "$result" = oom-kill ]; then
  echo "$name: killed: out of memory at $limit"
  exit 137
fi
echo "$name: finished"
EOF
chmod +x ~/bin/limited-run
