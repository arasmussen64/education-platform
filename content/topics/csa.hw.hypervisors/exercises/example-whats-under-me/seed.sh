#!/bin/bash
# The scenery for "What's under this machine?": the two captures, readable by
# everyone and changeable only by root, lab-capture itself, and the launcher
# that boots the VM with QEMU's default hardware.
set -euo pipefail
install -m 755 /usr/local/lib/lab/lab-capture /usr/local/bin/lab-capture
install -m 755 /usr/local/lib/lab/boot-default /opt/vm/boot-default
chown -R root:root /srv/captures
chmod -R u=rwX,go=rX /srv/captures
chown -R learner:learner /home/learner
