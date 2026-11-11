# Wrong: the database gets the whole allowance because the nightly sort
# is stopped, and disabled so it stays stopped. The sort's work still has
# to be done every night. The cap and the spool are put right.
sudo sed -i 's|^IOWriteIOPSMax=/dev/lab/data 16$|IOWriteIOPSMax=/dev/lab/data 400|' /etc/systemd/system/shop.slice.d/data-disk.conf
sudo sed -i 's|^SPOOL_DIR=.*|SPOOL_DIR=/srv/data/spool|' /etc/shop/shop.conf
sudo systemctl daemon-reload
sudo systemctl disable --now shop-sort
sudo systemctl restart shop-db
sleep 3
