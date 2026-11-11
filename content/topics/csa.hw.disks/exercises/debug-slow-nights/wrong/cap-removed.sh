# Wrong: the cap is taken away instead of put right. The database is
# quick on the lab machine, and on the cloud the disk would still hold it
# to 400 writes a second: the lab no longer behaves like the server it
# stands in for. The other two faults are fixed.
sudo rm /etc/systemd/system/shop.slice.d/data-disk.conf
sudo mkdir -p /etc/systemd/system/shop-sort.service.d
printf '[Service]\nEnvironment=TMPDIR=/srv/scratch/sort-tmp\n' | sudo tee /etc/systemd/system/shop-sort.service.d/scratch.conf > /dev/null
sudo sed -i 's|^SPOOL_DIR=.*|SPOOL_DIR=/srv/data/spool|' /etc/shop/shop.conf
sudo systemctl daemon-reload
sudo systemctl restart shop-db shop-sort
sleep 3
