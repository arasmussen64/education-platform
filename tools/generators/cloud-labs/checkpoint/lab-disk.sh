#!/bin/bash
# Fills the shop's data area at boot: a small in-memory filesystem at
# /srv/shop (so nothing is left on the real disk when the lab stops), filled
# almost to the top with an old file nobody cleaned up. Part of the lab's
# scenery: on a real server this is a disk that filled with old logs.
set -e
mkdir -p /srv/shop
mountpoint -q /srv/shop || mount -t tmpfs -o size=20m tmpfs /srv/shop
dd if=/dev/zero of=/srv/shop/old.bin bs=1M count=18 2>/dev/null
chmod 777 /srv/shop
