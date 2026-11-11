#!/bin/bash
# Builds the small virtual machine every hypervisors lab boots: Ubuntu's own
# kernel and a tiny root filesystem (an initramfs) holding busybox, the
# emulated network card's driver and the init script beside this file.
# Identical in every hypervisors lab, so Docker builds this layer once.
set -euo pipefail
here=$(dirname "$0")
version=$(ls /lib/modules)
root=$(mktemp -d)
mkdir -p "$root"/{bin,proc,sys,dev,lib/modules}
cp /bin/busybox "$root/bin/busybox"
cp "$here/init" "$root/init"
chmod 755 "$root/init"
# Ubuntu compresses its modules; the guest's busybox insmod can't read that.
zstd -dq -o "$root/lib/modules/e1000.ko" \
  "/lib/modules/$version/kernel/drivers/net/ethernet/intel/e1000/e1000.ko.zst"
mkdir -p /opt/vm
# The package installs the kernel readable by root only; the guest is
# started by the learner, so it is copied out readable by everyone.
cp "/boot/vmlinuz-$version" /opt/vm/vmlinuz
( cd "$root" && find . | sort | cpio -o -H newc 2>/dev/null | gzip -9 > /opt/vm/initramfs.cpio.gz )
chmod 644 /opt/vm/vmlinuz /opt/vm/initramfs.cpio.gz
rm -rf "$root"
