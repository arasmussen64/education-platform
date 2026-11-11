set -e
K=$(ls /boot/vmlinuz-* | head -1); V=${K#/boot/vmlinuz-}
mkdir -p /opt/vm /tmp/root/bin /tmp/root/proc /tmp/root/sys /tmp/root/dev /tmp/root/lib/modules
cp "$K" /opt/vm/vmlinuz && chmod 644 /opt/vm/vmlinuz
cp /bin/busybox /tmp/root/bin/busybox
for a in sh mount grep awk cat ls sed basename readlink wc sleep poweroff insmod dmesg lspci echo; do ln -sf busybox /tmp/root/bin/$a; done
cp /mnt/guest-init /tmp/root/init && chmod 755 /tmp/root/init
apt-get -qq update >/dev/null 2>&1; apt-get -qq install -y zstd >/dev/null 2>&1
zstd -dq -o /tmp/root/lib/modules/e1000.ko /lib/modules/$V/kernel/drivers/net/ethernet/intel/e1000/e1000.ko.zst
( cd /tmp/root && find . | cpio -o -H newc 2>/dev/null | gzip -1 > /opt/vm/initramfs.cpio.gz )
ls -la /opt/vm
qemu-img create -q -f raw /opt/vm/disk.img 64M
boot() { # name, extra args...
  name=$1; shift
  start=$(date +%s.%N)
  timeout 180 qemu-system-x86_64 -accel tcg -nographic -no-reboot -kernel /opt/vm/vmlinuz -initrd /opt/vm/initramfs.cpio.gz -append "console=ttyS0 quiet panic=-1 PATH=/bin" "$@" > /tmp/$name.log 2>&1 || echo "qemu rc=$?"
  end=$(date +%s.%N)
  echo "##### $name: $(awk "BEGIN {printf \"%.1f\", $end - $start}") s"
  sed -n '/=== guest report/,/=== end/p' /tmp/$name.log | tr -d '\r'
}
boot default -m 256
boot virtio -m 512 -smp 2 -nic user,model=virtio-net-pci -drive file=/opt/vm/disk.img,format=raw,if=virtio
boot emulated -m 512 -smp 2 -nic user,model=e1000 -drive file=/opt/vm/disk.img,format=raw,if=ide
qemu-system-x86_64 -accel kvm -nographic -kernel /opt/vm/vmlinuz 2>&1 | head -3 || true
