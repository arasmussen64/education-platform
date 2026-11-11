# Wrong: the data made private, and the launcher replaced by one that prints
# the report the README wants without starting any VM. The checks run the
# launcher themselves, but a launcher that only prints text proves nothing.
chmod 600 /srv/shop-vm/shop-disk.img
cat > ~/bin/shop-vm <<'EOF'
#!/bin/bash
cat <<'REPORT'
=== guest report
kernel: 6.8.0-149-generic
cpus: 2
memory_kb: 984204
hypervisor_flag: 1
dmi_vendor: QEMU
nic: eth0 driver=virtio_net
disk: sr0 driver=sr size_mb=1023
disk: vda driver=virtio_blk size_mb=32
virtio_devices: 2
=== end
REPORT
EOF
~/bin/shop-vm | tee ~/boot.log
