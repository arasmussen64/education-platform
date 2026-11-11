# Wrong: the CPU cap and the memory throttle are fixed, but the database is
# still pinned to CPU 0, where it takes turns with the batch job while the
# other CPUs idle. Only the CPU-list check fails.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nCPUQuota=150%%\nMemoryHigh=infinity\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
sleep 3
