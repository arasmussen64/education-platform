# Wrong: the trace is switched off, which is the right fix, but the file
# that gives shop.slice the disk's allowance was deleted on the way.
# Nothing shows it today, because the kernel keeps the limit it was given
# when the slice started. At the next boot the slice starts with no limit
# at all, and the lab stops behaving like the cloud server it stands in
# for.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
sudo rm /etc/systemd/system/shop.slice.d/data-disk.conf
sudo systemctl daemon-reload
sudo sed -i 's/^TRACE=on$/TRACE=off/' /etc/shop/sync.conf
sudo systemctl restart shop-sync
sleep 3
