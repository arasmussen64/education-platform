# Wrong: the throttling stops because the cap is gone altogether (an empty
# CPUQuota= clears it). On a machine of its own that could be the right
# answer; on this shared one the cap has to stay, with room for the work.
sudo mkdir -p /etc/systemd/system/shop-api.service.d
printf '[Service]\nCPUQuota=\nNice=0\nCPUWeight=100\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-api
sleep 2
