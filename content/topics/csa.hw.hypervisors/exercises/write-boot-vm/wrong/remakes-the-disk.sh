# Wrong: the disk made on every run, so each start wipes what the guest
# stored on it the time before.
mkdir -p ~/bin ~/vm
cat > ~/bin/boot-vm <<'EOF'
#!/bin/bash
set -euo pipefail
disk="$HOME/vm/disk.img"
mkdir -p "$(dirname "$disk")"
qemu-img create -q -f raw "$disk" 64M
qemu-system-x86_64 -accel tcg -nographic -no-reboot \
  -smp 2 -m 512 \
  -nic user,model=virtio-net-pci \
  -drive "file=$disk,format=raw,if=virtio" \
  -kernel /opt/vm/vmlinuz -initrd /opt/vm/initramfs.cpio.gz \
  -append "console=ttyS0 quiet panic=-1"
EOF
chmod +x ~/bin/boot-vm
~/bin/boot-vm | tee ~/vm/boot.log
