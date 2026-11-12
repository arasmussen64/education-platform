# Wrong: a cap only just over the one CPU the work needs, 110%. It keeps a
# cap and looks like headroom, but the prompt's rule asks for at least one
# and a half CPUs, and a cap this tight can still throttle the service now
# and then. cap-kept must fail.
sudo mkdir -p /etc/systemd/system/shop-api.service.d
printf '[Service]\nCPUQuota=110%%\nNice=0\nCPUWeight=100\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-api
sleep 2
