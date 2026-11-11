# Wrong: the spool leaves the local disk for /tmp. That isn't the data
# disk either: on Ubuntu, systemd empties /tmp at every boot (the "D /tmp"
# line in /usr/lib/tmpfiles.d/tmp.conf), so the orders would still be lost
# at the next stop. The cap and the sort are put right.
sudo sed -i 's|^IOWriteIOPSMax=/dev/lab/data 16$|IOWriteIOPSMax=/dev/lab/data 400|' /etc/systemd/system/shop.slice.d/data-disk.conf
sudo mkdir -p /etc/systemd/system/shop-sort.service.d
printf '[Service]\nEnvironment=TMPDIR=/srv/scratch/sort-tmp\n' | sudo tee /etc/systemd/system/shop-sort.service.d/scratch.conf > /dev/null
sudo sed -i 's|^SPOOL_DIR=.*|SPOOL_DIR=/tmp/spool|' /etc/shop/shop.conf
sudo systemctl daemon-reload
sudo systemctl restart shop-db shop-sort
sleep 3
