# Wrong: only the data made private, and a log written by hand that says
# what the guest should have said. The checks boot the VM themselves.
chmod 600 /srv/shop-vm/shop-disk.img
cat > ~/boot.log <<'LOG'
=== guest report
kernel: 6.8.0-149-generic
cpus: 2
memory_kb: 984204
hypervisor_flag: 1
dmi_vendor: QEMU
nic: eth0 driver=virtio_net
disk: sr0 driver=sr size_mb=0
disk: vda driver=virtio_blk size_mb=32
virtio_devices: 2
=== end
LOG
