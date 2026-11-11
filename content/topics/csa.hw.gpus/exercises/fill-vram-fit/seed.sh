#!/bin/bash
# Lays down the lab: the learner's script with its three gaps. Nothing else
# is needed: the script works only on the numbers it is given.
set -euo pipefail

mkdir -p /home/learner/bin
cp /usr/local/lib/lab/vram-fit.starter /home/learner/bin/vram-fit
chmod 755 /home/learner/bin/vram-fit
chown -R learner:learner /home/learner/bin
rm /usr/local/lib/lab/vram-fit.starter
