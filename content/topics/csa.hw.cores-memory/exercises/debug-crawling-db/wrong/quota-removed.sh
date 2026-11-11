# Wrong: the throttling stops because the CPU cap is gone altogether (an
# empty CPUQuota= clears it). The database may use one and a half CPUs and
# no more, so the cap has to stay, raised to fit its work.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nCPUQuota=\nMemoryHigh=infinity\nAllowedCPUs=\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
sleep 3
