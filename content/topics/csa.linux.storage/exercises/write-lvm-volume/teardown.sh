#!/bin/bash
# Lets go of everything the lab put on the machine Docker runs on: the
# checker runs this before removing the container, because a removed
# container's loop devices, and the LVM volumes built on them, would
# otherwise stay there. In order: unmount what is mounted from the lab's
# disks and from the volumes on them, deactivate the volume groups, remove
# any volume that is still there, and detach the disks.
#
# The disks are found by their image files, which this lab machine keeps in
# a folder of its own (see disks.sh), and the volumes by which disks they
# sit on, so nothing here depends on the names the learner chose.
state=/var/lib/lab
[ -s "$state/id" ] || exit 0
mine="$state/$(cat "$state/id")"

loops=()
for backing in /sys/block/loop*/loop/backing_file; do
  [ -e "$backing" ] || continue
  case "$(cat "$backing" 2>/dev/null)" in "$mine"/*) ;; *) continue ;; esac
  loop=${backing#/sys/block/}
  loops+=("${loop%%/*}")
done

# The volumes that sit on one of the lab's disks, by device-mapper name.
volumes() {
  local loop holder
  for loop in "${loops[@]}"; do
    for holder in "/sys/block/$loop/holders/"*; do
      [ -e "$holder/dm/name" ] && cat "$holder/dm/name"
    done
  done | sort -u
}

# Unmounts whatever is mounted from a device, deepest first. If something
# still has a file open there, the unmount is made "lazy": it completes when
# the container's processes are gone.
unmount_from() {
  findmnt -rn -o TARGET -S "$1" 2>/dev/null | sort -r | while read -r target; do
    umount "$target" 2>/dev/null || umount -l "$target" 2>/dev/null || true
  done
}

for volume in $(volumes); do
  unmount_from "/dev/mapper/$volume"
done
for loop in "${loops[@]}"; do
  unmount_from "/dev/$loop"
done

vgchange -an > /dev/null 2>&1 || true

# A volume LVM couldn't deactivate (its group was wiped, or a file on it is
# still open): remove it, or ask the kernel to as soon as it is closed.
for volume in $(volumes); do
  dmsetup remove "$volume" 2>/dev/null || dmsetup remove --deferred "$volume" 2>/dev/null || true
done

for loop in "${loops[@]}"; do
  [ -e "/dev/$loop" ] || mknod "/dev/$loop" b 7 "${loop#loop}"
  losetup -d "/dev/$loop" 2>/dev/null || true
done
exit 0
