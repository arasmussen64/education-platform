#!/usr/bin/env bash
# The shop's report job: takes a second, writes the report (with its own PID
# in it) and exits 0. With the word "broken" it fails with status 3 instead.
sleep 1
if [ "${1:-}" = broken ]; then
  echo "report job: the database is unreachable" >&2
  exit 3
fi
echo "report made by PID $$" > /tmp/report.txt
echo "report written to /tmp/report.txt"
