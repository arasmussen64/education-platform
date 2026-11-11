# Wrong: the right drop-in, and systemd reloaded, but shop-db never
# restarted. The new CPU cap and memory throttle reach the running service;
# the emptied CPU list doesn't, and its process stays on CPU 0.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nCPUQuota=150%%\nMemoryHigh=infinity\nAllowedCPUs=\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sleep 3
