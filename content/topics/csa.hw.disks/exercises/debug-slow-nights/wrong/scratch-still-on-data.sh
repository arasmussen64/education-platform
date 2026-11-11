# Wrong: the cap and the spool are put right, and the sort is left with
# its scratch folder on the data disk. Its big writes still spend most of
# the disk's 6 MiB a second, and the database gets about a hundred writes
# a second of its 400.
sudo sed -i 's|^IOWriteIOPSMax=/dev/lab/data 16$|IOWriteIOPSMax=/dev/lab/data 400|' /etc/systemd/system/shop.slice.d/data-disk.conf
sudo sed -i 's|^SPOOL_DIR=.*|SPOOL_DIR=/srv/data/spool|' /etc/shop/shop.conf
sudo systemctl daemon-reload
sudo systemctl restart shop-db
sleep 3
