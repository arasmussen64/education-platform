# Wrong: the fix is right, but iostat's reports are saved after it. They
# show a quiet disk, which is proof of nothing: the evidence of the
# saturation went with the fault.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
sudo sed -i 's/^TRACE=on$/TRACE=off/' /etc/shop/sync.conf
sudo systemctl restart shop-sync
sleep 3
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
