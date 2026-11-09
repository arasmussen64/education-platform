# Wrong: the matching and the signal are fixed, but the report still reads
# pgrep's exit status the wrong way round.
cat > ~/bin/stop-workers <<'EOF'
#!/bin/bash
for name in order-worker mail-worker report-worker; do
  for pid in $(pgrep -x "$name"); do
    kill "$pid"
  done
done

sleep 2
status=0
for name in order-worker mail-worker report-worker; do
  if pgrep -x "$name" > /dev/null; then
    echo "$name stopped"
  else
    echo "$name still running"
    status=1
  fi
done
exit "$status"
EOF
~/bin/stop-workers || true
