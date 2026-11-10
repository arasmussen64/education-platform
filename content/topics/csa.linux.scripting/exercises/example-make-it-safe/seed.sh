#!/bin/bash
# The scenery for "The habits that make a script safe": the shop's logs, so
# the demonstrations have something real to work on, and an empty ~/bin.
set -euo pipefail
mkdir -p /var/log/shop
for n in 1 2 3; do
  echo "GET /item/$n 200 1024" >> /var/log/shop/access.log
done
echo "startup ok" > /var/log/shop/app.log
mkdir -p /home/learner/bin
chown -R learner:learner /home/learner
