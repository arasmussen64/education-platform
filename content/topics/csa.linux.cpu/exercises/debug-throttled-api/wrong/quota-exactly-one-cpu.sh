# Wrong: the cap is raised to exactly the one CPU the work needs, with no
# headroom. The kernel still stops the service a few times every ten
# seconds, because a job that uses all of its quota runs out now and then.
sudo mkdir -p /etc/systemd/system/shop-api.service.d
printf '[Service]\nCPUQuota=100%%\nNice=0\nCPUWeight=100\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-api
sleep 2
