# Wrong: the CPU cap and the memory throttle are fixed, and CPU 0 is given to
# the database by stopping the batch job, which has to keep running.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nCPUQuota=150%%\nMemoryHigh=infinity\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
sudo systemctl stop shop-batch
sleep 3
