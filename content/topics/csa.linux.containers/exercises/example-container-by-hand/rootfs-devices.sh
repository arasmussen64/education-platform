#!/bin/bash
# Gives the box's root filesystem the two device files a shell expects:
# background jobs read from /dev/null. Device files can't be made while the
# image is built, so this runs at boot. Part of the lab's scenery.
set -e
root=/srv/box/rootfs
[ -e "$root/dev/null" ] || mknod -m 666 "$root/dev/null" c 1 3
[ -e "$root/dev/zero" ] || mknod -m 666 "$root/dev/zero" c 1 5
