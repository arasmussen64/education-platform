# The reference script, written in one go; in the lab you'd use nano.
mkdir -p ~/bin
cat > ~/bin/graceful-stop <<'EOF'
#!/usr/bin/env bash
# Usage: graceful-stop NAME
# Asks the process called NAME to stop (TERM); after five seconds, makes it (KILL).
name="$1"
pid=$(pgrep -x "$name") || { echo "$name is not running"; exit 1; }
kill $pid
for _ in 1 2 3 4 5; do
  sleep 1
  kill -0 $pid 2>/dev/null || break
done
if kill -0 $pid 2>/dev/null; then
  kill -9 $pid
  echo "had to kill $name"
else
  echo "stopped $name politely"
fi
EOF
chmod +x ~/bin/graceful-stop
/srv/tools/polite-worker &
sleep 1
~/bin/graceful-stop polite-worker
