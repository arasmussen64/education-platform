#!/bin/bash
# The scenery for "Finish cidr-info": the learner's half-written script in
# ~/bin, executable, theirs to fill in.
set -euo pipefail
mkdir -p /home/learner/bin
cp /usr/local/lib/lab/cidr-info.starter /home/learner/bin/cidr-info
chmod 755 /home/learner/bin/cidr-info
chown -R learner:learner /home/learner/bin
