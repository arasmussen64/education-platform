#!/bin/bash
# The scenery for "Write a VM launcher": the guest in /opt/vm (built by the
# layer before this one), the worked example's launcher to copy the fixed
# part of the command from, and empty folders for the learner's launcher
# and the VM's disk.
set -euo pipefail
install -m 755 /usr/local/lib/lab/boot-default /opt/vm/boot-default
mkdir -p /home/learner/bin /home/learner/vm
chown -R learner:learner /home/learner
