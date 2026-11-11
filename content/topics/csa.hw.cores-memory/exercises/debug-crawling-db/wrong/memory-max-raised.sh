# Wrong: the paging stops because the hard limit was raised as well, past the
# 256 MB the database may have. The batch job needs the rest of the memory.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nCPUQuota=150%%\nMemoryHigh=infinity\nMemoryMax=512M\nAllowedCPUs=\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
sleep 3
