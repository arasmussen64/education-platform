# Wrong: the quota and the weight are fixed, but the process still runs at
# nice 19, last in line whenever a CPU is contended.
sudo mkdir -p /etc/systemd/system/shop-api.service.d
printf '[Service]\nCPUQuota=200%%\nCPUWeight=100\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-api
sleep 2
