# The three mistakes:
#   1. `pgrep worker` matched every process with "worker" in its name,
#      including this script, stop-workers, which therefore killed itself
#      before it could report. Each worker is found by its exact name.
#   2. `kill -9` gave the workers no chance to run their cleanup, so their
#      PID files stayed in /run/shop. Plain kill sends TERM.
#   3. `pgrep` exits 0 when it FINDS the process, so the report was
#      backwards: a running worker was called stopped.
cat > ~/bin/stop-workers <<'EOF'
#!/bin/bash
# Stops the shop's workers (order-worker, mail-worker, report-worker),
# politely, waits for them, and reports on each one.
# Exit status: 0 if they all stopped, 1 if one is still running.

for name in order-worker mail-worker report-worker; do
  for pid in $(pgrep -x "$name"); do
    kill "$pid"
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
