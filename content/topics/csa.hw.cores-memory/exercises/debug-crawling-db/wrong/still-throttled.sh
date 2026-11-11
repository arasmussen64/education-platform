# Wrong: the cap is raised, but to 60% of a CPU, still short of the whole CPU
# the database's work keeps busy, so the kernel stops it every period. The
# other two faults are fixed, so only the CPU checks fail.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nCPUQuota=60%%\nMemoryHigh=infinity\nAllowedCPUs=\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
sleep 3
