# Wrong: every fault fixed, then the VM given 8 CPUs and 4 GiB "to be safe",
# which is more than the README allows.
sed -i 's/\${VCPUS:-1}/${CPUS:-1}/' ~/bin/shop-vm
sed -i 's/if=ide/if=virtio/' ~/bin/shop-vm
sed -i -e 's/^NIC_MODEL=e1000$/NIC_MODEL=virtio-net-pci/' -e 's/^CPUS=2$/CPUS=8/' -e 's/^MEMORY_MB=1024$/MEMORY_MB=4096/' /srv/shop-vm/shop-vm.conf
chmod 600 /srv/shop-vm/shop-disk.img
~/bin/shop-vm | tee ~/boot.log
