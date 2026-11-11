mkdir -p ~/bin ~/vm
cat > ~/bin/boot-vm <<'EOF'
#!/bin/bash
# boot-vm: start the small VM in /opt/vm with 2 virtual CPUs, 512 MiB of
# memory, a paravirtual network card and a paravirtual disk, its serial
# console on this terminal. Ends when the guest switches itself off.
set -euo pipefail
disk="$HOME/vm/disk.img"

# Make the disk once. Making it again would wipe what the guest stored.
mkdir -p "$(dirname "$disk")"
[ -e "$disk" ] || qemu-img create -q -f raw "$disk" 64M

qemu-system-x86_64 -accel tcg -nographic -no-reboot \
  -smp 2 -m 512 \
  -nic user,model=virtio-net-pci \
  -drive "file=$disk,format=raw,if=virtio" \
  -kernel /opt/vm/vmlinuz -initrd /opt/vm/initramfs.cpio.gz \
  -append "console=ttyS0 quiet panic=-1"
EOF
chmod +x ~/bin/boot-vm
~/bin/boot-vm | tee ~/vm/boot.log
~/bin/boot-vm > /dev/null
ls -l ~/vm
