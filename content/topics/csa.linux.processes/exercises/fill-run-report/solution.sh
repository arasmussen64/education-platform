# The finished script. In the lab you'd fill the four gaps with nano; here
# it's written in one go.
cat > ~/bin/run-report <<'EOF'
#!/usr/bin/env bash
# Runs the shop's report job in the background, waits for it, and says how
# it went. Usage: run-report [broken]   (the word broken makes the job fail)
/srv/tools/make-report.sh "$@" &
pid=$!
echo "started report as PID $pid"
wait "$pid"
status=$?
if [ "$status" -eq 0 ]; then
  echo "report finished"
else
  echo "report failed with status $status"
fi
exit "$status"
EOF
~/bin/run-report
~/bin/run-report broken || echo "exit status $?"
