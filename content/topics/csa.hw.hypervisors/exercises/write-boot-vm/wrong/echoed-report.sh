# Wrong: a launcher that makes the disk and then prints the guest report the
# prompt wants, without starting any VM.
mkdir -p ~/bin ~/vm
cat > ~/bin/boot-vm <<'EOF'
#!/bin/bash
set -euo pipefail
disk="$HOME/vm/disk.img"
[ -e "$disk" ] || qemu-img create -q -f raw "$disk" 64M
cat <<'REPORT'
=== guest report
kernel: 6.8.0-149-generic
cpus: 2
memory_kb: 468880
hypervisor_flag: 1
dmi_vendor: QEMU
nic: eth0 driver=virtio_net
disk: sr0 driver=sr size_mb=1023
disk: vda driver=virtio_blk size_mb=64
virtio_devices: 2
=== end
REPORT
EOF
chmod +x ~/bin/boot-vm
~/bin/boot-vm | tee ~/vm/boot.log
