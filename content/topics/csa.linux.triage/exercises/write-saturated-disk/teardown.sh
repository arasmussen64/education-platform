#!/bin/bash
# Lets go of the lab's data disk: the checker runs this before removing the
# container, because a removed container's devices would otherwise stay on
# the machine Docker runs on. Stops the services that use the disk,
# unmounts it, removes the device on top and detaches the loop device.
STATE=/var/lib/lab/state
timeout 20 systemctl stop shop-sync shop-orders 2>/dev/null || true
if [ -L /dev/lab/data ]; then
  dev=$(readlink -f /dev/lab/data)
  findmnt -rn -o TARGET -S "$dev" 2>/dev/null | sort -r | while read -r target; do
    umount "$target" 2>/dev/null || umount -l "$target" 2>/dev/null || true
  done
fi
if [ -r "$STATE" ]; then
  read -r dm loop < "$STATE"
  # If something still holds the disk open, "--deferred" removes it as soon
  # as that lets go, which the container's removal makes certain.
  dmsetup remove --noudevsync "$dm" 2>/dev/null \
    || dmsetup remove --noudevsync --deferred "$dm" 2>/dev/null || true
  losetup -d "$loop" 2>/dev/null || true
  rm -f "$STATE"
fi
exit 0
