# Wrong: no trap, so an interrupted runner dies and leaves its jobs running.
mkdir -p ~/bin
cat > ~/bin/nightly <<'EOF'
#!/usr/bin/env bash
/srv/jobs/backup.sh > /dev/null &   backup=$!
/srv/jobs/report.sh > /dev/null &   report=$!
/srv/jobs/cleanup.sh > /dev/null &  cleanup=$!
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
