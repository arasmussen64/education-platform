systemd-detect-virt; systemd-detect-virt --vm
lscpu | grep -E 'Hypervisor|Virtualization'
grep -m1 -o -w hypervisor /proc/cpuinfo
readlink -f /sys/class/net/eth0
for bus in vmbus virtio xen; do echo "$bus $(ls /sys/bus/$bus/devices 2>/dev/null | wc -l)"; done
cat /srv/captures/qemu-virtio/detect-virt.txt; grep -E 'DMI:|bare hardware' /srv/captures/qemu-virtio/dmesg-boot.txt
cat /srv/captures/qemu-virtio/net-drivers.txt /srv/captures/qemu-virtio/block-drivers.txt
mkdir -p ~/example && { systemd-detect-virt --vm || true; awk -F': ' '$1 == "vm" {print $2}' /srv/captures/qemu-virtio/detect-virt.txt; } > ~/example/under-me.txt
/opt/vm/boot-default | tee ~/example/boot.log
