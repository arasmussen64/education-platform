# Wrong: the priority and the weight are fixed, but the 5% quota still
# throttles the API every period, and a quota doesn't care about priority.
sudo mkdir -p /etc/systemd/system/shop-api.service.d
printf '[Service]\nNice=0\nCPUWeight=100\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-api
sleep 2
