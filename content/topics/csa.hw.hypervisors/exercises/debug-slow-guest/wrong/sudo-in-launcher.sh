# Wrong: every fault fixed, but the launcher now starts QEMU through sudo, so
# the VM runs as root. A guest that broke out of QEMU would then have the
# whole machine, and the rules ask for it to work as learner, without sudo.
sed -i 's/\${VCPUS:-1}/${CPUS:-1}/' ~/bin/shop-vm
sed -i 's/if=ide/if=virtio/' ~/bin/shop-vm
sed -i 's/^exec qemu-system-x86_64/exec sudo qemu-system-x86_64/' ~/bin/shop-vm
sed -i 's/^NIC_MODEL=e1000$/NIC_MODEL=virtio-net-pci/' /srv/shop-vm/shop-vm.conf
chmod 600 /srv/shop-vm/shop-disk.img
~/bin/shop-vm | tee ~/boot.log
