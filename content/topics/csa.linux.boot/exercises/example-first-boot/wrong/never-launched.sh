# Wrong: the walkthrough rebooted twice and never launched a new instance,
# so first-boot.txt still has one line and once.txt is 1.
cloud-init status --long > /dev/null
lab-reboot > /dev/null
lab-reboot > /dev/null
mkdir -p ~/example
{ cloud-init status | head -1; echo "hostname: $(hostname)"; echo "instance: $(cloud-init query instance_id)"; } > ~/example/configured.txt
wc -l < /var/lib/shop/first-boot.txt | tr -d ' ' > ~/example/once.txt
