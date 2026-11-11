# Wrong: the 400 goes on reads, and the write cap goes. The database
# hardly reads, so the cap that holds it back is the one that's gone, and
# nothing holds the shop's writes to the disk's allowance any more. The
# other two faults are fixed.
sudo sed -i 's|^IOWriteIOPSMax=/dev/lab/data 16$|IOReadIOPSMax=/dev/lab/data 400|' /etc/systemd/system/shop.slice.d/data-disk.conf
sudo mkdir -p /etc/systemd/system/shop-sort.service.d
printf '[Service]\nEnvironment=TMPDIR=/srv/scratch/sort-tmp\n' | sudo tee /etc/systemd/system/shop-sort.service.d/scratch.conf > /dev/null
sudo sed -i 's|^SPOOL_DIR=.*|SPOOL_DIR=/srv/data/spool|' /etc/shop/shop.conf
sudo systemctl daemon-reload
sudo systemctl restart shop-db shop-sort
sleep 3
