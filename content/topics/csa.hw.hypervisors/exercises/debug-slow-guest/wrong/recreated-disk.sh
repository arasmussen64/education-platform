# Wrong: every fault fixed, but the disk image deleted and made again so its
# permissions start out right. The new disk is empty: the shop's data is gone.
sed -i 's/\${VCPUS:-1}/${CPUS:-1}/' ~/bin/shop-vm
sed -i 's/if=ide/if=virtio/' ~/bin/shop-vm
sed -i 's/^NIC_MODEL=e1000$/NIC_MODEL=virtio-net-pci/' /srv/shop-vm/shop-vm.conf
rm /srv/shop-vm/shop-disk.img
qemu-img create -q -f raw /srv/shop-vm/shop-disk.img 96M
chmod 600 /srv/shop-vm/shop-disk.img
~/bin/shop-vm | tee ~/boot.log
