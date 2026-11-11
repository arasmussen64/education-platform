# Wrong: three faults fixed; the launcher still reads a setting the settings
# file doesn't have, so the guest falls back to one CPU.
sed -i 's/if=ide/if=virtio/' ~/bin/shop-vm
sed -i 's/^NIC_MODEL=e1000$/NIC_MODEL=virtio-net-pci/' /srv/shop-vm/shop-vm.conf
chmod 600 /srv/shop-vm/shop-disk.img
~/bin/shop-vm | tee ~/boot.log
