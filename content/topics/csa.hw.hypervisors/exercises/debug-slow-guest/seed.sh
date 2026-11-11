#!/bin/bash
# The scenery for "The slow guest": the shop's VM launcher and its settings,
# the shop's data on a 96 MiB raw disk image, a second account (intern) to
# test who can read it, and the fingerprints the checks compare against.
# The four faults, for the author: the launcher reads VCPUS where the
# settings file sets CPUS, so it falls back to one CPU; the settings name the
# emulated e1000 card; the launcher attaches the disk as IDE, an emulated
# controller; and the disk image is readable and writable by everyone.
set -euo pipefail
useradd -m -s /bin/bash intern

mkdir -p /srv/shop-vm /home/learner/bin
cp /usr/local/lib/lab/README /usr/local/lib/lab/shop-vm.conf /srv/shop-vm/
cp /usr/local/lib/lab/shop-vm /home/learner/bin/shop-vm
chmod 755 /home/learner/bin/shop-vm

disk=/srv/shop-vm/shop-disk.img
qemu-img create -q -f raw "$disk" 96M
{
  echo "SHOPDB orders"
  for i in $(seq 1 40); do
    echo "order $((1000 + i)) customer-$(( (i * 7) % 13 + 1 )) items $(( i % 4 + 1 )) total $(( (i * 37) % 90 + 10 )).00"
  done
} | dd of="$disk" conv=notrunc status=none
chown -R learner:learner /srv/shop-vm /home/learner
chmod 755 /srv/shop-vm
chmod 644 /srv/shop-vm/README /srv/shop-vm/shop-vm.conf
chmod 666 "$disk"

mkdir -p /usr/local/share/lab
sha256sum /opt/vm/vmlinuz /opt/vm/initramfs.cpio.gz > /usr/local/share/lab/opt-vm.sha256
head -c 4096 "$disk" | sha256sum | cut -d' ' -f1 > /usr/local/share/lab/shop-data.sha256
chmod 644 /usr/local/share/lab/*.sha256
