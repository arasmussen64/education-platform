# Wrong: the settings file is corrected and the service is never
# restarted. shop-sync read the file when it started, so it is still
# tracing, the disk is still saturated and orders are still slow.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
sudo sed -i 's/^TRACE=on$/TRACE=off/' /etc/shop/sync.conf
sleep 2
