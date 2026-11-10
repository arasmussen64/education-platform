#!/bin/bash
# The scenery for "Write backup-logs": the shop's logs to archive, one of
# them with a space in its name, and an empty ~/bin.
set -euo pipefail
mkdir -p /var/log/shop
echo "GET /item/1 200 1024" > /var/log/shop/access.log
echo "startup ok" > /var/log/shop/app.log
echo "disk slow" > "/var/log/shop/error report.log"
mkdir -p /home/learner/bin
chown -R learner:learner /home/learner
