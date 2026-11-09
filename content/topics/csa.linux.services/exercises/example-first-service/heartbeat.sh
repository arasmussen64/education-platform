#!/usr/bin/env bash
# The smallest possible service: prints a line every two seconds, forever.
while true; do
  echo "heartbeat: alive at $(date +%T)"
  sleep 2
done
