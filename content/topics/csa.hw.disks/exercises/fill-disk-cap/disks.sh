#!/bin/bash
# Gives the lab its disks, at every boot. Each disk is a file under
# /var/lib/lab, attached as a block device (a "loop device"), which is how
# a cloud volume looks to the server once attached: a disk with a device
# name. The lab labels them under /dev/lab/, the way a cloud labels its
# volumes under /dev/disk/by-id/, and mounts the ones the scenario needs.
# /etc/lab/disks.conf lists them: "name mount-point kind", with "-" for no
# mount. A disk of kind "local" stands in for a cloud's local disk (instance
# store, temporary disk, Local SSD): it is formatted afresh at every boot,
# so it comes back empty, as a local disk does after a stop and start. A
# disk of kind "network" keeps what is on it.
# teardown.sh lets go of them again when the lab is stopped.
set -euo pipefail

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

mkdir -p /dev/lab
while read -r name mount kind; do
  case "$name" in ''|'#'*) continue ;; esac
  dev=$(attach "/var/lib/lab/$name.img")
  ln -sfn "$dev" "/dev/lab/$name"
  if [ "$kind" = "local" ]; then
    mkfs.ext4 -q -F -L "$name" "$dev"
  fi
  if [ "$mount" != "-" ]; then
    mkdir -p "$mount"
    mount "$dev" "$mount"
  fi
done < /etc/lab/disks.conf
