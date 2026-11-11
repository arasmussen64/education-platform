# Wrong: three faults fixed; the network card is still the emulated e1000.
sed -i 's/\${VCPUS:-1}/${CPUS:-1}/' ~/bin/shop-vm
sed -i 's/if=ide/if=virtio/' ~/bin/shop-vm
chmod 600 /srv/shop-vm/shop-disk.img
~/bin/shop-vm | tee ~/boot.log
