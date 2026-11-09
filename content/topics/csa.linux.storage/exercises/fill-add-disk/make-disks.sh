#!/bin/bash
# The lab's disks, made at image build: one blank 400 MB volume (XFS wants
# at least 300 MB).
set -euo pipefail
mkdir -p /var/lib/lab /etc/lab
truncate -s 400M /var/lib/lab/data2.img
echo "data2 -" > /etc/lab/disks.conf
