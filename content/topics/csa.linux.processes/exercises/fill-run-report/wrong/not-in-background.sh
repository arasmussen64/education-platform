# Wrong: no &, so the job runs in the foreground and $! is nobody.
cat > ~/bin/run-report <<'EOF'
#!/usr/bin/env bash
/srv/tools/make-report.sh "$@"
pid=$!
echo "started report as PID $pid"
wait "$pid" 2>/dev/null
status=$?
if [ "$status" -eq 0 ]; then
  echo "report finished"
else
  echo "report failed with status $status"
fi
exit "$status"
EOF
