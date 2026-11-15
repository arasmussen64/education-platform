# Wrong: iostat is run without an interval, so it prints one report, the
# average since the machine started, in which a disk that has been
# saturated for the last few minutes looks nearly idle. The fix itself is
# right.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" > ~/triage/iostat-before.txt
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
sudo sed -i 's/^TRACE=on$/TRACE=off/' /etc/shop/sync.conf
sudo systemctl restart shop-sync
sleep 3
