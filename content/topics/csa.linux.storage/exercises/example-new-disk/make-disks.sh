#!/bin/bash
# The lab's disks, made at image build: one blank 200 MB volume.
set -euo pipefail
mkdir -p /var/lib/lab /etc/lab
truncate -s 200M /var/lib/lab/data1.img
echo "data1 -" > /etc/lab/disks.conf
