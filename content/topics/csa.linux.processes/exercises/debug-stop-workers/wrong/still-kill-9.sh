# Wrong: the matching and the report are fixed, but KILL still skips the
# workers' cleanup, so their PID files stay behind.
cat > ~/bin/stop-workers <<'EOF'
#!/bin/bash
for name in order-worker mail-worker report-worker; do
  for pid in $(pgrep -x "$name"); do
    kill -9 "$pid"
  done
done

sleep 2
status=0
for name in order-worker mail-worker report-worker; do
  if pgrep -x "$name" > /dev/null; then
    echo "$name still running"
    status=1
  else
    echo "$name stopped"
  fi
done
exit "$status"
EOF
~/bin/stop-workers
