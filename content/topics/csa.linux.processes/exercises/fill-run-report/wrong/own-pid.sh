# Wrong: $$ is the script's own PID. The job's is $!.
cat > ~/bin/run-report <<'EOF'
#!/usr/bin/env bash
/srv/tools/make-report.sh "$@" &
pid=$$
echo "started report as PID $pid"
wait
status=$?
if [ "$status" -eq 0 ]; then
  echo "report finished"
else
  echo "report failed with status $status"
fi
exit "$status"
EOF
