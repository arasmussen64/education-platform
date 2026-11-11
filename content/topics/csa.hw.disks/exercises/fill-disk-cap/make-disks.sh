#!/bin/bash
# The lab's disks, made at image build: two 256 MB network-style disks,
# already formatted, which disks.sh attaches and mounts: the database's
# data disk at /srv/data and a logs disk at /srv/logs.
set -euo pipefail
mkdir -p /var/lib/lab /etc/lab
for name in data logs; do
  truncate -s 256M "/var/lib/lab/$name.img"
  mkfs.ext4 -q -L "$name" "/var/lib/lab/$name.img"
done
printf 'data /srv/data network\nlogs /srv/logs network\n' > /etc/lab/disks.conf
