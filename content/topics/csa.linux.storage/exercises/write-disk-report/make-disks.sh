#!/bin/bash
# The lab's disks, made at image build: the shop's data volume (200 MB,
# ext4), filled with folders of known sizes so the biggest is the logs.
# The log shipper deletes logs/shipping.log at boot while holding it open.
set -euo pipefail
mkdir -p /var/lib/lab /etc/lab
seed=$(mktemp -d)
mkdir -p "$seed/logs/old" "$seed/cache" "$seed/uploads" "$seed/db"
for day in 01 02 03; do
  head -c 25M /dev/urandom > "$seed/logs/old/app-2026-10-$day.log"
done
head -c 10M /dev/urandom > "$seed/logs/app.log"
head -c 20M /dev/urandom > "$seed/logs/shipping.log"
head -c 30M /dev/urandom > "$seed/cache/thumbnails.bin"
head -c 5M /dev/urandom > "$seed/uploads/photo-0001.jpg"
head -c 2M /dev/urandom > "$seed/db/shop.sqlite"
truncate -s 200M /var/lib/lab/data3.img
mkfs.ext4 -q -d "$seed" /var/lib/lab/data3.img
rm -rf "$seed"
echo "data3 /srv/shop" > /etc/lab/disks.conf
