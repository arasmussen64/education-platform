# Wrong: the trace stays on and shop-sync is cut from 32 workers to 2.
# Two writers can't fill the disk's queue, so orders are quick again, but
# the search page now gets about 20 products a second instead of 320, and
# the service still writes its trace to the data disk.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
sudo sed -i 's/^WORKERS=32$/WORKERS=2/' /etc/shop/sync.conf
sudo systemctl restart shop-sync
sleep 3
