# Wrong: the trace is left on, and shop-sync is moved out of the shop's
# slice (to system.slice) with a drop-in that lasts. Its writes no longer
# count against the slice's allowance, so orders are quick on the lab
# machine. On the cloud the disk itself would still hold every writer on
# the server to 100 writes a second, together, and the trace would still
# spend them.
disk=$(findmnt -n -o SOURCE /srv/data)
mkdir -p ~/triage
iostat -x "$disk" 1 4 > ~/triage/iostat-before.txt
printf 'culprit: shop-sync\nwhat: its debug trace, written straight to the data disk\n' > ~/triage/finding.txt
sudo mkdir -p /etc/systemd/system/shop-sync.service.d
printf '[Service]\nSlice=system.slice\n' | sudo tee /etc/systemd/system/shop-sync.service.d/slice.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-sync
sleep 3
