# Wrong: the throttle is raised, but to 64M, still far below the 150 MB the
# database keeps its tables in, so the kernel goes on slowing it. The other
# two faults are fixed, so only the memory check fails.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nCPUQuota=150%%\nMemoryHigh=64M\nAllowedCPUs=\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
sleep 3
