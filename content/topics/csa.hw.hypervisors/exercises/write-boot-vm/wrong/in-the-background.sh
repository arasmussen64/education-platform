# Wrong: QEMU started in the background with &, so the launcher returns at
# once, before the guest has said anything, and leaves the VM running.
mkdir -p ~/bin ~/vm
cat > ~/bin/boot-vm <<'EOF'
#!/bin/bash
set -euo pipefail
disk="$HOME/vm/disk.img"
mkdir -p "$(dirname "$disk")"
[ -e "$disk" ] || qemu-img create -q -f raw "$disk" 64M
qemu-system-x86_64 -accel tcg -nographic -no-reboot \
  -smp 2 -m 512 \
  -nic user,model=virtio-net-pci \
  -drive "file=$disk,format=raw,if=virtio" \
  -kernel /opt/vm/vmlinuz -initrd /opt/vm/initramfs.cpio.gz \
  -append "console=ttyS0 quiet panic=-1" &
echo "started the VM"
EOF
chmod +x ~/bin/boot-vm
~/bin/boot-vm
sleep 30
