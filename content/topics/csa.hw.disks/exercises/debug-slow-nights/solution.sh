# The three faults:
#   1. The shop's slice held writes to the data disk to 16 a second, a
#      twenty-fifth of the 400 the disk is provisioned for
#      (/etc/systemd/system/shop.slice.d/data-disk.conf). Everything the
#      shop wrote there waited its turn for 16 slots a second.
#   2. The nightly sort's scratch folder (TMPDIR in its unit) was on the
#      data disk, so its big writes spent the allowance the database needs:
#      with the cap put right, the sort still took most of the 6 MiB a
#      second and left the database about a hundred writes a second.
#      Scratch files belong on the local disk, which is fast, costs the
#      data disk nothing, and doesn't need to keep anything.
#   3. The order spool (SPOOL_DIR in /etc/shop/shop.conf) was on the local
#      disk, which comes back empty after every stop: the weekend's orders
#      were still in the spool on Sunday, and the stop wiped them.
# Look first: what the services run in and with, what the slice allows,
# and which disk each folder is on.
systemctl status shop-db shop-sort --no-pager | grep -E 'CGroup|Active'
systemctl cat shop.slice shop-sort
cat /etc/shop/shop.conf
findmnt -T /srv/data/sort-tmp; findmnt -T /srv/scratch/spool
# 1. The allowance (in the lab you'd edit it with sudo nano).
sudo sed -i 's|^IOWriteIOPSMax=/dev/lab/data 16$|IOWriteIOPSMax=/dev/lab/data 400|' /etc/systemd/system/shop.slice.d/data-disk.conf
# 2. The sort's scratch folder, with a drop-in (sudo systemctl edit shop-sort).
sudo mkdir -p /etc/systemd/system/shop-sort.service.d
printf '[Service]\nEnvironment=TMPDIR=/srv/scratch/sort-tmp\n' | sudo tee /etc/systemd/system/shop-sort.service.d/scratch.conf > /dev/null
# 3. The spool, on the data disk.
sudo sed -i 's|^SPOOL_DIR=.*|SPOOL_DIR=/srv/data/spool|' /etc/shop/shop.conf
sudo systemctl daemon-reload
sudo systemctl restart shop-db shop-sort
# The orders still in the old spool move with it, so none is lost.
sudo sh -c 'mv /srv/scratch/spool/order-* /srv/data/spool/ 2>/dev/null' || true
cat /sys/fs/cgroup/shop.slice/io.max
sleep 12
journalctl -u shop-db -n 1 -o cat --no-pager
