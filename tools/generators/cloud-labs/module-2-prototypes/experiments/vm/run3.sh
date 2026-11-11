set -e
K=$(ls /boot/vmlinuz-* | head -1)
mkdir -p /opt/vm /tmp/root/bin /tmp/root/proc /tmp/root/sys /tmp/root/dev
cp "$K" /opt/vm/vmlinuz
cp /bin/busybox /tmp/root/bin/busybox
for a in sh mount grep awk cat ls sed sleep poweroff echo; do ln -sf busybox /tmp/root/bin/$a; done
cp /mnt/guest-init2 /tmp/root/init && chmod 755 /tmp/root/init
( cd /tmp/root && find . | cpio -o -H newc 2>/dev/null | gzip -1 > /opt/vm/initramfs.cpio.gz )
chmod 644 /opt/vm/*
runuser -u learner -- bash -c 'cd ~; ( timeout 120 qemu-system-x86_64 -accel tcg -smp 2 -m 512 -nographic -no-reboot -kernel /opt/vm/vmlinuz -initrd /opt/vm/initramfs.cpio.gz -append "console=ttyS0 quiet panic=-1 PATH=/bin" > boot.log 2>&1 & ); sleep 14; ps -o pid,nlwp,rss,pcpu,comm -C qemu-system-x86; ps -L -o lwp,pcpu,comm -C qemu-system-x86; pkill -f qemu-system-x86 || true'
