#!/usr/bin/env bash
# The nightly report: takes two seconds. Fails with status 2 while the file
# /tmp/report-broken exists, so the runner's failure path can be tested.
sleep 2
if [ -e /tmp/report-broken ]; then
  echo "report: the database is unreachable" >&2
  exit 2
fi
echo "report: 1 page written"
