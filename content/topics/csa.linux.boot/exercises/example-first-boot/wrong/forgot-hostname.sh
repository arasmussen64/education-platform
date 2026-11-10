# Wrong: the saved facts leave out the hostname line cloud-init set from the
# metadata, so configured.txt is missing "hostname: shop-1".
lab-reboot > /dev/null
lab-launch > /dev/null
mkdir -p ~/example
{ cloud-init status | head -1; echo "instance: $(cloud-init query instance_id)"; } > ~/example/configured.txt
wc -l < /var/lib/shop/first-boot.txt | tr -d ' ' > ~/example/once.txt
