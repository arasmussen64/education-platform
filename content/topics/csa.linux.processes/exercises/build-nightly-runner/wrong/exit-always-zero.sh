# Wrong: reports the failure in words but exits 0, so whatever runs nightly
# (cron, a service) thinks it succeeded.
mkdir -p ~/bin
cat > ~/bin/nightly <<'EOF'
#!/usr/bin/env bash
/srv/jobs/backup.sh > /dev/null &   backup=$!
/srv/jobs/report.sh > /dev/null &   report=$!
/srv/jobs/cleanup.sh > /dev/null &  cleanup=$!
trap 'echo "nightly interrupted" >&2; kill $backup $report $cleanup 2>/dev/null; wait; exit 1' TERM INT
report_on() {
  local name="$1" pid="$2"
  if wait "$pid"; then
    echo "$name: ok"
  else
    echo "$name: failed (status $?)"
  fi
}
report_on backup "$backup"
report_on report "$report"
report_on cleanup "$cleanup"
exit 0
EOF
chmod +x ~/bin/nightly
