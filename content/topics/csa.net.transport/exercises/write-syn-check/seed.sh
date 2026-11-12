#!/bin/bash
# The scenery of "SYN check": an empty ~/bin for the script. The captures to
# try it on are in /srv/captures, one folder a pair.
set -euo pipefail
home=/home/learner
mkdir -p "$home/bin"
chown -R learner:learner "$home/bin"
