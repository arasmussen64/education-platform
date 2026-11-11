# Wrong: the quota and the priority are fixed, but the cgroup's weight is
# still 1, so under contention it gets a hundredth of a fair share.
sudo mkdir -p /etc/systemd/system/shop-api.service.d
printf '[Service]\nCPUQuota=200%%\nNice=0\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-api
sleep 2
