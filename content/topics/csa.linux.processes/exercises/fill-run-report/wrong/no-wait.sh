# Wrong: without wait, the script reports before the job has finished, and
# the status it reads is the shell's, not the job's.
cat > ~/bin/run-report <<'EOF'
#!/usr/bin/env bash
/srv/tools/make-report.sh "$@" &
pid=$!
echo "started report as PID $pid"
status=$?
if [ "$status" -eq 0 ]; then
  echo "report finished"
else
  echo "report failed with status $status"
fi
exit "$status"
EOF
