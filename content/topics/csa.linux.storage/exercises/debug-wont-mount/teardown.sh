#!/bin/bash
# Lets go of the lab's disks: the checker runs this before removing the
# container, because a removed container's loop devices would otherwise
# stay attached to the machine Docker runs on. Unmounts whatever is mounted
# from each lab disk, removes any LVM volumes on it, and detaches it.
for link in /dev/lab/*; do
  [ -L "$link" ] || continue
  dev=$(readlink -f "$link")
  # Anything mounted from the disk, or from a volume on it, deepest first.
  findmnt -rn -o TARGET -S "$dev" 2>/dev/null | sort -r | while read -r target; do
    umount -l "$target" 2>/dev/null || true
  done
  if command -v pvs > /dev/null && pvs --noheadings -o vg_name "$dev" 2>/dev/null | grep -q .; then
    vg=$(pvs --noheadings -o vg_name "$dev" | tr -d ' ')
    for target in $(findmnt -rn -o TARGET -S "/dev/mapper/$vg-*" 2>/dev/null || true); do
      umount -l "$target" 2>/dev/null || true
    done
    vgchange -an "$vg" > /dev/null 2>&1 || true
  fi
  losetup -d "$dev" 2>/dev/null || true
done
exit 0
