#!/bin/bash
# The scenery for "Report what the fleet runs on": the two fleets readable by
# everyone and changeable by nobody but root, and empty folders for the
# learner's script and report.
set -euo pipefail
chown -R root:root /srv/fleet-a /usr/local/share/lab/fleet-b
chmod -R u=rwX,go=rX /srv/fleet-a /usr/local/share/lab/fleet-b
mkdir -p /home/learner/bin /home/learner/report
chown -R learner:learner /home/learner
