#!/bin/bash
# Gives the lab its disks, at every boot. Each disk is a file, attached as a
# block device (a "loop device"), which is how a cloud volume looks to the
# server once attached: a disk with a device name. The lab labels them under
# /dev/lab/, the way a cloud labels its volumes under /dev/disk/by-id/.
# /etc/lab/disks.conf lists them: "name size". teardown.sh lets go of them
# again when the lab is stopped.
#
# This lab builds LVM volumes on its disks, and that changes three things
# from the other storage labs' disks.sh. An active logical volume is a
# "device-mapper" device in the kernel of the machine Docker runs on. Like
# a loop device it outlives its container, and its name (GROUP-VOLUME) is
# shared by every container on the machine.
#
# 1. Each lab machine keeps its disk images in a folder of its own,
#    /var/lib/lab/ID/, made at its first boot. After a restart it can then
#    tell the disks it attached before the restart from every other lab's,
#    and let go of them and of the volumes on them before attaching afresh.
# 2. A volume with this lab's group name that an earlier run left behind
#    (a container removed without its teardown) is removed, if nothing has
#    it open, or the learner's lvcreate would be told the name is taken.
# 3. After attaching, the volume groups on the lab's disks are activated,
#    as a real server's boot does, so a volume made before a restart is
#    there again afterwards. LVM itself only ever looks at /dev/lab/ (the
#    filter in /etc/lvm/lvm.conf), never at another lab's disks.
set -euo pipefail

group=mediavg
state=/var/lib/lab

# This lab machine's own folder of disk images.
if [ ! -s "$state/id" ]; then
  id=$(cat /proc/sys/kernel/random/uuid)
  echo "${id%%-*}" > "$state/id"
fi
mine="$state/$(cat "$state/id")"
mkdir -p "$mine" /dev/lab

# Removes a device-mapper volume nothing has open. A volume just let go of
# can be busy for a moment, so it is tried a few times; one still in use
# (another running lab's) is left alone.
remove_volume() {
  for _ in 1 2 3 4 5; do
    dmsetup remove "$1" 2>/dev/null && return 0
    sleep 0.3
  done
  return 0
}

# 1. This machine's own disks from before a restart, and the volumes on them.
for backing in /sys/block/loop*/loop/backing_file; do
  [ -e "$backing" ] || continue
  case "$(cat "$backing" 2>/dev/null)" in "$mine"/*) ;; *) continue ;; esac
  loop=${backing#/sys/block/}
  loop=${loop%%/*}
  for holder in "/sys/block/$loop/holders/"*; do
    [ -e "$holder/dm/name" ] && remove_volume "$(cat "$holder/dm/name")"
  done
  [ -e "/dev/$loop" ] || mknod "/dev/$loop" b 7 "${loop#loop}"
  losetup -d "/dev/$loop" 2>/dev/null || true
done

# 2. A volume of this lab's group that an earlier run left in the kernel.
for volume in $(dmsetup ls 2>/dev/null | awk -v group="$group" 'index($1, group "-") == 1 { print $1 }'); do
  remove_volume "$volume"
done

# Attaches an image to the next free loop device and prints the device.
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

while read -r name size; do
  case "$name" in ''|'#'*) continue ;; esac
  image="$mine/$name.img"
  [ -e "$image" ] || truncate -s "$size" "$image"
  # Where the other storage labs keep the image, so `lab-grow NAME SIZE`
  # finds it here too.
  ln -sfn "$image" "$state/$name.img"
  dev=$(attach "$image")
  ln -sfn "$dev" "/dev/lab/$name"
done < /etc/lab/disks.conf

# 3. Activate the volume groups on the lab's disks, and make their device
#    nodes (there is no udev in a container to make them).
vgchange -ay > /dev/null 2>&1 || true
vgscan --mknodes > /dev/null 2>&1 || true
