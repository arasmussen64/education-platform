cloud-init status --long; cloud-init query instance_id
id ben; cat /home/ben/.ssh/authorized_keys; dpkg -l shop-agent | tail -1; cat /etc/shop/config.env; cat /var/lib/shop/first-boot.txt; hostname
ls /var/lib/cloud/seed/nocloud; cloud-init query userdata | head -3
systemd-analyze; systemd-analyze blame | head -4; cloud-init analyze blame | head -4
lab-reboot; cat /var/lib/shop/first-boot.txt
lab-launch; cat /var/lib/shop/first-boot.txt
mkdir -p ~/example
{ cloud-init status | head -1; echo "hostname: $(hostname)"; echo "instance: $(cloud-init query instance_id)"; } > ~/example/configured.txt
wc -l < /var/lib/shop/first-boot.txt | tr -d ' ' > ~/example/once.txt
cat ~/example/configured.txt ~/example/once.txt
