#!/bin/bash
# The lab's disk, made at image build: a 256 MB network-style data disk,
# already formatted, which disks.sh attaches and mounts at /srv/data.
set -euo pipefail
mkdir -p /var/lib/lab /etc/lab
truncate -s 256M /var/lib/lab/data.img
mkfs.ext4 -q -L data /var/lib/lab/data.img
printf 'data /srv/data network\n' > /etc/lab/disks.conf
