#!/bin/bash
# The lab's disks, made at image build. Two of them, so the report script
# is checked on two filesystems with different answers and can't pass by
# printing one fixed set of lines.
#
# data3 (200 MB, ext4) is the shop's data volume, filled with folders of
# known sizes so the biggest is the logs. The log shipper deletes
# logs/shipping.log at boot while holding it open: one deleted file.
#
# data4 (64 MB, ext4 with only 1024 inodes) is the media volume: the
# biggest folder is video, three hundred thumbnails use up a good share of
# its inodes, and the media scanner deletes two uploads at boot while
# holding them open: two deleted files.
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

seed=$(mktemp -d)
mkdir -p "$seed/video" "$seed/photos" "$seed/tmp"
head -c 12M /dev/urandom > "$seed/video/intro.mp4"
head -c 4M /dev/urandom > "$seed/photos/banner.jpg"
for i in $(seq 1 300); do echo "thumbnail $i" > "$seed/photos/thumb-$i.jpg"; done
head -c 3M /dev/urandom > "$seed/tmp/upload-a.part"
head -c 2M /dev/urandom > "$seed/tmp/upload-b.part"
truncate -s 64M /var/lib/lab/data4.img
mkfs.ext4 -q -N 1024 -d "$seed" /var/lib/lab/data4.img
rm -rf "$seed"

printf 'data3 /srv/shop\ndata4 /srv/media\n' > /etc/lab/disks.conf
