# Wrong: waits for the jobs but never looks at how they ended, so every
# night is "ok".
mkdir -p ~/bin
cat > ~/bin/nightly <<'EOF'
#!/usr/bin/env bash
/srv/jobs/backup.sh > /dev/null &   backup=$!
/srv/jobs/report.sh > /dev/null &   report=$!
/srv/jobs/cleanup.sh > /dev/null &  cleanup=$!
trap 'echo "nightly interrupted" >&2; kill $backup $report $cleanup 2>/dev/null; wait; exit 1' TERM INT
wait
echo "backup: ok"
echo "report: ok"
echo "cleanup: ok"
EOF
chmod +x ~/bin/nightly
