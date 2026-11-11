# Which disk are the tables on? findmnt names the device behind /srv/data,
# and ls -l /dev/lab/ shows which label points at it: data.
findmnt -T /srv/data/db; ls -l /dev/lab/
# The finished drop-in. In the lab you'd fill the four gaps with
# sudo nano /etc/systemd/system/shop-db.service.d/tier.conf; here it's
# written in one go. 3 MiB is 3 x 1,048,576 = 3,145,728 bytes: systemd
# would read 3M as 3,000,000.
sudo tee /etc/systemd/system/shop-db.service.d/tier.conf > /dev/null <<'EOF'
# shop-db under the new disk tier's allowance: 300 writes a second and
# 3 MiB a second, on the disk its tables are on.
[Service]
IOWriteIOPSMax=/dev/lab/data 300
IOWriteBandwidthMax=/dev/lab/data 3145728
EOF
sudo systemctl daemon-reload
sudo systemctl restart shop-db
systemctl show shop-db -p IOWriteIOPSMax -p IOWriteBandwidthMax
cat /sys/fs/cgroup/system.slice/shop-db.service/io.max
