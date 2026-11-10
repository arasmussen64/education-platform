#!/bin/bash
# The scenery for "Build a safe deploy script": the app's source, and an
# empty ~/bin.
set -euo pipefail
mkdir -p /home/learner/app/src /home/learner/bin
echo "shop app" > /home/learner/app/src/app.txt
echo "SHOP_ENV=prod" > /home/learner/app/src/config.env
chown -R learner:learner /home/learner
