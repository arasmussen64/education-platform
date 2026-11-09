# Wrong: TERM and hope. A process that ignores TERM is still running afterwards.
mkdir -p ~/bin
cat > ~/bin/graceful-stop <<'EOF'
#!/usr/bin/env bash
name="$1"
pid=$(pgrep -x "$name") || { echo "$name is not running"; exit 1; }
kill $pid
for _ in 1 2 3 4 5; do
  sleep 1
  kill -0 $pid 2>/dev/null || break
done
if kill -0 $pid 2>/dev/null; then
  echo "had to kill $name"
else
  echo "stopped $name politely"
fi
EOF
chmod +x ~/bin/graceful-stop
