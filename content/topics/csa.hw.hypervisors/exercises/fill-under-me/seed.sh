#!/bin/bash
# The scenery for "Finish the under-me script": the captures, readable by
# everyone and changeable only by root, lab-capture itself, and the
# learner's script with its four gaps.
set -euo pipefail
install -m 755 /usr/local/lib/lab/lab-capture /usr/local/bin/lab-capture
chown -R root:root /srv/captures /usr/local/share/lab/captures
chmod -R u=rwX,go=rX /srv/captures /usr/local/share/lab/captures
mkdir -p /home/learner/bin
install -m 755 /usr/local/lib/lab/under-me.starter /home/learner/bin/under-me
chown -R learner:learner /home/learner
