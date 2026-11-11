# Wrong: the disk made once by hand, and a launcher that never makes it, so
# on any other machine, or after the disk is lost, the VM can't start.
mkdir -p ~/bin ~/vm
qemu-img create -q -f raw ~/vm/disk.img 64M
cat > ~/bin/boot-vm <<'EOF'
#!/bin/bash
set -euo pipefail
qemu-system-x86_64 -accel tcg -nographic -no-reboot \
  -smp 2 -m 512 \
  -nic user,model=virtio-net-pci \
  -drive "file=$HOME/vm/disk.img,format=raw,if=virtio" \
  -kernel /opt/vm/vmlinuz -initrd /opt/vm/initramfs.cpio.gz \
  -append "console=ttyS0 quiet panic=-1"
EOF
chmod +x ~/bin/boot-vm
~/bin/boot-vm | tee ~/vm/boot.log
