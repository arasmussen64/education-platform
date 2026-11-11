# Wrong: the cap is put right in its file, but the two folders are moved
# with drop-ins under /run, as "systemctl edit --runtime" makes them. The
# services use the new folders now, and the next reboot forgets the
# drop-ins: the sort is back on the data disk and the spool on the local
# disk.
sudo sed -i 's|^IOWriteIOPSMax=/dev/lab/data 16$|IOWriteIOPSMax=/dev/lab/data 400|' /etc/systemd/system/shop.slice.d/data-disk.conf
sudo mkdir -p /run/systemd/system/shop-sort.service.d /run/systemd/system/shop-db.service.d
printf '[Service]\nEnvironment=TMPDIR=/srv/scratch/sort-tmp\n' | sudo tee /run/systemd/system/shop-sort.service.d/override.conf > /dev/null
printf '[Service]\nEnvironmentFile=\nEnvironment=DATA_DIR=/srv/data/db SPOOL_DIR=/srv/data/spool\n' | sudo tee /run/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db shop-sort
sleep 3
