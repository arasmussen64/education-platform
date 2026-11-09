# Wrong: TERM and the report are fixed, but `pgrep worker` still matches
# this script's own name, so it still stops itself halfway.
cat > ~/bin/stop-workers <<'EOF'
#!/bin/bash
pids=$(pgrep worker)
for pid in $pids; do
  kill "$pid"
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
~/bin/stop-workers || true
