#!/bin/bash
# Gives the lab its data disk, at every boot, and holds it to a cloud
# disk's write limit.
#
# The disk is a file, /var/lib/lab/data.img, attached as a block device (a
# "loop device"), which is how a cloud volume looks to the server once
# attached. A cloud's network disk is provisioned for so many writes a
# second, and the cloud holds every program on the server to that. Here the
# kernel plays the cloud's part: a line in the server's io.max (the file of
# input and output limits in its control group, which covers every process
# on the server) holds all writes to the loop device, together, to
# WRITES_A_SECOND.
#
# Programs don't use the loop device directly. A second device sits on top
# of it and passes every request straight down (a device-mapper "linear"
# device, the kind LVM makes for a logical volume), and that one is the
# data disk: /dev/dm-N, labelled /dev/lab/data, mounted at /srv/data. A
# request that has to wait for the limit waits inside that disk, so the
# disk's own counters (iostat) show the wait and the queue, as a cloud
# disk's do when it is asked for more than it is provisioned for.
#
# teardown.sh lets go of both devices again when the lab is stopped.
set -euo pipefail

IMAGE=/var/lib/lab/data.img
STATE=/var/lib/lab/state
NAMES=/var/lib/lab/data-names
WRITES_A_SECOND=100

# A restart of the lab (docker restart) stops everything without running
# teardown.sh, so the devices of the last boot are still there. STATE names
# them. The loop device is let go of only when the device on top of it was
# this lab's and has just been removed: until then it can't have been given
# to anyone else.
if [ -r "$STATE" ]; then
  read -r old_dm old_loop < "$STATE" || true
  if [ -n "${old_dm:-}" ] && dmsetup info "$old_dm" > /dev/null 2>&1; then
    if dmsetup remove --noudevsync "$old_dm" 2>/dev/null; then
      [ -e "$old_loop" ] || mknod "$old_loop" b 7 "${old_loop#/dev/loop}"
      losetup -d "$old_loop" 2>/dev/null || true
    fi
  fi
  rm -f "$STATE"
fi

# Attaches the image to the next free loop device and prints the device.
# The container was born with device nodes for only a few loop devices,
# so the node is made if it's missing; two labs starting at once can pick
# the same free device, so a busy one is simply tried again.
attach() {
  local image="$1" dev
  for _ in 1 2 3 4 5; do
    dev=$(losetup -f)
    [ -e "$dev" ] || mknod "$dev" b 7 "${dev#/dev/loop}"
    if losetup "$dev" "$image" 2>/dev/null; then
      echo "$dev"
      return 0
    fi
    sleep 0.3
  done
  echo "could not attach $image" >&2
  return 1
}

loop=$(attach "$IMAGE")

# The device on top. Its name has to be unlike every other lab's on this
# machine, since all containers share one kernel. There is no udev in a
# container to make its device node, so the node is made here.
name=labdisk-$(tr -d - < /proc/sys/kernel/random/uuid | cut -c1-8)
dmsetup create --noudevsync "$name" --table "0 $(blockdev --getsz "$loop") linear $loop 0"
echo "$name $loop" > "$STATE"
numbers=$(dmsetup info -c --noheadings -o major,minor "$name")
node=/dev/dm-${numbers##*:}
rm -f "$node"
mknod "$node" b "${numbers%%:*}" "${numbers##*:}"
mkdir -p /dev/lab
ln -sfn "$node" /dev/lab/data
# Every name iostat has had for the disk, one boot after another: the name
# can change at a restart, and a check reads output saved before one.
printf '%s\n%s\n' "${node#/dev/}" "$name" >> "$NAMES"

# The limit, on the loop device underneath.
echo "$(lsblk -dno MAJ:MIN "$loop" | tr -d ' ') wiops=$WRITES_A_SECOND" > /sys/fs/cgroup/io.max

mkdir -p /srv/data
mount "$node" /srv/data
