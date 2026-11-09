# Wrong: $? is read after an echo, so it's always echo's 0.
cat > ~/bin/run-report <<'EOF'
#!/usr/bin/env bash
/srv/tools/make-report.sh "$@" &
pid=$!
echo "started report as PID $pid"
wait "$pid"
echo "the job has ended"
status=$?
if [ "$status" -eq 0 ]; then
  echo "report finished"
else
  echo "report failed with status $status"
fi
exit "$status"
EOF
