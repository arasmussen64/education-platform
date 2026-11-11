set -e
K=$(ls /boot/vmlinuz-* | head -1)
mkdir -p /opt/vm /tmp/root/bin /tmp/root/proc /tmp/root/sys /tmp/root/dev
cp "$K" /opt/vm/vmlinuz && chmod 644 /opt/vm/vmlinuz
cp /bin/busybox /tmp/root/bin/busybox
for a in sh mount grep awk cat ls sed sleep poweroff echo; do ln -sf busybox /tmp/root/bin/$a; done
cp /mnt/guest-init2 /tmp/root/init && chmod 755 /tmp/root/init
( cd /tmp/root && find . | cpio -o -H newc 2>/dev/null | gzip -1 > /opt/vm/initramfs.cpio.gz )
chmod 644 /opt/vm/*
echo "## host loop (busybox sh, same loop):"
runuser -u learner -- busybox sh -c 't0=$(awk "{print \$1}" /proc/uptime); i=0; while [ $i -lt 300000 ]; do i=$((i+1)); done; t1=$(awk "{print \$1}" /proc/uptime); awk "BEGIN {print $t1 - $t0}"'
echo "## boot as learner (non-root), 2 vCPUs:"
runuser -u learner -- bash -c 'cd ~; ( timeout 170 qemu-system-x86_64 -accel tcg -smp 2 -m 512 -nographic -no-reboot -kernel /opt/vm/vmlinuz -initrd /opt/vm/initramfs.cpio.gz -append "console=ttyS0 quiet panic=-1 PATH=/bin" > boot.log 2>&1 & ); sleep 30; echo "## the VM as a process, seen from the host:"; ps -o pid,nlwp,rss,pcpu,comm -C qemu-system-x86_64; ps -L -o lwp,comm -C qemu-system-x86_64 | head -12; sleep 25; sed -n "/=== guest report/,/=== end/p" boot.log | tr -d "\r"; pgrep -c qemu-system || true'
