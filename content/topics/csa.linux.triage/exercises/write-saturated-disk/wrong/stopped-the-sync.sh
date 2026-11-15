# Wrong: the evidence and the finding are right, and then shop-sync is
# stopped and disabled. Orders are quick, because nothing else writes to
# the disk, but the search page no longer gets its products: the service's
# work still has to be done.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
sudo systemctl disable --now shop-sync
sleep 2
