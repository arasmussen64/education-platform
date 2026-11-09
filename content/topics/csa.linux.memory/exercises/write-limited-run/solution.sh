# The reference script, written in one go; in the lab you'd use nano.
mkdir -p ~/bin
cat > ~/bin/limited-run <<'EOF'
#!/bin/bash
# Usage: limited-run NAME LIMIT COMMAND...
# Runs COMMAND as a service called NAME inside a memory limit, like a
# container. Exits 0 if it finished, 137 if the kernel killed it for
# reaching the limit.
name="$1"
limit="$2"
shift 2
out=$(sudo systemd-run --wait --collect --unit="$name" -p MemoryMax="$limit" -p MemorySwapMax=0 "$@" 2>&1 || true)
result=$(echo "$out" | awk -F': ' '/Finished with result/ {print $2}')
if [ "$result" = oom-kill ]; then
  echo "$name: killed: out of memory at $limit"
  exit 137
fi
echo "$name: finished"
EOF
chmod +x ~/bin/limited-run
~/bin/limited-run small 32M memhog 100 1; echo "exit status $?"
~/bin/limited-run big 256M memhog 50 1; echo "exit status $?"
