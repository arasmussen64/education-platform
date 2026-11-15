#!/bin/bash
# The lab's data disk, made at image build: a 256 MB image file, already
# formatted. disks.sh attaches it at every boot.
set -euo pipefail
mkdir -p /var/lib/lab
truncate -s 256M /var/lib/lab/data.img
mkfs.ext4 -q -L data /var/lib/lab/data.img
