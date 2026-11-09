# The reference runner, written in one go; in the lab you'd use nano.
mkdir -p ~/bin
cat > ~/bin/nightly <<'EOF'
#!/usr/bin/env bash
# Runs the shop's three nightly jobs at once, reports on each, and stops
# them all if it's interrupted.

# Start every job in the background and remember each one's PID.
/srv/jobs/backup.sh > /dev/null &   backup=$!
/srv/jobs/report.sh > /dev/null &   report=$!
/srv/jobs/cleanup.sh > /dev/null &  cleanup=$!

# On TERM or INT: ask the jobs to stop, wait for them, and give up.
stop_everything() {
  echo "nightly interrupted" >&2
  kill "$backup" "$report" "$cleanup" 2>/dev/null
  wait
  exit 1
}
trap stop_everything TERM INT

# Wait for each job and report its exit status.
status=0
report_on() {
  local name="$1" pid="$2"
  if wait "$pid"; then
    echo "$name: ok"
  else
    echo "$name: failed (status $?)"
    status=1
  fi
}
report_on backup "$backup"
report_on report "$report"
report_on cleanup "$cleanup"
exit "$status"
EOF
chmod +x ~/bin/nightly
~/bin/nightly
