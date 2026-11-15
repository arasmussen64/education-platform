# Wrong: the trace stays on, and shop-sync is given a write cap of its own
# on the data disk, 20 writes a second, in a drop-in that lasts. Orders are
# quick again, because the disk's queue is no longer full, but every worker
# still waits for its trace record: the service gets through about 20
# products a second instead of 320, and still spends a fifth of the disk's
# allowance on records nobody reads.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
sudo mkdir -p /etc/systemd/system/shop-sync.service.d
printf '[Service]\nIOWriteIOPSMax=/dev/lab/data 20\n' | sudo tee /etc/systemd/system/shop-sync.service.d/cap.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-sync
sleep 3
