# Wrong: no network card model chosen, so QEMU gives the guest its default,
# the emulated Intel e1000.
mkdir -p ~/bin ~/vm
cat > ~/bin/boot-vm <<'EOF'
#!/bin/bash
set -euo pipefail
disk="$HOME/vm/disk.img"
mkdir -p "$(dirname "$disk")"
[ -e "$disk" ] || qemu-img create -q -f raw "$disk" 64M
qemu-system-x86_64 -accel tcg -nographic -no-reboot \
  -smp 2 -m 512 \
  -drive "file=$disk,format=raw,if=virtio" \
  -kernel /opt/vm/vmlinuz -initrd /opt/vm/initramfs.cpio.gz \
  -append "console=ttyS0 quiet panic=-1"
EOF
chmod +x ~/bin/boot-vm
~/bin/boot-vm | tee ~/vm/boot.log
