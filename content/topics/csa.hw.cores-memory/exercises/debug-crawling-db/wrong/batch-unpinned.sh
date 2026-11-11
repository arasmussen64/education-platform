# Wrong: the database is freed from CPU 0, but so is the batch job, which is
# kept there on purpose so that it can never take the other CPUs.
sudo mkdir -p /etc/systemd/system/shop-db.service.d /etc/systemd/system/shop-batch.service.d
printf '[Service]\nCPUQuota=150%%\nMemoryHigh=infinity\nAllowedCPUs=\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
printf '[Service]\nAllowedCPUs=\n' | sudo tee /etc/systemd/system/shop-batch.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db shop-batch
sleep 3
