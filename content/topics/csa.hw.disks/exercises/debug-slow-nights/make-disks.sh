#!/bin/bash
# The lab's disks, made at image build: a 256 MB network disk for the
# shop's data, already formatted, and a 256 MB local disk for scratch
# space, which disks.sh formats afresh at every boot.
set -euo pipefail
mkdir -p /var/lib/lab /etc/lab
truncate -s 256M /var/lib/lab/data.img
mkfs.ext4 -q -L data /var/lib/lab/data.img
truncate -s 256M /var/lib/lab/scratch.img
printf 'data /srv/data network\nscratch /srv/scratch local\n' > /etc/lab/disks.conf
