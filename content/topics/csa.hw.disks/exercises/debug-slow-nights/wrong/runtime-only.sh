# Wrong: the cap is put right with set-property --runtime, which lasts
# only until the next reboot (the setting lives under /run); the file in
# /etc still says 16, and the next boot brings the fault back. The other
# two faults are fixed in files, so they last.
sudo systemctl set-property --runtime shop.slice "IOWriteIOPSMax=/dev/lab/data 400"
sudo mkdir -p /etc/systemd/system/shop-sort.service.d
printf '[Service]\nEnvironment=TMPDIR=/srv/scratch/sort-tmp\n' | sudo tee /etc/systemd/system/shop-sort.service.d/scratch.conf > /dev/null
sudo sed -i 's|^SPOOL_DIR=.*|SPOOL_DIR=/srv/data/spool|' /etc/shop/shop.conf
sudo systemctl daemon-reload
sudo systemctl restart shop-db shop-sort
sleep 3
