# Wrong: the cap and the spool are put right, and the sort is moved out of
# the shop's slice (to system.slice) instead of off the data disk. Its big
# writes no longer count against the slice's allowance, so the database
# gets the whole of it; but on the cloud the disk itself would still hold
# every writer on the server to 400 writes and 6 MiB a second, together,
# and the sort's scratch files would still spend them.
sudo sed -i 's|^IOWriteIOPSMax=/dev/lab/data 16$|IOWriteIOPSMax=/dev/lab/data 400|' /etc/systemd/system/shop.slice.d/data-disk.conf
sudo mkdir -p /etc/systemd/system/shop-sort.service.d
printf '[Service]\nSlice=system.slice\n' | sudo tee /etc/systemd/system/shop-sort.service.d/slice.conf > /dev/null
sudo sed -i 's|^SPOOL_DIR=.*|SPOOL_DIR=/srv/data/spool|' /etc/shop/shop.conf
sudo systemctl daemon-reload
sudo systemctl restart shop-db shop-sort
sleep 3
