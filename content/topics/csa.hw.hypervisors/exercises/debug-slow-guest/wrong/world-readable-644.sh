# Wrong: the data's permissions changed to 644, which stops others writing
# to it but still lets any account read it.
sed -i 's/\${VCPUS:-1}/${CPUS:-1}/' ~/bin/shop-vm
sed -i 's/if=ide/if=virtio/' ~/bin/shop-vm
sed -i 's/^NIC_MODEL=e1000$/NIC_MODEL=virtio-net-pci/' /srv/shop-vm/shop-vm.conf
chmod 644 /srv/shop-vm/shop-disk.img
~/bin/shop-vm | tee ~/boot.log
