#!/bin/bash
# The lab's disks, made at image build. data1 (200 MB, ext4) is the shop's
# data volume, almost full of logs; at boot the log shipper deletes
# logs/shipping.log while holding it open. data4 (20 MB, ext4 with only
# 2048 inodes) is the uploads volume, which fill-inodes.service fills with
# tiny files at boot so that it has space but no inodes.
set -euo pipefail
mkdir -p /var/lib/lab /etc/lab

seed=$(mktemp -d)
mkdir -p "$seed/logs/old" "$seed/db"
for day in 01 02 03; do
  head -c 35M /dev/urandom > "$seed/logs/old/app-2026-10-$day.log"
done
head -c 40M /dev/urandom > "$seed/logs/shipping.log"
head -c 10M /dev/urandom > "$seed/logs/app.log"
head -c 2M /dev/urandom > "$seed/db/shop.sqlite"
truncate -s 200M /var/lib/lab/data1.img
mkfs.ext4 -q -d "$seed" /var/lib/lab/data1.img
rm -rf "$seed"

seed=$(mktemp -d)
mkdir -p "$seed/tmp"
echo "a photo" > "$seed/photo-0001.jpg"
echo "a photo" > "$seed/photo-0002.jpg"
for i in $(seq 1 1900); do echo "$i" > "$seed/tmp/upload-$i.part"; done
truncate -s 20M /var/lib/lab/data4.img
mkfs.ext4 -q -N 2048 -d "$seed" /var/lib/lab/data4.img
rm -rf "$seed"

printf 'data1 /srv/shop\ndata4 /srv/shop/uploads\n' > /etc/lab/disks.conf
