#!/bin/bash
# The scenery for "Write cidr-overlaps": an empty ~/bin for the script, and
# a sample plan to try it on.
set -euo pipefail
mkdir -p /home/learner/bin /home/learner/plans
cp /usr/local/lib/lab/sites.txt /home/learner/plans/sites.txt
chown -R learner:learner /home/learner/bin /home/learner/plans
