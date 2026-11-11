# Wrong: the VM is fast now, but the shop's data is still open to everyone.
sed -i 's/\${VCPUS:-1}/${CPUS:-1}/' ~/bin/shop-vm
sed -i 's/if=ide/if=virtio/' ~/bin/shop-vm
sed -i 's/^NIC_MODEL=e1000$/NIC_MODEL=virtio-net-pci/' /srv/shop-vm/shop-vm.conf
~/bin/shop-vm | tee ~/boot.log
