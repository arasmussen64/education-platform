#!/bin/bash
# A report job gone wrong: it loops forever, writing a line every second.
# It listens for TERM, writes a last line and exits cleanly; KILL would give
# it no chance to.
log=/var/log/shop/runaway.log
trap 'echo "caught TERM, cleaning up and exiting" >> "$log"; exit 0' TERM
while true; do
  echo "still working on the report... $(date +%T)" >> "$log"
  sleep 1
done
