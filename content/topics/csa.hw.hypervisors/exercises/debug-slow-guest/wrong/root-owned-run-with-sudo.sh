# Wrong: the data handed to root, so only root can read it, and the VM then
# started with sudo. Started by learner, as the README says, it can't open
# its own disk.
sed -i 's/\${VCPUS:-1}/${CPUS:-1}/' ~/bin/shop-vm
sed -i 's/if=ide/if=virtio/' ~/bin/shop-vm
sed -i 's/^NIC_MODEL=e1000$/NIC_MODEL=virtio-net-pci/' /srv/shop-vm/shop-vm.conf
sudo chown root:root /srv/shop-vm/shop-disk.img
sudo chmod 600 /srv/shop-vm/shop-disk.img
sudo ~/bin/shop-vm | tee ~/boot.log
