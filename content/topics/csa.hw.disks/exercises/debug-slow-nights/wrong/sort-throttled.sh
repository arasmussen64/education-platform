# Wrong: the cap and the spool are put right, and the sort is held to a
# small cap of its own on the data disk instead of being moved off it. The
# database gets more of the allowance, but the sort's scratch files still
# spend some of it, and the sort no longer gets through its night's work.
sudo sed -i 's|^IOWriteIOPSMax=/dev/lab/data 16$|IOWriteIOPSMax=/dev/lab/data 400|' /etc/systemd/system/shop.slice.d/data-disk.conf
sudo mkdir -p /etc/systemd/system/shop-sort.service.d
printf '[Service]\nIOWriteBandwidthMax=/dev/lab/data 1048576\n' | sudo tee /etc/systemd/system/shop-sort.service.d/cap.conf > /dev/null
sudo sed -i 's|^SPOOL_DIR=.*|SPOOL_DIR=/srv/data/spool|' /etc/shop/shop.conf
sudo systemctl daemon-reload
sudo systemctl restart shop-db shop-sort
sleep 3
