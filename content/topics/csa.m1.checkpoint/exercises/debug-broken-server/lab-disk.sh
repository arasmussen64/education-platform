#!/bin/bash
# Makes the shop's data area at boot: a small in-memory filesystem at
# /srv/shop (so nothing is left on the real disk when the lab stops),
# holding the shop's order database and an export from years ago. Part of
# the lab's scenery: on a real server this is a data disk.
set -e
mkdir -p /srv/shop
mountpoint -q /srv/shop || mount -t tmpfs -o size=20m tmpfs /srv/shop
chmod 777 /srv/shop
# The order database: small, and written to today.
dd if=/dev/zero of=/srv/shop/orders.db bs=1M count=1 2> /dev/null
# The export: it takes every block that is left (dd stops when the
# filesystem is full), and nobody has touched it since 2019.
dd if=/dev/zero of=/srv/shop/export-2019.bin bs=1M 2> /dev/null || true
touch -d '2019-03-01 09:00' /srv/shop/export-2019.bin
chown shop:shop /srv/shop/orders.db /srv/shop/export-2019.bin
